import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import EditModal from "../../components/EditModal";
import PaginationBar from "../../components/PaginationBar";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { employeeService, getErrorMessage } from "../../services/crudService";
import { projectService, taskService } from "../../services/phase2Service";

const empty = { project_id: "", title: "", description: "", priority: "medium", assigned_employee_id: "", due_date: "", status: "pending" };

export default function TasksPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [open, setOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await taskService.list({ page, page_size: 10, search: search || undefined });
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
    projectService.list({ page_size: 100 }).then((r) => setProjects(r.data.items));
    employeeService.list({ page_size: 100 }).then((r) => setEmployees(r.data.items));
  }, [load]);

  const save = async () => {
    const payload = {
      ...form,
      project_id: Number(form.project_id),
      assigned_employee_id: form.assigned_employee_id ? Number(form.assigned_employee_id) : null,
    };
    try {
      if (editId) await taskService.update(editId, payload);
      else await taskService.create(payload);
      showToast(editId ? "Task updated" : "Task created");
      setOpen(false);
      load();
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  const columns = [
    { key: "title", label: "Title" },
    { key: "project_name", label: "Project" },
    { key: "assignee_name", label: "Assignee" },
    { key: "priority", label: "Priority" },
    { key: "due_date", label: "Due" },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="space-x-2">
          <button onClick={() => { setEditId(r.id); setForm({ ...empty, ...r, project_id: r.project_id, assigned_employee_id: r.assigned_employee_id || "" }); setOpen(true); }} className="text-blue-600 text-sm">Edit</button>
          <button onClick={() => setDeleteTarget(r)} className="text-red-600 text-sm">Delete</button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h2 className="text-2xl font-bold">Tasks</h2>
        <button onClick={() => { setEditId(null); setForm(empty); setOpen(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg">+ Create Task</button>
      </div>
      <input className="border p-2 rounded max-w-md" placeholder="Search tasks..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 10)} total={total} onPageChange={setPage} />
      <EditModal title={editId ? "Edit Task" : "Create Task"} open={open} onClose={() => setOpen(false)} onSubmit={save}>
        <select className="w-full border p-2 rounded mb-2" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })}>
          <option value="">Select project</option>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <input className="w-full border p-2 rounded mb-2" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <textarea className="w-full border p-2 rounded mb-2" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <select className="w-full border p-2 rounded mb-2" value={form.assigned_employee_id} onChange={(e) => setForm({ ...form, assigned_employee_id: e.target.value })}>
          <option value="">Assign to</option>
          {employees.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
        </select>
        <input type="date" className="w-full border p-2 rounded mb-2" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
        <select className="w-full border p-2 rounded mb-2" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="blocked">Blocked</option>
        </select>
      </EditModal>
      <DeleteConfirmation open={!!deleteTarget} title="Delete Task" message={`Delete "${deleteTarget?.title}"?`} onConfirm={async () => { await taskService.remove(deleteTarget.id); setDeleteTarget(null); load(); }} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
}
