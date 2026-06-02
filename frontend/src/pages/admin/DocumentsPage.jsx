import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import PaginationBar from "../../components/PaginationBar";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage, uploadBaseUrl } from "../../services/crudService";
import { documentService } from "../../services/phase2Service";

const CATEGORIES = ["Employee Handbook", "Company Policies", "NDA Templates", "SOP Documents"];

export default function DocumentsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [file, setFile] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await documentService.list({ page, page_size: 10, search: search || undefined });
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

  const upload = async (e) => {
    e.preventDefault();
    if (!file) return showToast("Select a file", "error");
    const fd = new FormData();
    fd.append("title", title);
    fd.append("category", category);
    fd.append("file", file);
    try {
      await documentService.upload(fd);
      showToast("Document uploaded");
      setTitle("");
      setFile(null);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const base = uploadBaseUrl();
  const columns = [
    { key: "title", label: "Title" },
    { key: "category", label: "Category" },
    { key: "download_count", label: "Downloads" },
    { key: "last_accessed", label: "Last Access", render: (r) => (r.last_accessed ? new Date(r.last_accessed).toLocaleString() : "—") },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="space-x-2">
          <a href={`${base}/${r.file_path}`} target="_blank" rel="noreferrer" className="text-indigo-600 text-sm">View</a>
          <button onClick={() => setDeleteTarget(r)} className="text-red-600 text-sm">Delete</button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Document Center</h2>
      <form onSubmit={upload} className="bg-white p-4 rounded-xl shadow grid md:grid-cols-4 gap-3">
        <input className="border p-2 rounded" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <select className="border p-2 rounded" value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
        </select>
        <input type="file" className="border p-2 rounded" onChange={(e) => setFile(e.target.files[0])} required />
        <button type="submit" className="bg-indigo-600 text-white rounded-lg">Upload</button>
      </form>
      <input className="border p-2 rounded max-w-md" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 10)} total={total} onPageChange={setPage} />
      <DeleteConfirmation open={!!deleteTarget} title="Delete" message={`Delete "${deleteTarget?.title}"?`} onConfirm={async () => { await documentService.remove(deleteTarget.id); setDeleteTarget(null); load(); }} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
}
