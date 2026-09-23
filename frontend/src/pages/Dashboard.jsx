import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Dashboard() {
  const [students, setStudents] = useState([])
  const [lives, setLives] = useState([])
  const [report, setReport] = useState(null)
  const role = localStorage.getItem('role')

  useEffect(() => {
    if (!localStorage.getItem('token')) { location.href = '/login'; return }
    api('/users/students').then(setStudents).catch(() => {})
    api('/live-classes').then(setLives).catch(() => {})
  }, [])

  async function loadReport(id) {
    setReport(await api(`/reports/student/${id}`))
  }

  return (
    <main className="container">
      <h2>Panel {role === 'apoderado' ? 'del apoderado' : ''}</h2>

      {role === 'apoderado' && (
        <section className="card">
          <h3>Mis alumnos</h3>
          {students.length === 0 && <p className="muted">Aún no registras alumnos.</p>}
          <ul>
            {students.map(s => (
              <li key={s.id}>
                Alumno #{s.id} — Nivel {s.level}{' '}
                <button onClick={() => loadReport(s.id)}>Ver progreso</button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {report && (
        <section className="card">
          <h3>Reporte de progreso</h3>
          <p>Lecciones completadas: {report.lessons_completed} / {report.lessons_total}</p>
          <p>Promedio simulaciones: {report.exam_average ?? '—'}%</p>
          <ul>
            {report.recent_attempts.map((a, i) => (
              <li key={i}>{a.exam}: {a.score}% ({a.date?.slice(0, 10)})</li>
            ))}
          </ul>
        </section>
      )}

      <section className="card">
        <h3>Próximas clases en vivo</h3>
        <ul>
          {lives.map(l => (
            <li key={l.id}>
              {l.title} — {new Date(l.starts_at).toLocaleString('es-CL')}{' '}
              <a className="btn-link" href={l.room_url} target="_blank" rel="noreferrer">Unirse</a>
            </li>
          ))}
          {lives.length === 0 && <p className="muted">No hay clases programadas.</p>}
        </ul>
      </section>

      <section className="card muted">
        <h3>Recordatorio importante</h3>
        <p>La inscripción oficial a Exámenes Libres se realiza por el apoderado
        en el portal <strong>Ayuda Mineduc</strong>. El Mineduc asigna el colegio
        donde se rinde la prueba y emite el certificado oficial ante aprobación.</p>
      </section>
    </main>
  )
}
