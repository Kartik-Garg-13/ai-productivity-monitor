export function Field({ label, children, className = "" }) {
  return (
    <label className={`block text-sm ${className}`}>
      <span className="text-slate-600 mb-1 block">{label}</span>
      {children}
    </label>
  );
}

export function Input({ className = "", ...props }) {
  return <input className={`w-full border border-slate-300 rounded-lg px-3 py-2 ${className}`} {...props} />;
}

export function Select({ className = "", children, ...props }) {
  return (
    <select className={`w-full border border-slate-300 rounded-lg px-3 py-2 ${className}`} {...props}>
      {children}
    </select>
  );
}

export function TextArea({ className = "", ...props }) {
  return <textarea className={`w-full border border-slate-300 rounded-lg px-3 py-2 ${className}`} rows={3} {...props} />;
}
