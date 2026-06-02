import { useEffect, useState } from "react";
import LoadingSpinner from "../../components/LoadingSpinner";
import { useToast } from "../../context/ToastContext";
import { attendanceService, employeeService, getErrorMessage } from "../../services/crudService";

export default function AttendanceAdminPage() {
  const { showToast } = useToast();
  const [rows, setRows] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    employee_id: "",
    attendance_date: "",
    department: "",
  });

  const load = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.employee_id) params.employee_id = Number(filters.employee_id);
      if (filters.attendance_date) params.attendance_date = filters.attendance_date;
      if (filters.department) params.department = filters.department;
      const { data } = await attendanceService.adminList(params);
      setRows(data);
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    employeeService.list({ page: 1, page_size: 100 }).then((res) => setEmployees(res.data.items || []));
  }, []);

  useEffect(() => {
    load();
  }, [filters]);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Attendance Audit</h2>

      <div className="grid md:grid-cols-3 gap-3 bg-white p-4 rounded shadow">
        <select
          className="border p-2 rounded"
          value={filters.employee_id}
          onChange={(e) => setFilters((p) => ({ ...p, employee_id: e.target.value }))}
        >
          <option value="">All Employees</option>
          {employees.map((emp) => (
            <option key={emp.id} value={emp.id}>
              {emp.name} ({emp.employee_code})
            </option>
          ))}
        </select>
        <input
          type="date"
          className="border p-2 rounded"
          value={filters.attendance_date}
          onChange={(e) => setFilters((p) => ({ ...p, attendance_date: e.target.value }))}
        />
        <input
          className="border p-2 rounded"
          placeholder="Filter by department"
          value={filters.department}
          onChange={(e) => setFilters((p) => ({ ...p, department: e.target.value }))}
        />
      </div>

      {loading ? (
        <LoadingSpinner label="Loading attendance records..." />
      ) : (
        <div className="bg-white rounded shadow overflow-auto">
          <table className="w-full text-left min-w-[900px]">
            <thead className="bg-slate-100">
              <tr>
                <th className="p-3">Employee</th>
                <th className="p-3">Department</th>
                <th className="p-3">Date</th>
                <th className="p-3">Check In</th>
                <th className="p-3">Check Out</th>
                <th className="p-3">Duration</th>
                <th className="p-3">IP Address</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No attendance records found.
                  </td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={row.id} className="border-t">
                    <td className="p-3">
                      {row.employee_name}
                      <div className="text-xs text-slate-500">{row.employee_code}</div>
                    </td>
                    <td className="p-3">{row.department}</td>
                    <td className="p-3">{row.date}</td>
                    <td className="p-3">{new Date(row.check_in).toLocaleTimeString()}</td>
                    <td className="p-3">{row.check_out ? new Date(row.check_out).toLocaleTimeString() : "-"}</td>
                    <td className="p-3">{row.work_duration || "-"}</td>
                    <td className="p-3 font-mono text-sm">{row.ip_address || "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
