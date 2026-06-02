import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import EmployeeProfileForm from "../../components/employee/EmployeeProfileForm";
import LoadingSpinner from "../../components/LoadingSpinner";
import { profileFromApi } from "../../constants/employeeProfile";
import { useToast } from "../../context/ToastContext";
import { employeeService, getErrorMessage } from "../../services/crudService";

async function uploadPendingFiles(employeeId, pendingFiles) {
  const entries = Object.entries(pendingFiles || {}).filter(([, file]) => file);
  for (const [docType, file] of entries) {
    await employeeService.uploadDocument(employeeId, docType, file);
  }
}

export default function EmployeeFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [initial, setInitial] = useState(null);
  const [loading, setLoading] = useState(isEdit);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isEdit) {
      setInitial(profileFromApi(null));
      return;
    }
    (async () => {
      try {
        const { data } = await employeeService.getFull(id);
        setInitial(profileFromApi(data));
      } catch (error) {
        showToast(getErrorMessage(error), "error");
        navigate("/admin/employees");
      } finally {
        setLoading(false);
      }
    })();
  }, [id, isEdit, navigate, showToast]);

  const handleSubmit = async (payload, pendingFiles) => {
    setSubmitting(true);
    try {
      if (isEdit) {
        await employeeService.update(id, payload);
        await uploadPendingFiles(id, pendingFiles);
        showToast("Employee updated successfully");
        navigate(`/admin/employees/${id}`);
      } else {
        const { data } = await employeeService.create(payload);
        await uploadPendingFiles(data.id, pendingFiles);
        showToast("Employee created successfully");
        navigate(`/admin/employees/${data.id}`);
      }
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading employee profile..." />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{isEdit ? "Edit Employee" : "Add Employee"}</h2>
        <Link to="/admin/employees" className="text-indigo-600 hover:underline">
          Back to list
        </Link>
      </div>
      <EmployeeProfileForm initial={initial} isEdit={isEdit} onSubmit={handleSubmit} submitting={submitting} />
    </div>
  );
}
