import "./Login.css";
import "../../styles/authentication.css";

import {
  ArrowRight,
  Building2,
  Shield,
  Sparkles,
} from "lucide-react";

import { useState } from "react";

import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [role, setRole] = useState(null);

  const trimmedName = name.trim();

  const canContinue = trimmedName.length > 0 && role !== null;

  function handleContinue(event) {
    event.preventDefault();

    if (!canContinue) {
      return;
    }

    sessionStorage.setItem("nexus_pending_name", trimmedName);
    sessionStorage.setItem("nexus_pending_role", role);

    if (role === "admin") {
      navigate("/admin-login");
    } else {
      navigate("/user-login");
    }
  }

  return (
    <div className="login-page">
      <div className="login-background-glow glow-one" />
      <div className="login-background-glow glow-two" />

      <div className="login-container">
        <div className="login-card">
          <div className="login-card-header">
            <div className="sparkle-circle">
              <Sparkles size={20} />
            </div>

            <h1>Welcome to Nexus</h1>

            <p>Your company's knowledge assistant.</p>
          </div>

          <form onSubmit={handleContinue} className="login-form">
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
              Continue as

              <div className="role-options">
                <button
                  type="button"
                  className={`role-option ${role === "employee" ? "selected" : ""}`}
                  onClick={() => setRole("employee")}
                >
                  <Building2 size={20} />

                  <div>
                    <strong>Employee</strong>

                    <span>Ask questions and explore knowledge</span>
                  </div>
                </button>

                <button
                  type="button"
                  className={`role-option ${role === "admin" ? "selected" : ""}`}
                  onClick={() => setRole("admin")}
                >
                  <Shield size={20} />

                  <div>
                    <strong>Admin</strong>

                    <span>Manage company knowledge</span>
                  </div>
                </button>
              </div>
            </label>

            <button
              type="submit"
              className="login-button"
              disabled={!canContinue}
            >
              Continue
              <ArrowRight size={18} />
            </button>
          </form>

          <div className="login-note">
            <span className="status-dot" />
            Secure authentication
          </div>
        </div>
      </div>
    </div>
  );
}