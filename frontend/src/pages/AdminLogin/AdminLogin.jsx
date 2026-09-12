import "../../styles/authentication.css";

import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  Shield,
  Sparkles,
} from "lucide-react";

import { useState } from "react";

import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

export default function AdminLogin() {
  const navigate = useNavigate();

  const { loginAdmin } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await loginAdmin(email.trim(), password);

      sessionStorage.removeItem("nexus_pending_name");
      sessionStorage.removeItem("nexus_pending_role");

      navigate("/admin");
    } catch (err) {
      setError(err?.response?.data?.detail || "Invalid admin credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-background-glow glow-one" />
      <div className="login-background-glow glow-two" />

      <div className="login-container">
        <div className="login-card">
          <button
            type="button"
            className="login-back-button"
            onClick={() => navigate("/login")}
          >
            <ArrowLeft size={16} />
            Back
          </button>

          <div className="login-card-header">
            <div className="sparkle-circle">
              <Shield size={20} />
            </div>

            <h1>Admin Login</h1>

            <p>Authorized administrators only.</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <label>
              Admin email

              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="admin@company.com"
                required
              />
            </label>

            <label>
              Password

              <div className="password-input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter admin password"
                  required
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="password-toggle"
                >
                  {showPassword ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>
              </div>
            </label>

            {error && <div className="auth-error">{error}</div>}

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading ? "Authenticating..." : "Sign in"}
              <ArrowRight size={18} />
            </button>
          </form>

          <div className="login-note">
            <span className="status-dot" />
            Restricted administrator access
          </div>
        </div>
      </div>
    </div>
  );
}