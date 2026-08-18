import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Wraps admin-only routes. If there's no token, redirect to login instead
// of rendering the dashboard and letting every API call 401.
export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }
  return children;
}
