import { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

// Components
import Navbar from "./components/Navbar";
import Login from "./components/auth/Login";
import Register from "./components/auth/Register";
import AdminDashboard from "./components/admin/Dashboard";
import TeacherDashboard from "./components/teacher/Dashboard";
import StudentDashboard from "./components/student/Dashboard";
import CreateTest from "./components/teacher/CreateTest";
import AITestGenerator from "./components/teacher/AITestGenerator";
import TakeTest from "./components/student/TakeTest";
import TestResults from "./components/student/TestResults";
import PendingApproval from "./components/auth/PendingApproval";
import NotFound from "./components/common/NotFound";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar user={user} onLogout={handleLogout} />

        <div className="container mx-auto px-4 py-8">
          <Routes>
            {/* Public routes */}
            <Route
              path="/"
              element={
                user ? (
                  <Navigate to={`/${user.role}/dashboard`} replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />

            <Route
              path="/login"
              element={
                user ? (
                  <Navigate to={`/${user.role}/dashboard`} replace />
                ) : (
                  <Login setUser={setUser} />
                )
              }
            />

            <Route
              path="/register"
              element={
                user ? (
                  <Navigate to={`/${user.role}/dashboard`} replace />
                ) : (
                  <Register setUser={setUser} />
                )
              }
            />

            <Route
              path="/pending-approval"
              element={
                user && user.role === "teacher" && !user.is_approved ? (
                  <PendingApproval />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* Admin routes */}
            <Route
              path="/admin/dashboard"
              element={
                user && user.role === "admin" ? (
                  <AdminDashboard />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* Teacher routes */}
            <Route
              path="/teacher/dashboard"
              element={
                user && user.role === "teacher" && user.is_approved ? (
                  <TeacherDashboard />
                ) : user && user.role === "teacher" ? (
                  <Navigate to="/pending-approval" replace />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            <Route
              path="/teacher/create-test"
              element={
                user && user.role === "teacher" && user.is_approved ? (
                  <CreateTest userId={user._id} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            <Route
              path="/teacher/ai-test-generator"
              element={
                user && user.role === "teacher" && user.is_approved ? (
                  <AITestGenerator userId={user._id} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* Student routes */}
            <Route
              path="/student/dashboard"
              element={
                user && user.role === "student" ? (
                  <StudentDashboard userId={user._id} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            <Route
              path="/student/test/:testId"
              element={
                user && user.role === "student" ? (
                  <TakeTest userId={user._id} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            <Route
              path="/student/results/:attemptId"
              element={
                user && user.role === "student" ? (
                  <TestResults userId={user._id} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* 404 route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
