import os
import uuid
from pathlib import Path

from sqlalchemy.orm import Session, joinedload

from app.core.security import get_password_hash
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.employee_address import EmployeeAddress
from app.models.employee_bank import EmployeeBankDetail
from app.models.employee_document import EmployeeDocument
from app.models.employee_education import EmployeeEducation
from app.models.employee_experience import EmployeeExperience
from app.models.employee_family import EmployeeFamily
from app.models.employee_interest import EmployeeInterest
from app.models.employee_language import EmployeeLanguage
from app.models.employee_skills import EmployeeSkills
from app.models.leave import LeaveApplication, LeaveBalance
from app.models.sod_eod import EODEntry, SODEntry
from app.models.user import User
from app.schemas.employee import (
    AddressSchema,
    BankDetailsSchema,
    EducationSchema,
    EmployeeListItem,
    EmployeeProfileCreate,
    EmployeeProfileFull,
    EmployeeProfileUpdate,
    ExperienceSchema,
    FamilyMemberSchema,
    LanguageSchema,
    SkillsSchema,
)

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "employees"


def _address_by_type(employee: Employee, address_type: str) -> AddressSchema | None:
    for addr in employee.addresses:
        if addr.address_type == address_type:
            return AddressSchema(
                address_line_1=addr.address_line_1,
                address_line_2=addr.address_line_2,
                city=addr.city,
                state=addr.state,
                country=addr.country,
                pin_code=addr.pin_code,
            )
    return None


def _set_addresses(db: Session, employee: Employee, permanent: AddressSchema | None, correspondence: AddressSchema | None, same: bool):
    employee.addresses.clear()
    if permanent:
        db.add(
            EmployeeAddress(
                employee_id=employee.id,
                address_type="permanent",
                address_line_1=permanent.address_line_1,
                address_line_2=permanent.address_line_2,
                city=permanent.city,
                state=permanent.state,
                country=permanent.country,
                pin_code=permanent.pin_code,
            )
        )
    corr = correspondence
    if same and permanent:
        corr = permanent
    if corr:
        db.add(
            EmployeeAddress(
                employee_id=employee.id,
                address_type="correspondence",
                address_line_1=corr.address_line_1,
                address_line_2=corr.address_line_2,
                city=corr.city,
                state=corr.state,
                country=corr.country,
                pin_code=corr.pin_code,
            )
        )


def _set_family(db: Session, employee: Employee, members: list[FamilyMemberSchema]):
    employee.family_members.clear()
    for m in members:
        if not m.name.strip():
            continue
        db.add(
            EmployeeFamily(
                employee_id=employee.id,
                name=m.name,
                relation_type=m.relationship,
                date_of_birth=m.date_of_birth,
                occupation=m.occupation,
                company=m.company,
            )
        )


def _set_education(db: Session, employee: Employee, items: list[EducationSchema]):
    employee.education.clear()
    for e in items:
        if not any([e.degree, e.institute]):
            continue
        db.add(
            EmployeeEducation(
                employee_id=employee.id,
                degree=e.degree,
                institute=e.institute,
                board_university=e.board_university,
                year_of_passing=e.year_of_passing,
                percentage=e.percentage,
                major_subjects=e.major_subjects,
            )
        )


def _set_experience(db: Session, employee: Employee, items: list[ExperienceSchema]):
    employee.experience.clear()
    for x in items:
        if not x.company_name:
            continue
        db.add(
            EmployeeExperience(
                employee_id=employee.id,
                company_name=x.company_name,
                industry=x.industry,
                designation=x.designation,
                employment_type=x.employment_type,
                start_date=x.start_date,
                end_date=x.end_date,
                reason_for_leaving=x.reason_for_leaving,
            )
        )


def _set_bank(db: Session, employee: Employee, bank: BankDetailsSchema | None):
    if employee.bank_details:
        db.delete(employee.bank_details)
    if not bank or not any([bank.bank_name, bank.account_number]):
        return
    db.add(
        EmployeeBankDetail(
            employee_id=employee.id,
            bank_name=bank.bank_name,
            account_number=bank.account_number,
            ifsc_code=bank.ifsc_code,
            branch_name=bank.branch_name,
            branch_address=bank.branch_address,
        )
    )


