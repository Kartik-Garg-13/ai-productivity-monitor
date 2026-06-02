import { useEffect, useState } from "react";
import { holidayService } from "../../services/phase2Service";

export default function EmployeeHolidaysPage() {
  const [items, setItems] = useState([]);
  const [year, setYear] = useState(new Date().getFullYear());

  useEffect(() => {
    holidayService.list({ page_size: 50, year }).then((r) => setItems(r.data.items));
  }, [year]);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Holiday Calendar</h2>
      <input type="number" className="border p-2 rounded w-32" value={year} onChange={(e) => setYear(Number(e.target.value))} />
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
        {items.map((h) => (
          <div key={h.id} className="bg-white rounded-xl p-4 shadow">
            <p className="font-semibold">{h.name}</p>
            <p className="text-sm text-indigo-600">{h.date}</p>
            <p className="text-xs text-slate-500">{h.type}</p>
            {h.description && <p className="text-sm mt-2">{h.description}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
