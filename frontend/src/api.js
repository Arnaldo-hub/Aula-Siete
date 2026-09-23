// URL de la API: en local usa el proxy de Vite (/api);
// en Render se define VITE_API_URL=https://tu-backend.onrender.com/api
const BASE = import.meta.env.VITE_API_URL || '/api'

export function token() { return localStorage.getItem('token') }

export async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token() ? { Authorization: `Bearer ${token()}` } : {})
    },
    body: body ? JSON.stringify(body) : undefined
  })
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText)
  return res.json()
}
export const login = (email, password) =>
  api('/auth/login', { method: 'POST', body: { email, password } })
