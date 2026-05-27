import { useEffect, useState } from "react";
import api from "../../services/api";

export default function WorkflowReviewPage() {
  const [sods, setSods] = useState([]);
  const [eods, setEods] = useState([]);

  const load = async () => {
    const [sodRes, eodRes] = await Promise.all([api.get("/workflow/admin/sod"), api.get("/workflow/admin/eod")]);
    setSods(sodRes.data);
    setEods(eodRes.data);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">SOD / EOD Reviews</h2>
      <section className="bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">SOD Entries</h3>
        {sods.map((x) => (
          <div key={x.id} className="border rounded p-2 mb-2">
            #{x.id} | Emp {x.employee_id} | {x.project} | {x.review_status}
          </div>
        ))}
      </section>
      <section className="bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">EOD Entries</h3>
        {eods.map((x) => (
          <div key={x.id} className="border rounded p-2 mb-2">
            #{x.id} | Emp {x.employee_id} | {x.submitted_for_date} | {x.review_status}
          </div>
        ))}
      </section>
    </div>
  );
}
