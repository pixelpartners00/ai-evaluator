import { useState, useEffect } from "react";
import { adminService } from "../../services/api";

const Dashboard = () => {
  const [pendingTeachers, setPendingTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    fetchPendingTeachers();
  }, []);

  const fetchPendingTeachers = async () => {
    try {
      setLoading(true);
      const response = await adminService.getPendingTeachers();
      setPendingTeachers(response.teachers || []);
    } catch (err) {
      console.error("Failed to fetch pending teachers:", err);
      setError(
        "Failed to load pending teacher approvals. Please try again later."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleApproveTeacher = async (teacherId) => {
    try {
      await adminService.approveTeacher(teacherId);

      // Remove approved teacher from list
      setPendingTeachers((prev) =>
        prev.filter((teacher) => teacher._id !== teacherId)
      );

      setSuccessMessage("Teacher approved successfully!");

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 3000);
    } catch (err) {
      console.error("Failed to approve teacher:", err);
      setError("Failed to approve teacher. Please try again.");

      // Clear error after 3 seconds
      setTimeout(() => {
        setError("");
      }, 3000);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {successMessage}
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">
          Teachers Pending Approval
        </h2>

        {loading ? (
          <p>Loading pending teachers...</p>
        ) : pendingTeachers.length === 0 ? (
          <p className="text-gray-500">No teachers pending approval.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead className="bg-gray-100">
                <tr>
                  <th className="py-3 px-4 text-left">Name</th>
                  <th className="py-3 px-4 text-left">Username</th>
                  <th className="py-3 px-4 text-left">Email</th>
                  <th className="py-3 px-4 text-left">Registration Date</th>
                  <th className="py-3 px-4 text-left">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pendingTeachers.map((teacher) => (
                  <tr key={teacher._id}>
                    <td className="py-3 px-4">
                      {teacher.first_name && teacher.last_name
                        ? `${teacher.first_name} ${teacher.last_name}`
                        : "N/A"}
                    </td>
                    <td className="py-3 px-4">{teacher.username}</td>
                    <td className="py-3 px-4">{teacher.email}</td>
                    <td className="py-3 px-4">
                      {new Date(teacher.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => handleApproveTeacher(teacher._id)}
                        className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                      >
                        Approve
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
