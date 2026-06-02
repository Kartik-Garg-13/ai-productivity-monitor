const styles = {
  active: "bg-green-100 text-green-800",
  pending: "bg-amber-100 text-amber-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  paid: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  in_progress: "bg-blue-100 text-blue-800",
  blocked: "bg-red-100 text-red-800",
  generated: "bg-slate-100 text-slate-800",
};

export default function StatusBadge({ status }) {
  const key = (status || "").toLowerCase().replace(" ", "_");
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${styles[key] || "bg-slate-100 text-slate-700"}`}>
      {status}
    </span>
  );
}
