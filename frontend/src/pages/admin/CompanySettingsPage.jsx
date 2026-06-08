import { useEffect, useState } from "react";
import DragDropUpload from "../../components/DragDropUpload";
import { useToast } from "../../context/ToastContext";
import { IMAGE_ACCEPT } from "../../constants/uploadConfig";
import api from "../../services/api";
import { getErrorMessage, uploadBaseUrl } from "../../services/crudService";
import { companySettingsService } from "../../services/leaveService";

export default function CompanySettingsPage() {
  const { showToast } = useToast();
  const [form, setForm] = useState({ company_name: "", company_address: "", gst_number: "", company_logo_path: "" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    companySettingsService.get().then((r) => {
      setForm({
        company_name: r.data.company_name || "",
        company_address: r.data.company_address || "",
        gst_number: r.data.gst_number || "",
        company_logo_path: r.data.company_logo_path || "",
      });
    }).finally(() => setLoading(false));
  }, []);

  const save = async (e) => {
    e.preventDefault();
    try {
      await companySettingsService.update({
        company_name: form.company_name,
        company_address: form.company_address,
        gst_number: form.gst_number,
      });
      showToast("Company settings saved");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const uploadLogo = async (file, setProgress) => {
    const fd = new FormData();
    fd.append("file", file);
    const { data } = await api.post("/company-settings/logo", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (e.total) setProgress(Math.round((e.loaded * 100) / e.total));
      },
    });
    setForm((p) => ({ ...p, company_logo_path: data.company_logo_path }));
    showToast("Logo uploaded");
  };

  if (loading) return <p className="text-slate-400">Loading...</p>;
  const base = uploadBaseUrl();
  const logoUrl = form.company_logo_path ? `${base}/${form.company_logo_path}` : null;

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-2xl font-bold">Company Settings</h2>
      <p className="text-slate-500 text-sm">Configure company details displayed on salary slips</p>
      <form onSubmit={save} className="bg-white rounded-xl shadow p-6 space-y-4">
        <div>
          <label className="block text-sm text-slate-600 mb-1">Company Name</label>
          <input className="w-full border rounded-lg p-2.5" value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} required />
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Company Address</label>
          <textarea className="w-full border rounded-lg p-2.5" rows={3} value={form.company_address} onChange={(e) => setForm({ ...form, company_address: e.target.value })} />
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">GST Number</label>
          <input className="w-full border rounded-lg p-2.5" value={form.gst_number} onChange={(e) => setForm({ ...form, gst_number: e.target.value })} />
        </div>
        <DragDropUpload
          label="Company Logo"
          accept={IMAGE_ACCEPT}
          onUpload={uploadLogo}
          existingUrl={logoUrl}
          existingName="Current logo"
          hint="PNG or JPG — max 10 MB"
        />
        <button type="submit" className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg">Save Settings</button>
      </form>
    </div>
  );
}
