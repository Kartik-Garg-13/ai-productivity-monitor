import { useMemo } from "react";
import { LEAVE_TYPES } from "../../constants/payroll";

function daysBetween(start, end) {
  if (!start || !end) return 0;
  const s = new Date(start);
  const e = new Date(end);
  return Math.max(0, Math.round((e - s) / (1000 * 60 * 60 * 24)) + 1);
}

export default function LeaveApplicationForm({ form, setForm, onSubmit, submitting }) {
  const duration = useMemo(() => daysBetween(form.start_date, form.end_date), [form.start_date, form.end_date]);

  return (
    <form className="bg-white rounded-xl shadow p-6 space-y-4" onSubmit={onSubmit}>
      <h3 className="text-lg font-semibold text-slate-800">Apply for Leave</h3>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-slate-600 mb-1">Leave Type *</label>
          <select
            className="w-full border border-slate-200 rounded-lg p-2.5"
            value={form.leave_type}
            onChange={(e) => setForm((p) => ({ ...p, leave_type: e.target.value }))}
            required
          >
            {LEAVE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Emergency Contact *</label>
          <input
            className="w-full border border-slate-200 rounded-lg p-2.5"
            placeholder="+91-XXXXXXXXXX"
            value={form.emergency_contact_number}
            onChange={(e) => setForm((p) => ({ ...p, emergency_contact_number: e.target.value }))}
            required
          />
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Start Date *</label>
          <input
            type="date"
            className="w-full border border-slate-200 rounded-lg p-2.5"
            value={form.start_date}
            onChange={(e) => setForm((p) => ({ ...p, start_date: e.target.value }))}
            required
          />
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">End Date *</label>
          <input
            type="date"
            className="w-full border border-slate-200 rounded-lg p-2.5"
            value={form.end_date}
            onChange={(e) => setForm((p) => ({ ...p, end_date: e.target.value }))}
            required
          />
        </div>
      </div>
      {duration > 0 && (
        <p className="text-sm text-indigo-600 font-medium">Duration: {duration} day(s)</p>
      )}
      <div>
        <label className="block text-sm text-slate-600 mb-1">Reason *</label>
        <textarea
          className="w-full border border-slate-200 rounded-lg p-2.5"
          rows={3}
          value={form.reason}
          onChange={(e) => setForm((p) => ({ ...p, reason: e.target.value }))}
          required
        />
      </div>
      <div>
        <label className="block text-sm text-slate-600 mb-1">Mitigation Plan</label>
        <textarea
          className="w-full border border-slate-200 rounded-lg p-2.5"
          rows={2}
          placeholder="How will work be covered during your absence?"
          value={form.mitigation_plan}
          onChange={(e) => setForm((p) => ({ ...p, mitigation_plan: e.target.value }))}
        />
      </div>
      <button
        type="submit"
        disabled={submitting}
        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium disabled:opacity-50"
      >
        {submitting ? "Submitting..." : "Submit Application"}
      </button>
    </form>
  );
}
