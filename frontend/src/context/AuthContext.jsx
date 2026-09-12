import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  loginUserApi,
  signupApi,
  loginAdminApi,
  googleLoginApi,
  getCurrentUser,
} from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore the authenticated session when the application starts.

  useEffect(() => {
    async function restoreSession() {
      const token = localStorage.getItem("nexus_access_token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const data = await getCurrentUser();
        setUser(data.user);
      } catch {
        localStorage.removeItem("nexus_access_token");
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, []);

  // Store our application's JWT and authenticated user.

  function storeSession(data) {
    localStorage.setItem("nexus_access_token", data.access_token);
    setUser(data.user);
  }

  // Employee email/password login.

  async function loginUser(name, email, password) {
    const data = await loginUserApi(name, email, password);
    storeSession(data);
    return data;
  }

  // Employee signup.

  async function signup(name, email, password) {
    const data = await signupApi(name, email, password);
    storeSession(data);
    return data;
  }

  // Admin login.

  async function loginAdmin(email, password) {
    const data = await loginAdminApi(email, password);

    if (data.user?.role !== "admin") {
      throw new Error("Admin access required.");
    }

    storeSession(data);
    return data;
  }

  // Google login. credential = Google ID token.

  async function loginWithGoogle(credential) {
    if (!credential) {
      throw new Error("Google credential was not received.");
    }

    const data = await googleLoginApi(credential);
    storeSession(data);
    return data;
  }

  // Logout.

  function logout() {
    localStorage.removeItem("nexus_access_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, loginUser, signup, loginAdmin, loginWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}