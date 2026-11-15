const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    });
  } catch {
    throw new Error(`Could not connect to ${API_BASE_URL}.`);
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail;
    const message = Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail;
    throw new Error(message || `Request failed (${response.status}).`);
  }
  return payload;
}

export function fetchDashboard() {
  return request('/api/dashboard/summary');
}

export function fetchDataset(name, limit = 100, offset = 0) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return request(`/api/data/${encodeURIComponent(name)}?${params}`);
}

export function runSchedule({ scale, seed }) {
  return request('/api/scheduling/run', { method: 'POST', body: JSON.stringify({ scale, seed }) });
}