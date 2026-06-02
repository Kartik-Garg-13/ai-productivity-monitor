import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/employee/dashboard", label: "Dashboard" },
  { to: "/employee/projects", label: "Projects" },
  { to: "/employee/tasks", label: "Tasks" },
  { to: "/employee/attendance", label: "Attendance" },
  { to: "/employee/workflow", label: "SOD/EOD" },
  { to: "/employee/leaves", label: "Leaves" },
  { to: "/employee/announcements", label: "Announcements" },
  { to: "/employee/holidays", label: "Holidays" },
  { to: "/employee/documents", label: "Documents" },
  { to: "/employee/expenses", label: "Expenses" },
  { to: "/employee/salary", label: "Salary" },
  { to: "/employee/profile", label: "Profile" },
];

export default function EmployeeLayout() {
  const { logout } = useAuth();
  return (
    <div className="flex bg-slate-100 dark:bg-slate-950 dark:text-white min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-6">
        <div className="flex justify-end mb-6">
          <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded">
            Logout
          </button>
        </div>
        <Outlet />
      </main>
    </div>
  );
}
