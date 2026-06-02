import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import LoadingSpinner from "../../components/LoadingSpinner";
import DeleteConfirmation from "../../components/DeleteConfirmation";
import { useToast } from "../../context/ToastContext";
import { employeeService, getErrorMessage, uploadBaseUrl } from "../../services/crudService";

function Section({ title, children }) {
  return (
    <section className="bg-white rounded-xl shadow p-5">
      <h3 className="text-lg font-semibold border-b pb-2 mb-4">{title}</h3>
      {children}
    </section>
  );
}

function Grid({ items }) {
  return (
    <dl className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
      {items.map(([label, value]) => (
        <div key={label}>
          <dt className="text-slate-500">{label}</dt>
          <dd className="font-medium text-slate-900">{value || "—"}</dd>
        </div>
      ))}
    </dl>
  );
}

export default function EmployeeViewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await employeeService.getFull(id);
      setProfile(data);
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await employeeService.remove(id);
      showToast("Employee deleted successfully");
      navigate("/admin/employees");
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading profile..." />;
  if (!profile) return <p className="text-slate-500">Employee not found.</p>;

  const base = uploadBaseUrl();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">{profile.full_name}</h2>
          <p className="text-slate-600">
            {profile.employee_code} · {profile.designation} · {profile.department}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to={`/admin/employees/${id}/edit`} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">
            Edit
          </Link>
          <button onClick={() => setDeleteOpen(true)} className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm">
            Delete
          </button>
          <Link to="/admin/employees" className="px-4 py-2 border rounded-lg text-sm">
            Back
          </Link>
        </div>
      </div>

      {profile.profile_photo_path && (
        <img
          src={`${base}/${profile.profile_photo_path}`}
          alt="Profile"
          className="w-24 h-24 rounded-full object-cover border"
        />
      )}

      <Section title="Employment Details">
        <Grid
          items={[
            ["Employee ID", profile.employee_id],
            ["Employee Code", profile.employee_code],
            ["Designation", profile.designation],
            ["Department", profile.department],
            ["Joining Date", profile.joining_date],
            ["Employment Type", profile.employment_type],
            ["Reporting Manager", profile.reporting_manager],
            ["Project Lead", profile.project_lead],
            ["Tech Owner", profile.tech_owner],
            ["Company Email", profile.company_email],
            ["Status", profile.employment_status],
            ["Login Email", profile.login_email],
          ]}
        />
      </Section>

      <Section title="Personal Details">
        <Grid
          items={[
            ["Title", profile.title],
            ["First Name", profile.first_name],
            ["Middle Name", profile.middle_name],
            ["Last Name", profile.last_name],
            ["Gender", profile.gender],
            ["Father Name", profile.father_name],
            ["Date of Birth", profile.date_of_birth],
            ["Nationality", profile.nationality],
            ["Marital Status", profile.marital_status],
            ["Blood Group", profile.blood_group],
          ]}
        />
      </Section>

      <Section title="Government Documents">
        <Grid
          items={[
            ["PAN", profile.pan_number],
            ["Aadhaar", profile.aadhaar_number],
            ["Passport", profile.passport_number],
            ["Passport Issue", profile.passport_issue_date],
            ["Passport Expiry", profile.passport_expiry_date],
            ["Issue Place", profile.passport_issue_place],
          ]}
        />
      </Section>

      <div className="grid lg:grid-cols-2 gap-6">
        <Section title="Permanent Address">
          <Grid
            items={Object.entries(profile.permanent_address || {}).map(([k, v]) => [k.replaceAll("_", " "), v])}
          />
        </Section>
        <Section title="Correspondence Address">
          <Grid
            items={Object.entries(profile.correspondence_address || {}).map(([k, v]) => [k.replaceAll("_", " "), v])}
          />
        </Section>
      </div>

      <Section title="Communication">
        <Grid
          items={[
            ["Mobile", profile.mobile_number],
            ["Alternate", profile.alternate_number],
            ["Personal Email", profile.personal_email],
          ]}
        />
      </Section>

      <Section title="Family">
        {profile.family_members?.length ? (
          <div className="space-y-3">
            {profile.family_members.map((f, i) => (
              <div key={i} className="border rounded p-3 text-sm">
                {f.name} ({f.relationship}) — {f.occupation} @ {f.company}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">No family records.</p>
        )}
      </Section>

      <Section title="Bank Details">
        <Grid items={profile.bank_details ? Object.entries(profile.bank_details).map(([k, v]) => [k.replaceAll("_", " "), v]) : []} />
      </Section>

      <Section title="Education">
        {profile.education?.map((e, i) => (
          <p key={i} className="text-sm border-b py-2">
            {e.degree} — {e.institute} ({e.year_of_passing})
          </p>
        ))}
      </Section>

      <Section title="Experience">
        {profile.experience?.map((x, i) => (
          <p key={i} className="text-sm border-b py-2">
            {x.designation} at {x.company_name} ({x.start_date} – {x.end_date || "Present"})
          </p>
        ))}
      </Section>

      <Section title="Skills & Certifications">
        <Grid
          items={profile.skills ? Object.entries(profile.skills).map(([k, v]) => [k.replaceAll("_", " "), v]) : []}
        />
      </Section>

      <Section title="Languages">
        {profile.languages?.map((l, i) => (
          <p key={i} className="text-sm">
            {l.language}: Speak {l.can_speak ? "✓" : "✗"}, Read {l.can_read ? "✓" : "✗"}, Write {l.can_write ? "✓" : "✗"}
          </p>
        ))}
      </Section>

      <Section title="Interests">
        <p className="text-sm">{profile.interests?.join(", ") || "—"}</p>
      </Section>

      <Section title="Documents">
        <ul className="text-sm space-y-1">
          {profile.documents?.map((d) => (
            <li key={d.id}>
              <a className="text-indigo-600 hover:underline" href={`${base}/${d.file_path}`} target="_blank" rel="noreferrer">
                {d.document_type}: {d.original_filename || d.file_path}
              </a>
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Attendance (recent)">
        <div className="overflow-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="bg-slate-100">
                <th className="p-2">Date</th>
                <th className="p-2">Check In</th>
                <th className="p-2">Check Out</th>
                <th className="p-2">Duration</th>
                <th className="p-2">IP</th>
              </tr>
            </thead>
            <tbody>
              {profile.attendance?.map((a) => (
                <tr key={a.id} className="border-t">
                  <td className="p-2">{a.date}</td>
                  <td className="p-2">{a.check_in ? new Date(a.check_in).toLocaleString() : "—"}</td>
                  <td className="p-2">{a.check_out ? new Date(a.check_out).toLocaleString() : "—"}</td>
                  <td className="p-2">{a.work_duration || "—"}</td>
                  <td className="p-2">{a.ip_address || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Leave History">
        {profile.leave_history?.map((l) => (
          <p key={l.id} className="text-sm border-b py-2">
            {l.leave_type}: {l.start_date} → {l.end_date} ({l.status})
          </p>
        ))}
      </Section>

      <DeleteConfirmation
        open={deleteOpen}
        title="Delete Employee"
        message={`Delete ${profile.full_name} and all related records?`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteOpen(false)}
        loading={deleting}
      />
    </div>
  );
}
