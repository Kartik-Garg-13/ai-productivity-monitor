import { useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import StatusBadge from "../../components/StatusBadge";
import { uploadBaseUrl } from "../../services/crudService";
import { salaryService } from "../../services/phase2Service";

export default function EmployeeSalaryPage() {
  const [items, setItems] = useState([]);
  const base = uploadBaseUrl();

  useEffect(() => {
    salaryService.list({ page_size: 50 }).then((r) => setItems(r.data.items));
  }, []);

  const columns = [
    { key: "month", label: "Month" },
    { key: "net_salary", label: "Net Salary", render: (r) => `₹${r.net_salary}` },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    {
      key: "pdf",
      label: "Slip",
      render: (r) =>
        r.pdf_path ? (
          <a href={`${base}/${r.pdf_path}`} target="_blank" rel="noreferrer" className="text-indigo-600 text-sm">
            Download
          </a>
        ) : (
          "—"
        ),
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Salary Slips</h2>
      <DataTable columns={columns} rows={items} loading={false} emptyMessage="No salary slips yet." />
    </div>
  );
}
