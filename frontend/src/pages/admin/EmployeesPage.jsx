import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import LoadingSpinner from "../../components/LoadingSpinner";
import { useToast } from "../../context/ToastContext";
import { employeeService, getErrorMessage } from "../../services/crudService";

export default function EmployeesPage() {
  const { showToast } = useToast();
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [search, setSearch] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const loadEmployees = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await employeeService.list({
        page,
        page_size: pageSize,
        search: search || undefined,
        department: departmentFilter || undefined,
      });
      setEmployees(data.items || []);
      setTotal(data.total || 0);
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, departmentFilter, showToast]);

  useEffect(() => {
    loadEmployees();
  }, [loadEmployees]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await employeeService.remove(deleteTarget.id);
      showToast("Employee deleted successfully");
      setDeleteTarget(null);
      await loadEmployees();
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setDeleting(false);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-bold">Employee Management</h2>
        <Link
          to="/admin/employees/new"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          + Add Employee
        </Link>
      </div>

      <div className="flex flex-col md:flex-row gap-3">
        <input
          className="border p-2 rounded flex-1"
          placeholder="Search by name, email, or code"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <input
          className="border p-2 rounded md:w-64"
          placeholder="Filter by department"
          value={departmentFilter}
          onChange={(e) => {
            setDepartmentFilter(e.target.value);
            setPage(1);
          }}
        />
      </div>

      {loading ? (
        <LoadingSpinner label="Loading employees..." />
      ) : (
        <div className="bg-white rounded shadow overflow-auto">
          <table className="w-full text-left min-w-[900px]">
            <thead className="bg-slate-100">
              <tr>
                <th className="p-3">Code</th>
                <th className="p-3">Name</th>
                <th className="p-3">Designation</th>
                <th className="p-3">Department</th>
                <th className="p-3">Company Email</th>
                <th className="p-3">Joining Date</th>
                <th className="p-3">Status</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-slate-500">
                    No employees found.
                  </td>
                </tr>
              ) : (
                employees.map((emp) => (
                  <tr key={emp.id} className="border-t hover:bg-slate-50">
                    <td className="p-3">{emp.employee_code}</td>
                    <td className="p-3">{emp.name}</td>
                    <td className="p-3">{emp.designation}</td>
                    <td className="p-3">{emp.department}</td>
                    <td className="p-3">{emp.company_email || "—"}</td>
                    <td className="p-3">{emp.joining_date}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${
                          emp.status === "active" ? "bg-green-100 text-green-800" : "bg-slate-100"
                        }`}
                      >
                        {emp.status}
                      </span>
                    </td>
                    <td className="p-3 space-x-2 whitespace-nowrap">
                      <Link to={`/admin/employees/${emp.id}`} className="px-3 py-1 rounded bg-slate-600 text-white text-sm">
                        View
                      </Link>
                      <Link
                        to={`/admin/employees/${emp.id}/edit`}
                        className="px-3 py-1 rounded bg-blue-600 text-white text-sm"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => setDeleteTarget(emp)}
                        className="px-3 py-1 rounded bg-red-600 text-white text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-600">
          Showing {employees.length} of {total} employees
        </p>
        <div className="flex gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-3 py-1">
            Page {page} of {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>

      <DeleteConfirmation
        open={!!deleteTarget}
        title="Delete Employee"
        message={`Are you sure you want to delete ${deleteTarget?.name}? This will remove all related records.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        loading={deleting}
      />
    </div>
  );
}
