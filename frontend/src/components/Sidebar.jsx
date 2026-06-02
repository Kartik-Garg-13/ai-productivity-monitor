import { Link, useLocation } from "react-router-dom";

export default function Sidebar({ links }) {
  const { pathname } = useLocation();
  return (
    <aside className="w-64 min-h-screen bg-slate-900 text-white p-4">
      <h1 className="text-xl font-bold mb-6">Goldilocks HRMS</h1>
      <nav className="space-y-2">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`block rounded px-3 py-2 ${
              pathname === link.to || (link.to !== "/admin" && link.to !== "/employee/dashboard" && pathname.startsWith(link.to))
                ? "bg-indigo-500"
                : "hover:bg-slate-800"
            }`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