def _set_skills(db: Session, employee: Employee, skills: SkillsSchema | None):
    if employee.skills:
        db.delete(employee.skills)
    if not skills:
        return
    db.add(
        EmployeeSkills(
            employee_id=employee.id,
            certification_name=skills.certification_name,
            certification_provider=skills.certification_provider,
            certification_issue_date=skills.certification_issue_date,
            certification_expiry_date=skills.certification_expiry_date,
            technical_skills=skills.technical_skills,
            soft_skills=skills.soft_skills,
            programming_languages=skills.programming_languages,
            frameworks=skills.frameworks,
            tools=skills.tools,
        )
    )


def _set_languages(db: Session, employee: Employee, langs: list[LanguageSchema]):
    employee.languages.clear()
    for lang in langs:
        if not lang.language.strip():
            continue
        db.add(
            EmployeeLanguage(
                employee_id=employee.id,
                language=lang.language,
                can_speak=lang.can_speak,
                can_read=lang.can_read,
                can_write=lang.can_write,
                can_understand=lang.can_understand,
            )
        )


def _set_interests(db: Session, employee: Employee, interests: list[str]):
    employee.interests.clear()
    for interest in interests:
        if interest.strip():
            db.add(EmployeeInterest(employee_id=employee.id, interest=interest.strip()))


def _apply_scalar_fields(employee: Employee, data: EmployeeProfileCreate | EmployeeProfileUpdate):
    scalar_fields = [
        "employee_id",
        "employee_code",
        "designation",
        "department",
        "joining_date",
        "employment_type",
        "reporting_manager",
        "project_lead",
        "tech_owner",
        "company_email",
        "employment_status",
        "manager_name",
        "title",
        "first_name",
        "middle_name",
        "last_name",
        "gender",
        "father_name",
        "date_of_birth",
        "nationality",
        "marital_status",
        "anniversary_date",
        "number_of_children",
        "blood_group",
        "pan_number",
        "aadhaar_number",
        "passport_number",
        "passport_issue_date",
        "passport_expiry_date",
        "passport_issue_place",
        "mobile_number",
        "alternate_number",
        "personal_email",
    ]
    for field in scalar_fields:
        value = getattr(data, field, None)
        if value is not None:
            setattr(employee, field, value)


