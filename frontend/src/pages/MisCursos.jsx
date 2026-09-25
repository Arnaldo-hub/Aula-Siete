import { useEffect, useState } from 'react'
import { api } from '../api'

const LEVELS = ["PREKINDER","KINDER","BASICA_1","BASICA_2","BASICA_3","BASICA_4",
  "BASICA_5","BASICA_6","BASICA_7","BASICA_8","MEDIA_1","MEDIA_2","MEDIA_3","MEDIA_4"]

export default function MisCursos() {
  const [courses, setCourses] = useState([])
  const [subjects, setSubjects] = useState([])
  const [expanded, setExpanded] = useState(null)
  const [students, setStudents] = useState({})
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [newCourse, setNewCourse] = useState({ title: '', subject_id: '', level: 'BASICA_8', description: '' })
  const [mat, setMat] = useState({})
  const [live, setLive] = useState({})
  const [rec, setRec] = useState({})

  function load() { api('/my/courses').then(setCourses).catch(e => setErr(e.message)) }
  useEffect(() => {
    load()
    api('/subjects').then(setSubjects).catch(() => {})
  }, [])

  async function createCourse(e) {
    e.preventDefault(); setMsg(''); setErr('')
    try {
      await api('/courses', { method: 'POST', body: { ...newCourse, subject_id: Number(newCourse.subject_id) } })
      setMsg('Curso creado. Ya aparece en tu lista.'); setNewCourse({ title: '', subject_id: '', level: 'BASICA_8', description: '' }); load()
    } catch (e2) { setErr(e2.message) }
  }

  async function toggleStudents(cid) {
    if (expanded === cid) { setExpanded(null); return }
    setExpanded(cid)
    if (!students[cid]) {
      try { const s = await api(`/courses/${cid}/students`); setStudents(st => ({ ...st, [cid]: s })) }
      catch (e2) { setErr(e2.message) }
    }
  }

  async function addMaterial(cid) {
    const f = mat[cid] || {}
    if (!f.title || !f.file_url) { setErr('Completa titulo y URL del material'); return }
    try {
      await api('/materials', { method: 'POST', body: { course_id: cid, title: f.title, file_url: f.file_url, file_type: f.file_type || 'link' } })
      setMsg('Material agregado al curso'); setMat(m => ({ ...m, [cid]: {} }))
    } catch (e2) { setErr(e2.message) }
  }

  async function scheduleLive(cid) {
    const f = live[cid] || {}
    if (!f.title || !f.starts_at || !f.ends_at) { setErr('Completa titulo, inicio y termino de la clase'); return }
    try {
      const r = await api('/live-classes', { method: 'POST',
        body: { course_id: cid, title: f.title, starts_at: f.starts_at, ends_at: f.ends_at } })
      setMsg('Clase agendada. Sala: ' + r.room_url); setLive(l => ({ ...l, [cid]: {} })); setErr('')
    } catch (e2) { setErr(e2.message) }
  }

  async function addRecording(cid) {
    const f = rec[cid] || {}
    if (!f.title || !f.video_url) { setErr('Completa titulo y URL del video'); return }
    try {
      await api('/recordings', { method: 'POST', body: { course_id: cid, title: f.title, video_url: f.video_url } })
      setMsg('Grabacion publicada en la biblioteca'); setRec(r => ({ ...r, [cid]: {} }))
    } catch (e2) { setErr(e2.message) }
  }

  const fld = { width: '100%', padding: '.65rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '.7rem', fontFamily: 'inherit' }

  return (
    <div>
      <h2 className="page-title">Mis cursos</h2>
      {msg && <div className="card ok">{msg}</div>}
      {err && <div className="error">{err}</div>}

      <section className="card">
        <h3>➕ Crear nuevo curso</h3>
        <form onSubmit={createCourse}>
          <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '.8rem'}}>
            <input style={fld} placeholder="Nombre del curso (ej: Matematica 8° Basica)"
                   value={newCourse.title} onChange={e => setNewCourse({ ...newCourse, title: e.target.value })} required />
            <select style={fld} value={newCourse.subject_id} onChange={e => setNewCourse({ ...newCourse, subject_id: e.target.value })} required>
              <option value="">Asignatura...</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <select style={fld} value={newCourse.level} onChange={e => setNewCourse({ ...newCourse, level: e.target.value })}>
              {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
          <input style={fld} placeholder="Descripcion breve (opcional)"
                 value={newCourse.description} onChange={e => setNewCourse({ ...newCourse, description: e.target.value })} />
          <button className="btn btn-primary btn-sm" type="submit">Crear curso</button>
        </form>
      </section>

      {courses.length === 0 && <div className="card muted">Aun no tienes cursos. Crea el primero arriba.</div>}

      {courses.map(c => (
        <section className="card" key={c.id}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '.6rem'}}>
            <h3 style={{margin: 0}}>{c.title}</h3>
            <span className="chip" style={{fontSize: '.8rem'}}>{c.level} · {c.subject} · 👨‍🎓 {c.students} alumno(s)</span>
          </div>
          {c.description && <p className="muted" style={{marginTop: '.5rem'}}>{c.description}</p>}

          <div style={{display: 'flex', gap: '.6rem', marginTop: '.9rem', flexWrap: 'wrap'}}>
            <button className="btn btn-outline btn-sm" onClick={() => toggleStudents(c.id)}>
              {expanded === c.id ? 'Ocultar alumnos' : '👨‍🎓 Ver alumnos'}
            </button>
          </div>

          {expanded === c.id && (
            <div style={{marginTop: '1rem'}}>
              {(students[c.id] || []).length === 0 && <p className="muted">Sin alumnos inscritos aun.</p>}
              {(students[c.id] || []).map(s => (
                <div key={s.id} className="chip" style={{display: 'inline-block', margin: '0 .5rem .5rem 0'}}>
                  Alumno #{s.id} · {s.level}
                </div>
              ))}

              <h3 style={{marginTop: '1.2rem'}}>📚 Agregar material al curso</h3>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 2fr 1fr auto', gap: '.6rem'}}>
                <input style={fld} placeholder="Titulo (ej: Guia fracciones)" value={(mat[c.id] || {}).title || ''}
                       onChange={e => setMat(m => ({ ...m, [c.id]: { ...(m[c.id] || {}), title: e.target.value } }))} />
                <input style={fld} placeholder="URL (Google Drive, link PDF...)" value={(mat[c.id] || {}).file_url || ''}
                       onChange={e => setMat(m => ({ ...m, [c.id]: { ...(m[c.id] || {}), file_url: e.target.value } }))} />
                <select style={fld} value={(mat[c.id] || {}).file_type || 'link'}
                        onChange={e => setMat(m => ({ ...m, [c.id]: { ...(m[c.id] || {}), file_type: e.target.value } }))}>
                  <option value="link">Enlace</option><option value="pdf">PDF</option>
                  <option value="docx">Documento</option><option value="video">Video</option>
                </select>
                <button className="btn btn-primary btn-sm" onClick={() => addMaterial(c.id)}>Subir</button>
              </div>

              <h3 style={{marginTop: '1.2rem'}}>🎥 Agendar clase en vivo</h3>
              <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: '.6rem'}}>
                <input style={fld} placeholder="Titulo de la clase" value={(live[c.id] || {}).title || ''}
                       onChange={e => setLive(l => ({ ...l, [c.id]: { ...(l[c.id] || {}), title: e.target.value } }))} />
                <input style={fld} type="datetime-local" value={(live[c.id] || {}).starts_at || ''}
                       onChange={e => setLive(l => ({ ...l, [c.id]: { ...(l[c.id] || {}), starts_at: e.target.value } }))} />
                <input style={fld} type="datetime-local" value={(live[c.id] || {}).ends_at || ''}
                       onChange={e => setLive(l => ({ ...l, [c.id]: { ...(l[c.id] || {}), ends_at: e.target.value } }))} />
                <button className="btn btn-primary btn-sm" onClick={() => scheduleLive(c.id)}>Agendar</button>
              </div>

              <h3 style={{marginTop: '1.2rem'}}>📼 Publicar grabacion en biblioteca</h3>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 2fr auto', gap: '.6rem'}}>
                <input style={fld} placeholder="Titulo de la clase grabada" value={(rec[c.id] || {}).title || ''}
                       onChange={e => setRec(r => ({ ...r, [c.id]: { ...(r[c.id] || {}), title: e.target.value } }))} />
                <input style={fld} placeholder="URL del video (YouTube/Drive...)" value={(rec[c.id] || {}).video_url || ''}
                       onChange={e => setRec(r => ({ ...r, [c.id]: { ...(r[c.id] || {}), video_url: e.target.value } }))} />
                <button className="btn btn-primary btn-sm" onClick={() => addRecording(c.id)}>Publicar</button>
              </div>
            </div>
          )}
        </section>
      ))}
    </div>
  )
}
