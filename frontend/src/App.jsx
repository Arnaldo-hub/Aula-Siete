import { Routes, Route, Navigate, Link } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Biblioteca from './pages/Biblioteca'
import Simulaciones from './pages/Simulaciones'

function Nav() {
  const t = localStorage.getItem('token')
  if (!t) return null
  return (
    <nav className="nav">
      <span className="brand">Aula Site</span>
      <Link to="/">Panel</Link>
      <Link to="/biblioteca">Biblioteca</Link>
      <Link to="/simulaciones">Simulaciones</Link>
      <a href="#" onClick={() => { localStorage.clear(); location.href = '/' }}>Salir</a>
    </nav>
  )
}

export default function App() {
  return (
    <>
      <Nav />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/biblioteca" element={<Biblioteca />} />
        <Route path="/simulaciones" element={<Simulaciones />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </>
  )
}
