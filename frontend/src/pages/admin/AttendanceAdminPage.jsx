import { useEffect, useState } from "react";
import api from "../../services/api";

export default function AttendanceAdminPage() {
  const [rows, setRows] = useState([]);
  useEffect(() => {
    api.get("/attendance/admin").then((res) => setRows(res.data));
  }, []);
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Attendance Overview</h2>
      <div className="bg-white rounded shadow p-4 space-y-2">
        {rows.map((row) => (
          <div key={row.id} className="border rounded p-3">
            Emp #{row.employee_id} | {row.date} | In: {new Date(row.check_in).toLocaleTimeString()} | Out:{" "}
            {row.check_out ? new Date(row.check_out).toLocaleTimeString() : "-"} | Duration: {row.work_duration || "-"}
          </div>
        ))}
      </div>
    </div>
  );
}
