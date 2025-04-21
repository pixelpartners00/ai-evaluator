import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { studentService } from "../../services/api";

const Dashboard = ({ userId }) => {
  const [availableTests, setAvailableTests] = useState([]);
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch both available tests and attempts in parallel
      const [testsResponse, attemptsResponse] = await Promise.all([
        studentService.getAvailableTests(),
        studentService.getAttempts(userId),
      ]);

      setAvailableTests(testsResponse.tests || []);
      setAttempts(attemptsResponse.attempts || []);
    } catch (err) {
      console.error("Failed to fetch data:", err);
      setError("Failed to load tests or attempts. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  // Filter out tests that have already been completed
  const getAvailableTests = () => {
    const completedTestIds = attempts
      .filter((attempt) => attempt.is_completed)
      .map((attempt) => attempt.test_id);

    return availableTests.filter(
      (test) => !completedTestIds.includes(test._id)
    );
  };

  // Get completed test attempts
  const getCompletedAttempts = () => {
    return attempts.filter((attempt) => attempt.is_completed);
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Student Dashboard</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Available Tests Section */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Available Tests</h2>

        {getAvailableTests().length === 0 ? (
          <p className="text-gray-500">No tests available at the moment.</p>
        ) : (
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {getAvailableTests().map((test) => (
              <div
                key={test._id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <h3 className="font-medium text-lg mb-2">{test.title}</h3>
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {test.description}
                </p>
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>{test.questions.length} questions</span>
                  <span>{test.time_limit} minutes</span>
                </div>
                <div className="mt-4">
                  <Link
                    to={`/student/test/${test._id}`}
                    className="block w-full text-center px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    Start Test
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Completed Tests Section */}
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Your Test Results</h2>

        {getCompletedAttempts().length === 0 ? (
          <p className="text-gray-500">You haven't completed any tests yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead className="bg-gray-100">
                <tr>
                  <th className="py-3 px-4 text-left">Test</th>
                  <th className="py-3 px-4 text-left">Score</th>
                  <th className="py-3 px-4 text-left">Completion Date</th>
                  <th className="py-3 px-4 text-left">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {getCompletedAttempts().map((attempt) => (
                  <tr key={attempt._id}>
                    <td className="py-3 px-4 font-medium">
                      {attempt.test?.title || "Unknown Test"}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`font-medium ${
                          attempt.score >= 70
                            ? "text-green-600"
                            : attempt.score >= 50
                            ? "text-amber-600"
                            : "text-red-600"
                        }`}
                      >
                        {attempt.score.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {new Date(attempt.completed_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <Link
                        to={`/student/results/${attempt._id}`}
                        className="text-indigo-600 hover:text-indigo-800 underline"
                      >
                        View Results
                      </Link>
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
