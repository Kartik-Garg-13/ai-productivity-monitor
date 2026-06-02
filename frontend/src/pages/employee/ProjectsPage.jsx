import { useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import StatusBadge from "../../components/StatusBadge";
import { projectService } from "../../services/phase2Service";

export default function EmployeeProjectsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectService.list({ page_size: 50 }).then((r) => {
      setItems(r.data.items);
      setLoading(false);
    });
  }, []);

  const columns = [
    { key: "name", label: "Project" },
    { key: "client_name", label: "Client" },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "project_lead_name", label: "Lead" },
    { key: "task_count", label: "Tasks" },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">My Projects</h2>
      <DataTable columns={columns} rows={items} loading={loading} emptyMessage="No projects assigned." />
    </div>
  );
}
