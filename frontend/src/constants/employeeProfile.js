export const PROFILE_STEPS = [
  { id: 1, title: "Employment" },
  { id: 2, title: "Personal" },
  { id: 3, title: "Government IDs" },
  { id: 4, title: "Address" },
  { id: 5, title: "Communication" },
  { id: 6, title: "Family" },
  { id: 7, title: "Bank" },
  { id: 8, title: "Education" },
  { id: 9, title: "Experience" },
  { id: 10, title: "Skills" },
  { id: 11, title: "Languages" },
  { id: 12, title: "Interests" },
  { id: 13, title: "Documents" },
];

export const INTEREST_OPTIONS = [
  "Adventure Sports",
  "Movies",
  "Games",
  "Music",
  "Reading",
  "Social Work",
  "Singing",
  "Painting",
  "Dancing",
  "Theatre",
  "Other",
];

export const DOCUMENT_TYPES = [
  { key: "resume", label: "Resume" },
  { key: "pan_card", label: "PAN Card" },
  { key: "aadhaar_card", label: "Aadhaar Card" },
  { key: "passport", label: "Passport" },
  { key: "offer_letter", label: "Offer Letter" },
  { key: "experience_certificates", label: "Experience Certificates" },
  { key: "educational_certificates", label: "Educational Certificates" },
  { key: "profile_photo", label: "Profile Photo" },
];

export const GOV_DOC_TYPES = [
  { key: "pan_upload", label: "PAN Document" },
  { key: "aadhaar_upload", label: "Aadhaar Document" },
  { key: "passport_upload", label: "Passport Document" },
];

export const emptyAddress = () => ({
  address_line_1: "",
  address_line_2: "",
  city: "",
  state: "",
  country: "",
  pin_code: "",
});

export const defaultProfile = () => ({
  password: "",
  employee_id: "",
  employee_code: "",
  designation: "",
  department: "",
  joining_date: "",
  employment_type: "full-time",
  reporting_manager: "",
  project_lead: "",
  tech_owner: "",
  company_email: "",
  employment_status: "active",
  manager_name: "",
  title: "",
  first_name: "",
  middle_name: "",
  last_name: "",
  gender: "",
  father_name: "",
  date_of_birth: "",
  nationality: "",
  marital_status: "",
  anniversary_date: "",
  number_of_children: "",
  blood_group: "",
  pan_number: "",
  uan_number: "",
  pf_number: "",
  work_location: "",
  aadhaar_number: "",
  passport_number: "",
  passport_issue_date: "",
  passport_expiry_date: "",
  passport_issue_place: "",
  mobile_number: "",
  alternate_number: "",
  personal_email: "",
  permanent_address: emptyAddress(),
  correspondence_address: emptyAddress(),
  same_as_permanent: false,
  family_members: [{ name: "", relationship: "", date_of_birth: "", occupation: "", company: "" }],
  bank_details: {
    bank_name: "",
    account_number: "",
    ifsc_code: "",
    branch_name: "",
    branch_address: "",
  },
  education: [{ degree: "", institute: "", board_university: "", year_of_passing: "", percentage: "", major_subjects: "" }],
  experience: [
    {
      company_name: "",
      industry: "",
      designation: "",
      employment_type: "",
      start_date: "",
      end_date: "",
      reason_for_leaving: "",
    },
  ],
  skills: {
    certification_name: "",
    certification_provider: "",
    certification_issue_date: "",
    certification_expiry_date: "",
    technical_skills: "",
    soft_skills: "",
    programming_languages: "",
    frameworks: "",
    tools: "",
  },
  languages: [{ language: "", can_speak: false, can_read: false, can_write: false, can_understand: false }],
  interests: [],
  pendingFiles: {},
});

export function profileFromApi(data) {
  if (!data) return defaultProfile();
  return {
    password: "",
    employee_id: data.employee_id || "",
    employee_code: data.employee_code || "",
    designation: data.designation || "",
    department: data.department || "",
    joining_date: data.joining_date || "",
    employment_type: data.employment_type || "",
    reporting_manager: data.reporting_manager || data.manager_name || "",
    project_lead: data.project_lead || "",
    tech_owner: data.tech_owner || "",
    company_email: data.company_email || data.login_email || "",
    employment_status: data.employment_status || "active",
    manager_name: data.manager_name || "",
    title: data.title || "",
    first_name: data.first_name || "",
    middle_name: data.middle_name || "",
    last_name: data.last_name || "",
    gender: data.gender || "",
    father_name: data.father_name || "",
    date_of_birth: data.date_of_birth || "",
    nationality: data.nationality || "",
    marital_status: data.marital_status || "",
    anniversary_date: data.anniversary_date || "",
    number_of_children: data.number_of_children ?? "",
    blood_group: data.blood_group || "",
    pan_number: data.pan_number || "",
    uan_number: data.uan_number || "",
    pf_number: data.pf_number || "",
    work_location: data.work_location || "",
    aadhaar_number: data.aadhaar_number || "",
    passport_number: data.passport_number || "",
    passport_issue_date: data.passport_issue_date || "",
    passport_expiry_date: data.passport_expiry_date || "",
    passport_issue_place: data.passport_issue_place || "",
    mobile_number: data.mobile_number || "",
    alternate_number: data.alternate_number || "",
    personal_email: data.personal_email || "",
    permanent_address: data.permanent_address || emptyAddress(),
    correspondence_address: data.correspondence_address || emptyAddress(),
    same_as_permanent: false,
    family_members: data.family_members?.length
      ? data.family_members
      : [{ name: "", relationship: "", date_of_birth: "", occupation: "", company: "" }],
    bank_details: data.bank_details || defaultProfile().bank_details,
    education: data.education?.length
      ? data.education
      : [{ degree: "", institute: "", board_university: "", year_of_passing: "", percentage: "", major_subjects: "" }],
    experience: data.experience?.length
      ? data.experience
      : [
          {
            company_name: "",
            industry: "",
            designation: "",
            employment_type: "",
            start_date: "",
            end_date: "",
            reason_for_leaving: "",
          },
        ],
    skills: data.skills || defaultProfile().skills,
    languages: data.languages?.length
      ? data.languages
      : [{ language: "", can_speak: false, can_read: false, can_write: false, can_understand: false }],
    interests: data.interests || [],
    pendingFiles: {},
  };
}

export function buildPayload(form, isEdit) {
  const payload = { ...form };
  delete payload.pendingFiles;
  if (payload.number_of_children === "") payload.number_of_children = null;
  else payload.number_of_children = Number(payload.number_of_children);
  if (isEdit && !payload.password) delete payload.password;
  if (!isEdit && !payload.password) payload.password = "ChangeMe@123";
  return payload;
}
