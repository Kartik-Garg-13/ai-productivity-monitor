import { useEffect, useState } from "react";
import { getErrorMessage, uploadBaseUrl } from "../../services/crudService";
import { documentService } from "../../services/phase2Service";
import { useToast } from "../../context/ToastContext";

export default function EmployeeDocumentsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);

  useEffect(() => {
    documentService.list({ page_size: 50 }).then((r) => setItems(r.data.items));
  }, []);

  const download = async (doc) => {
    try {
      const { data } = await documentService.trackDownload(doc.id);
      window.open(`${uploadBaseUrl()}/${data.file_path}`, "_blank");
    } catch (e) {
      showToast(getErrorMessage(e), "error");
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Document Center</h2>
      <div className="grid md:grid-cols-2 gap-3">
        {items.map((d) => (
          <div key={d.id} className="bg-white rounded-xl p-4 shadow flex justify-between items-center">
            <div>
              <p className="font-medium">{d.title}</p>
              <p className="text-sm text-slate-500">{d.category}</p>
            </div>
            <button onClick={() => download(d)} className="text-indigo-600 text-sm font-medium">
              Download
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
