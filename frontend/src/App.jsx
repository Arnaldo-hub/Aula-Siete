import { Routes, Route, Navigate, NavLink } from 'react-router-dom'
import Logo from './Logo'
import Chatbot from './Chatbot'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Agenda from './pages/Agenda'
import Biblioteca from './pages/Biblioteca'
import Simulaciones from './pages/Simulaciones'
import Dudas from './pages/Dudas'
import MisCursos from './pages/MisCursos'

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
        <div className="brand" style={{display: 'flex', alignItems: 'center', gap: '.6rem'}}>
          <Logo size={30} /> Aula<span>Site</span>
        </div>
        <div className="role">{role === 'apoderado' ? 'Portal del apoderado' : role === 'profesor' ? 'Portal del docente' : 'Administracion'}</div>
        <nav>
          <NavLink to="/app" end>📊 Panel</NavLink>
          <NavLink to="/app/agenda">📅 Agenda</NavLink>
          <NavLink to="/app/biblioteca">🎬 Biblioteca</NavLink>
          <NavLink to="/app/simulaciones">📝 Simulaciones</NavLink>
          <NavLink to="/app/dudas">💬 Dudas</NavLink>
          {(role === 'profesor' || role === 'admin') && <NavLink to="/app/cursos">🧑‍🏫 Mis Cursos</NavLink>}
        </nav>
        <div className="foot"><a href="#" onClick={logout}>Cerrar sesion</a></div>
      </aside>
      <main className="main">{children}</main>
      <Chatbot />
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
      <Route path="/app/agenda" element={<Protected><Agenda /></Protected>} />
      <Route path="/app/biblioteca" element={<Protected><Biblioteca /></Protected>} />
      <Route path="/app/simulaciones" element={<Protected><Simulaciones /></Protected>} />
      <Route path="/app/dudas" element={<Protected><Dudas /></Protected>} />
      <Route path="/app/cursos" element={<Protected><MisCursos /></Protected>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
