from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate
from app.services.audit_service import log_action
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/projects", tags=["projects"])


def _member_brief(emp: Employee):
    return {"id": emp.id, "employee_code": emp.employee_code, "name": emp.full_name}


def _to_response(project: Project) -> ProjectResponse:
    members = [_member_brief(m.employee) for m in project.members if m.employee]
    return ProjectResponse(
        id=project.id,
        name=project.name,
        client_name=project.client_name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        status=project.status,
        project_lead_id=project.project_lead_id,
        tech_owner_id=project.tech_owner_id,
        project_lead_name=project.project_lead.full_name if project.project_lead else None,
        tech_owner_name=project.tech_owner.full_name if project.tech_owner else None,
        members=members,
        task_count=len(project.tasks),
        created_at=project.created_at,
    )


def _sync_members(db: Session, project: Project, member_ids: list[int]):
    project.members.clear()
    seen = set()
    for eid in member_ids:
        if eid in seen:
            continue
        seen.add(eid)
        emp = db.query(Employee).filter(Employee.id == eid).first()
        if emp:
            db.add(ProjectMember(project_id=project.id, employee_id=eid))
    if project.project_lead_id and project.project_lead_id not in seen:
        db.add(ProjectMember(project_id=project.id, employee_id=project.project_lead_id))
    if project.tech_owner_id and project.tech_owner_id not in seen:
        db.add(ProjectMember(project_id=project.id, employee_id=project.tech_owner_id))


@router.get("", response_model=ProjectListResponse)
def list_projects(
    search: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Project).options(
        joinedload(Project.members).joinedload(ProjectMember.employee),
        joinedload(Project.project_lead),
        joinedload(Project.tech_owner),
        joinedload(Project.tasks),
    )
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee:
            return ProjectListResponse(items=[], total=0, page=page, page_size=page_size)
        query = query.join(ProjectMember).filter(ProjectMember.employee_id == employee.id).distinct()
    if search:
        term = f"%{search.lower()}%"
        query = query.filter((Project.name.ilike(term)) | (Project.client_name.ilike(term)))
    if status:
        query = query.filter(Project.status == status)
    query = query.order_by(Project.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return ProjectListResponse(
        items=[_to_response(p) for p in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = (
        db.query(Project)
        .options(
            joinedload(Project.members).joinedload(ProjectMember.employee),
            joinedload(Project.project_lead),
            joinedload(Project.tech_owner),
            joinedload(Project.tasks),
        )
        .filter(Project.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee or not any(m.employee_id == employee.id for m in project.members):
            raise HTTPException(status_code=403, detail="Not assigned to this project")
    return _to_response(project)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    project = Project(
        name=payload.name,
        client_name=payload.client_name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=payload.status,
        project_lead_id=payload.project_lead_id,
        tech_owner_id=payload.tech_owner_id,
    )
    db.add(project)
    db.flush()
    _sync_members(db, project, payload.member_ids)
    db.commit()
    db.refresh(project)
    log_action(db, user=current_user, action="Project Created", entity_type="project", entity_id=project.id, ip_address=get_client_ip(request))
    db.commit()
    for m in project.members:
        if m.employee and m.employee.user:
            NotificationService.project_assigned(m.employee.user.email, project.name)
    project = db.query(Project).options(
        joinedload(Project.members).joinedload(ProjectMember.employee),
        joinedload(Project.project_lead),
        joinedload(Project.tech_owner),
        joinedload(Project.tasks),
    ).filter(Project.id == project.id).first()
    return _to_response(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field in ["name", "client_name", "description", "start_date", "end_date", "status", "project_lead_id", "tech_owner_id"]:
        val = getattr(payload, field)
        if val is not None:
            setattr(project, field, val)
    if payload.member_ids is not None:
        _sync_members(db, project, payload.member_ids)
    db.commit()
    log_action(db, user=current_user, action="Project Updated", entity_type="project", entity_id=project.id, ip_address=get_client_ip(request))
    db.commit()
    project = db.query(Project).options(
        joinedload(Project.members).joinedload(ProjectMember.employee),
        joinedload(Project.project_lead),
        joinedload(Project.tech_owner),
        joinedload(Project.tasks),
    ).filter(Project.id == project_id).first()
    return _to_response(project)


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    log_action(db, user=current_user, action="Project Deleted", entity_type="project", entity_id=project_id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Project deleted"}
