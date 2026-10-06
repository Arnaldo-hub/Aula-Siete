import { useEffect, useState } from 'react'
import { api } from '../api'

const fld = { width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '.6rem', fontFamily: 'inherit' }

const LEVELS = [
  ['BASICA_1', '1° Básico'], ['BASICA_2', '2° Básico'], ['BASICA_3', '3° Básico'],
  ['BASICA_4', '4° Básico'], ['BASICA_5', '5° Básico'], ['BASICA_6', '6° Básico'],
  ['BASICA_7', '7° Básico'], ['BASICA_8', '8° Básico'],
  ['MEDIA_1', '1° Medio'], ['MEDIA_2', '2° Medio'], ['MEDIA_3', '3° Medio'], ['MEDIA_4', '4° Medio'],
]

const subStatus = {
  pending: '⏳ Pendiente', authorized: '✅ Activa',
  paused: '⏸ Pausada', cancelled: '❌ Cancelada',
}

export default function AdminPanel() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [subs, setSubs] = useState([])
  const [teachers, setTeachers] = useState([])
  const [board, setBoard] = useState([])
  const [subFilter, setSubFilter] = useState('')
  const [filter, setFilter] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [seed, setSeed] = useState({ level: 'BASICA_8', teacher_id: '' })
  const [nu, setNu] = useState({ email: '', password: '', full_name: '', role: 'profesor' })

  function load() {
    api('/admin/stats').then(setStats).catch(e => setErr(e.message))
    api('/admin/users').then(setUsers).catch(() => {})
    api('/admin/subscriptions').then(setSubs).catch(() => {})
    api('/admin/users?role=profesor').then(setTeachers).catch(() => {})
    api('/levels/board').then(setBoard).catch(() => {})
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

  async function seedLevel() {
    setMsg(''); setErr('')
    try {
      const r = await api('/levels/seed', { method: 'POST',
        body: { level: seed.level, teacher_id: seed.teacher_id ? Number(seed.teacher_id) : null } })
      setMsg(`${r.cursos_total} cursos listos en ${r.level} (${r.cursos_nuevos} nuevos) — ` +
        `${r.alumnos_inscritos} inscripciones automaticas.` +
        (r.docente ? ` Docente: ${r.docente}.` : ' Ojo: sin docente asignado, el profesor no vera estos cursos.'))
      load()
    } catch (e2) { setErr(e2.message) }
  }

  const shown = filter ? users.filter(u => u.role === filter) : users
  const shownSubs = subFilter ? subs.filter(s => s.status === subFilter) : subs

  const CARDS = stats ? [
    ['👨‍👩‍👧 Apoderados', stats.users_apoderados],
    ['🧑‍🏫 Profesores', stats.users_profesores],
    ['🎒 Alumnos', stats.students],
    ['📚 Cursos', stats.courses],
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
        <h3>🏫 Cursos por nivel (1 click — asignaturas oficiales Mineduc)</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr auto', gap: '.6rem' }}>
          <select style={fld} value={seed.level} onChange={e => setSeed({ ...seed, level: e.target.value })}>
            {LEVELS.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <select style={fld} value={seed.teacher_id} onChange={e => setSeed({ ...seed, teacher_id: e.target.value })}>
            <option value="">Sin docente asignado aun...</option>
            {teachers.map(t => <option key={t.id} value={t.id}>{t.full_name}</option>)}
          </select>
          <button className="btn btn-primary" onClick={seedLevel}>Crear cursos</button>
        </div>
        <p className="muted" style={{ fontSize: '.82rem', margin: 0 }}>
          Crea las asignaturas y cursos oficiales del nivel (4 en 1°-6° básico; 5 desde 7° con Inglés;
          5 en media) e inscribe automaticamente a los alumnos ya registrados de ese nivel.
          Puedes repetirlo: no duplica.
        </p>
      </section>

      {board.length > 0 && (
        <section className="card">
          <h3>🗂️ Relación curso — docente — alumnos</h3>
          <table>
            <thead><tr><th>Curso</th><th>Asignatura</th><th>Nivel</th><th>Docente</th><th>Alumnos</th></tr></thead>
            <tbody>
              {board.map(c => (
                <tr key={c.course_id}>
                  <td>{c.title}</td>
                  <td>{c.subject}</td>
                  <td>{c.level_label}</td>
                  <td>{c.teacher}</td>
                  <td>{c.students.length === 0 ? '—' : c.students.map(s => s.name).join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
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
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '.8rem' }}>
            <h3 style={{ margin: 0 }}>💳 Suscripciones ({shownSubs.length})</h3>
            <select value={subFilter} onChange={e => setSubFilter(e.target.value)} style={{ ...fld, width: 'auto', margin: 0 }}>
              <option value="">Todos los estados</option>
              <option value="authorized">✅ Activas</option>
              <option value="pending">⏳ Pendientes</option>
              <option value="paused">⏸ Pausadas</option>
              <option value="cancelled">❌ Canceladas</option>
            </select>
          </div>
          <table>
            <thead><tr><th>Apoderado</th><th>Plan</th><th>Monto</th><th>Estado</th><th>Fecha</th></tr></thead>
            <tbody>
              {shownSubs.map(s => (
                <tr key={s.id}>
                  <td>{s.guardian}</td>
                  <td>{s.plan === 'grupal' ? 'Grupo En Vivo' : 'Intensivo 1 a 1'}</td>
                  <td>${s.amount.toLocaleString('es-CL')}</td>
                  <td>{subStatus[s.status] || s.status}</td>
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
