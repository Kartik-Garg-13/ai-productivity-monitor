import { useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import StatusBadge from "../../components/StatusBadge";
import SalarySlipPreview from "../../components/salary/SalarySlipPreview";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage, uploadBaseUrl } from "../../services/crudService";
import { salaryService } from "../../services/phase2Service";

export default function EmployeeSalaryPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [preview, setPreview] = useState(null);
  const base = uploadBaseUrl();

  useEffect(() => {
    salaryService.list({ page_size: 50 }).then((r) => setItems(r.data.items));
  }, []);

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
      if (fallbackPath) window.open(`${base}/${fallbackPath}`, "_blank");
    }
  };

  const columns = [
    { key: "month", label: "Month" },
    { key: "gross_salary", label: "Gross", render: (r) => `₹${r.gross_salary || r.net_salary}` },
    { key: "net_salary", label: "Net Salary", render: (r) => `₹${r.net_salary}` },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    {
      key: "actions",
      label: "Actions",
      render: (r) => (
        <div className="space-x-2">
          <button onClick={() => openPreview(r.id)} className="text-indigo-600 text-sm">Preview</button>
          {r.pdf_path && (
            <button onClick={() => downloadPdf(r.id, r.pdf_path)} className="text-indigo-600 text-sm">Download PDF</button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold">Salary Slips</h2>
        <p className="text-slate-500 text-sm">View and download your payslips</p>
      </div>
      <DataTable columns={columns} rows={items} loading={false} emptyMessage="No salary slips yet." />
      {preview && <SalarySlipPreview slip={preview} onClose={() => setPreview(null)} />}
    </div>
  );
}
