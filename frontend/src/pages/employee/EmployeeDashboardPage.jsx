import { useEffect, useState } from "react";
import LoadingSpinner from "../../components/LoadingSpinner";
import { useToast } from "../../context/ToastContext";
import { dashboardService, getErrorMessage } from "../../services/crudService";

export default function EmployeeDashboardPage() {
  const { showToast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService
      .employee()
      .then((res) => setData(res.data))
      .catch((err) => showToast(getErrorMessage(err), "error"))
      .finally(() => setLoading(false));
  }, [showToast]);

  if (loading) return <LoadingSpinner label="Loading dashboard..." />;
  if (!data) return <div className="text-red-500">Unable to load dashboard.</div>;

  const attendance = data.today_attendance || {};

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">Welcome, {data.name}</h2>
        <p className="text-slate-600">Your productivity overview for today</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">Employee ID</p>
          <p className="text-xl font-bold">{data.employee_id}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">Department</p>
          <p className="text-xl font-bold">{data.department}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">Designation</p>
          <p className="text-xl font-bold">{data.designation}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">Today&apos;s Attendance</p>
          <p className="text-xl font-bold">{attendance.checked_in ? "Checked In" : "Not Checked In"}</p>
          {attendance.check_in && (
            <p className="text-xs text-slate-500 mt-1">
              In: {new Date(attendance.check_in).toLocaleTimeString()}
              {attendance.check_out && ` | Out: ${new Date(attendance.check_out).toLocaleTimeString()}`}
            </p>
          )}
          {attendance.ip_address && <p className="text-xs text-slate-500 mt-1">IP: {attendance.ip_address}</p>}
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">Pending Leaves</p>
          <p className="text-xl font-bold">{data.pending_leaves}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">SOD Status</p>
          <p className="text-xl font-bold capitalize">{data.sod_status?.replaceAll("_", " ")}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">EOD Status</p>
          <p className="text-xl font-bold capitalize">{data.eod_status?.replaceAll("_", " ")}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-sm text-slate-500">Open Tasks</p>
          <p className="text-xl font-bold">{data.open_tasks ?? 0}</p>
        </div>
      </div>
    </div>
  );
}
