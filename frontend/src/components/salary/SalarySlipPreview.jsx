import { DEDUCTION_FIELDS, EARNINGS_FIELDS } from "../../constants/payroll";

function MoneyRow({ label, value }) {
  if (!value || Number(value) === 0) return null;
  return (
    <div className="flex justify-between py-1 text-sm border-b border-slate-50">
      <span className="text-slate-600">{label}</span>
      <span className="font-medium">₹{Number(value).toLocaleString("en-IN")}</span>
    </div>
  );
}

export default function SalarySlipPreview({ slip, onClose }) {
  if (!slip) return null;
  const company = slip.company_snapshot || {};
  const emp = slip.employee_snapshot || {};
  const att = slip.attendance_snapshot || {};

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full my-4">
        <div className="bg-indigo-600 text-white p-6 rounded-t-xl">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold">{company.company_name || "Company"}</h2>
              {company.company_address && <p className="text-indigo-200 text-sm mt-1">{company.company_address}</p>}
              {company.gst_number && <p className="text-indigo-200 text-xs">GST: {company.gst_number}</p>}
            </div>
            <button onClick={onClose} className="text-white/80 hover:text-white text-2xl leading-none">&times;</button>
          </div>
          <p className="mt-3 font-semibold">Salary Slip — {slip.month?.slice?.(0, 7) || slip.month}</p>
        </div>
        <div className="p-6 space-y-5">
          <div className="grid md:grid-cols-2 gap-3 text-sm">
            <p><span className="text-slate-500">Employee:</span> <strong>{emp.name || slip.employee_name}</strong></p>
            <p><span className="text-slate-500">Employee ID:</span> <strong>{emp.employee_id || slip.employee_code}</strong></p>
            <p><span className="text-slate-500">Designation:</span> {emp.designation}</p>
            <p><span className="text-slate-500">Department:</span> {emp.department}</p>
            <p><span className="text-slate-500">PAN:</span> {emp.pan_number || "—"}</p>
            <p><span className="text-slate-500">UAN:</span> {emp.uan_number || "—"}</p>
            <p><span className="text-slate-500">Bank:</span> {slip.bank_snapshot?.bank_name || "—"}</p>
            <p><span className="text-slate-500">Account:</span> {slip.bank_snapshot?.account_number || "—"}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold text-indigo-700 mb-2">Earnings</h4>
              {EARNINGS_FIELDS.map((f) => <MoneyRow key={f.key} label={f.label} value={slip[f.key]} />)}
              <div className="flex justify-between pt-2 font-bold text-sm border-t mt-2">
                <span>Total Earnings</span>
                <span className="text-emerald-600">₹{Number(slip.total_earnings || 0).toLocaleString("en-IN")}</span>
              </div>
            </div>
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold text-red-700 mb-2">Deductions</h4>
              {DEDUCTION_FIELDS.map((f) => <MoneyRow key={f.key} label={f.label} value={slip[f.key]} />)}
              <div className="flex justify-between pt-2 font-bold text-sm border-t mt-2">
                <span>Total Deductions</span>
                <span className="text-red-600">₹{Number(slip.total_deductions || slip.deductions || 0).toLocaleString("en-IN")}</span>
              </div>
            </div>
          </div>

          {att.working_days != null && (
            <div className="bg-slate-50 rounded-lg p-4 grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              <div><span className="text-slate-500">Working Days</span><p className="font-bold">{att.working_days}</p></div>
              <div><span className="text-slate-500">Present</span><p className="font-bold">{att.present_days}</p></div>
              <div><span className="text-slate-500">Paid Leave</span><p className="font-bold">{att.paid_leave_days}</p></div>
              <div><span className="text-slate-500">Overtime Hrs</span><p className="font-bold">{att.overtime_hours}</p></div>
            </div>
          )}

          <div className="bg-emerald-50 rounded-lg p-4 space-y-1">
            <div className="flex justify-between"><span>Gross Salary</span><strong>₹{Number(slip.gross_salary || 0).toLocaleString("en-IN")}</strong></div>
            <div className="flex justify-between text-lg"><span>Net Salary</span><strong className="text-emerald-700">₹{Number(slip.net_salary).toLocaleString("en-IN")}</strong></div>
            <div className="flex justify-between"><span>In-Hand Salary</span><strong>₹{Number(slip.in_hand_salary || slip.net_salary).toLocaleString("en-IN")}</strong></div>
            {slip.amount_in_words && <p className="text-xs text-slate-600 italic pt-2">In words: {slip.amount_in_words}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
