import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import EditModal from "../../components/EditModal";
import PaginationBar from "../../components/PaginationBar";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../services/crudService";
import { announcementService } from "../../services/phase2Service";

const empty = { title: "", type: "general", content: "", publish_date: "", expiry_date: "", is_pinned: false };

export default function AnnouncementsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [open, setOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await announcementService.list({ page, page_size: 10, search: search || undefined });
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    } finally {
      setLoading(false);
    }
  }, [page, search, showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const save = async () => {
    const payload = { ...form, publish_date: new Date(form.publish_date).toISOString(), expiry_date: form.expiry_date ? new Date(form.expiry_date).toISOString() : null };
    try {
      if (editId) await announcementService.update(editId, payload);
      else await announcementService.create(payload);
      showToast("Saved");
      setOpen(false);
      load();
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  const columns = [
    { key: "title", label: "Title" },
    { key: "type", label: "Type" },
    { key: "publish_date", label: "Publish", render: (r) => new Date(r.publish_date).toLocaleString() },
    { key: "is_pinned", label: "Pinned", render: (r) => (r.is_pinned ? "Yes" : "No") },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="space-x-2">
          <button onClick={() => { setEditId(r.id); setForm({ ...r, publish_date: r.publish_date?.slice(0, 16), expiry_date: r.expiry_date?.slice(0, 16) || "" }); setOpen(true); }} className="text-blue-600 text-sm">Edit</button>
          <button onClick={() => setDeleteTarget(r)} className="text-red-600 text-sm">Delete</button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h2 className="text-2xl font-bold">Announcements</h2>
        <button onClick={() => { setEditId(null); setForm(empty); setOpen(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg">+ Create</button>
      </div>
      <input className="border p-2 rounded max-w-md" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 10)} total={total} onPageChange={setPage} />
      <EditModal title={editId ? "Edit" : "Create"} open={open} onClose={() => setOpen(false)} onSubmit={save}>
        <input className="w-full border p-2 rounded mb-2" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <input className="w-full border p-2 rounded mb-2" placeholder="Type" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} />
        <textarea className="w-full border p-2 rounded mb-2 h-24" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
        <input type="datetime-local" className="w-full border p-2 rounded mb-2" value={form.publish_date} onChange={(e) => setForm({ ...form, publish_date: e.target.value })} />
        <input type="datetime-local" className="w-full border p-2 rounded mb-2" value={form.expiry_date} onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} />
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_pinned} onChange={(e) => setForm({ ...form, is_pinned: e.target.checked })} /> Pin announcement</label>
      </EditModal>
      <DeleteConfirmation open={!!deleteTarget} title="Delete" message={`Delete "${deleteTarget?.title}"?`} onConfirm={async () => { await announcementService.remove(deleteTarget.id); setDeleteTarget(null); load(); }} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
}
