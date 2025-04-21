import { Link, useNavigate } from "react-router-dom";

const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  return (
    <nav className="bg-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold">AI Evaluator</span>
            </Link>

            {user && (
              <div className="ml-10 flex items-baseline space-x-4">
                {user.role === "admin" && (
                  <Link
                    to="/admin/dashboard"
                    className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                  >
                    Dashboard
                  </Link>
                )}

                {user.role === "teacher" && user.is_approved && (
                  <>
                    <Link
                      to="/teacher/dashboard"
                      className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/teacher/create-test"
                      className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                    >
                      Create Test
                    </Link>
                  </>
                )}

                {user.role === "student" && (
                  <Link
                    to="/student/dashboard"
                    className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                  >
                    Dashboard
                  </Link>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center">
            {user ? (
              <div className="flex items-center gap-4">
                <span className="text-sm">
                  Welcome, {user.first_name || user.username}!
                </span>
                <button
                  onClick={handleLogout}
                  className="px-3 py-2 rounded-md text-sm font-medium bg-indigo-700 hover:bg-indigo-800"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  to="/login"
                  className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-3 py-2 rounded-md text-sm font-medium bg-indigo-700 hover:bg-indigo-800"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
