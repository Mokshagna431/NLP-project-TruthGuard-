/**
 * TruthGuard API Client
 * Manages JWT tokens, authenticated requests, and error handling.
 */

const API_BASE = 'http://localhost:8000/api';

// Token Storage Helpers
export const getToken = () => localStorage.getItem('truthguard_token');
export const setToken = (token) => localStorage.setItem('truthguard_token', token);
export const removeToken = () => localStorage.removeItem('truthguard_token');

export const getUser = () => {
  try {
    const u = localStorage.getItem('truthguard_user');
    return u ? JSON.parse(u) : null;
  } catch {
    return null;
  }
};
export const setUser = (user) => localStorage.setItem('truthguard_user', JSON.stringify(user));
export const removeUser = () => localStorage.removeItem('truthguard_user');

// Centralized Request Handler
async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const config = {
    ...options,
    headers
  };

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, config);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || `Request failed with status ${res.status}`);
    }
    // Return blob for PDF / file downloads
    if (options.responseType === 'blob') {
      return await res.blob();
    }
    // Return text for CSV / TXT
    if (options.responseType === 'text') {
      return await res.text();
    }
    return await res.json();
  } catch (err) {
    console.error(`[API Error] ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Auth
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  logout: () => {
    removeToken();
    removeUser();
    return request('/auth/logout', { method: 'POST' }).catch(() => {});
  },
  getMe: () => request('/auth/me'),
  forgotPassword: (email) => request('/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) }),
  resetPassword: (data) => request('/auth/reset-password', { method: 'POST', body: JSON.stringify(data) }),

  // Profile & Settings
  getProfile: () => request('/profile'),
  updateProfile: (data) => request('/profile', { method: 'PUT', body: JSON.stringify(data) }),
  changePassword: (data) => request('/profile/password', { method: 'PUT', body: JSON.stringify(data) }),
  deleteAccount: () => request('/profile', { method: 'DELETE' }),
  getSettings: () => request('/settings'),
  updateSettings: (data) => request('/settings', { method: 'PUT', body: JSON.stringify(data) }),

  // Verification
  createVerification: (data) => request('/verification', { method: 'POST', body: JSON.stringify(data) }),
  listVerifications: (params = '') => request(`/verification?${params}`),
  getVerification: (id) => request(`/verification/${id}`),
  rerunVerification: (id) => request(`/verification/${id}/rerun`, { method: 'POST' }),
  deleteVerification: (id) => request(`/verification/${id}`, { method: 'DELETE' }),
  saveVerification: (id) => request(`/verification/${id}/save`, { method: 'POST' }),
  removeSaved: (id) => request(`/saved/${id}`, { method: 'DELETE' }),
  listSaved: () => request('/saved'),

  // Analytics
  getAnalyticsOverview: (days = 30) => request(`/analytics/overview?days=${days}`),
  getAnalyticsTrends: (days = 30) => request(`/analytics/trends?days=${days}`),
  getAnalyticsDistribution: (days = 30) => request(`/analytics/distribution?days=${days}`),

  // Reports
  downloadPdfUrl: (id) => `${API_BASE}/reports/${id}/pdf`,
  downloadCsvUrl: (id) => `${API_BASE}/reports/${id}/csv`,
  downloadJsonUrl: (id) => `${API_BASE}/reports/${id}/json`,
  downloadTxtUrl: (id) => `${API_BASE}/reports/${id}/txt`,

  // Feedback
  submitFeedback: (data) => request('/feedback', { method: 'POST', body: JSON.stringify(data) }),
  listFeedback: () => request('/feedback'),

  // Admin
  getAdminOverview: () => request('/admin/overview'),
  listAdminUsers: (params = '') => request(`/admin/users?${params}`),
  toggleUserStatus: (id, active) => request(`/admin/users/${id}/status?active=${active}`, { method: 'PUT' }),
  getSystemHealth: () => request('/admin/system-health'),

  // Health & Benchmarks
  checkHealth: () => request('/health'),
  getBenchmarkResults: () => request('/results'),

  // Citation Verification
  verifyCitations: (text) => request('/citation/verify', { method: 'POST', body: JSON.stringify({ text }) })
};
