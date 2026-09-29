import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Logo from '../Logo'
import { BASE } from '../api'

export default function Register() {
  const [f, setF] = useState({ full_name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [ok, setOk] = useState(false)
  const nav = useNavigate()

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      const res = await fetch(`${BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...f, role: 'apoderado' })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'No se pudo registrar')
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role)
      setOk(true)
      setTimeout(() => nav('/app'), 1200)
    } catch (err) { setError(err.message) }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-side">
        <h2>Crea tu cuenta de apoderado</h2>
        <p>Gratis. Registra a tu hijo, ríndele el diagnóstico y mira cómo se crea su ruta personalizada de estudio.</p>
        <ul>
          <li>✓ Diagnóstico de ingreso con ruta automática</li>
          <li>✓ Tutor IA 24/7 y simulaciones de examen</li>
          <li>✓ Primera clase de prueba gratis</li>
        </ul>
      </div>
      <div className="auth-card">
        <form onSubmit={submit}>
          <div className="brand" style={{ display: 'flex', alignItems: 'center', gap: '.5rem' }}>
            <Logo size={34} /> Aula<span>Siete</span>
          </div>
          <p className="muted" style={{ marginBottom: '1.4rem' }}>Registro de apoderado</p>
          {error && <div className="error" style={{ marginBottom: '1rem' }}>{error}</div>}
          {ok && <div className="card ok" style={{ marginBottom: '1rem' }}>Cuenta creada. Entrando...</div>}
          <label>Tu nombre completo</label>
          <input value={f.full_name} onChange={e => setF({ ...f, full_name: e.target.value })}
                 placeholder="Ej: María Pérez" required />
          <label>Correo electrónico</label>
          <input type="email" value={f.email} onChange={e => setF({ ...f, email: e.target.value })}
                 placeholder="tu@correo.cl" required />
          <label>Contraseña</label>
          <input type="password" value={f.password} onChange={e => setF({ ...f, password: e.target.value })}
                 placeholder="Mínimo 8 caracteres" minLength={8} required />
          <button type="submit" className="btn btn-primary btn-block">Crear mi cuenta gratis</button>
          <p className="auth-note">
            ¿Ya tienes cuenta? <Link to="/login" style={{ color: 'var(--primary)' }}>Inicia sesión aquí</Link>
            {' · '}<Link to="/" style={{ color: 'var(--primary)' }}>Volver al inicio</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
