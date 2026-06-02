import { useCallback, useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import EditModal from "../../components/EditModal";
import PaginationBar from "../../components/PaginationBar";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../services/crudService";
import { expenseService } from "../../services/phase2Service";

export default function ExpensesPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [reviewTarget, setReviewTarget] = useState(null);
  const [review, setReview] = useState({ status: "approved", admin_remarks: "", payment_date: "", transaction_id: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await expenseService.list({ page, page_size: 10, status: status || undefined });
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    } finally {
      setLoading(false);
    }
  }, [page, status, showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const columns = [
    { key: "employee_name", label: "Employee" },
    { key: "expense_date", label: "Date" },
    { key: "expense_type", label: "Type" },
    { key: "amount", label: "Amount", render: (r) => `₹${r.amount}` },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
    {
      key: "actions",
      label: "Actions",
      render: (r) =>
        r.status === "pending" ? (
          <button onClick={() => { setReviewTarget(r); setReview({ status: "approved", admin_remarks: "", payment_date: "", transaction_id: "" }); }} className="text-indigo-600 text-sm">Review</button>
        ) : (
          "—"
        ),
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Expense Management</h2>
      <select className="border p-2 rounded" value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}>
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="paid">Paid</option>
      </select>
      <DataTable columns={columns} rows={items} loading={loading} />
      <PaginationBar page={page} totalPages={Math.ceil(total / 10)} total={total} onPageChange={setPage} />
      <EditModal title="Review Expense" open={!!reviewTarget} onClose={() => setReviewTarget(null)} onSubmit={async () => {
        try {
          await expenseService.review(reviewTarget.id, review);
          showToast("Updated");
          setReviewTarget(null);
          load();
        } catch (e) { showToast(getErrorMessage(e), "error"); }
      }}>
        <select className="w-full border p-2 rounded mb-2" value={review.status} onChange={(e) => setReview({ ...review, status: e.target.value })}>
          <option value="approved">Approve</option>
          <option value="rejected">Reject</option>
          <option value="paid">Mark Paid</option>
        </select>
        <textarea className="w-full border p-2 rounded mb-2" placeholder="Remarks" value={review.admin_remarks} onChange={(e) => setReview({ ...review, admin_remarks: e.target.value })} />
        {review.status === "paid" && (
          <>
            <input type="date" className="w-full border p-2 rounded mb-2" value={review.payment_date} onChange={(e) => setReview({ ...review, payment_date: e.target.value })} />
            <input className="w-full border p-2 rounded mb-2" placeholder="Transaction ID" value={review.transaction_id} onChange={(e) => setReview({ ...review, transaction_id: e.target.value })} />
          </>
        )}
      </EditModal>
    </div>
  );
}
