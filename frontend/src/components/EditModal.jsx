export default function EditModal({ title, open, onClose, children, onSubmit, submitLabel = "Save" }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">{title}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800">
            ✕
          </button>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
          className="space-y-3"
        >
          {children}
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded border">
              Cancel
            </button>
            <button type="submit" className="px-4 py-2 rounded bg-indigo-600 text-white">
              {submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
