import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminLayout from "./layouts/AdminLayout";
import EmployeeLayout from "./layouts/EmployeeLayout";
import LoginPage from "./pages/LoginPage";
import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import AttendanceAdminPage from "./pages/admin/AttendanceAdminPage";
import EmployeeFormPage from "./pages/admin/EmployeeFormPage";
import EmployeeViewPage from "./pages/admin/EmployeeViewPage";
import EmployeesPage from "./pages/admin/EmployeesPage";
import AnnouncementsPage from "./pages/admin/AnnouncementsPage";
import AuditLogsPage from "./pages/admin/AuditLogsPage";
import DocumentsPage from "./pages/admin/DocumentsPage";
import ExpensesPage from "./pages/admin/ExpensesPage";
import HolidaysPage from "./pages/admin/HolidaysPage";
import LeaveApprovalsPage from "./pages/admin/LeaveApprovalsPage";
import ProjectsPage from "./pages/admin/ProjectsPage";
import LeaveReportsPage from "./pages/admin/LeaveReportsPage";
import CompanySettingsPage from "./pages/admin/CompanySettingsPage";
import SalaryPage from "./pages/admin/SalaryPage";
import TasksPage from "./pages/admin/TasksPage";
import WorkflowReviewPage from "./pages/admin/WorkflowReviewPage";
import EmployeeAnnouncementsPage from "./pages/employee/AnnouncementsPage";
import EmployeeDocumentsPage from "./pages/employee/DocumentsPage";
import EmployeeExpensesPage from "./pages/employee/ExpensesPage";
import EmployeeHolidaysPage from "./pages/employee/HolidaysPage";
import EmployeeProjectsPage from "./pages/employee/ProjectsPage";
import EmployeeSalaryPage from "./pages/employee/SalaryPage";
import EmployeeTasksPage from "./pages/employee/TasksPage";
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
        <Route path="employees/new" element={<EmployeeFormPage />} />
        <Route path="employees/:id/edit" element={<EmployeeFormPage />} />
        <Route path="employees/:id" element={<EmployeeViewPage />} />
        <Route path="attendance" element={<AttendanceAdminPage />} />
        <Route path="workflow" element={<WorkflowReviewPage />} />
        <Route path="leaves" element={<LeaveApprovalsPage />} />
        <Route path="leave-reports" element={<LeaveReportsPage />} />
        <Route path="company-settings" element={<CompanySettingsPage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="tasks" element={<TasksPage />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="holidays" element={<HolidaysPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="expenses" element={<ExpensesPage />} />
        <Route path="salary" element={<SalaryPage />} />
        <Route path="audit" element={<AuditLogsPage />} />
      </Route>
      <Route
        path="/employee"
        element={
          <ProtectedRoute role="employee">
            <EmployeeLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/employee/dashboard" replace />} />
        <Route path="dashboard" element={<EmployeeDashboardPage />} />
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="workflow" element={<WorkflowPage />} />
        <Route path="leaves" element={<LeavePage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="projects" element={<EmployeeProjectsPage />} />
        <Route path="tasks" element={<EmployeeTasksPage />} />
        <Route path="announcements" element={<EmployeeAnnouncementsPage />} />
        <Route path="holidays" element={<EmployeeHolidaysPage />} />
        <Route path="documents" element={<EmployeeDocumentsPage />} />
        <Route path="expenses" element={<EmployeeExpensesPage />} />
        <Route path="salary" element={<EmployeeSalaryPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
