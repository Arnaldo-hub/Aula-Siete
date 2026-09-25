import { Routes, Route, Navigate, NavLink, useNavigate, Link } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Biblioteca from './pages/Biblioteca'
import Simulaciones from './pages/Simulaciones'

export function useAuth() {
  return {
    token: localStorage.getItem('token'),
    role: localStorage.getItem('role'),
    logout: () => { localStorage.clear(); location.href = '/login' }
  }
}

function AppShell({ children }) {
  const { role, logout } = useAuth()
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">Aula<span>Site</span></div>
        <div className="role">{role === 'apoderado' ? 'Portal del apoderado' : role === 'profesor' ? 'Portal del docente' : 'Administracion'}</div>
        <nav>
          <NavLink to="/app" end>📊 Panel</NavLink>
          <NavLink to="/app/biblioteca">🎬 Biblioteca</NavLink>
          <NavLink to="/app/simulaciones">📝 Simulaciones</NavLink>
        </nav>
        <div className="foot"><a href="#" onClick={logout}>Cerrar sesion</a></div>
      </aside>
      <main className="main">{children}</main>
    </div>
  )
}

function Protected({ children }) {
  const { token } = useAuth()
  if (!token) return <Navigate to="/login" />
  return <AppShell>{children}</AppShell>
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/app" element={<Protected><Dashboard /></Protected>} />
      <Route path="/app/biblioteca" element={<Protected><Biblioteca /></Protected>} />
      <Route path="/app/simulaciones" element={<Protected><Simulaciones /></Protected>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
