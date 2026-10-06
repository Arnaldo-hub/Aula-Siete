import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

const LEVELS = [
  ['PREKINDER', 'Prekínder'], ['KINDER', 'Kínder'],
  ['BASICA_1', '1° Básico'], ['BASICA_2', '2° Básico'], ['BASICA_3', '3° Básico'],
  ['BASICA_4', '4° Básico'], ['BASICA_5', '5° Básico'], ['BASICA_6', '6° Básico'],
  ['BASICA_7', '7° Básico'], ['BASICA_8', '8° Básico'],
  ['MEDIA_1', '1° Medio'], ['MEDIA_2', '2° Medio'], ['MEDIA_3', '3° Medio'], ['MEDIA_4', '4° Medio'],
]
const nivelLabel = (lv) => (LEVELS.find(([k]) => k === lv) || [null, lv || '—'])[1]
const fld = { width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '.6rem', fontFamily: 'inherit' }

export default function Dashboard() {
  const [me, setMe] = useState(null)
  const [students, setStudents] = useState([])
  const [lives, setLives] = useState([])
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [ns, setNs] = useState({ run: '', birth_date: '', level: 'BASICA_1', full_name: '' })
  const [coursesByLevel, setCoursesByLevel] = useState({})
  const [reports, setReports] = useState({})

  function load() {
    api('/users/me').then(setMe).catch(() => {})
    api('/users/students').then(setStudents).catch(() => {})
    api('/live-classes').then(setLives).catch(() => {})
  }
  useEffect(() => { load() }, [])

  useEffect(() => {
    const lvls = [...new Set(students.map((s) => s.level).filter(Boolean))]
    lvls.forEach((lv) => {
      if (!coursesByLevel[lv]) {
        api(`/courses?level=${lv}`).then((rows) =>
          setCoursesByLevel((prev) => ({ ...prev, [lv]: rows }))
        ).catch(() => {})
      }
    })
  }, [students])

  async function addStudent(e) {
    e.preventDefault(); setMsg(''); setErr('')
    try {
      const r = await api('/users/students', { method: 'POST', body: ns })
      setMsg(`Alumno registrado: ${r.name || 'OK'} (${nivelLabel(r.level)})`)
      setNs({ run: '', birth_date: '', level: 'BASICA_1', full_name: '' }); load()
    } catch (e2) { setErr(e2.message) }
  }

  async function enroll(student, course) {
    setMsg(''); setErr('')
    try {
      await api(`/enroll?student_id=${student.id}&course_id=${course.id}`, { method: 'POST' })
      setMsg(`${student.name} inscrito en "${course.title}" ✅`)
    } catch (e2) { setErr(e2.message) }
  }

  async function verProgreso(s) {
    setErr('')
    try {
      const r = await api(`/reports/student/${s.id}`)
      setReports((prev) => ({ ...prev, [s.id]: r }))
    } catch (e2) { setErr(e2.message) }
  }

  return (
    <div>
      <h2 className="page-title">Bienvenido/a{me ? ", " + me.full_name?.split(" ")[0] : ""}</h2>
      {msg && <div className="card ok">{msg}</div>}
      {err && <div className="error">{err}</div>}

      <section className="card">
        <h3>➕ Registrar alumno</h3>
        <form onSubmit={addStudent} style={{ display: 'grid', gridTemplateColumns: '2fr 1.4fr 1fr 1fr auto', gap: '.6rem' }}>
          <input style={fld} placeholder="Nombre completo del alumno" value={ns.full_name}
            onChange={(e) => setNs({ ...ns, full_name: e.target.value })} required />
          <select style={fld} value={ns.level} onChange={(e) => setNs({ ...ns, level: e.target.value })}>
            {LEVELS.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <input style={fld} placeholder="RUN (opcional)" value={ns.run}
            onChange={(e) => setNs({ ...ns, run: e.target.value })} />
          <input style={fld} type="date" value={ns.birth_date}
            onChange={(e) => setNs({ ...ns, birth_date: e.target.value })} />
          <button className="btn btn-primary btn-sm" type="submit">Registrar</button>
        </form>
      </section>

      {students.length === 0 && (
        <div className="card">
          <p>Aún no registras alumnos. Usa el formulario de arriba: indica el nivel que validará
            (1° Básico a 4° Medio) según el examen que rendirá.</p>
        </div>
      )}

      {students.length > 0 && (
        <section className="card">
          <h3>🎒 Mis alumnos</h3>
          <table>
            <thead><tr><th>Nombre</th><th>Nivel</th><th>Inscripción en cursos</th><th>Progreso</th></tr></thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id}>
                  <td><strong>{s.name}</strong></td>
                  <td>{nivelLabel(s.level)}</td>
                  <td>
                    {(coursesByLevel[s.level] || []).length === 0
                      ? <span className="muted">Sin cursos disponibles aún</span>
                      : (coursesByLevel[s.level] || []).map((c) => (
                          <button key={c.id} className="btn btn-sm" style={{ marginRight: '.4rem', marginBottom: '.3rem' }}
                            onClick={() => enroll(s, c)}>Inscribir: {c.title}</button>
                        ))}
                  </td>
                  <td><button className="btn btn-sm" onClick={() => verProgreso(s)}>Ver progreso</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {Object.values(coursesByLevel).every((arr) => arr.length === 0) && (
            <p className="muted" style={{ marginTop: '.6rem' }}>
              No hay cursos creados aún para estos niveles: el administrador debe crearlos.
            </p>
          )}
          {Object.entries(reports).map(([sid, r]) => (
            <div key={sid} className="card" style={{ marginTop: '1rem', background: 'var(--bg-soft)' }}>
              <h4 style={{ margin: '0 0 .5rem' }}>
                📊 {students.find((s) => s.id === Number(sid))?.name || `Alumno #${sid}`}
                {' '}— Promedio simulaciones: {r.exam_average != null ? r.exam_average + '%' : 'sin rendir aún'}
                {' '}· Lecciones: {r.lessons_completed}/{r.lessons_total} · Puntos: {r.points}
              </h4>
              {r.recent_attempts.length === 0 && <p className="muted">Aún no rinde simulaciones.</p>}
              {r.recent_attempts.map((a, i) => (
                <p key={i} style={{ margin: '.2rem 0', fontSize: '.9rem' }}>
                  {a.exam}: <strong>{a.score}%</strong> <span className="muted">({a.date?.slice(0, 10)})</span>
                </p>
              ))}
            </div>
          ))}
        </section>
      )}

      <div className="card">
        <h3>🔴 Próximas clases en vivo</h3>
        {lives.length === 0 && <p className="muted">Aún no hay clases programadas. Tu profesor publicará la próxima sesión.</p>}
        {lives.map((c) => (
          <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '.7rem 0', borderBottom: '1px solid var(--border)' }}>
            <div>
              <strong>{c.title}</strong>
              <div className="muted" style={{ fontSize: '.85rem' }}>
                {new Date(c.starts_at).toLocaleString('es-CL')}
              </div>
            </div>
            <a className="btn btn-sm" href={c.room_url} target="_blank" rel="noreferrer">Unirse</a>
          </div>
        ))}
      </div>

      <div className="card" style={{ background: 'var(--bg-soft)' }}>
        <h3>📅 Fechas clave Mineduc</h3>
        <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
          <li>Inscripción exámenes libres: <strong>marzo</strong> (portal Ayuda Mineduc)</li>
          <li>Rendición: <strong>noviembre–diciembre</strong></li>
          <li>Entrevista de validación: <strong>febrero del año siguiente</strong></li>
        </ul>
      </div>
    </div>
  )
}
