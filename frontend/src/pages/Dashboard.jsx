import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Dashboard() {
  const [students, setStudents] = useState([])
  const [lives, setLives] = useState([])
  const [report, setReport] = useState(null)
  const [err, setErr] = useState('')
  const role = localStorage.getItem('role')

  useEffect(() => {
    if (!localStorage.getItem('token')) { location.href = '/login'; return }
    api('/users/students').then(setStudents).catch(e => setErr('Alumnos: ' + e.message))
    api('/live-classes').then(setLives).catch(e => setErr('Clases: ' + e.message))
  }, [])

  async function loadReport(id) {
    try { setReport(await api(`/reports/student/${id}`)) }
    catch (e) { setErr('Reporte: ' + e.message) }
  }

  return (
    <main className="container">
      <h2>Panel {role === 'apoderado' ? 'del apoderado' : ''}</h2>

      {err && <div className="card error">Error de conexion con el servidor: {err}
        <br /><small>Si el servicio estaba inactivo, espera 1 minuto y recarga la pagina.</small></div>}

      {role === 'apoderado' && (
        <section className="card">
          <h3>Mis alumnos</h3>
          {students.length === 0 && !err && <p className="muted">Aun no registras alumnos.</p>}
          <ul>
            {students.map(s => (
              <li key={s.id}>
                Alumno #{s.id} - Nivel {s.level}{' '}
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
          <p>Promedio simulaciones: {report.exam_average ?? '-'}%</p>
          <ul>
            {report.recent_attempts.map((a, i) => (
              <li key={i}>{a.exam}: {a.score}% ({a.date?.slice(0, 10)})</li>
            ))}
          </ul>
        </section>
      )}

      <section className="card">
        <h3>Proximas clases en vivo</h3>
        <ul>
          {lives.map(l => (
            <li key={l.id}>
              {l.title} - {new Date(l.starts_at).toLocaleString('es-CL')}{' '}
              <a className="btn-link" href={l.room_url} target="_blank" rel="noreferrer">Unirse</a>
            </li>
          ))}
          {lives.length === 0 && <p className="muted">No hay clases programadas.</p>}
        </ul>
      </section>

      <section className="card muted">
        <h3>Recordatorio importante</h3>
        <p>La inscripcion oficial a Examenes Libres se realiza por el apoderado
        en el portal <strong>Ayuda Mineduc</strong>. El Mineduc asigna el colegio
        donde se rinde la prueba y emite el certificado oficial ante aprobacion.</p>
      </section>
    </main>
  )
}
