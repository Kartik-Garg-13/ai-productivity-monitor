import { useEffect, useState } from "react";
import LeaveApplicationForm from "../../components/leave/LeaveApplicationForm";
import LeaveBalanceCards, { LeaveBalanceChart } from "../../components/leave/LeaveBalanceCards";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { LEAVE_TYPE_MAP } from "../../constants/payroll";
import { getErrorMessage } from "../../services/crudService";
import { leaveService } from "../../services/leaveService";

const init = {
  leave_type: "casual",
  start_date: "",
  end_date: "",
  reason: "",
  mitigation_plan: "",
  emergency_contact_number: "",
};

export default function LeavePage() {
  const { showToast } = useToast();
  const [form, setForm] = useState(init);
  const [history, setHistory] = useState([]);
  const [balances, setBalances] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  const load = () =>
    leaveService.history().then((res) => {
      setHistory(res.data.history || []);
      setBalances(res.data.balances || []);
    });

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await leaveService.apply(form);
      showToast("Leave application submitted");
      setForm(init);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSubmitting(false);
    }
  };

  const cancel = async (id) => {
    try {
      await leaveService.cancel(id);
      showToast("Leave cancelled");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Leave Management</h2>
        <p className="text-slate-500 text-sm mt-1">Track balances, apply for leave, and view history</p>
      </div>

      <LeaveBalanceCards balances={balances} />
      <LeaveBalanceChart balances={balances} />

      <LeaveApplicationForm form={form} setForm={setForm} onSubmit={submit} submitting={submitting} />

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <div className="px-5 py-4 border-b">
          <h3 className="font-semibold">Leave History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left p-3">Type</th>
                <th className="text-left p-3">Dates</th>
                <th className="text-left p-3">Days</th>
                <th className="text-left p-3">Reason</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 && (
                <tr><td colSpan={6} className="p-6 text-center text-slate-400">No leave applications yet</td></tr>
              )}
              {history.map((x) => (
                <tr key={x.id} className="border-t hover:bg-slate-50">
                  <td className="p-3">{LEAVE_TYPE_MAP[x.leave_type] || x.leave_type}</td>
                  <td className="p-3">{x.start_date} → {x.end_date}</td>
                  <td className="p-3">{x.duration_days}</td>
                  <td className="p-3 max-w-xs truncate">{x.reason}</td>
                  <td className="p-3"><StatusBadge status={x.status} /></td>
                  <td className="p-3">
                    {x.status === "pending" && (
                      <button onClick={() => cancel(x.id)} className="text-red-600 text-xs hover:underline">Cancel</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
