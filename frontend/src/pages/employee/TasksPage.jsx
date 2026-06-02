import { useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../services/crudService";
import { taskService } from "../../services/phase2Service";

export default function EmployeeTasksPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentTask, setCommentTask] = useState(null);
  const [comment, setComment] = useState("");

  const load = () => {
    setLoading(true);
    taskService.list({ page_size: 50 }).then((r) => {
      setItems(r.data.items);
      setLoading(false);
    });
  };

  useEffect(() => {
    load();
  }, []);

  const updateStatus = async (id, status) => {
    try {
      await taskService.updateStatus(id, status);
      showToast("Status updated");
      load();
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  const columns = [
    { key: "title", label: "Task" },
    { key: "project_name", label: "Project" },
    { key: "priority", label: "Priority" },
    { key: "due_date", label: "Due" },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="flex flex-wrap gap-2">
          {r.status !== "completed" && (
            <>
              <button onClick={() => updateStatus(r.id, "in_progress")} className="text-blue-600 text-xs">Start</button>
              <button onClick={() => updateStatus(r.id, "completed")} className="text-green-600 text-xs">Complete</button>
              <button onClick={() => updateStatus(r.id, "blocked")} className="text-red-600 text-xs">Blocked</button>
            </>
          )}
          <button onClick={() => setCommentTask(r)} className="text-slate-600 text-xs">Comment</button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">My Tasks</h2>
      <DataTable columns={columns} rows={items} loading={loading} />
      {commentTask && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="font-semibold mb-2">Comment on {commentTask.title}</h3>
            <textarea className="w-full border p-2 rounded mb-3" rows={3} value={comment} onChange={(e) => setComment(e.target.value)} />
            <div className="flex justify-end gap-2">
              <button onClick={() => setCommentTask(null)} className="px-3 py-1 border rounded">Cancel</button>
              <button
                onClick={async () => {
                  await taskService.addComment(commentTask.id, comment);
                  showToast("Comment added");
                  setComment("");
                  setCommentTask(null);
                }}
                className="px-3 py-1 bg-indigo-600 text-white rounded"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
