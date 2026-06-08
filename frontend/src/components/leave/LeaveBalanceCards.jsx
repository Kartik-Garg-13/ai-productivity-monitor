import { LEAVE_TYPES } from "../../constants/payroll";

function ProgressBar({ used, total, color }) {
  const pct = total ? Math.min(100, Math.round((used / total) * 100)) : 0;
  return (
    <div className="w-full bg-slate-100 rounded-full h-2.5 mt-2">
      <div className={`${color} h-2.5 rounded-full transition-all`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function LeaveBalanceCards({ balances = [] }) {
  const byType = Object.fromEntries(balances.map((b) => [b.leave_type, b]));

  return (
    <div className="grid md:grid-cols-3 gap-4">
      {LEAVE_TYPES.map((t) => {
        const b = byType[t.value] || { total_leave: 0, leave_taken: 0, remaining_leave: 0 };
        return (
          <div key={t.value} className="bg-white rounded-xl shadow p-5 border border-slate-100">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-slate-500">{t.label}</p>
                <p className="text-3xl font-bold text-slate-800 mt-1">{b.remaining_leave}</p>
                <p className="text-xs text-slate-400 mt-1">days remaining</p>
              </div>
              <span className={`${t.color} text-white text-xs px-2 py-1 rounded-full`}>{t.label.split(" ")[0]}</span>
            </div>
            <ProgressBar used={b.leave_taken} total={b.total_leave} color={t.color} />
            <div className="flex justify-between text-xs text-slate-500 mt-2">
              <span>Used: {b.leave_taken}</span>
              <span>Total: {b.total_leave}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function LeaveBalanceChart({ balances = [] }) {
  const max = Math.max(...balances.map((b) => b.total_leave), 1);
  return (
    <div className="bg-white rounded-xl shadow p-4 space-y-3">
      <h3 className="font-semibold text-slate-700">Leave Utilization</h3>
      {balances.map((b) => (
        <div key={b.leave_type} className="flex items-center gap-3 text-sm">
          <span className="w-24 text-slate-500 truncate">{b.label || b.leave_type}</span>
          <div className="flex-1 bg-slate-100 rounded h-5 overflow-hidden relative">
            <div className="bg-indigo-500 h-full rounded" style={{ width: `${(b.leave_taken / max) * 100}%` }} />
            <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-slate-700">
              {b.leave_taken}/{b.total_leave}
            </div>
          </div>
          <span className="w-16 text-right text-emerald-600 font-medium">{b.remaining_leave} left</span>
        </div>
      ))}
    </div>
  );
}
