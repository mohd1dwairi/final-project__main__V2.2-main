import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem("user_token");

  // إذا ما في توكن → رجعه على login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // إذا في توكن → اعرض الصفحة
  return children;
}
