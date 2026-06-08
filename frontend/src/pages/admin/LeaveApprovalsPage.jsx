import { useEffect, useState } from "react";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { LEAVE_TYPE_MAP } from "../../constants/payroll";
import { getErrorMessage } from "../../services/crudService";
import { leaveService } from "../../services/leaveService";

export default function LeaveApprovalsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [remarks, setRemarks] = useState({});
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    leaveService.pending().then((res) => setItems(res.data)).finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const updateStatus = async (id, status) => {
    try {
      await leaveService.review(id, { status, admin_remarks: remarks[id] || `${status.replace(/_/g, " ")} by admin` });
      showToast(`Leave ${status.replace(/_/g, " ")}`);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Leave Approvals</h2>
        <p className="text-slate-500 text-sm">Review and action pending leave requests</p>
      </div>

      {loading ? (
        <p className="text-slate-400">Loading...</p>
      ) : items.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-slate-400">No pending leave requests</div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.id} className="bg-white rounded-xl shadow p-5 border border-slate-100">
              <div className="flex flex-wrap justify-between gap-2 mb-3">
                <div>
                  <h3 className="font-semibold text-lg">{item.employee_name || `Employee #${item.employee_id}`}</h3>
                  <p className="text-sm text-slate-500">{item.employee_code} · {item.department}</p>
                </div>
                <StatusBadge status={item.status} />
              </div>
              <div className="grid md:grid-cols-2 gap-3 text-sm mb-3">
                <p><span className="text-slate-500">Leave Type:</span> <strong>{LEAVE_TYPE_MAP[item.leave_type] || item.leave_type}</strong></p>
                <p><span className="text-slate-500">Duration:</span> <strong>{item.duration_days} day(s)</strong></p>
                <p><span className="text-slate-500">From:</span> {item.start_date}</p>
                <p><span className="text-slate-500">To:</span> {item.end_date}</p>
                <p className="md:col-span-2"><span className="text-slate-500">Emergency Contact:</span> {item.emergency_contact_number || "—"}</p>
                <p className="md:col-span-2"><span className="text-slate-500">Reason:</span> {item.reason}</p>
                {item.mitigation_plan && (
                  <p className="md:col-span-2"><span className="text-slate-500">Mitigation Plan:</span> {item.mitigation_plan}</p>
                )}
              </div>
              <textarea
                className="w-full border rounded-lg p-2 text-sm mb-3"
                placeholder="Admin remarks (optional)"
                rows={2}
                value={remarks[item.id] || ""}
                onChange={(e) => setRemarks((p) => ({ ...p, [item.id]: e.target.value }))}
              />
              <div className="flex flex-wrap gap-2">
                <button className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm" onClick={() => updateStatus(item.id, "approved")}>
                  Approve
                </button>
                <button className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm" onClick={() => updateStatus(item.id, "rejected")}>
                  Reject
                </button>
                <button className="bg-amber-500 text-white px-4 py-2 rounded-lg text-sm" onClick={() => updateStatus(item.id, "clarification_requested")}>
                  Request Clarification
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
