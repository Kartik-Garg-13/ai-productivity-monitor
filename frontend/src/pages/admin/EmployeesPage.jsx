import { useEffect, useState } from "react";
import api from "../../services/api";

const defaultForm = {
  name: "",
  email: "",
  password: "",
  designation: "",
  department: "",
  joining_date: "",
  manager_name: "",
};

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState(defaultForm);

  const loadEmployees = () => api.get("/employees").then((res) => setEmployees(res.data));

  useEffect(() => {
    loadEmployees();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await api.post("/employees", form);
    setForm(defaultForm);
    loadEmployees();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Employee Management</h2>
      <form onSubmit={submit} className="grid md:grid-cols-3 gap-3 bg-white p-4 rounded shadow">
        {Object.keys(defaultForm).map((key) => (
          <input
            key={key}
            className="border p-2 rounded"
            placeholder={key.replaceAll("_", " ")}
            value={form[key]}
            type={key.includes("date") ? "date" : key === "password" ? "password" : "text"}
            onChange={(e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))}
          />
        ))}
        <button className="bg-indigo-600 text-white rounded px-4 py-2">Add Employee</button>
      </form>
      <div className="bg-white rounded shadow overflow-auto">
        <table className="w-full text-left">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3">Code</th>
              <th className="p-3">Name</th>
              <th className="p-3">Email</th>
              <th className="p-3">Designation</th>
              <th className="p-3">Department</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((emp) => (
              <tr key={emp.id} className="border-t">
                <td className="p-3">{emp.employee_code}</td>
                <td className="p-3">{emp.name}</td>
                <td className="p-3">{emp.email}</td>
                <td className="p-3">{emp.designation}</td>
                <td className="p-3">{emp.department}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
