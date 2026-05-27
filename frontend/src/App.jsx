import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminLayout from "./layouts/AdminLayout";
import EmployeeLayout from "./layouts/EmployeeLayout";
import LoginPage from "./pages/LoginPage";
import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import AttendanceAdminPage from "./pages/admin/AttendanceAdminPage";
import EmployeesPage from "./pages/admin/EmployeesPage";
import LeaveApprovalsPage from "./pages/admin/LeaveApprovalsPage";
import WorkflowReviewPage from "./pages/admin/WorkflowReviewPage";
import AttendancePage from "./pages/employee/AttendancePage";
import EmployeeDashboardPage from "./pages/employee/EmployeeDashboardPage";
import LeavePage from "./pages/employee/LeavePage";
import ProfilePage from "./pages/employee/ProfilePage";
import WorkflowPage from "./pages/employee/WorkflowPage";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute role="admin">
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminDashboardPage />} />
        <Route path="employees" element={<EmployeesPage />} />
        <Route path="attendance" element={<AttendanceAdminPage />} />
        <Route path="workflow" element={<WorkflowReviewPage />} />
        <Route path="leaves" element={<LeaveApprovalsPage />} />
      </Route>
      <Route
        path="/employee"
        element={
          <ProtectedRoute role="employee">
            <EmployeeLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<EmployeeDashboardPage />} />
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="workflow" element={<WorkflowPage />} />
        <Route path="leaves" element={<LeavePage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
