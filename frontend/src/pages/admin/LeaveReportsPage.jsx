import { useEffect, useState } from "react";
import { leaveService } from "../../services/leaveService";
import { employeeService } from "../../services/crudService";

export default function LeaveReportsPage() {
  const [tab, setTab] = useState("monthly");
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [department, setDepartment] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [employees, setEmployees] = useState([]);
  const [report, setReport] = useState(null);

  useEffect(() => {
    employeeService.list({ page_size: 200 }).then((r) => setEmployees(r.data.items));
  }, []);

  const load = async () => {
    if (tab === "monthly") {
      const { data } = await leaveService.monthlyReport({ year, month });
      setReport(data);
    } else if (tab === "department") {
      const { data } = await leaveService.departmentReport(department ? { department } : {});
      setReport(data);
    } else if (tab === "employee" && employeeId) {
      const { data } = await leaveService.employeeReport(Number(employeeId));
      setReport(data);
    }
  };

  useEffect(() => {
    load();
  }, [tab, year, month, department, employeeId]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Leave Reports</h2>
      <div className="flex gap-2">
        {["monthly", "department", "employee"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm capitalize ${tab === t ? "bg-indigo-600 text-white" : "bg-white border"}`}
          >
            {t === "employee" ? "Employee History" : `${t} Report`}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow p-4 flex flex-wrap gap-3">
        {tab === "monthly" && (
          <>
            <input type="number" className="border rounded p-2 w-24" value={year} onChange={(e) => setYear(Number(e.target.value))} />
            <select className="border rounded p-2" value={month} onChange={(e) => setMonth(Number(e.target.value))}>
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i + 1} value={i + 1}>{new Date(2000, i).toLocaleString("default", { month: "long" })}</option>
              ))}
            </select>
          </>
        )}
        {tab === "department" && (
          <input className="border rounded p-2" placeholder="Department filter" value={department} onChange={(e) => setDepartment(e.target.value)} />
        )}
        {tab === "employee" && (
          <select className="border rounded p-2 min-w-[200px]" value={employeeId} onChange={(e) => setEmployeeId(e.target.value)}>
            <option value="">Select employee</option>
            {employees.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
          </select>
        )}
      </div>

      {report && (
        <div className="bg-white rounded-xl shadow p-5">
          {tab === "monthly" && (
            <>
              <p className="text-sm text-slate-500 mb-4">{report.month}/{report.year} — {report.total_applications} applications</p>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-emerald-50 p-3 rounded-lg text-center"><p className="text-2xl font-bold">{report.approved}</p><p className="text-xs">Approved</p></div>
                <div className="bg-amber-50 p-3 rounded-lg text-center"><p className="text-2xl font-bold">{report.pending}</p><p className="text-xs">Pending</p></div>
                <div className="bg-red-50 p-3 rounded-lg text-center"><p className="text-2xl font-bold">{report.rejected}</p><p className="text-xs">Rejected</p></div>
              </div>
            </>
          )}
          {tab === "department" && (
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b"><th className="p-2">Department</th><th>Total</th><th>Approved</th><th>Pending</th><th>Rejected</th></tr></thead>
              <tbody>
                {(report.departments || []).map((d) => (
                  <tr key={d.department} className="border-b"><td className="p-2">{d.department}</td><td>{d.total}</td><td>{d.approved}</td><td>{d.pending}</td><td>{d.rejected}</td></tr>
                ))}
              </tbody>
            </table>
          )}
          {tab === "employee" && report.employee && (
            <>
              <p className="font-semibold mb-2">{report.employee.name} ({report.employee.code})</p>
              <div className="grid grid-cols-3 gap-2 mb-4">
                {(report.balances || []).map((b) => (
                  <div key={b.leave_type} className="bg-slate-50 p-2 rounded text-sm">
                    <p className="font-medium capitalize">{b.leave_type}</p>
                    <p>{b.remaining_leave}/{b.total_leave} remaining</p>
                  </div>
                ))}
              </div>
            </>
          )}
          {(report.items || report.history || []).length > 0 && (
            <div className="overflow-x-auto mt-4">
              <table className="w-full text-sm">
                <thead className="bg-slate-50"><tr><th className="p-2 text-left">Type</th><th>Dates</th><th>Days</th><th>Status</th><th>Reason</th></tr></thead>
                <tbody>
                  {(report.items || report.history || []).map((x) => (
                    <tr key={x.id} className="border-t">
                      <td className="p-2">{x.leave_type}</td>
                      <td>{x.start_date} → {x.end_date}</td>
                      <td>{x.duration_days}</td>
                      <td>{x.status}</td>
                      <td className="max-w-xs truncate">{x.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
