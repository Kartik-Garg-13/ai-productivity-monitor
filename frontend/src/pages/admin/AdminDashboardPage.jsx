import { useEffect, useState } from "react";
import api from "../../services/api";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/dashboard/admin").then((res) => setStats(res.data));
  }, []);

  const cards = stats
    ? [
        ["Total Employees", stats.total_employees],
        ["Present Employees", stats.present_today],
        ["Absent Employees", stats.absent_today],
        ["Pending Leaves", stats.pending_leaves],
        ["Pending SOD/EOD", stats.pending_sod_eod],
      ]
    : [];

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Admin Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map(([label, value]) => (
          <div key={label} className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
