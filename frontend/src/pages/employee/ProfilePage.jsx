import { useEffect, useState } from "react";
import api from "../../services/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  useEffect(() => {
    api.get("/employees/profile").then((res) => setProfile(res.data));
  }, []);
  if (!profile) return <div>Loading profile...</div>;
  return (
    <div className="bg-white p-6 rounded shadow max-w-2xl">
      <h2 className="text-2xl font-bold mb-4">Employee Profile</h2>
      <p>Name: {profile.name}</p>
      <p>Email: {profile.email}</p>
      <p>Employee Code: {profile.employee_code}</p>
      <p>Designation: {profile.designation}</p>
      <p>Department: {profile.department}</p>
      <p>Manager: {profile.manager_name || "-"}</p>
    </div>
  );
}
