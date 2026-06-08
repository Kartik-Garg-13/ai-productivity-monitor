from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class AddressSchema(BaseModel):
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pin_code: str | None = None


class FamilyMemberSchema(BaseModel):
    name: str
    relationship: str | None = None
    date_of_birth: date | None = None
    occupation: str | None = None
    company: str | None = None


class BankDetailsSchema(BaseModel):
    bank_name: str | None = None
    account_number: str | None = None
    ifsc_code: str | None = None
    branch_name: str | None = None
    branch_address: str | None = None


class EducationSchema(BaseModel):
    degree: str | None = None
    institute: str | None = None
    board_university: str | None = None
    year_of_passing: str | None = None
    percentage: str | None = None
    major_subjects: str | None = None


class ExperienceSchema(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    designation: str | None = None
    employment_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    reason_for_leaving: str | None = None


class SkillsSchema(BaseModel):
    certification_name: str | None = None
    certification_provider: str | None = None
    certification_issue_date: date | None = None
    certification_expiry_date: date | None = None
    technical_skills: str | None = None
    soft_skills: str | None = None
    programming_languages: str | None = None
    frameworks: str | None = None
    tools: str | None = None


class LanguageSchema(BaseModel):
    language: str
    can_speak: bool = False
    can_read: bool = False
    can_write: bool = False
    can_understand: bool = False


class DocumentSchema(BaseModel):
    id: int
    document_type: str
    file_path: str
    original_filename: str | None = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class EmployeeProfileBase(BaseModel):
    password: str | None = Field(default=None, min_length=6)
    employee_id: str | None = None
    employee_code: str | None = None
    designation: str = Field(min_length=1)
    department: str = Field(min_length=1)
    joining_date: date
    employment_type: str | None = None
    reporting_manager: str | None = None
    project_lead: str | None = None
    tech_owner: str | None = None
    company_email: EmailStr | None = None
    employment_status: str = "active"
    manager_name: str | None = None

    title: str | None = None
    first_name: str = Field(min_length=1)
    middle_name: str | None = None
    last_name: str = Field(min_length=1)
    gender: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    marital_status: str | None = None
    anniversary_date: date | None = None
    number_of_children: int | None = None
    blood_group: str | None = None

    pan_number: str | None = None
    uan_number: str | None = None
    pf_number: str | None = None
    work_location: str | None = None
    aadhaar_number: str | None = None
    passport_number: str | None = None
    passport_issue_date: date | None = None
    passport_expiry_date: date | None = None
    passport_issue_place: str | None = None

    mobile_number: str | None = None
    alternate_number: str | None = None
    personal_email: EmailStr | None = None

    permanent_address: AddressSchema | None = None
    correspondence_address: AddressSchema | None = None
    same_as_permanent: bool = False

    family_members: list[FamilyMemberSchema] = []
    bank_details: BankDetailsSchema | None = None
    education: list[EducationSchema] = []
    experience: list[ExperienceSchema] = []
    skills: SkillsSchema | None = None
    languages: list[LanguageSchema] = []
    interests: list[str] = []


class EmployeeProfileCreate(EmployeeProfileBase):
    company_email: EmailStr
    password: str = Field(min_length=6)


class EmployeeProfileUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=6)
    employee_id: str | None = None
    employee_code: str | None = None
    designation: str | None = None
    department: str | None = None
    joining_date: date | None = None
    employment_type: str | None = None
    reporting_manager: str | None = None
    project_lead: str | None = None
    tech_owner: str | None = None
    company_email: EmailStr | None = None
    employment_status: str | None = None
    manager_name: str | None = None
    title: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    marital_status: str | None = None
    anniversary_date: date | None = None
    number_of_children: int | None = None
    blood_group: str | None = None
    pan_number: str | None = None
    uan_number: str | None = None
    pf_number: str | None = None
    work_location: str | None = None
    aadhaar_number: str | None = None
    passport_number: str | None = None
    passport_issue_date: date | None = None
    passport_expiry_date: date | None = None
    passport_issue_place: str | None = None
    mobile_number: str | None = None
    alternate_number: str | None = None
    personal_email: EmailStr | None = None
    permanent_address: AddressSchema | None = None
    correspondence_address: AddressSchema | None = None
    same_as_permanent: bool = False
    family_members: list[FamilyMemberSchema] | None = None
    bank_details: BankDetailsSchema | None = None
    education: list[EducationSchema] | None = None
    experience: list[ExperienceSchema] | None = None
    skills: SkillsSchema | None = None
    languages: list[LanguageSchema] | None = None
    interests: list[str] | None = None


class EmployeeListItem(BaseModel):
    id: int
    employee_code: str
    name: str
    designation: str
    department: str
    company_email: str | None = None
    joining_date: date
    status: str

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    items: list[EmployeeListItem]
    total: int
    page: int
    page_size: int


class AttendanceSummary(BaseModel):
    id: int
    date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    work_duration: str | None = None
    ip_address: str | None = None

    class Config:
        from_attributes = True


class LeaveSummary(BaseModel):
    id: int
    leave_type: str
    start_date: date
    end_date: date
    duration_days: int
    status: str
    reason: str

    class Config:
        from_attributes = True


class EmployeeProfileFull(BaseModel):
    id: int
    user_id: int
    employee_id: str | None = None
    employee_code: str
    login_email: EmailStr
    designation: str
    department: str
    joining_date: date
    employment_type: str | None = None
    reporting_manager: str | None = None
    project_lead: str | None = None
    tech_owner: str | None = None
    company_email: str | None = None
    employment_status: str
    manager_name: str | None = None
    full_name: str

    title: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    marital_status: str | None = None
    anniversary_date: date | None = None
    number_of_children: int | None = None
    blood_group: str | None = None
    profile_photo_path: str | None = None

    pan_number: str | None = None
    uan_number: str | None = None
    pf_number: str | None = None
    work_location: str | None = None
    aadhaar_number: str | None = None
    passport_number: str | None = None
    passport_issue_date: date | None = None
    passport_expiry_date: date | None = None
    passport_issue_place: str | None = None

    mobile_number: str | None = None
    alternate_number: str | None = None
    personal_email: str | None = None

    permanent_address: AddressSchema | None = None
    correspondence_address: AddressSchema | None = None
    family_members: list[FamilyMemberSchema] = []
    bank_details: BankDetailsSchema | None = None
    education: list[EducationSchema] = []
    experience: list[ExperienceSchema] = []
    skills: SkillsSchema | None = None
    languages: list[LanguageSchema] = []
    interests: list[str] = []
    documents: list[DocumentSchema] = []
    attendance: list[AttendanceSummary] = []
    leave_history: list[LeaveSummary] = []

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    email: EmailStr
    designation: str
    department: str
    joining_date: date
    manager_name: str | None = None

    class Config:
        from_attributes = True
