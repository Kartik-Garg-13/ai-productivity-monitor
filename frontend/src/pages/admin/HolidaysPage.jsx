import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import EditModal from "../../components/EditModal";
import PaginationBar from "../../components/PaginationBar";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../services/crudService";
import { holidayService } from "../../services/phase2Service";

const empty = { name: "", date: "", type: "public", description: "" };

export default function HolidaysPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [open, setOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await holidayService.list({ page, page_size: 20, year });
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    } finally {
      setLoading(false);
    }
  }, [page, year, showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const columns = [
    { key: "name", label: "Holiday" },
    { key: "date", label: "Date" },
    { key: "type", label: "Type" },
    { key: "description", label: "Description" },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="space-x-2">
          <button onClick={() => { setEditId(r.id); setForm(r); setOpen(true); }} className="text-blue-600 text-sm">Edit</button>
          <button onClick={() => setDeleteTarget(r)} className="text-red-600 text-sm">Delete</button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h2 className="text-2xl font-bold">Holidays</h2>
        <button onClick={() => { setEditId(null); setForm(empty); setOpen(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg">+ Add Holiday</button>
      </div>
      <input type="number" className="border p-2 rounded w-32" value={year} onChange={(e) => setYear(Number(e.target.value))} />
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 20)} total={total} onPageChange={setPage} />
      <EditModal title={editId ? "Edit Holiday" : "Add Holiday"} open={open} onClose={() => setOpen(false)} onSubmit={async () => {
        try {
          if (editId) await holidayService.update(editId, form);
          else await holidayService.create(form);
          showToast("Saved");
          setOpen(false);
          load();
        } catch (e) { showToast(getErrorMessage(e), "error"); }
      }}>
        <input className="w-full border p-2 rounded mb-2" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input type="date" className="w-full border p-2 rounded mb-2" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
        <input className="w-full border p-2 rounded mb-2" placeholder="Type" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} />
        <textarea className="w-full border p-2 rounded" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
      </EditModal>
      <DeleteConfirmation open={!!deleteTarget} title="Delete" message={`Delete ${deleteTarget?.name}?`} onConfirm={async () => { await holidayService.remove(deleteTarget.id); setDeleteTarget(null); load(); }} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
}
