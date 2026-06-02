import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import EditModal from "../../components/EditModal";
import PaginationBar from "../../components/PaginationBar";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { employeeService, getErrorMessage, uploadBaseUrl } from "../../services/crudService";
import { salaryService } from "../../services/phase2Service";

const empty = { employee_id: "", month: "", basic_salary: "", hra: "0", bonus: "0", deductions: "0" };

export default function SalaryPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState(empty);
  const [open, setOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await salaryService.list({ page, page_size: 10 });
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    } finally {
      setLoading(false);
    }
  }, [page, showToast]);

  useEffect(() => {
    load();
    employeeService.list({ page_size: 100 }).then((r) => setEmployees(r.data.items));
  }, [load]);

  const generate = async () => {
    try {
      await salaryService.generate({
        employee_id: Number(form.employee_id),
        month: form.month,
        basic_salary: Number(form.basic_salary),
        hra: Number(form.hra),
        bonus: Number(form.bonus),
        deductions: Number(form.deductions),
      });
      showToast("Salary slip generated");
      setOpen(false);
      load();
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  const base = uploadBaseUrl();
  const columns = [
    { key: "employee_name", label: "Employee" },
    { key: "month", label: "Month" },
    { key: "net_salary", label: "Net", render: (r) => `₹${r.net_salary}` },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="space-x-2">
          {r.pdf_path && <a href={`${base}/${r.pdf_path}`} target="_blank" rel="noreferrer" className="text-indigo-600 text-sm">PDF</a>}
          {r.status !== "paid" && (
            <button onClick={async () => { await salaryService.markPaid(r.id, {}); showToast("Marked paid"); load(); }} className="text-green-600 text-sm">Mark Paid</button>
          )}
          <button onClick={() => setDeleteTarget(r)} className="text-red-600 text-sm">Delete</button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h2 className="text-2xl font-bold">Salary Management</h2>
        <button onClick={() => { setForm(empty); setOpen(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg">Generate Slip</button>
      </div>
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 10)} total={total} onPageChange={setPage} />
      <EditModal title="Generate Salary Slip" open={open} onClose={() => setOpen(false)} onSubmit={generate}>
        <select className="w-full border p-2 rounded mb-2" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })}>
          <option value="">Employee</option>
          {employees.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
        </select>
        <input type="date" className="w-full border p-2 rounded mb-2" value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} />
        <input className="w-full border p-2 rounded mb-2" placeholder="Basic" value={form.basic_salary} onChange={(e) => setForm({ ...form, basic_salary: e.target.value })} />
        <input className="w-full border p-2 rounded mb-2" placeholder="HRA" value={form.hra} onChange={(e) => setForm({ ...form, hra: e.target.value })} />
        <input className="w-full border p-2 rounded mb-2" placeholder="Bonus" value={form.bonus} onChange={(e) => setForm({ ...form, bonus: e.target.value })} />
        <input className="w-full border p-2 rounded mb-2" placeholder="Deductions" value={form.deductions} onChange={(e) => setForm({ ...form, deductions: e.target.value })} />
      </EditModal>
      <DeleteConfirmation open={!!deleteTarget} title="Delete" message="Delete salary slip?" onConfirm={async () => { await salaryService.remove(deleteTarget.id); setDeleteTarget(null); load(); }} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
}
