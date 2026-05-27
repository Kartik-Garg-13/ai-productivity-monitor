import { useEffect, useState } from "react";
import api from "../../services/api";

const init = { leave_type: "annual", start_date: "", end_date: "", reason: "", mitigation_plan: "" };

export default function LeavePage() {
  const [form, setForm] = useState(init);
  const [history, setHistory] = useState([]);
  const [balance, setBalance] = useState(null);

  const load = () =>
    api.get("/leave/history").then((res) => {
      setHistory(res.data.history || []);
      setBalance(res.data.balance || null);
    });

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-bold">Leave Management</h2>
      {balance && (
        <div className="bg-white rounded shadow p-4">
          Remaining Leave: <span className="font-bold">{balance.remaining_leave}</span>
        </div>
      )}
      <form
        className="bg-white p-4 rounded shadow grid md:grid-cols-2 gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          api.post("/leave/apply", form).then(() => {
            setForm(init);
            load();
          });
        }}
      >
        {Object.keys(init).map((k) => (
          <input
            key={k}
            className="border p-2 rounded"
            placeholder={k}
            value={form[k]}
            onChange={(e) => setForm((p) => ({ ...p, [k]: e.target.value }))}
          />
        ))}
        <button className="bg-indigo-600 text-white rounded px-4 py-2">Apply Leave</button>
      </form>
      <div className="bg-white rounded shadow p-4 space-y-2">
        {history.map((x) => (
          <div key={x.id} className="border rounded p-2">
            {x.leave_type} | {x.start_date} to {x.end_date} | {x.status}
          </div>
        ))}
      </div>
    </div>
  );
}
