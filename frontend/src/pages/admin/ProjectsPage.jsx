import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import EditModal from "../../components/EditModal";
import PaginationBar from "../../components/PaginationBar";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { employeeService, getErrorMessage } from "../../services/crudService";
import { projectService } from "../../services/phase2Service";

const empty = {
  name: "",
  client_name: "",
  description: "",
  start_date: "",
  end_date: "",
  status: "active",
  project_lead_id: "",
  tech_owner_id: "",
  member_ids: [],
};

export default function ProjectsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [open, setOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await projectService.list({ page, page_size: 10, search: search || undefined });
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

  useEffect(() => {
    employeeService.list({ page_size: 100 }).then((r) => setEmployees(r.data.items || []));
  }, []);

  const openCreate = () => {
    setEditId(null);
    setForm(empty);
    setOpen(true);
  };

  const openEdit = (row) => {
    setEditId(row.id);
    setForm({
      name: row.name,
      client_name: row.client_name || "",
      description: row.description || "",
      start_date: row.start_date || "",
      end_date: row.end_date || "",
      status: row.status,
      project_lead_id: row.project_lead_id || "",
      tech_owner_id: row.tech_owner_id || "",
      member_ids: row.members?.map((m) => m.id) || [],
    });
    setOpen(true);
  };

  const save = async () => {
    const payload = {
      ...form,
      project_lead_id: form.project_lead_id ? Number(form.project_lead_id) : null,
      tech_owner_id: form.tech_owner_id ? Number(form.tech_owner_id) : null,
      member_ids: form.member_ids.map(Number),
    };
    try {
      if (editId) {
        await projectService.update(editId, payload);
        showToast("Project updated");
      } else {
        await projectService.create(payload);
        showToast("Project created");
      }
      setOpen(false);
      load();
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  const columns = [
    { key: "name", label: "Project" },
    { key: "client_name", label: "Client" },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "project_lead_name", label: "Lead" },
    { key: "task_count", label: "Tasks" },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="space-x-2">
          <button onClick={() => openEdit(r)} className="text-blue-600 text-sm">
            Edit
          </button>
          <button onClick={() => setDeleteTarget(r)} className="text-red-600 text-sm">
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Projects</h2>
        <button onClick={openCreate} className="bg-indigo-600 text-white px-4 py-2 rounded-lg">
          + Create Project
        </button>
      </div>
      <input
        className="border p-2 rounded w-full max-w-md"
        placeholder="Search projects..."
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setPage(1);
        }}
      />
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 10)} total={total} onPageChange={setPage} />

      <EditModal title={editId ? "Edit Project" : "Create Project"} open={open} onClose={() => setOpen(false)} onSubmit={save}>
        <input className="w-full border p-2 rounded mb-2" placeholder="Project name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input className="w-full border p-2 rounded mb-2" placeholder="Client" value={form.client_name} onChange={(e) => setForm({ ...form, client_name: e.target.value })} />
        <textarea className="w-full border p-2 rounded mb-2" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <div className="grid grid-cols-2 gap-2 mb-2">
          <input type="date" className="border p-2 rounded" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
          <input type="date" className="border p-2 rounded" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
        </div>
        <select className="w-full border p-2 rounded mb-2" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="on_hold">On Hold</option>
        </select>
        <select className="w-full border p-2 rounded mb-2" value={form.project_lead_id} onChange={(e) => setForm({ ...form, project_lead_id: e.target.value })}>
          <option value="">Project Lead</option>
          {employees.map((e) => (
            <option key={e.id} value={e.id}>
              {e.name}
            </option>
          ))}
        </select>
        <select className="w-full border p-2 rounded mb-2" value={form.tech_owner_id} onChange={(e) => setForm({ ...form, tech_owner_id: e.target.value })}>
          <option value="">Tech Owner</option>
          {employees.map((e) => (
            <option key={e.id} value={e.id}>
              {e.name}
            </option>
          ))}
        </select>
        <label className="text-sm text-slate-600">Team Members</label>
        <select
          multiple
          className="w-full border p-2 rounded h-28"
          value={form.member_ids.map(String)}
          onChange={(e) => setForm({ ...form, member_ids: Array.from(e.target.selectedOptions, (o) => o.value) })}
        >
          {employees.map((e) => (
            <option key={e.id} value={e.id}>
              {e.name}
            </option>
          ))}
        </select>
      </EditModal>

      <DeleteConfirmation
        open={!!deleteTarget}
        title="Delete Project"
        message={`Delete project "${deleteTarget?.name}"?`}
        onConfirm={async () => {
          await projectService.remove(deleteTarget.id);
          showToast("Project deleted");
          setDeleteTarget(null);
          load();
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