def list_employees(db: Session, search: str | None, department: str | None, page: int, page_size: int):
    query = db.query(Employee).join(User, Employee.user_id == User.id).options(joinedload(Employee.user))
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            (User.name.ilike(term))
            | (User.email.ilike(term))
            | (Employee.employee_code.ilike(term))
            | (Employee.first_name.ilike(term))
            | (Employee.last_name.ilike(term))
            | (Employee.company_email.ilike(term))
        )
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    query = query.order_by(Employee.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    items = [
        EmployeeListItem(
            id=e.id,
            employee_code=e.employee_code,
            name=e.full_name,
            designation=e.designation,
            department=e.department,
            company_email=e.company_email or (e.user.email if e.user else None),
            joining_date=e.joining_date,
            status=e.employment_status,
        )
        for e in rows
    ]
    return items, total


def get_employee_full(db: Session, employee_id: int) -> Employee | None:
    return (
        db.query(Employee)
        .options(
            joinedload(Employee.user),
            joinedload(Employee.addresses),
            joinedload(Employee.documents),
            joinedload(Employee.family_members),
            joinedload(Employee.bank_details),
            joinedload(Employee.education),
            joinedload(Employee.experience),
            joinedload(Employee.skills),
            joinedload(Employee.languages),
            joinedload(Employee.interests),
        )
        .filter(Employee.id == employee_id)
        .first()
    )


def build_profile_response(db: Session, employee: Employee) -> EmployeeProfileFull:
    from app.schemas.employee import DocumentSchema, LeaveSummary, AttendanceSummary

    skills = None
    if employee.skills:
        skills = SkillsSchema(
            certification_name=employee.skills.certification_name,
            certification_provider=employee.skills.certification_provider,
            certification_issue_date=employee.skills.certification_issue_date,
            certification_expiry_date=employee.skills.certification_expiry_date,
            technical_skills=employee.skills.technical_skills,
            soft_skills=employee.skills.soft_skills,
            programming_languages=employee.skills.programming_languages,
            frameworks=employee.skills.frameworks,
            tools=employee.skills.tools,
        )

    attendance = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee.id)
        .order_by(Attendance.date.desc())
        .limit(30)
        .all()
    )
    leaves = (
        db.query(LeaveApplication)
        .filter(LeaveApplication.employee_id == employee.id)
        .order_by(LeaveApplication.created_at.desc())
        .limit(20)
        .all()
    )

    return EmployeeProfileFull(
        id=employee.id,
        user_id=employee.user_id,
        employee_id=employee.employee_id,
        employee_code=employee.employee_code,
        login_email=employee.user.email,
        full_name=employee.full_name,
        designation=employee.designation,
        department=employee.department,
        joining_date=employee.joining_date,
        employment_type=employee.employment_type,
        reporting_manager=employee.reporting_manager,
        project_lead=employee.project_lead,
        tech_owner=employee.tech_owner,
        company_email=employee.company_email,
        employment_status=employee.employment_status,
        manager_name=employee.manager_name,
        title=employee.title,
        first_name=employee.first_name,
        middle_name=employee.middle_name,
        last_name=employee.last_name,
        gender=employee.gender,
        father_name=employee.father_name,
        date_of_birth=employee.date_of_birth,
        nationality=employee.nationality,
        marital_status=employee.marital_status,
        anniversary_date=employee.anniversary_date,
        number_of_children=employee.number_of_children,
        blood_group=employee.blood_group,
        profile_photo_path=employee.profile_photo_path,
        pan_number=employee.pan_number,
        aadhaar_number=employee.aadhaar_number,
        passport_number=employee.passport_number,
        passport_issue_date=employee.passport_issue_date,
        passport_expiry_date=employee.passport_expiry_date,
        passport_issue_place=employee.passport_issue_place,
        mobile_number=employee.mobile_number,
        alternate_number=employee.alternate_number,
        personal_email=employee.personal_email,
        permanent_address=_address_by_type(employee, "permanent"),
        correspondence_address=_address_by_type(employee, "correspondence"),
        family_members=[
            FamilyMemberSchema(
                name=f.name,
                relationship=f.relation_type,
                date_of_birth=f.date_of_birth,
                occupation=f.occupation,
                company=f.company,
            )
            for f in employee.family_members
        ],
        bank_details=(
            BankDetailsSchema(
                bank_name=employee.bank_details.bank_name,
                account_number=employee.bank_details.account_number,
                ifsc_code=employee.bank_details.ifsc_code,
                branch_name=employee.bank_details.branch_name,
                branch_address=employee.bank_details.branch_address,
            )
            if employee.bank_details
            else None
        ),
        education=[
            EducationSchema(
                degree=e.degree,
                institute=e.institute,
                board_university=e.board_university,
                year_of_passing=e.year_of_passing,
                percentage=e.percentage,
                major_subjects=e.major_subjects,
            )
            for e in employee.education
        ],
        experience=[
            ExperienceSchema(
                company_name=x.company_name,
                industry=x.industry,
                designation=x.designation,
                employment_type=x.employment_type,
                start_date=x.start_date,
                end_date=x.end_date,
                reason_for_leaving=x.reason_for_leaving,
            )
            for x in employee.experience
        ],
        skills=skills,
        languages=[
            LanguageSchema(
                language=l.language,
                can_speak=l.can_speak,
                can_read=l.can_read,
                can_write=l.can_write,
                can_understand=l.can_understand,
            )
            for l in employee.languages
        ],
        interests=[i.interest for i in employee.interests],
        documents=[DocumentSchema.model_validate(d) for d in employee.documents],
        attendance=[AttendanceSummary.model_validate(a) for a in attendance],
        leave_history=[LeaveSummary.model_validate(l) for l in leaves],
    )


