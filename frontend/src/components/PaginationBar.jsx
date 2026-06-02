export default function PaginationBar({ page, totalPages, total, onPageChange }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <p className="text-slate-600">Total: {total}</p>
      <div className="flex gap-2">
        <button disabled={page <= 1} onClick={() => onPageChange(page - 1)} className="px-3 py-1 border rounded disabled:opacity-50">
          Previous
        </button>
        <span className="px-3 py-1">
          Page {page} of {Math.max(1, totalPages)}
        </span>
        <button
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
