export const LEAVE_TYPES = [
  { value: "casual", label: "Casual Leave", color: "bg-blue-500" },
  { value: "sick", label: "Sick Leave", color: "bg-amber-500" },
  { value: "paid", label: "Paid Leave", color: "bg-emerald-500" },
];

export const LEAVE_TYPE_MAP = Object.fromEntries(LEAVE_TYPES.map((t) => [t.value, t.label]));

export const EARNINGS_FIELDS = [
  { key: "basic_salary", label: "Basic Salary" },
  { key: "hra", label: "House Rent Allowance (HRA)" },
  { key: "da", label: "Dearness Allowance (DA)" },
  { key: "conveyance_allowance", label: "Conveyance Allowance" },
  { key: "medical_allowance", label: "Medical Allowance" },
  { key: "internet_allowance", label: "Internet Allowance" },
  { key: "special_allowance", label: "Special Allowance" },
  { key: "bonus", label: "Performance Bonus" },
  { key: "incentive", label: "Incentives" },
  { key: "overtime_pay", label: "Overtime Pay" },
  { key: "project_bonus", label: "Project Bonus" },
  { key: "other_earnings", label: "Other Earnings" },
];

export const DEDUCTION_FIELDS = [
  { key: "pf", label: "Provident Fund (PF)" },
  { key: "esi", label: "Employee State Insurance (ESI)" },
  { key: "professional_tax", label: "Professional Tax" },
  { key: "tds", label: "Income Tax (TDS)" },
  { key: "loan_deduction", label: "Loan Deduction" },
  { key: "advance_salary_recovery", label: "Advance Salary Recovery" },
  { key: "leave_deduction", label: "Leave Deduction" },
  { key: "late_attendance_deduction", label: "Late Attendance Deduction" },
  { key: "penalty_deduction", label: "Penalty Deduction" },
  { key: "other_deductions", label: "Other Deductions" },
];

export const emptySalaryForm = () => {
  const form = { employee_id: "", month: "", apply_auto_leave_deduction: true };
  EARNINGS_FIELDS.forEach((f) => { form[f.key] = f.key === "basic_salary" ? "" : "0"; });
  DEDUCTION_FIELDS.forEach((f) => { form[f.key] = "0"; });
  return form;
};