def create_employee_profile(db: Session, data: EmployeeProfileCreate) -> Employee:
    email = str(data.company_email)
    if db.query(User).filter(User.email == email).first():
        raise ValueError("Email already exists")

    full_name = " ".join(p for p in [data.first_name, data.middle_name, data.last_name] if p)
    user = User(
        name=full_name,
        email=email,
        password=get_password_hash(data.password),
        role="employee",
        department=data.department,
    )
    db.add(user)
    db.flush()

    code = data.employee_code or f"GLD-{user.id:05d}"
    employee = Employee(
        user_id=user.id,
        employee_code=code,
        designation=data.designation,
        department=data.department,
        joining_date=data.joining_date,
        company_email=email,
        employment_status=data.employment_status or "active",
        reporting_manager=data.reporting_manager or data.manager_name,
        manager_name=data.reporting_manager or data.manager_name,
    )
    db.add(employee)
    db.flush()
    _apply_scalar_fields(employee, data)
    db.add(LeaveBalance(employee_id=employee.id))
    db.flush()

    _set_addresses(db, employee, data.permanent_address, data.correspondence_address, data.same_as_permanent)
    _set_family(db, employee, data.family_members)
    _set_education(db, employee, data.education)
    _set_experience(db, employee, data.experience)
    _set_bank(db, employee, data.bank_details)
    _set_skills(db, employee, data.skills)
    _set_languages(db, employee, data.languages)
    _set_interests(db, employee, data.interests)

    db.commit()
    db.refresh(employee)
    return employee


def update_employee_profile(db: Session, employee: Employee, data: EmployeeProfileUpdate) -> Employee:
    if data.company_email:
        email = str(data.company_email)
        existing = db.query(User).filter(User.email == email, User.id != employee.user_id).first()
        if existing:
            raise ValueError("Email already exists")
        employee.user.email = email
        employee.company_email = email

    if data.password:
        employee.user.password = get_password_hash(data.password)

    if data.first_name or data.last_name or data.middle_name is not None:
        parts = [
            data.first_name or employee.first_name,
            data.middle_name if data.middle_name is not None else employee.middle_name,
            data.last_name or employee.last_name,
        ]
        employee.user.name = " ".join(p for p in parts if p)

    _apply_scalar_fields(employee, data)
    if data.permanent_address is not None or data.correspondence_address is not None:
        _set_addresses(
            db, employee, data.permanent_address, data.correspondence_address, data.same_as_permanent
        )
    if data.family_members is not None:
        _set_family(db, employee, data.family_members)
    if data.education is not None:
        _set_education(db, employee, data.education)
    if data.experience is not None:
        _set_experience(db, employee, data.experience)
    if data.bank_details is not None:
        _set_bank(db, employee, data.bank_details)
    if data.skills is not None:
        _set_skills(db, employee, data.skills)
    if data.languages is not None:
        _set_languages(db, employee, data.languages)
    if data.interests is not None:
        _set_interests(db, employee, data.interests)

    db.commit()
    db.refresh(employee)
    return employee


def delete_employee_profile(db: Session, employee: Employee) -> None:
    user = employee.user
    eid = employee.id
    db.query(LeaveApplication).filter(LeaveApplication.employee_id == eid).delete()
    db.query(LeaveBalance).filter(LeaveBalance.employee_id == eid).delete()
    db.query(Attendance).filter(Attendance.employee_id == eid).delete()
    db.query(SODEntry).filter(SODEntry.employee_id == eid).delete()
    db.query(EODEntry).filter(EODEntry.employee_id == eid).delete()
    db.delete(employee)
    if user:
        db.delete(user)
    db.commit()


def save_document(db: Session, employee_id: int, document_type: str, filename: str, content: bytes) -> EmployeeDocument:
    folder = UPLOAD_ROOT / str(employee_id)
    folder.mkdir(parents=True, exist_ok=True)
    ext = os.path.splitext(filename)[1]
    stored_name = f"{document_type}_{uuid.uuid4().hex}{ext}"
    path = folder / stored_name
    path.write_bytes(content)
    rel_path = f"uploads/employees/{employee_id}/{stored_name}"
    doc = EmployeeDocument(
        employee_id=employee_id,
        document_type=document_type,
        file_path=rel_path,
        original_filename=filename,
    )
    db.add(doc)
    if document_type == "profile_photo":
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            employee.profile_photo_path = rel_path
    db.commit()
    db.refresh(doc)
    return doc
