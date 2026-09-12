import "./UserLogin.css";
import "../../styles/authentication.css";

import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  Sparkles,
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

export default function UserLogin() {
  const navigate = useNavigate();

  const {
    loginUser,
    loginWithGoogle,
  } = useAuth();

  const googleButtonRef = useRef(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  /*
   * Google Sign-In
   */
  useEffect(() => {
    let intervalId = null;
    let timeoutId = null;

    function initializeGoogle() {
      const clientId =
        import.meta.env.VITE_GOOGLE_CLIENT_ID;

      if (!clientId) {
        console.error(
          "VITE_GOOGLE_CLIENT_ID is missing."
        );

        return true;
      }

      if (!window.google?.accounts?.id) {
        return false;
      }

      if (!googleButtonRef.current) {
        return false;
      }

      window.google.accounts.id.initialize({
        client_id: clientId,

        callback: async (response) => {
          setError("");
          setGoogleLoading(true);

          try {
            await loginWithGoogle(
              response.credential
            );

            sessionStorage.removeItem(
              "nexus_pending_name"
            );

            sessionStorage.removeItem(
              "nexus_pending_role"
            );

            navigate("/chat");
          } catch (err) {
            setError(
              err?.response?.data?.detail ||
                "Google Sign-In failed."
            );
          } finally {
            setGoogleLoading(false);
          }
        },
      });

      googleButtonRef.current.innerHTML = "";

      window.google.accounts.id.renderButton(
        googleButtonRef.current,
        {
          theme: "outline",
          size: "large",
          width: 368,
          text: "signin_with",
          shape: "rectangular",
        }
      );

      return true;
    }

    if (initializeGoogle()) {
      return;
    }

    intervalId = setInterval(() => {
      if (initializeGoogle()) {
        clearInterval(intervalId);
      }
    }, 100);

    timeoutId = setTimeout(() => {
      clearInterval(intervalId);

      if (!window.google?.accounts?.id) {
        console.error(
          "Google Identity Services failed to load."
        );
      }
    }, 10000);

    return () => {
      clearInterval(intervalId);
      clearTimeout(timeoutId);
    };
  }, [loginWithGoogle, navigate]);

  /*
   * Email + Password Login
   */
  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      /*
       * Your existing AuthContext expects:
       * loginUser(name, email, password)
       *
       * Name is no longer collected on this page,
       * so we pass an empty string.
       */
      await loginUser(
        "",
        email.trim(),
        password
      );

      sessionStorage.removeItem(
        "nexus_pending_name"
      );

      sessionStorage.removeItem(
        "nexus_pending_role"
      );

      navigate("/chat");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Invalid email or password."
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

        {/* Login Card */}
        <div className="login-card">

          {/* Back */}
          <button
            type="button"
            className="login-back-button"
            onClick={() => navigate("/login")}
          >
            <ArrowLeft size={16} />
            Back
          </button>


          {/* Header */}
          <div className="login-card-header">

            <div className="sparkle-circle">
              <Sparkles size={20} />
            </div>

            <h1>Employee Login</h1>

            <p>
              Sign in to access your company's knowledge.
            </p>

          </div>


          {/* Login Form */}
          <form
            onSubmit={handleSubmit}
            className="login-form"
          >

            {/* Email */}
            <label>
              Email

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="you@company.com"
                required
              />
            </label>


            {/* Password */}
            <label>
              Password

              <div className="password-input-wrapper">

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  placeholder="Enter your password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      !showPassword
                    )
                  }
                >
                  {showPassword ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>

              </div>
            </label>


            {/* Error */}
            {error && (
              <div className="auth-error">
                {error}
              </div>
            )}


            {/* Sign In */}
            <button
              type="submit"
              className="login-button"
              disabled={
                loading || googleLoading
              }
            >
              {loading
                ? "Signing in..."
                : "Sign in"}

              <ArrowRight size={18} />
            </button>

          </form>


          {/* OR Divider */}
          <div className="google-divider">

            <span></span>

            <div>OR</div>

            <span></span>

          </div>


          {/* Google Sign In */}
          <div
            ref={googleButtonRef}
            className="google-login-button"
          />


          {googleLoading && (
            <div className="google-loading">
              Signing in with Google...
            </div>
          )}


          {/* Create Account */}
          <div className="auth-switch">

            <span>
              Don't have an account?
            </span>

            <Link to="/signup">
              Create account
            </Link>

          </div>


          {/* Security Note */}
          <div className="login-note">

            <span className="status-dot" />

            Secure employee authentication

          </div>

        </div>
      </div>
    </div>
  );
}