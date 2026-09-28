import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Dashboard() {
  const [students, setStudents] = useState([])
  const [lives, setLives] = useState([])
  const [report, setReport] = useState(null)
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/users/students').then(setStudents).catch(e => setErr('Alumnos: ' + e.message))
    api('/live-classes').then(setLives).catch(e => setErr('Clases: ' + e.message))
  }, [])

  async function loadReport(id) {
    try { setReport(await api(`/reports/student/${id}`)) }
    catch (e) { setErr('Reporte: ' + e.message) }
  }

  return (
    <div>
      <h2 className="page-title">Panel</h2>
      {err && <div className="error">Error de conexion con el servidor: {err}
        <br /><small>Si el servicio estaba inactivo, espera 1 minuto y recarga.</small></div>}

      <section className="card">
        <h3>Mis alumnos</h3>
        {students.length === 0 && !err && <p className="muted">Aun no registras alumnos.</p>}
        <table>
          <tbody>
            {students.map(s => (
              <tr key={s.id}>
                <td>Alumno #{s.id}</td>
                <td>Nivel {s.level}</td>
                <td style={{textAlign:'right'}}><button className="btn btn-primary btn-sm" onClick={() => loadReport(s.id)}>Ver progreso</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {report && (
        <section className="card">
          <h3>Reporte de progreso</h3>
          <p>Lecciones completadas: <strong>{report.lessons_completed} / {report.lessons_total}</strong></p>
          <p>Promedio simulaciones: <strong>{report.exam_average ?? '-'}%</strong> · Puntos de practica: <strong>{report.points ?? 0}</strong> ⭐</p>
          {report.ranking_position && <p>Ranking de practica: <strong>#{report.ranking_position}</strong> de {report.ranking_total} alumnos</p>}
          {report.badges && report.badges.length > 0 && (
            <p style={{ marginTop: '.5rem' }}>{report.badges.map(b => <span key={b} className="chip" style={{ display: 'inline-block', margin: '0 .4rem .4rem 0', background: '#fef9c3', borderColor: '#fde047' }}>🏅 {b}</span>)}</p>
          )}
          <table>
            <thead><tr><th>Simulacion</th><th>Puntaje</th><th>Fecha</th></tr></thead>
            <tbody>
              {report.recent_attempts.map((a, i) => (
                <tr key={i}><td>{a.exam}</td><td>{a.score}%</td><td>{a.date?.slice(0, 10)}</td></tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <section className="card">
        <h3>Proximas clases en vivo</h3>
        {lives.length === 0 && <p className="muted">No hay clases programadas.</p>}
        <table>
          <tbody>
            {lives.map(l => (
              <tr key={l.id}>
                <td>{l.title}</td>
                <td>{new Date(l.starts_at).toLocaleString('es-CL')}</td>
                <td style={{textAlign:'right'}}><a className="btn btn-primary btn-sm" href={l.room_url} target="_blank" rel="noreferrer">Unirse</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="card muted">
        <h3>Recordatorio importante</h3>
        <p>La inscripcion oficial a Examenes Libres se realiza por el apoderado en el
        portal <strong>Ayuda Mineduc</strong>. El Mineduc asigna el colegio donde se
        rinde la prueba y emite el certificado oficial ante aprobacion.</p>
      </section>
    </div>
  )
}
