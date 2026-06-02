import { useEffect, useState } from "react";
import LoadingSpinner from "../../components/LoadingSpinner";
import { useToast } from "../../context/ToastContext";
import { attendanceService, getErrorMessage } from "../../services/crudService";

export default function AttendancePage() {
  const { showToast } = useToast();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await attendanceService.history();
      setHistory(data);
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const checkIn = async () => {
    setActionLoading(true);
    try {
      const { data } = await attendanceService.checkIn();
      showToast(`Check-in successful${data.ip_address ? ` (IP: ${data.ip_address})` : ""}`);
      await load();
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setActionLoading(false);
    }
  };

  const checkOut = async () => {
    setActionLoading(true);
    try {
      const { data } = await attendanceService.checkOut();
      showToast(`Check-out successful. Duration: ${data.duration}`);
      await load();
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">My Attendance</h2>
      <div className="flex gap-3">
        <button
          disabled={actionLoading}
          className="bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={checkIn}
        >
          Check-In
        </button>
        <button
          disabled={actionLoading}
          className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={checkOut}
        >
          Check-Out
        </button>
      </div>
      {loading ? (
        <LoadingSpinner label="Loading attendance history..." />
      ) : (
        <div className="bg-white rounded p-4 shadow overflow-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-100">
              <tr>
                <th className="p-3">Date</th>
                <th className="p-3">Check In</th>
                <th className="p-3">Check Out</th>
                <th className="p-3">Duration</th>
                <th className="p-3">IP Address</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-slate-500">
                    No attendance records yet.
                  </td>
                </tr>
              ) : (
                history.map((row) => (
                  <tr key={row.id} className="border-t">
                    <td className="p-3">{row.date}</td>
                    <td className="p-3">{new Date(row.check_in).toLocaleTimeString()}</td>
                    <td className="p-3">{row.check_out ? new Date(row.check_out).toLocaleTimeString() : "-"}</td>
                    <td className="p-3">{row.work_duration || "-"}</td>
                    <td className="p-3 font-mono text-sm">{row.ip_address || "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
