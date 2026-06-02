import LoadingSpinner from "./LoadingSpinner";

export default function DataTable({ columns, rows, loading, emptyMessage = "No records found." }) {
  if (loading) return <LoadingSpinner />;
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow overflow-auto">
      <table className="w-full text-left text-sm min-w-[600px]">
        <thead className="bg-slate-100 dark:bg-slate-700">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="p-3 font-medium">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="p-6 text-center text-slate-500">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={row.id} className="border-t hover:bg-slate-50 dark:hover:bg-slate-700/50">
                {columns.map((col) => (
                  <td key={col.key} className="p-3">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
