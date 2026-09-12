import axios from "axios";

// API CONFIGURATION
const API_URL = import.meta.env.VITE_BACKEND_URL;


// AXIOS INSTANCE
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// AUTHENTICATION INTERCEPTOR

// Every authenticated request automatically receives the JWT stored after employee/admin/Google login.
// Token key MUST match AuthContext.jsx: nexus_access_token.
// Flow: Frontend → api.js → Authorization: Bearer <JWT> → FastAPI → get_current_user().

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("nexus_access_token");

    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// AUTHENTICATION APIs

// Employee signup.
// POST /api/auth/signup.
// Used by: AuthContext.jsx → signup().

export async function signupApi(name, email, password) {
  const response = await api.post(
    "/api/auth/signup",
    {
      name,
      email,
      password,
    }
  );

  return response.data;
}

// Employee normal login.
// POST /api/auth/login.
// Used by: AuthContext.jsx → loginUser().
// NOTE: The name is accepted by the frontend flow, but the backend login endpoint authenticates using email + password.

export async function loginUserApi(name, email, password) {
  const response = await api.post(
    "/api/auth/login",
    {
      email,
      password,
    }
  );

  return response.data;
}

// Google login.
// POST /api/auth/google.
// The Google Identity Services frontend provides a credential JWT.
// That credential is sent to FastAPI.
// FastAPI then verifies the Google token, gets the Google user's identity, finds or creates the employee account, creates our Nexus JWT, and returns our JWT + user.

export async function googleLoginApi(credential) {
  const response = await api.post(
    "/api/auth/google",
    {
      credential,
    }
  );

  return response.data;
}

// Admin login.
// POST /api/auth/admin-login.
// Used by: AuthContext.jsx → loginAdmin().

export async function loginAdminApi(email, password) {
  const response = await api.post(
    "/api/auth/admin-login",
    {
      email,
      password,
    }
  );

  return response.data;
}

// Get currently authenticated user.
// GET /api/auth/me.
// Used when the application starts to restore an existing JWT session.

export async function getCurrentUser() {
  const response = await api.get("/api/auth/me");

  return response.data;
}

// CHAT APIs

// Send a chat message.
// POST /api/chat.
// JWT is automatically attached by the Axios interceptor above.

export async function sendMessage(
  message,
  conversationId = null
) {
  const response = await api.post(
    "/api/chat",
    {
      message,
      conversation_id: conversationId,
    }
  );

  return response.data;
}

// CONVERSATION HISTORY APIs

// Get all conversations.
// GET /api/history.

export async function getConversations() {
  const response = await api.get("/api/history");

  return response.data;
}

// Get one conversation.
// GET /api/history/{conversationId}.

export async function getConversation(conversationId) {
  const response = await api.get(
    `/api/history/${conversationId}`
  );

  return response.data;
}

// Delete conversation.
// DELETE /api/history/{conversationId}.

export async function deleteConversation(conversationId) {
  const response = await api.delete(
    `/api/history/${conversationId}`
  );

  return response.data;
}

// DOCUMENT APIs

// Get company documents.
// Admin-only backend endpoint.
// GET /api/documents.

export async function getDocuments() {
  const response = await api.get("/api/documents");

  return response.data;
}

// Upload company document.
// Admin-only backend endpoint.
// This is for the existing Admin Documents page.
// It is NOT the paperclip/PDF chat attachment feature.

export async function uploadDocument(
  file,
  department = "",
  docType = ""
) {
  const formData = new FormData();

  formData.append("file", file);

  if (department) {
    formData.append("department", department);
  }

  if (docType) {
    formData.append("doc_type", docType);
  }

  const response = await api.post(
    "/api/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

// Delete company document.
// Admin-only backend endpoint.
// DELETE /api/documents/{filename}.

export async function deleteDocument(filename) {
  const response = await api.delete(
    `/api/documents/${encodeURIComponent(filename)}`
  );

  return response.data;
}

// SEARCH API

// Search company knowledge.
// GET /api/search.
// Requires authentication.

export async function searchKnowledge(query, k = 5) {
  const response = await api.get(
    "/api/search",
    {
      params: {
        q: query,
        k,
      },
    }
  );

  return response.data;
}

// HEALTH API

// Backend health check.
// GET /api/health.
// This endpoint is public.

export async function healthCheck() {
  const response = await api.get("/api/health");

  return response.data;
}

// DEFAULT EXPORT

export default api;