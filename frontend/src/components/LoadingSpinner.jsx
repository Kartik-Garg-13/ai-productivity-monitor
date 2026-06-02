export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="flex items-center gap-2 text-slate-600">
      <div className="h-5 w-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      <span>{label}</span>
    </div>
  );
}
