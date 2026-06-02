from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.project import Project, ProjectMember, ProjectTask, TaskComment
from app.models.user import User
from app.schemas.task import (
    CommentCreate,
    CommentResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.audit_service import log_action
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/tasks", tags=["tasks"])
VALID_STATUS = {"pending", "in_progress", "completed", "blocked"}


def _to_task_response(task: ProjectTask) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        project_name=task.project.name if task.project else None,
        title=task.title,
        description=task.description,
        priority=task.priority,
        assigned_employee_id=task.assigned_employee_id,
        assignee_name=task.assignee.full_name if task.assignee else None,
        assigned_by_name=task.assigned_by.name if task.assigned_by else None,
        due_date=task.due_date,
        status=task.status,
        created_at=task.created_at,
    )


@router.get("", response_model=TaskListResponse)
def list_tasks(
    search: str | None = None,
    status: str | None = None,
    project_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ProjectTask).options(
        joinedload(ProjectTask.project),
        joinedload(ProjectTask.assignee),
        joinedload(ProjectTask.assigned_by),
    )
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee:
            return TaskListResponse(items=[], total=0, page=page, page_size=page_size)
        query = query.filter(ProjectTask.assigned_employee_id == employee.id)
    if search:
        query = query.filter(ProjectTask.title.ilike(f"%{search.lower()}%"))
    if status:
        query = query.filter(ProjectTask.status == status)
    if project_id:
        query = query.filter(ProjectTask.project_id == project_id)
    query = query.order_by(ProjectTask.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return TaskListResponse(
        items=[_to_task_response(t) for t in rows], total=total, page=page, page_size=page_size
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if payload.status not in VALID_STATUS:
        raise HTTPException(status_code=400, detail="Invalid status")
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    task = ProjectTask(
        project_id=payload.project_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        assigned_employee_id=payload.assigned_employee_id,
        assigned_by_user_id=current_user.id,
        due_date=payload.due_date,
        status=payload.status,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    log_action(db, user=current_user, action="Task Created", entity_type="task", entity_id=task.id, ip_address=get_client_ip(request))
    db.commit()
    if task.assignee and task.assignee.user:
        NotificationService.task_assigned(task.assignee.user.email, task.title, project.name)
    task = db.query(ProjectTask).options(
        joinedload(ProjectTask.project), joinedload(ProjectTask.assignee), joinedload(ProjectTask.assigned_by)
    ).filter(ProjectTask.id == task.id).first()
    return _to_task_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    task = db.query(ProjectTask).filter(ProjectTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field in ["title", "description", "priority", "assigned_employee_id", "due_date", "status", "project_id"]:
        val = getattr(payload, field)
        if val is not None:
            if field == "status" and val not in VALID_STATUS:
                raise HTTPException(status_code=400, detail="Invalid status")
            setattr(task, field, val)
    db.commit()
    log_action(db, user=current_user, action="Task Updated", entity_type="task", entity_id=task.id, ip_address=get_client_ip(request))
    db.commit()
    task = db.query(ProjectTask).options(
        joinedload(ProjectTask.project), joinedload(ProjectTask.assignee), joinedload(ProjectTask.assigned_by)
    ).filter(ProjectTask.id == task_id).first()
    return _to_task_response(task)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in VALID_STATUS:
        raise HTTPException(status_code=400, detail="Invalid status")
    task = db.query(ProjectTask).filter(ProjectTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee or task.assigned_employee_id != employee.id:
            raise HTTPException(status_code=403, detail="Not your task")
    task.status = payload.status
    db.commit()
    log_action(db, user=current_user, action=f"Task Status -> {payload.status}", entity_type="task", entity_id=task.id, ip_address=get_client_ip(request))
    db.commit()
    task = db.query(ProjectTask).options(
        joinedload(ProjectTask.project), joinedload(ProjectTask.assignee), joinedload(ProjectTask.assigned_by)
    ).filter(ProjectTask.id == task_id).first()
    return _to_task_response(task)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    task = db.query(ProjectTask).filter(ProjectTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    log_action(db, user=current_user, action="Task Deleted", entity_type="task", entity_id=task_id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Task deleted"}


@router.get("/{task_id}/comments", response_model=list[CommentResponse])
def list_comments(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(ProjectTask).filter(ProjectTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comments = (
        db.query(TaskComment)
        .options(joinedload(TaskComment.user))
        .filter(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
        .all()
    )
    return [CommentResponse(id=c.id, user_name=c.user.name, comment=c.comment, created_at=c.created_at) for c in comments]


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(ProjectTask).filter(ProjectTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comment = TaskComment(task_id=task_id, user_id=current_user.id, comment=payload.comment)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentResponse(id=comment.id, user_name=current_user.name, comment=comment.comment, created_at=comment.created_at)
