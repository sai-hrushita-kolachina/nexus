import "../../styles/authentication.css";

import {
  ArrowLeft,
  ArrowRight,
  Bot,
  Eye,
  EyeOff,
  Sparkles,
} from "lucide-react";

import { useState } from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

export default function Signup() {
  const navigate = useNavigate();

  const { signup } = useAuth();

  const pendingName =
    sessionStorage.getItem("nexus_pending_name") || "";

  const [name, setName] = useState(pendingName);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await signup(
        name.trim(),
        email.trim(),
        password
      );

      sessionStorage.removeItem("nexus_pending_name");
      sessionStorage.removeItem("nexus_pending_role");

      navigate("/chat");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create your account."
      );
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
            onClick={() => navigate("/user-login")}
          >
            <ArrowLeft size={16} />
            Back
          </button>

          <div className="login-card-header">
            <div className="sparkle-circle">
              <Sparkles size={20} />
            </div>

            <h1>Create account</h1>

            <p>Join Nexus as an employee.</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <label>
              Your name

              <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Enter your name"
                required
              />
            </label>

            <label>
              Email

              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@company.com"
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
                  placeholder="Create a password"
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

            <label>
              Confirm password

              <input
                type={showPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Confirm your password"
                required
              />
            </label>

            {error && (
              <div className="auth-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Create account"}
              <ArrowRight size={18} />
            </button>
          </form>

          <div className="auth-switch">
            Already have an account?

            <Link to="/user-login">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}