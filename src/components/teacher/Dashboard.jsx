import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { teacherService } from "../../services/api";

const Dashboard = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const user = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    fetchTeacherTests();
  }, []);

  const fetchTeacherTests = async () => {
    try {
      setLoading(true);
      const response = await teacherService.getTests(user._id);
      setTests(response.tests || []);
    } catch (err) {
      console.error("Failed to fetch tests:", err);
      setError("Failed to load tests. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTest = async (testId) => {
    if (
      window.confirm(
        "Are you sure you want to delete this test? This action cannot be undone."
      )
    ) {
      try {
        await teacherService.deleteTest(testId);

        // Remove deleted test from list
        setTests((prev) => prev.filter((test) => test._id !== testId));

        setSuccessMessage("Test deleted successfully!");

        // Clear success message after 3 seconds
        setTimeout(() => {
          setSuccessMessage("");
        }, 3000);
      } catch (err) {
        console.error("Failed to delete test:", err);
        setError("Failed to delete test. Please try again.");

        // Clear error after 3 seconds
        setTimeout(() => {
          setError("");
        }, 3000);
      }
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Teacher Dashboard</h1>
        <div className="flex gap-3">
          <Link
            to="/teacher/ai-test-generator"
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"
                clipRule="evenodd"
              />
            </svg>
            Generate with AI
          </Link>
          <Link
            to="/teacher/create-test"
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Create New Test
          </Link>
        </div>
      </div>

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
        <h2 className="text-lg font-semibold mb-4">Your Tests</h2>

        {loading ? (
          <p>Loading your tests...</p>
        ) : tests.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">
              You haven't created any tests yet.
            </p>
            <Link
              to="/teacher/create-test"
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Create Your First Test
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead className="bg-gray-100">
                <tr>
                  <th className="py-3 px-4 text-left">Title</th>
                  <th className="py-3 px-4 text-left">Description</th>
                  <th className="py-3 px-4 text-left">Questions</th>
                  <th className="py-3 px-4 text-left">Time Limit</th>
                  <th className="py-3 px-4 text-left">Created Date</th>
                  <th className="py-3 px-4 text-left">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {tests.map((test) => (
                  <tr key={test._id}>
                    <td className="py-3 px-4 font-medium">{test.title}</td>
                    <td className="py-3 px-4 truncate max-w-xs">
                      {test.description}
                    </td>
                    <td className="py-3 px-4">{test.questions.length}</td>
                    <td className="py-3 px-4">{test.time_limit} minutes</td>
                    <td className="py-3 px-4">
                      {new Date(test.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex space-x-2">
                        <Link
                          to={`/teacher/edit-test/${test._id}`}
                          className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() => handleDeleteTest(test._id)}
                          className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                          Delete
                        </button>
                      </div>
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
