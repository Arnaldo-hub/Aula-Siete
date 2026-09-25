import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Simulaciones() {
  const [exams, setExams] = useState([])
  const [active, setActive] = useState(null)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [err, setErr] = useState('')

  useEffect(() => { api('/exams').then(setExams).catch(e => setErr(e.message)) }, [])

  async function start(id) {
    try {
      const data = await api(`/exams/${id}/start`)
      setActive(data); setAnswers({}); setResult(null); setErr('')
    } catch (e) { setErr(e.message) }
  }

  async function submit() {
    const sid = studentsFirstId()
    try {
      const r = await api(`/exams/${active.exam_id}/submit?student_id=${sid}`,
        { method: 'POST', body: answers })
      setResult(r); setActive(null)
    } catch (e) { setErr(e.message) }
  }

  function studentsFirstId() { return 1 }

  return (
    <div>
      <h2 className="page-title">Simulaciones de Examenes Libres</h2>
      {err && <div className="error">{err}</div>}

      {result && (
        <div className="card ok">
          <h3>Resultado: {result.score}%</h3>
          <p className="muted">{result.correct} de {result.total} respuestas correctas.</p>
        </div>
      )}

      {!active ? (
        <div className="card">
          <table>
            <thead><tr><th>Simulacion</th><th>Duracion</th><th></th></tr></thead>
            <tbody>
              {exams.map(e => (
                <tr key={e.id}>
                  <td>{e.title}</td>
                  <td>{e.time_limit_min} min</td>
                  <td style={{textAlign:'right'}}><button className="btn btn-primary btn-sm" onClick={() => start(e.id)}>Comenzar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {exams.length === 0 && !err && <p className="muted">No hay simulaciones disponibles aun.</p>}
        </div>
      ) : (
        <div className="card">
          <h3>Rindiendo simulacion</h3>
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
          <button className="btn btn-primary" onClick={submit}>Entregar respuestas</button>
        </div>
      )}
    </div>
  )
}
