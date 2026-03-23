/**
 * app.js — Shared JS utilities for AI Coding Mentor frontend
 * Place this file in: /frontend/app.js
 */

// ── Auth guard ──────────────────────────────────────────────
async function checkAuth() {
  try {
    const res = await fetch('/api/me');
    const data = await res.json();
    if (!data.userId) {
      window.location.href = 'login.html';
      return false;
    }
    // Show email in navbar
    const emailEl = document.getElementById('nav-email');
    if (emailEl) emailEl.textContent = data.email || '';
    return true;
  } catch (e) {
    window.location.href = 'login.html';
    return false;
  }
}

// ── Logout ──────────────────────────────────────────────────
async function doLogout() {
  try {
    await fetch('/logout', { method: 'POST' });
  } catch (e) {
    console.error('Logout error:', e);
  } finally {
    window.location.href = 'login.html';
  }
}

// ── Toast notification ──────────────────────────────────────
function showToast(msg, type = 'success') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.className = `toast ${type} show`;
  // Auto hide after 3.5 seconds
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}

// ── Loading overlay ──────────────────────────────────────────
function showLoading(msg = 'Loading…') {
  const el = document.getElementById('loading');
  const txt = document.getElementById('loading-text');
  if (el) el.classList.add('show');
  if (txt) txt.textContent = msg;
}

function hideLoading() {
  const el = document.getElementById('loading');
  if (el) el.classList.remove('show');
}

// ── HTML escape (prevent XSS) ────────────────────────────────
function escHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

// ── Fetch wrapper with error handling ───────────────────────
async function apiFetch(url, options = {}) {
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || `Request failed: ${res.status}`);
    return data;
  } catch (e) {
    throw e;
  }
}