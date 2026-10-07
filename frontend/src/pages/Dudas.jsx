import { useEffect, useState } from 'react'
import { api } from '../api'

const LEVELS = [
  ['PREKINDER', 'Prekínder'], ['KINDER', 'Kínder'],
  ['BASICA_1', '1° Básico'], ['BASICA_2', '2° Básico'], ['BASICA_3', '3° Básico'],
  ['BASICA_4', '4° Básico'], ['BASICA_5', '5° Básico'], ['BASICA_6', '6° Básico'],
  ['BASICA_7', '7° Básico'], ['BASICA_8', '8° Básico'],
  ['MEDIA_1', '1° Medio'], ['MEDIA_2', '2° Medio'], ['MEDIA_3', '3° Medio'], ['MEDIA_4', '4° Medio'],
]
const nivelLabel = (lv) => (LEVELS.find(([k]) => k === lv) || [null, lv || '—'])[1]

export default function Dudas() {
  const [doubts, setDoubts] = useState([])
  const [students, setStudents] = useState([])
  const [question, setQuestion] = useState('')
  const [sid, setSid] = useState('')
  const [answers, setAnswers] = useState({})
  const [msg, setMsg] = useState('')
  const role = localStorage.getItem('role')
  const isTeacher = role === 'profesor' || role === 'admin'

  function load() { api('/doubts').then(setDoubts).catch(() => {}) }
  useEffect(() => {
    load()
    if (!isTeacher) api('/users/students').then(s => { setStudents(s); if (s[0]) setSid(String(s[0].id)) }).catch(() => {})
  }, [])

  async function send(e) {
    e.preventDefault()
    setMsg('')
    try {
      await api('/doubts', { method: 'POST', body: { student_id: Number(sid), question } })
      setQuestion(''); setMsg('Duda enviada. Un docente te respondera pronto.'); load()
    } catch (e2) { setMsg('Error: ' + e2.message) }
  }

  async function reply(id) {
    try {
      await api(`/doubts/${id}/answer`, { method: 'POST', body: { answer: answers[id] || '' } })
      setAnswers({ ...answers, [id]: '' }); load()
    } catch (e2) { setMsg('Error: ' + e2.message) }
  }

  const nameOf = (id) => students.find(x => x.id === id)?.name || `Alumno #${id}`

  return (
    <div>
      <h2 className="page-title">Dudas express con docente</h2>
      {msg && <div className="card ok">{msg}</div>}

      {!isTeacher && (
        <section className="card">
          <h3>Hacer una pregunta</h3>
          <form onSubmit={send}>
            <label style={{fontSize: '.85rem', fontWeight: 600}}>Alumno</label>
            <select value={sid} onChange={e => setSid(e.target.value)} required
                    style={{width: '100%', padding: '.7rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '1rem'}}>
              {students.map(s => <option key={s.id} value={s.id}>{s.name} — {nivelLabel(s.level)}</option>)}
            </select>
            <label style={{fontSize: '.85rem', fontWeight: 600}}>Pregunta</label>
            <textarea value={question} onChange={e => setQuestion(e.target.value)} required rows={3}
                      placeholder="Escribe la duda de tu hijo (ej: no entiende factorizacion...)"
                      style={{width: '100%', padding: '.7rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '1rem', fontFamily: 'inherit'}} />
            <button className="btn btn-primary" type="submit">Enviar duda</button>
          </form>
        </section>
      )}

      <section className="card">
        <h3>{isTeacher ? 'Dudas de los estudiantes' : 'Mis dudas'}</h3>
        {doubts.length === 0 && <p className="muted">No hay dudas registradas.</p>}
        {doubts.map(d => (
          <div key={d.id} className="doubt">
            <p><strong>Pregunta</strong> <span className="muted">({nameOf(d.student_id)} · {d.date})</span></p>
            <p style={{marginBottom: '.8rem'}}>{d.question}</p>
            {d.answer ? (
              <div className="answer-box"><strong>Respuesta del docente:</strong> {d.answer}</div>
            ) : isTeacher ? (
              <div style={{display: 'flex', gap: '.6rem'}}>
                <input value={answers[d.id] || ''} onChange={e => setAnswers({ ...answers, [d.id]: e.target.value })}
                       placeholder="Escribir respuesta..." style={{flex: 1, padding: '.6rem .8rem', borderRadius: '8px', border: '1.5px solid var(--border)'}} />
                <button className="btn btn-primary btn-sm" onClick={() => reply(d.id)}>Responder</button>
              </div>
            ) : (
              <p className="muted">⏳ Pendiente de respuesta del docente.</p>
            )}
          </div>
        ))}
      </section>
    </div>
  )
}
