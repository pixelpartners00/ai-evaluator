import React from "react";
import { useNavigate } from "react-router-dom";

const PendingApproval = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-amber-100 text-amber-500 mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-8 w-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800">
          Account Pending Approval
        </h2>
      </div>

      <p className="text-gray-600 mb-6">
        Thank you for registering as a teacher. Your account is currently
        pending approval from an administrator. You will be notified once your
        account has been approved.
      </p>

      <p className="text-gray-600 mb-6">
        If you believe this is an error or have any questions, please contact
        the administrator.
      </p>

      <div className="flex justify-center">
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50"
        >
          Log Out
        </button>
      </div>
    </div>
  );
};

export default PendingApproval;
