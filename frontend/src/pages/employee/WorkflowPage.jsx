import { useState } from "react";
import api from "../../services/api";

export default function WorkflowPage() {
  const [sod, setSod] = useState({
    submitted_for_date: "",
    type: "",
    category: "",
    subcategory: "",
    project: "",
    work_type: "Feature",
    start_time: "",
    end_time: "",
    completion_percentage: 0,
    ticket_number: "",
  });
  const [eod, setEod] = useState({ submitted_for_date: "", morning_activity: "", incomplete_reason: "", completion_remarks: "" });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">SOD / EOD</h2>
      <div className="grid md:grid-cols-2 gap-4">
        <form
          className="bg-white p-4 rounded shadow space-y-2"
          onSubmit={(e) => {
            e.preventDefault();
            api.post("/workflow/sod", sod);
          }}
        >
          <h3 className="font-semibold">Submit SOD</h3>
          {Object.keys(sod).map((k) => (
            <input
              key={k}
              className="w-full border p-2 rounded"
              placeholder={k}
              value={sod[k]}
              onChange={(e) => setSod((p) => ({ ...p, [k]: e.target.value }))}
            />
          ))}
          <button className="bg-indigo-600 text-white px-4 py-2 rounded">Submit SOD</button>
        </form>
        <form
          className="bg-white p-4 rounded shadow space-y-2"
          onSubmit={(e) => {
            e.preventDefault();
            api.post("/workflow/eod", eod);
          }}
        >
          <h3 className="font-semibold">Submit EOD</h3>
          {Object.keys(eod).map((k) => (
            <input
              key={k}
              className="w-full border p-2 rounded"
              placeholder={k}
              value={eod[k]}
              onChange={(e) => setEod((p) => ({ ...p, [k]: e.target.value }))}
            />
          ))}
          <button className="bg-indigo-600 text-white px-4 py-2 rounded">Submit EOD</button>
        </form>
      </div>
    </div>
  );
}
