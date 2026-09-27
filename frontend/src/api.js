// Thin wrapper around the KittenConnect FastAPI backend.
// Keeps the JWT in localStorage and attaches it to authenticated requests.

// In production this is set to the Render backend URL via the VITE_API_URL
// environment variable (see DEPLOY.md). Falls back to localhost for dev.
const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "kittenconnect_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// Core request helper. Adds JSON headers + the auth token, and turns
// non-2xx responses into thrown Errors carrying the backend's detail message.
async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const resp = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (resp.status === 204) return null;

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || `Request failed (${resp.status})`);
  }
  return data;
}

// --- Auth ---
export const signup = (payload) =>
  request("/signup", { method: "POST", body: payload });

export const login = (email, password) =>
  request("/login", { method: "POST", body: { email, password } });

export const getMe = () => request("/me", { auth: true });

// --- Photo upload (multipart, not JSON) ---
export async function uploadPhoto(fileObj) {
  const form = new FormData();
  form.append("file", fileObj);

  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers, // note: no Content-Type — the browser sets the multipart boundary
    body: form,
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.detail || "Upload failed");
  return data.url;
}

// --- Kittens ---
export const listKittens = () => request("/kitten_list");

export const createKitten = (payload) =>
  request("/kittens", { method: "POST", body: payload, auth: true });

export const updateKitten = (id, payload) =>
  request(`/kittens/${id}`, { method: "PUT", body: payload, auth: true });

export const deleteKitten = (id) =>
  request(`/kittens/${id}`, { method: "DELETE", auth: true });
