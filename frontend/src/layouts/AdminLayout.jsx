import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/admin", label: "Dashboard" },
  { to: "/admin/employees", label: "Employees" },
  { to: "/admin/attendance", label: "Attendance" },
  { to: "/admin/workflow", label: "SOD/EOD Review" },
  { to: "/admin/leaves", label: "Leave Approvals" },
];

export default function AdminLayout() {
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
