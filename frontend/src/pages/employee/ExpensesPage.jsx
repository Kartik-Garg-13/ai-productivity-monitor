import { useEffect, useState } from "react";
import DataTable from "../../components/DataTable";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../services/crudService";
import { expenseService } from "../../services/phase2Service";

export default function EmployeeExpensesPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ expense_date: "", expense_type: "", expense_category: "", amount: "", description: "" });
  const [bill, setBill] = useState(null);

  const load = () => {
    expenseService.list({ page_size: 50 }).then((r) => {
      setItems(r.data.items);
      setLoading(false);
    });
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => fd.append(k, v));
    if (bill) fd.append("bill", bill);
    try {
      await expenseService.submit(fd);
      showToast("Expense submitted");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const columns = [
    { key: "expense_date", label: "Date" },
    { key: "expense_type", label: "Type" },
    { key: "amount", label: "Amount", render: (r) => `₹${r.amount}` },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} /> },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">My Expenses</h2>
      <form onSubmit={submit} className="bg-white p-4 rounded-xl shadow grid md:grid-cols-3 gap-3">
        <input type="date" className="border p-2 rounded" required value={form.expense_date} onChange={(e) => setForm({ ...form, expense_date: e.target.value })} />
        <input className="border p-2 rounded" placeholder="Type" required value={form.expense_type} onChange={(e) => setForm({ ...form, expense_type: e.target.value })} />
        <input className="border p-2 rounded" placeholder="Category" required value={form.expense_category} onChange={(e) => setForm({ ...form, expense_category: e.target.value })} />
        <input className="border p-2 rounded" placeholder="Amount" required value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        <input className="border p-2 rounded" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <input type="file" className="border p-2 rounded" onChange={(e) => setBill(e.target.files[0])} />
        <button type="submit" className="bg-indigo-600 text-white rounded-lg md:col-span-3">Submit Expense</button>
      </form>
      <DataTable columns={columns} rows={items} loading={loading} />
    </div>
  );
}
