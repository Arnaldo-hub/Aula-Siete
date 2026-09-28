import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'

const TABS = [
  ['alumnos', 'Alumnos'], ['asistencia', 'Asistencia'], ['plan', 'Planificacion'],
  ['notas', 'Notas'], ['anotaciones', 'Anotaciones'], ['reuniones', 'Reuniones']
]
const fld = { width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '.7rem', fontFamily: 'inherit' }

import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'

const TABS = [
  ['alumnos', 'Alumnos'], ['asistencia', 'Asistencia'], ['plan', 'Planificacion'],
  ['notas', 'Notas'], ['anotaciones', 'Anotaciones'], ['reuniones', 'Reuniones']
]
const fld = { width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '.7rem', fontFamily: 'inherit' }

export default function Libro() {
  const [classrooms, setClassrooms] = useState([])
  const [cid, setCid] = useState(null)
  const [students, setStudents] = useState([])
  const [tab, setTab] = useState('asistencia')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [creating, setCreating] = useState(false)

  function loadClassrooms() {
    return api('/libro/classrooms').then(cs => setClassrooms(cs)).catch(e => setErr(e.message))
  }
  function loadStudents() {
    if (cid) api(`/libro/classrooms/${cid}/students`).then(setStudents).catch(() => {})
  }
  useEffect(() => { loadClassrooms() }, [])
  useEffect(() => { setMsg(''); setErr(''); loadStudents() }, [cid])

  const current = classrooms.find(c => c.id === cid)

  // ----- Vista 1: sin curso seleccionado -> lista de cursos como tarjetas -----
  if (!cid) {
    return (
      <div>
        <h2 className="page-title">Libro de Clases Digital</h2>
        {err && <div className="error">{err}</div>}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
          <p className="muted" style={{ margin: 0 }}>Elige un curso para abrir su libro, o crea uno nuevo.</p>
          <button className="btn btn-primary btn-sm" onClick={() => setCreating(!creating)}>
            {creating ? 'Cerrar formulario' : '+ Nuevo curso'}
          </button>
        </div>

        {creating && (
          <section className="card">
            <h3>Crear curso</h3>
            <NewClassroom onDone={id => { setCreating(false); loadClassrooms().then(() => setCid(id)) }} />
          </section>
        )}

        {classrooms.length === 0 && !creating && (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ fontSize: '2.5rem', margin: 0 }}>📒</p>
            <h3>Aun no tienes cursos</h3>
            <p className="muted">Crea tu primer curso para comenzar el libro de clases digital.<br />
            Ejemplo: curso "4 Básico B", año 2026, Colegio El Tabo.</p>
            <button className="btn btn-primary" onClick={() => setCreating(true)}>+ Crear mi primer curso</button>
          </div>
        )}

        <div className="grid">
          {classrooms.map(c => (
            <div className="card" key={c.id} style={{ cursor: 'pointer' }} onClick={() => setCid(c.id)}>
              <h3 style={{ margin: '0 0 .4rem' }}>📒 {c.name}</h3>
              <p className="muted" style={{ margin: 0 }}>{c.level} · Año {c.year}{c.school ? ' · ' + c.school : ''}</p>
              <button className="btn btn-outline btn-sm" style={{ marginTop: '1rem' }}>Abrir libro</button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // ----- Vista 2: curso abierto -> pestañas del libro -----
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.4rem' }}>
        <button className="btn btn-outline btn-sm" onClick={() => setCid(null)}>← Volver a cursos</button>
        <h2 className="page-title" style={{ margin: 0 }}>📒 {current ? current.name : ''}</h2>
        <span className="chip" style={{ fontSize: '.8rem' }}>{current ? `${current.level} · ${current.year}${current.school ? ' · ' + current.school : ''}` : ''}</span>
      </div>
      {msg && <div className="card ok">{msg}</div>}
      {err && <div className="error">{err}</div>}

      <div style={{ display: 'flex', gap: '.4rem', flexWrap: 'wrap', marginBottom: '1.2rem' }}>
        {TABS.map(([k, label]) => (
          <button key={k} className="btn btn-sm" onClick={() => setTab(k)}
            style={tab === k ? { background: 'var(--primary)', color: '#fff' } : { background: '#fff', color: 'var(--ink)', border: '1px solid var(--border)' }}>
            {label}
          </button>
        ))}
      </div>
      {tab === 'alumnos' && <Alumnos cid={cid} students={students} reload={loadStudents} setMsg={setMsg} setErr={setErr} />}
      {tab === 'asistencia' && <Asistencia cid={cid} students={students} setMsg={setMsg} setErr={setErr} />}
      {tab === 'plan' && <Plan cid={cid} setMsg={setMsg} setErr={setErr} />}
      {tab === 'notas' && <Notas cid={cid} students={students} setMsg={setMsg} setErr={setErr} />}
      {tab === 'anotaciones' && <Anotaciones cid={cid} students={students} setMsg={setMsg} setErr={setErr} />}
      {tab === 'reuniones' && <Reuniones cid={cid} setMsg={setMsg} setErr={setErr} />}
    </div>
  )
}

function NewClassroom({ onDone }) {
  const [f, setF] = useState({ name: '', level: 'BASICA_4', year: 2026, school: '' })
  async function create(e) {
    e.preventDefault()
    const r = await api('/libro/classrooms', { method: 'POST', body: { ...f, year: Number(f.year) } })
    onDone(r.id)
  }
  return (
    <form onSubmit={create} style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap' }}>
      <input style={{ ...fld, width: '170px', margin: 0 }} placeholder="Nombre del curso (ej: 4 Básico B)" value={f.name} onChange={e => setF({ ...f, name: e.target.value })} required />
      <select style={{ ...fld, width: '140px', margin: 0 }} value={f.level} onChange={e => setF({ ...f, level: e.target.value })}>
        {['PREKINDER','KINDER','BASICA_1','BASICA_2','BASICA_3','BASICA_4','BASICA_5','BASICA_6','BASICA_7','BASICA_8','MEDIA_1','MEDIA_2','MEDIA_3','MEDIA_4'].map(l => <option key={l}>{l}</option>)}
      </select>
      <input style={{ ...fld, width: '90px', margin: 0 }} type="number" value={f.year} onChange={e => setF({ ...f, year: e.target.value })} required />
      <input style={{ ...fld, width: '180px', margin: 0 }} placeholder="Establecimiento (ej: Colegio El Tabo)" value={f.school} onChange={e => setF({ ...f, school: e.target.value })} />
      <button className="btn btn-primary btn-sm" type="submit">Crear curso</button>
    </form>
  )
}

function Alumnos({ cid, students, reload, setMsg, setErr }) {
  const [text, setText] = useState('')
  async function add(e) {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      const names = text.split('\n').map(l => l.trim()).filter(Boolean)
      const r = await api(`/libro/classrooms/${cid}/students`, { method: 'POST', body: { names } })
      setMsg(r.added + ' alumnos agregados.')
      setText(''); reload()
    } catch (e2) { setErr(e2.message) }
  }
  async function del(id) {
    if (!confirm('Eliminar alumno del curso?')) return
    await api(`/libro/students/${id}`, { method: 'DELETE' }); reload()
  }
  return (
    <section className="card">
      <h3>Cargar alumnos (un nombre por linea: "Nombre Apellido")</h3>
      <form onSubmit={add}>
        <textarea style={{ ...fld, minHeight: '120px' }} value={text} onChange={e => setText(e.target.value)}
          placeholder={'Juan Perez\nMaria Gonzalez\n...'} />
        <button className="btn btn-primary btn-sm">Agregar alumnos</button>
      </form>
      <h3 style={{ marginTop: '1.5rem' }}>Lista del curso ({students.length})</h3>
      <table>
        <tbody>
          {students.map((s, i) => (
            <tr key={s.id}><td style={{ width: '40px' }}>{i + 1}</td><td>{s.name}</td>
              <td style={{ textAlign: 'right' }}><button className="btn btn-sm" style={{ background: '#fee2e2', color: '#b91c1c' }} onClick={() => del(s.id)}>Eliminar</button></td></tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

function Asistencia({ cid, students, setMsg, setErr }) {
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7))
  const [grid, setGrid] = useState({})
  const days = useMemo(() => {
    const [y, m] = month.split('-').map(Number)
    return new Date(y, m, 0).getDate()
  }, [month])
  const DOW = ['D', 'L', 'M', 'M', 'J', 'V', 'S']

  useEffect(() => {
    if (!cid) return
    api(`/libro/classrooms/${cid}/attendance?month=${month}`).then(rows => {
      const g = {}
      rows.forEach(r => { g[r.student_id + '|' + Number(r.date.slice(8, 10))] = r.status })
      setGrid(g)
    }).catch(e => setErr(e.message))
  }, [cid, month])

  function cycle(sid, day) {
    const k = sid + '|' + day
    const cur = grid[k] || ''
    const next = cur === '' ? 'P' : cur === 'P' ? 'A' : cur === 'A' ? 'R' : ''
    setGrid({ ...grid, [k]: next })
  }
  async function save() {
    const items = Object.entries(grid).map(([k, status]) => {
      const [student_id, d] = k.split('|')
      return { student_id: Number(student_id), date: month + '-' + String(d).padStart(2, '0'), status }
    })
    try {
      await api(`/libro/classrooms/${cid}/attendance`, { method: 'POST', body: items })
      setMsg('Asistencia de ' + month + ' guardada (' + items.length + ' marcas).')
    } catch (e2) { setErr(e2.message) }
  }
  const color = { P: '#16a34a', A: '#dc2626', R: '#d97706' }

  return (
    <section className="card">
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <h3 style={{ margin: 0 }}>Asistencia mensual</h3>
        <input type="month" value={month} onChange={e => setMonth(e.target.value)} style={{ ...fld, width: 'auto', margin: 0 }} />
        <button className="btn btn-primary btn-sm" onClick={save}>Guardar mes</button>
      </div>
      <p className="muted" style={{ fontSize: '.85rem' }}>Clic en cada casilla: vacio - Presente (P) - Ausente (A) - Atraso (R) - vacio.</p>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ fontSize: '.8rem' }}>
          <thead>
            <tr><th style={{ minWidth: '140px' }}>Alumno</th>
              {Array.from({ length: days }, (_, i) => {
                const dow = new Date(month + '-' + String(i + 1).padStart(2, '0') + 'T12:00:00').getDay()
                return <th key={i} style={{ textAlign: 'center', padding: '.3rem' }}>{i + 1}<br /><span style={{ color: dow === 0 || dow === 6 ? '#dc2626' : '#94a3b8' }}>{DOW[dow]}</span></th>
              })}</tr>
          </thead>
          <tbody>
            {students.map(s => (
              <tr key={s.id}>
                <td style={{ whiteSpace: 'nowrap' }}>{s.name}</td>
                {Array.from({ length: days }, (_, i) => {
                  const st = grid[s.id + '|' + (i + 1)] || ''
                  return (
                    <td key={i} onClick={() => cycle(s.id, i + 1)}
                      style={{ textAlign: 'center', cursor: 'pointer', padding: '.3rem', border: '1px solid #eef2f7',
                               color: '#fff', background: st ? color[st] : '#fff', fontWeight: 700, minWidth: '26px' }}>
                      {st}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function Plan({ cid, setMsg, setErr }) {
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7))
  const [rows, setRows] = useState([])
  const [f, setF] = useState({ date: new Date().toISOString().slice(0, 10), block: '', objective: '', activity: '' })
  function load() { api(`/libro/classrooms/${cid}/plan?month=${month}`).then(setRows).catch(e => setErr(e.message)) }
  useEffect(() => { load() }, [cid, month])
  async function add(e) {
    e.preventDefault()
    try {
      await api(`/libro/classrooms/${cid}/plan`, { method: 'POST', body: f })
      setF({ ...f, activity: '', objective: '' }); setMsg('Registro de clase guardado.'); load()
    } catch (e2) { setErr(e2.message) }
  }
  return (
    <section className="card">
      <h3>Registro de clases (control de asignatura)</h3>
      <form onSubmit={add} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr 2fr auto', gap: '.6rem' }}>
        <input type="date" style={fld} value={f.date} onChange={e => setF({ ...f, date: e.target.value })} required />
        <input style={fld} placeholder="Hora (ej: 3ra)" value={f.block} onChange={e => setF({ ...f, block: e.target.value })} />
        <input style={fld} placeholder="Objetivo (OA/OAT)" value={f.objective} onChange={e => setF({ ...f, objective: e.target.value })} />
        <input style={fld} placeholder="Actividad realizada" value={f.activity} onChange={e => setF({ ...f, activity: e.target.value })} required />
        <button className="btn btn-primary btn-sm">Guardar</button>
      </form>
      <div style={{ marginTop: '1rem' }}>
        <input type="month" value={month} onChange={e => setMonth(e.target.value)} style={{ ...fld, width: 'auto' }} />
      </div>
      <table>
        <thead><tr><th>Fecha</th><th>Hora</th><th>Objetivo</th><th>Actividad</th></tr></thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id}><td>{r.date}</td><td>{r.block}</td><td className="muted">{r.objective}</td><td>{r.activity}</td></tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

function Notas({ cid, students, setMsg, setErr }) {
  const [f, setF] = useState({ subject: '', title: '', date: new Date().toISOString().slice(0, 10), max_score: 7 })
  const [grades, setGrades] = useState([])
  function load() { api(`/libro/classrooms/${cid}/grades`).then(setGrades).catch(e => setErr(e.message)) }
  useEffect(() => { load() }, [cid])
  const evals = {}
  grades.forEach(g => { const k = g.subject + '|' + g.title + '|' + g.date; (evals[k] = evals[k] || []).push(g) })
  const byStudent = {}
  students.forEach(s => byStudent[s.id] = s.name)

  async function createEval(e) {
    e.preventDefault()
    try {
      const r = await api(`/libro/classrooms/${cid}/evaluations`, { method: 'POST', body: { ...f, max_score: Number(f.max_score) } })
      setMsg('Evaluacion creada para ' + r.students + ' alumnos. Ingresa las notas abajo.'); load()
    } catch (e2) { setErr(e2.message) }
  }
  async function setScore(g, value) {
    const score = value === '' ? null : Number(value)
    await api(`/libro/grades/${g.id}`, { method: 'POST', body: { student_id: g.student_id, score } })
    setGrades(gs => gs.map(x => x.id === g.id ? { ...x, score } : x))
  }
  return (
    <section className="card">
      <h3>Crear evaluacion</h3>
      <form onSubmit={createEval} style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr 1fr auto', gap: '.6rem' }}>
        <input style={fld} placeholder="Asignatura" value={f.subject} onChange={e => setF({ ...f, subject: e.target.value })} required />
        <input style={fld} placeholder="Nombre (ej: Prueba unidad 1)" value={f.title} onChange={e => setF({ ...f, title: e.target.value })} required />
        <input type="date" style={fld} value={f.date} onChange={e => setF({ ...f, date: e.target.value })} required />
        <input type="number" step="0.1" style={fld} placeholder="Nota max" value={f.max_score} onChange={e => setF({ ...f, max_score: e.target.value })} />
        <button className="btn btn-primary btn-sm">Crear</button>
      </form>

      {Object.entries(evals).map(([k, rows]) => {
        const [subject, title, date] = k.split('|')
        return (
          <div key={k} style={{ marginTop: '1.5rem' }}>
            <h3>{subject} - {title} <span className="muted">({date})</span></h3>
            <table>
              <tbody>
                {rows.map(g => (
                  <tr key={g.id}>
                    <td>{byStudent[g.student_id] || 'Alumno #' + g.student_id}</td>
                    <td style={{ textAlign: 'right', width: '120px' }}>
                      <input type="number" step="0.1" min="0" max={g.max_score} defaultValue={g.score ?? ''}
                        onBlur={e => setScore(g, e.target.value)}
                        style={{ width: '80px', padding: '.4rem', borderRadius: '8px', border: '1.5px solid var(--border)', textAlign: 'center' }} />
                      <span className="muted"> / {g.max_score}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      })}
    </section>
  )
}

function Anotaciones({ cid, students, setMsg, setErr }) {
  const [rows, setRows] = useState([])
  const [filter, setFilter] = useState('')
  const [f, setF] = useState({ student_id: '', date: new Date().toISOString().slice(0, 10), subject: '', kind: 'anotacion', text: '', guardian_informed: false })
  function load() {
    const q = filter ? `?student_id=${filter}` : ''
    api(`/libro/classrooms/${cid}/annotations${q}`).then(setRows).catch(e => setErr(e.message))
  }
  useEffect(() => { load() }, [cid, filter])
  const byStudent = {}
  students.forEach(s => byStudent[s.id] = s.name)

  async function add(e) {
    e.preventDefault()
    try {
      await api(`/libro/classrooms/${cid}/annotations`, { method: 'POST', body: { ...f, student_id: Number(f.student_id) } })
      setF({ ...f, text: '', subject: '' }); setMsg('Anotacion registrada.'); load()
    } catch (e2) { setErr(e2.message) }
  }
  const kindColor = { positiva: '#16a34a', negativa: '#dc2626', entrevista: '#4f46e5', anotacion: '#64748b' }
  return (
    <section className="card">
      <h3>Nueva anotacion de convivencia</h3>
      <form onSubmit={add} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: '.6rem' }}>
        <select style={fld} value={f.student_id} onChange={e => setF({ ...f, student_id: e.target.value })} required>
          <option value="">Alumno...</option>
          {students.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <input type="date" style={fld} value={f.date} onChange={e => setF({ ...f, date: e.target.value })} required />
        <input style={fld} placeholder="Asignatura" value={f.subject} onChange={e => setF({ ...f, subject: e.target.value })} />
        <select style={fld} value={f.kind} onChange={e => setF({ ...f, kind: e.target.value })}>
          <option value="anotacion">Anotacion</option><option value="positiva">Positiva</option>
          <option value="negativa">Negativa (llamado)</option><option value="entrevista">Entrevista apoderado</option>
        </select>
        <textarea style={{ ...fld, gridColumn: '1 / 4', minHeight: '70px' }} placeholder="Descripcion de lo ocurrido..."
          value={f.text} onChange={e => setF({ ...f, text: e.target.value })} required />
        <label style={{ display: 'flex', gap: '.5rem', alignItems: 'center', fontSize: '.9rem' }}>
          <input type="checkbox" checked={f.guardian_informed} onChange={e => setF({ ...f, guardian_informed: e.target.checked })} />
          Apoderado informado
        </label>
        <button className="btn btn-primary btn-sm">Registrar</button>
      </form>

      <div style={{ marginTop: '1.2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>Historial</h3>
        <select value={filter} onChange={e => setFilter(e.target.value)} style={{ ...fld, width: 'auto', margin: 0 }}>
          <option value="">Todos los alumnos</option>
          {students.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>
      {rows.map(r => (
        <div key={r.id} className="doubt">
          <p><strong style={{ color: kindColor[r.kind] || '#64748b' }}>{r.kind.toUpperCase()}</strong>{' '}
            · {byStudent[r.student_id] || 'Alumno #' + r.student_id} · {r.date}{r.subject ? ' · ' + r.subject : ''}
            {r.guardian_informed ? ' · Apoderado informado' : ''}</p>
          <p>{r.text}</p>
        </div>
      ))}
      {rows.length === 0 && <p className="muted">Sin anotaciones.</p>}
    </section>
  )
}

function Reuniones({ cid, setMsg, setErr }) {
  const [rows, setRows] = useState([])
  const [f, setF] = useState({ date: new Date().toISOString().slice(0, 10), topic: '', agreements: '' })
  function load() { api(`/libro/classrooms/${cid}/meetings`).then(setRows).catch(e => setErr(e.message)) }
  useEffect(() => { load() }, [cid])
  async function add(e) {
    e.preventDefault()
    try {
      await api(`/libro/classrooms/${cid}/meetings`, { method: 'POST', body: f })
      setF({ ...f, topic: '', agreements: '' }); setMsg('Reunion registrada.'); load()
    } catch (e2) { setErr(e2.message) }
  }
  return (
    <section className="card">
      <h3>Reuniones de padres y apoderados</h3>
      <form onSubmit={add} style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '.6rem' }}>
        <input type="date" style={fld} value={f.date} onChange={e => setF({ ...f, date: e.target.value })} required />
        <input style={fld} placeholder="Tema de la reunion" value={f.topic} onChange={e => setF({ ...f, topic: e.target.value })} required />
        <textarea style={{ ...fld, gridColumn: '1 / 3', minHeight: '70px' }} placeholder="Acuerdos y compromisos..."
          value={f.agreements} onChange={e => setF({ ...f, agreements: e.target.value })} />
        <button className="btn btn-primary btn-sm" style={{ gridColumn: '1 / 3', justifySelf: 'start' }}>Registrar reunion</button>
      </form>
      <table style={{ marginTop: '1rem' }}>
        <thead><tr><th>Fecha</th><th>Tema</th><th>Acuerdos</th></tr></thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id}><td style={{ whiteSpace: 'nowrap' }}>{r.date}</td><td>{r.topic}</td><td className="muted">{r.agreements}</td></tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
