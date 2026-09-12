import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { useAuth } from "./context/AuthContext";
import { ChatProvider } from "./context/ChatContext";

import Login from "./pages/Login/Login";
import UserLogin from "./pages/UserLogin/UserLogin";
import Signup from "./pages/Signup/Signup";
import AdminLogin from "./pages/AdminLogin/AdminLogin";

import Chat from "./pages/Chat/Chat";
import AdminDashboard from "./pages/AdminDashboard/AdminDashboard";
import Documents from "./pages/Documents/Documents";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== "admin") {
    return <Navigate to="/chat" replace />;
  }

  return children;
}

export default function App() {
  return (
    <Routes>
      
      {/* PUBLIC */}
      <Route
        path="/"
        element={<Navigate to="/login" replace />}
      />

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/user-login"
        element={<UserLogin />}
      />

      <Route
        path="/signup"
        element={<Signup />}
      />

      <Route
        path="/admin-login"
        element={<AdminLogin />}
      />

      {/* USER / ADMIN PROTECTED */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatProvider>
              <Chat />
            </ChatProvider>
          </ProtectedRoute>
        }
      />

      {/* ADMIN ONLY */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <ChatProvider>
              <AdminDashboard />
            </ChatProvider>
          </AdminRoute>
        }
      />

      <Route
        path="/documents"
        element={
          <AdminRoute>
            <ChatProvider>
              <Documents />
            </ChatProvider>
          </AdminRoute>
        }
      />

      {/* UNKNOWN ROUTES */}
      <Route
        path="*"
        element={<Navigate to="/login" replace />}
      />
    </Routes>
  );
}