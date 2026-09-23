import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Simulaciones() {
  const [exams, setExams] = useState([])
  const [active, setActive] = useState(null)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [studentId, setStudentId] = useState(1)

  useEffect(() => { api('/exams').then(setExams).catch(() => {}) }, [])

  async function start(id) {
    const data = await api(`/exams/${id}/start`)
    setActive(data); setAnswers({}); setResult(null)
  }

  async function submit() {
    const sid = studentId || 1
    const r = await api(`/exams/${active.exam_id}/submit?student_id=${sid}`,
      { method: 'POST', body: answers })
    setResult(r); setActive(null)
  }

  return (
    <main className="container">
      <h2>Simulaciones de Exámenes Libres</h2>
      {result && (
        <div className="card ok">
          Resultado: {result.score}% — {result.correct} de {result.total} correctas.
        </div>
      )}
      {!active ? (
        <ul className="card">
          {exams.map(e => (
            <li key={e.id}>
              {e.title} ({e.time_limit_min} min){' '}
              <button onClick={() => start(e.id)}>Comenzar</button>
            </li>
          ))}
          {exams.length === 0 && <p className="muted">No hay simulaciones disponibles aún.</p>}
        </ul>
      ) : (
        <div className="card">
          <h3>Rendiendo simulación</h3>
          {active.questions.map(q => (
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
          <button onClick={submit}>Entregar respuestas</button>
        </div>
      )}
    </main>
  )
}
