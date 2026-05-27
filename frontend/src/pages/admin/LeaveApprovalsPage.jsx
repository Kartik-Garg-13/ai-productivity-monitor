import { useEffect, useState } from "react";
import api from "../../services/api";

export default function LeaveApprovalsPage() {
  const [items, setItems] = useState([]);

  const load = () => api.get("/leave/admin/pending").then((res) => setItems(res.data));
  useEffect(() => {
    load();
  }, []);

  const updateStatus = async (id, status) => {
    await api.patch(`/leave/admin/${id}`, { status, admin_remarks: `${status} by admin` });
    load();
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Pending Leave Requests</h2>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.id} className="bg-white p-4 rounded shadow">
            <p>
              Employee #{item.employee_id} | {item.leave_type} | {item.duration_days} days
            </p>
            <div className="space-x-2 mt-2">
              <button className="bg-green-600 text-white px-3 py-1 rounded" onClick={() => updateStatus(item.id, "approved")}>
                Approve
              </button>
              <button className="bg-red-600 text-white px-3 py-1 rounded" onClick={() => updateStatus(item.id, "rejected")}>
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
