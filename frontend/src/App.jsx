import { Routes, Route, Navigate, NavLink } from 'react-router-dom'
import Logo from './Logo'
import Chatbot from './Chatbot'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Agenda from './pages/Agenda'
import Biblioteca from './pages/Biblioteca'
import Simulaciones from './pages/Simulaciones'
import Dudas from './pages/Dudas'
import MisCursos from './pages/MisCursos'
import Libro from './pages/Libro'
import Ruta from './pages/Ruta'
import Tutor from './pages/Tutor'
import Suscripcion from './pages/Suscripcion'
import AdminPanel from './pages/AdminPanel'

export function useAuth() {
  return {
    token: localStorage.getItem('token'),
    role: localStorage.getItem('role'),
    logout: () => { localStorage.clear(); location.href = '/login' }
  }
}

// Menu segun rol: cada uno ve SOLO lo suyo
const MENU = {
  admin: [
    ['/app/admin', '⚙️ Panel admin'],
    ['/app/agenda', '📅 Agenda'],
    ['/app/simulaciones', '📝 Simulaciones'],
    ['/app/tutor', '🤖 Tutor IA'],
  ],
  profesor: [
    ['/app/cursos', '🧑‍🏫 Mis Cursos'],
    ['/app/agenda', '📅 Agenda'],
    ['/app/dudas', '💬 Dudas'],
    ['/app/biblioteca', '🎬 Biblioteca'],
    ['/app/simulaciones', '📝 Simulaciones'],
    ['/app/tutor', '🤖 Tutor IA'],
  ],
  apoderado: [
    ['/app', '📊 Panel'],
    ['/app/agenda', '📅 Agenda'],
    ['/app/biblioteca', '🎬 Biblioteca'],
    ['/app/simulaciones', '📝 Simulaciones'],
    ['/app/ruta', '🎯 Mi Ruta'],
    ['/app/tutor', '🤖 Tutor IA'],
    ['/app/suscripcion', '💳 Suscripción'],
    ['/app/dudas', '💬 Dudas'],
  ],
}
const HOME = { admin: '/app/admin', profesor: '/app/cursos', apoderado: '/app' }

function AppShell({ children }) {
  const { role, logout } = useAuth()
  const items = MENU[role] || MENU.apoderado
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand" style={{ display: 'flex', alignItems: 'center', gap: '.6rem' }}>
          <Logo size={30} /> Aula<span>Siete</span>
        </div>
        <div className="role">
          {role === 'apoderado' ? 'Portal del apoderado' : role === 'profesor' ? 'Portal del docente' : 'Administración'}
        </div>
        <nav>
          {items.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === '/app'}>{label}</NavLink>
          ))}
        </nav>
        <div className="foot"><a href="#" onClick={logout}>Cerrar sesión</a></div>
      </aside>
      <main className="main">{children}</main>
      <Chatbot />
    </div>
  )
}

function Protected({ children }) {
  const { token, role } = useAuth()
  if (!token) return <Navigate to="/login" />
  return <AppShell>{children}</AppShell>
}

// Redirige la raiz /app segun el rol
function RoleHome() {
  const { role } = useAuth()
  return <Navigate to={HOME[role] || '/app'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Register />} />
      <Route path="/app" element={<Protected><RoleHome /></Protected>} />
      <Route path="/app/admin" element={<Protected><AdminPanel /></Protected>} />
      <Route path="/app/agenda" element={<Protected><Agenda /></Protected>} />
      <Route path="/app/biblioteca" element={<Protected><Biblioteca /></Protected>} />
      <Route path="/app/simulaciones" element={<Protected><Simulaciones /></Protected>} />
      <Route path="/app/dudas" element={<Protected><Dudas /></Protected>} />
      <Route path="/app/cursos" element={<Protected><MisCursos /></Protected>} />
      <Route path="/app/ruta" element={<Protected><Ruta /></Protected>} />
      <Route path="/app/tutor" element={<Protected><Tutor /></Protected>} />
      <Route path="/app/suscripcion" element={<Protected><Suscripcion /></Protected>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
