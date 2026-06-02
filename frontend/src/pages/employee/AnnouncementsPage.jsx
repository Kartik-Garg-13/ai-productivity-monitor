import { useEffect, useState } from "react";
import { announcementService } from "../../services/phase2Service";

export default function EmployeeAnnouncementsPage() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    announcementService.list({ page_size: 50 }).then((r) => setItems(r.data.items));
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Announcements</h2>
      <div className="space-y-3">
        {items.map((a) => (
          <article key={a.id} className={`bg-white rounded-xl p-5 shadow ${a.is_pinned ? "border-l-4 border-indigo-500" : ""}`}>
            <div className="flex justify-between">
              <h3 className="font-semibold">{a.title}</h3>
              {a.is_pinned && <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded">Pinned</span>}
            </div>
            <p className="text-xs text-slate-500 mt-1">{a.type} · {new Date(a.publish_date).toLocaleString()}</p>
            <p className="mt-3 text-slate-700 whitespace-pre-wrap">{a.content}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
