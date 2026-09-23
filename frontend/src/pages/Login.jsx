import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api'

export default function Login() {
  const [email, setEmail] = useState('apoderado@demo.cl')
  const [password, setPassword] = useState('demo1234')
  const [error, setError] = useState('')
  const nav = useNavigate()

  async function submit(e) {
    e.preventDefault()
    try {
      const data = await login(email, password)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role)
      nav('/')
    } catch (err) { setError(err.message) }
  }

  return (
    <div className="auth-wrap">
      <form className="card" onSubmit={submit}>
        <h1>Aula Site</h1>
        <p className="muted">Apoyo pedagógico para Exámenes Libres · Chile</p>
        {error && <p className="error">{error}</p>}
        <input type="email" value={email} onChange={e => setEmail(e.target.value)}
               placeholder="Correo" required />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)}
               placeholder="Contraseña" required />
        <button type="submit">Ingresar</button>
        <p className="small muted">
          La certificación oficial de estudios la emite el Mineduc mediante
          Exámenes Libres. Aula Site prepara y acompaña.
        </p>
      </form>
    </div>
  )
}
