import { useEffect, useState } from "react";
import api from "../../services/api";

export default function AttendancePage() {
  const [history, setHistory] = useState([]);

  const load = () => api.get("/attendance/history").then((res) => setHistory(res.data));
  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">My Attendance</h2>
      <div className="flex gap-3">
        <button className="bg-green-600 text-white px-4 py-2 rounded" onClick={() => api.post("/attendance/check-in").then(load)}>
          Check-In
        </button>
        <button className="bg-indigo-600 text-white px-4 py-2 rounded" onClick={() => api.post("/attendance/check-out").then(load)}>
          Check-Out
        </button>
      </div>
      <div className="bg-white rounded p-4 shadow space-y-2">
        {history.map((row) => (
          <div key={row.id} className="border rounded p-2">
            {row.date} | {row.work_duration || "-"}
          </div>
        ))}
      </div>
    </div>
  );
}
