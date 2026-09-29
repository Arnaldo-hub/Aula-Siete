import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../api'
import Logo from '../Logo'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [showPwd, setShowPwd] = useState(false)
  const nav = useNavigate()

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      const data = await login(email, password)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role)
      nav('/app')
    } catch (err) { setError(err.message) }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-side">
        <h2>Bienvenido al campus virtual</h2>
        <p>Clases en vivo, biblioteca de grabaciones, simulaciones de Examenes Libres y reportes de progreso para tu familia.</p>
        <ul>
          <li>🎥 Clases online en vivo con docentes</li>
          <li>📝 Simulaciones con evaluacion automatica</li>
          <li>📈 Seguimiento del progreso en tiempo real</li>
        </ul>
      </div>
      <div className="auth-card">
        <form onSubmit={submit}>
          <div className="brand" style={{display:'flex',alignItems:'center',gap:'.5rem'}}><Logo size={34} />Aula<span>Siete</span></div>
          <p className="muted" style={{marginBottom:'1.6rem'}}>Apoyo pedagogico para Examenes Libres</p>
          {error && <div className="error" style={{marginBottom:'1rem'}}>{error}</div>}
          <label>Correo electronico</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                 placeholder="tu@correo.cl" required autoFocus />
          <label>Contraseña</label>
          <div className="pwd-field">
            <input type={showPwd ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)}
                   placeholder="********" required autoComplete="current-password" />
            <button type="button" className="pwd-eye" onClick={() => setShowPwd(!showPwd)}
                    title={showPwd ? 'Ocultar contraseña' : 'Ver contraseña'}>
              {showPwd ? '🙈' : '👁️'}
            </button>
          </div>
          <button type="submit" className="btn btn-primary btn-block">Ingresar</button>
          <p className="auth-note">
            ¿No tienes cuenta? <Link to="/registro" style={{ color: 'var(--primary)' }}>Regístrate gratis</Link>
            <br />
            La certificación oficial de estudios la emite el Mineduc mediante Exámenes
            Libres presenciales. Aula Siete prepara y acompaña.{' '}
            <Link to="/" style={{color:'var(--primary)'}}>Volver al inicio</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
