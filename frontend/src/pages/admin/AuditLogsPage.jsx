import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import PaginationBar from "../../components/PaginationBar";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../services/crudService";
import { auditService } from "../../services/phase2Service";

export default function AuditLogsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await auditService.list({ page, page_size: 20, search: search || undefined });
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

  const columns = [
    { key: "created_at", label: "Time", render: (r) => new Date(r.created_at).toLocaleString() },
    { key: "user_name", label: "User" },
    { key: "action", label: "Action" },
    { key: "entity_type", label: "Entity" },
    { key: "entity_id", label: "ID" },
    { key: "ip_address", label: "IP" },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Audit Logs</h2>
      <input className="border p-2 rounded max-w-md" placeholder="Search actions..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 20)} total={total} onPageChange={setPage} />
    </div>
  );
}
