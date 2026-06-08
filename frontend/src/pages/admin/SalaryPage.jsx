import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import EditModal from "../../components/EditModal";
import PaginationBar from "../../components/PaginationBar";
import StatusBadge from "../../components/StatusBadge";
import SalarySlipPreview from "../../components/salary/SalarySlipPreview";
import { useToast } from "../../context/ToastContext";
import { DEDUCTION_FIELDS, EARNINGS_FIELDS, emptySalaryForm } from "../../constants/payroll";
import { employeeService, getErrorMessage, uploadBaseUrl } from "../../services/crudService";
import { salaryService } from "../../services/phase2Service";

function num(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

export default function SalaryPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState(emptySalaryForm());
  const [open, setOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [preview, setPreview] = useState(null);

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

  const buildPayload = () => {
    const payload = {
      employee_id: Number(form.employee_id),
      month: form.month,
      apply_auto_leave_deduction: form.apply_auto_leave_deduction !== false,
    };
    EARNINGS_FIELDS.forEach((f) => { payload[f.key] = num(form[f.key]); });
    DEDUCTION_FIELDS.forEach((f) => { payload[f.key] = num(form[f.key]); });
    return payload;
  };

  const generate = async () => {
    try {
      await salaryService.generate(buildPayload());
      showToast("Salary slip generated");
      setOpen(false);
      setForm(emptySalaryForm());
      load();
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  const openPreview = async (id) => {
    try {
      const { data } = await salaryService.preview(id);
      setPreview(data);
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  const downloadPdf = async (id, fallbackPath) => {
    try {
      const { data } = await salaryService.download(id);
      const url = URL.createObjectURL(data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `salary_slip_${id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      if (fallbackPath) window.open(`${uploadBaseUrl()}/${fallbackPath}`, "_blank");
    }
  };

  const base = uploadBaseUrl();
  const columns = [
    { key: "employee_name", label: "Employee" },
    { key: "month", label: "Month" },
    { key: "gross_salary", label: "Gross", render: (r) => `₹${r.gross_salary || r.net_salary}` },
    { key: "net_salary", label: "Net", render: (r) => `₹${r.net_salary}` },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="flex flex-wrap gap-2">
          <button onClick={() => openPreview(r.id)} className="text-indigo-600 text-sm">Preview</button>
          {r.pdf_path && (
            <button onClick={() => downloadPdf(r.id, r.pdf_path)} className="text-indigo-600 text-sm">PDF</button>
          )}
          <button
            onClick={async () => {
              await salaryService.regenerate(r.id);
              showToast("Regenerated");
              load();
            }}
            className="text-blue-600 text-sm"
          >
            Regenerate
          </button>
          {r.status !== "paid" && (
            <button
              onClick={async () => {
                await salaryService.markPaid(r.id, {});
                showToast("Marked paid");
                load();
              }}
              className="text-green-600 text-sm"
            >
              Mark Paid
            </button>
          )}
          <button onClick={() => setDeleteTarget(r)} className="text-red-600 text-sm">Delete</button>
        </div>
      ),
    },
  ];

  const updateField = (key, value) => setForm((p) => ({ ...p, [key]: value }));

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Payroll Management</h2>
          <p className="text-slate-500 text-sm">Generate professional salary slips with earnings & deductions</p>
        </div>
        <button onClick={() => { setForm(emptySalaryForm()); setOpen(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg">
          Generate Slip
        </button>
      </div>
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 10)} total={total} onPageChange={setPage} />

      <EditModal title="Generate Salary Slip" open={open} onClose={() => setOpen(false)} onSubmit={generate}>
        <select className="w-full border p-2 rounded mb-3" value={form.employee_id} onChange={(e) => updateField("employee_id", e.target.value)} required>
          <option value="">Select Employee</option>
          {employees.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
        </select>
        <input type="date" className="w-full border p-2 rounded mb-3" value={form.month} onChange={(e) => updateField("month", e.target.value)} required />
        <label className="flex items-center gap-2 text-sm mb-4">
          <input type="checkbox" checked={form.apply_auto_leave_deduction !== false} onChange={(e) => updateField("apply_auto_leave_deduction", e.target.checked)} />
          Auto-calculate leave deduction
        </label>
        <p className="font-semibold text-sm text-indigo-700 mb-2">Earnings</p>
        <div className="grid md:grid-cols-2 gap-2 mb-4 max-h-48 overflow-y-auto">
          {EARNINGS_FIELDS.map((f) => (
            <input key={f.key} className="border p-2 rounded text-sm" placeholder={f.label} value={form[f.key]} onChange={(e) => updateField(f.key, e.target.value)} />
          ))}
        </div>
        <p className="font-semibold text-sm text-red-700 mb-2">Deductions</p>
        <div className="grid md:grid-cols-2 gap-2 max-h-48 overflow-y-auto">
          {DEDUCTION_FIELDS.map((f) => (
            <input key={f.key} className="border p-2 rounded text-sm" placeholder={f.label} value={form[f.key]} onChange={(e) => updateField(f.key, e.target.value)} />
          ))}
        </div>
      </EditModal>

      <DeleteConfirmation
        open={!!deleteTarget}
        title="Delete"
        message="Delete salary slip?"
        onConfirm={async () => { await salaryService.remove(deleteTarget.id); setDeleteTarget(null); load(); }}
        onCancel={() => setDeleteTarget(null)}
      />
      {preview && <SalarySlipPreview slip={preview} onClose={() => setPreview(null)} />}
    </div>
  );
}
