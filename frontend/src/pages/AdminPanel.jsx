import { useEffect, useState } from 'react'
import { api } from '../api'

const fld = { width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '.6rem', fontFamily: 'inherit' }

export default function AdminPanel() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [subs, setSubs] = useState([])
  const [filter, setFilter] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [nu, setNu] = useState({ email: '', password: '', full_name: '', role: 'profesor' })

  function load() {
    api('/admin/stats').then(setStats).catch(e => setErr(e.message))
    api('/admin/users').then(setUsers).catch(() => {})
    api('/admin/subscriptions').then(setSubs).catch(() => {})
  }
  useEffect(() => { load() }, [])

  async function createUser(e) {
    e.preventDefault(); setMsg(''); setErr('')
    try {
      await api('/admin/users', { method: 'POST', body: nu })
      setMsg(`Cuenta creada: ${nu.email} (${nu.role})`)
      setNu({ email: '', password: '', full_name: '', role: 'profesor' }); load()
    } catch (e2) { setErr(e2.message) }
  }

  const shown = filter ? users.filter(u => u.role === filter) : users

  const CARDS = stats ? [
    ['👨‍👩‍👧 Apoderados', stats.users_apoderados],
    ['🧑‍🏫 Profesores', stats.users_profesores],
    ['🎒 Alumnos', stats.students],
    ['📚 Cursos', stats.courses],
    ['📎 Materiales', stats.materials],
    ['📝 Simulaciones rendidas', stats.attempts],
    ['⭐ Promedio general', stats.attempts_avg ? stats.attempts_avg + '%' : '—'],
    ['💳 Suscripciones activas', stats.subscriptions_active],
    ['💬 Dudas pendientes', stats.doubts_pending],
  ] : []

  return (
    <div>
      <h2 className="page-title">⚙️ Panel de administración</h2>
      {msg && <div className="card ok">{msg}</div>}
      {err && <div className="error">{err}</div>}

      {stats && (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))' }}>
          {CARDS.map(([label, val]) => (
            <div className="card" key={label} style={{ textAlign: 'center', padding: '1rem' }}>
              <p style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--primary)', margin: 0 }}>{val}</p>
              <p className="muted" style={{ margin: '.3rem 0 0', fontSize: '.82rem' }}>{label}</p>
            </div>
          ))}
        </div>
      )}

      <section className="card">
        <h3>➕ Crear cuenta (profesor / apoderado / admin)</h3>
        <form onSubmit={createUser} style={{ display: 'grid', gridTemplateColumns: '2fr 2fr 1fr 1fr auto', gap: '.6rem' }}>
          <input style={fld} placeholder="Nombre completo" value={nu.full_name} onChange={e => setNu({ ...nu, full_name: e.target.value })} required />
          <input style={fld} type="email" placeholder="correo@ejemplo.cl" value={nu.email} onChange={e => setNu({ ...nu, email: e.target.value })} required />
          <input style={fld} type="password" placeholder="Contraseña" value={nu.password} onChange={e => setNu({ ...nu, password: e.target.value })} minLength={8} required />
          <select style={fld} value={nu.role} onChange={e => setNu({ ...nu, role: e.target.value })}>
            <option value="profesor">Profesor</option><option value="apoderado">Apoderado</option><option value="admin">Admin</option>
          </select>
          <button className="btn btn-primary btn-sm" type="submit">Crear</button>
        </form>
      </section>

      <section className="card">
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '.8rem' }}>
          <h3 style={{ margin: 0 }}>👥 Usuarios ({shown.length})</h3>
          <select value={filter} onChange={e => setFilter(e.target.value)} style={{ ...fld, width: 'auto', margin: 0 }}>
            <option value="">Todos los roles</option>
            <option value="apoderado">Apoderados</option>
            <option value="profesor">Profesores</option>
            <option value="admin">Admins</option>
          </select>
        </div>
        <table>
          <thead><tr><th>#</th><th>Nombre</th><th>Correo</th><th>Rol</th><th>Registro</th></tr></thead>
          <tbody>
            {shown.map(u => (
              <tr key={u.id}>
                <td>{u.id}</td><td>{u.full_name}</td><td>{u.email}</td>
                <td><span className="chip" style={{ fontSize: '.75rem' }}>{u.role}</span></td>
                <td>{u.created}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {subs.length > 0 && (
        <section className="card">
          <h3>💳 Suscripciones ({subs.length})</h3>
          <table>
            <thead><tr><th>Apoderado</th><th>Plan</th><th>Monto</th><th>Estado</th><th>Fecha</th></tr></thead>
            <tbody>
              {subs.map(s => (
                <tr key={s.id}>
                  <td>{s.guardian}</td>
                  <td>{s.plan === 'grupal' ? 'Grupo En Vivo' : 'Intensivo 1 a 1'}</td>
                  <td>${s.amount.toLocaleString('es-CL')}</td>
                  <td>{s.status === 'authorized' ? '✅ Activa' : s.status}</td>
                  <td>{s.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}
