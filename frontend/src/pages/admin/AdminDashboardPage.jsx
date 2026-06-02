import { useEffect, useState } from "react";
import api from "../../services/api";

function BarChart({ data, labelKey, valueKey, color = "bg-indigo-500" }) {
  const max = Math.max(...data.map((d) => d[valueKey]), 1);
  return (
    <div className="space-y-2">
      {data.map((d) => (
        <div key={d[labelKey]} className="flex items-center gap-2 text-sm">
          <span className="w-20 text-slate-500 truncate">{d[labelKey]}</span>
          <div className="flex-1 bg-slate-100 rounded h-6 overflow-hidden">
            <div className={`${color} h-full rounded`} style={{ width: `${(d[valueKey] / max) * 100}%` }} />
          </div>
          <span className="w-8 text-right font-medium">{d[valueKey]}</span>
        </div>
      ))}
    </div>
  );
}

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  );
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/dashboard/admin").then((res) => setStats(res.data));
  }, []);

  if (!stats) return <p className="text-slate-500">Loading analytics...</p>;

  const kpiCards = [
    ["Employees", stats.total_employees],
    ["Present Today", stats.present_today],
    ["Absent Today", stats.absent_today],
    ["Pending Leaves", stats.pending_leaves],
    ["Task Completion", `${stats.task_completion_rate}%`],
    ["Pending SOD/EOD", stats.pending_sod_eod],
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Admin Dashboard</h2>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpiCards.map(([label, value]) => (
          <StatCard key={label} label={label} value={value} />
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <section className="bg-white dark:bg-slate-800 rounded-xl p-5 shadow">
          <h3 className="font-semibold mb-4">Attendance Trend (7 days)</h3>
          <BarChart
            data={stats.attendance_trend.map((d) => ({ day: d.date.slice(5), present: d.present }))}
            labelKey="day"
            valueKey="present"
            color="bg-green-500"
          />
        </section>

        <section className="bg-white dark:bg-slate-800 rounded-xl p-5 shadow">
          <h3 className="font-semibold mb-4">Leave Statistics</h3>
          <BarChart
            data={[
              { label: "Pending", count: stats.leave_stats.pending },
              { label: "Approved", count: stats.leave_stats.approved },
              { label: "Rejected", count: stats.leave_stats.rejected },
            ]}
            labelKey="label"
            valueKey="count"
            color="bg-amber-500"
          />
        </section>

        <section className="bg-white dark:bg-slate-800 rounded-xl p-5 shadow">
          <h3 className="font-semibold mb-4">Expense Statistics</h3>
          <div className="grid grid-cols-2 gap-3 mb-4">
            <StatCard label="Pending" value={stats.expense_stats.pending} />
            <StatCard label="Paid Total" value={`₹${stats.expense_stats.total_amount}`} />
          </div>
          <BarChart
            data={[
              { label: "Pending", count: stats.expense_stats.pending },
              { label: "Approved", count: stats.expense_stats.approved },
              { label: "Paid", count: stats.expense_stats.paid },
            ]}
            labelKey="label"
            valueKey="count"
          />
        </section>

        <section className="bg-white dark:bg-slate-800 rounded-xl p-5 shadow">
          <h3 className="font-semibold mb-4">Salary & Projects</h3>
          <div className="grid grid-cols-2 gap-3 mb-4">
            <StatCard label="Slips Generated" value={stats.salary_stats.generated} />
            <StatCard label="Salary Paid" value={`₹${stats.salary_stats.total_paid}`} />
          </div>
          <BarChart
            data={[
              { label: "Active", count: stats.project_stats.active },
              { label: "Completed", count: stats.project_stats.completed },
              { label: "On Hold", count: stats.project_stats.on_hold },
            ]}
            labelKey="label"
            valueKey="count"
            color="bg-purple-500"
          />
          <p className="text-sm text-slate-500 mt-4">
            Tasks: {stats.completed_tasks} / {stats.total_tasks} completed
          </p>
        </section>
      </div>
    </div>
  );
}
