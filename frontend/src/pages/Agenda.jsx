import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Agenda() {
  const [lives, setLives] = useState([])
  const [err, setErr] = useState('')

  useEffect(() => { api('/live-classes').then(setLives).catch(e => setErr(e.message)) }, [])

  const byDay = {}
  lives.forEach(l => {
    const day = l.starts_at.slice(0, 10)
    ;(byDay[day] = byDay[day] || []).push(l)
  })

  return (
    <div>
      <h2 className="page-title">Agenda de clases en vivo</h2>
      {err && <div className="error">{err}</div>}
      {lives.length === 0 && !err && (
        <div className="card muted">
          <h3>Aun no hay clases programadas</h3>
          <p>El equipo docente publica las clases de la semana aqui. Vuelve pronto o consulta al asistente.</p>
        </div>
      )}
      {Object.keys(byDay).sort().map(day => (
        <section className="card" key={day}>
          <h3>📅 {new Date(day + 'T12:00:00').toLocaleDateString('es-CL', { weekday: 'long', day: 'numeric', month: 'long' })}</h3>
          <table>
            <tbody>
              {byDay[day].map(l => (
                <tr key={l.id}>
                  <td style={{width: '110px'}}>{new Date(l.starts_at).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })}</td>
                  <td>{l.title}</td>
                  <td style={{textAlign: 'right'}}>
                    <a className="btn btn-primary btn-sm" href={l.room_url} target="_blank" rel="noreferrer">Unirse a la sala</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </div>
  )
}
