import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

const LEVELS = [
  ['BASICA_1', '1° Básico'], ['BASICA_2', '2° Básico'], ['BASICA_3', '3° Básico'],
  ['BASICA_4', '4° Básico'], ['BASICA_5', '5° Básico'], ['BASICA_6', '6° Básico'],
  ['BASICA_7', '7° Básico'], ['BASICA_8', '8° Básico'],
  ['MEDIA_1', '1° Medio'], ['MEDIA_2', '2° Medio'], ['MEDIA_3', '3° Medio'], ['MEDIA_4', '4° Medio'],
]
const nivelLabel = (lv) => (LEVELS.find(([k]) => k === lv) || [null, lv || '—'])[1]

export default function Simulaciones() {
  const [students, setStudents] = useState([])
  const [sid, setSid] = useState('')
  const [exams, setExams] = useState([])
  const [diags, setDiags] = useState([])
  const [weak, setWeak] = useState(null)
  const [active, setActive] = useState(null)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/users/students').then((s) => {
      setStudents(s)
      if (s[0]) setSid(String(s[0].id))
    }).catch(() => {})
  }, [])

  const selStudent = students.find((s) => String(s.id) === String(sid))

  useEffect(() => {
    if (!selStudent) return
    api(`/exams?level=${selStudent.level}`).then((all) => {
      setExams(all.filter((e) => e.kind !== 'diagnostico'))
      setDiags(all.filter((e) => e.kind === 'diagnostico'))
    }).catch((e) => setErr(e.message))
  }, [sid, students])

  async function start(id) {
    try {
      const data = await api(`/exams/${id}/start`)
      setActive(data); setAnswers({}); setResult(null); setErr('')
    } catch (e) { setErr(e.message) }
  }

  async function submit() {
    setErr('')
    try {
      const r = await api(`/exams/${active.exam_id}/submit?student_id=${sid}`,
        { method: 'POST', body: answers })
      setResult(r); setActive(null); setWeak(r.weak_oa || null)
    } catch (e) { setErr(e.message) }
  }

  if (students.length === 0) return (
    <div>
      <h2 className="page-title">Simulaciones de Exámenes Libres</h2>
      <div className="card"><p>Primero registra a tu alumno en el <Link to="/app"><strong>Panel</strong></Link> para ver las simulaciones de su nivel.</p></div>
    </div>
  )

  return (
    <div>
      <h2 className="page-title">Simulaciones de Exámenes Libres</h2>
      {err && <div className="error">{err}</div>}

      <div className="card" style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <label style={{ fontSize: '.85rem', fontWeight: 600 }}>Alumno:</label>
        <select value={sid} onChange={(e) => { setSid(e.target.value); setResult(null); setWeak(null) }}
          style={{ padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', fontFamily: 'inherit' }}>
          {students.map((s) => <option key={s.id} value={s.id}>{s.name} — {nivelLabel(s.level)}</option>)}
        </select>
        <span className="muted" style={{ fontSize: '.85rem' }}>
          Mostrando solo simulaciones de {selStudent ? nivelLabel(selStudent.level) : '…'}
        </span>
      </div>

      {result && (
        <div className="card ok">
          <h3>Resultado: {result.score}%</h3>
          <p className="muted">{result.correct} de {result.total} respuestas correctas{selStudent ? ` — ${selStudent.name}` : ''}.</p>
        </div>
      )}

      {weak && weak.length > 0 && (
        <div className="card">
          <h3>OA débiles detectados — se creó su ruta de refuerzo</h3>
          <p className="muted">Revisa <strong>Mi Ruta</strong> en el menú para ver las micro-tareas asignadas a {selStudent?.name}.</p>
          <div>{weak.map((o) => <span key={o} className="chip" style={{ display: 'inline-block', margin: '0 .5rem .5rem 0', background: '#fef2f2', borderColor: '#fecaca' }}>{o}</span>)}</div>
        </div>
      )}

      {diags.length > 0 && !active && (
        <section className="card">
          <h3>Diagnósticos de ingreso ({nivelLabel(selStudent?.level)})</h3>
          <p className="muted">Ríndelos primero: detectamos los vacíos y creamos la ruta personalizada del alumno.</p>
          <table>
            <tbody>
              {diags.map((e) => (
                <tr key={e.id}>
                  <td>{e.title}</td>
                  <td style={{ textAlign: 'right' }}><button className="btn btn-accent btn-sm" onClick={() => start(e.id)}>Rendir diagnóstico</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {!active ? (
        <div className="card">
          <h3>Simulacros disponibles</h3>
          <table>
            <thead><tr><th>Simulación</th><th>Duración</th><th></th></tr></thead>
            <tbody>
              {exams.map((e) => (
                <tr key={e.id}>
                  <td>{e.title}</td>
                  <td>{e.time_limit_min} min</td>
                  <td style={{ textAlign: 'right' }}><button className="btn btn-primary btn-sm" onClick={() => start(e.id)}>Comenzar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {exams.length === 0 && diags.length === 0 && !err && (
            <p className="muted">Aún no hay simulaciones para este nivel. Estamos trabajando en ello.</p>
          )}
        </div>
      ) : (
        <div className="card">
          <h3>Rindiendo simulación {selStudent ? `— ${selStudent.name}` : ''}</h3>
          {active.questions.map((q) => (
            <div key={q.id} className="question">
              <p><strong>{q.prompt}</strong></p>
              {q.options.map((op, i) => (
                <label key={i}>
                  <input type="radio" name={q.id}
                    onChange={() => setAnswers({ ...answers, [q.id]: op })} /> {op}
                </label>
              ))}
            </div>
          ))}
          <button className="btn btn-primary" onClick={submit}>Entregar respuestas</button>
        </div>
      )}
    </div>
  )
}
