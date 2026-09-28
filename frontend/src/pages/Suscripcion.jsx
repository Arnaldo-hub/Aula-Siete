import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Suscripcion() {
  const [plans, setPlans] = useState([])
  const [students, setStudents] = useState([])
  const [sid, setSid] = useState('')
  const [subs, setSubs] = useState([])
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/payments/plans').then(setPlans).catch(e => setErr(e.message))
    api('/users/students').then(s => { setStudents(s); if (s[0]) setSid(String(s[0].id)) }).catch(() => {})
    if (location.search.includes('estado=ok')) setMsg('Suscripción iniciada en Mercado Pago. El estado se confirma en segundos.')
  }, [])

  useEffect(() => {
    if (sid) api(`/payments/status?student_id=${sid}`).then(setSubs).catch(() => {})
  }, [sid])

  async function subscribe(planId) {
    setErr(''); setMsg('')
    try {
      const r = await api(`/payments/subscribe?plan=${planId}&student_id=${sid}`, { method: 'POST', body: {} })
      window.location.href = r.init_point   // va a Mercado Pago a autorizar el pago
    } catch (e2) { setErr(e2.message) }
  }

  const statusTxt = { pending: '⏳ Pendiente de confirmación', authorized: '✅ Activa',
                      paused: '⏸ Pausada', cancelled: '❌ Cancelada' }

  return (
    <div>
      <h2 className="page-title">Suscripción</h2>
      {msg && <div className="card ok">{msg}</div>}
      {err && <div className="error">{err}</div>}

      <section className="card">
        <label style={{ fontSize: '.85rem', fontWeight: 600 }}>Alumno a inscribir</label>
        <select value={sid} onChange={e => setSid(e.target.value)} style={{ width: '100%', padding: '.65rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)' }}>
          {students.map(s => <option key={s.id} value={s.id}>Alumno #{s.id} - Nivel {s.level}</option>)}
        </select>
      </section>

      <div className="grid">
        {plans.map(p => (
          <div className="card" key={p.id} style={{ textAlign: 'center' }}>
            <h3>{p.name.replace(' - Aula Siete', '')}</h3>
            <p style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--primary)', margin: '.5rem 0' }}>{p.formatted}</p>
            <p className="muted">Cobro mensual automático con Mercado Pago. Cancela cuando quieras.</p>
            <button className="btn btn-primary" onClick={() => subscribe(p.id)}>Suscribirse</button>
          </div>
        ))}
      </div>

      {subs.length > 0 && (
        <section className="card">
          <h3>Mis suscripciones</h3>
          <table>
            <thead><tr><th>Plan</th><th>Monto</th><th>Estado</th><th>Fecha</th></tr></thead>
            <tbody>
              {subs.map(s => (
                <tr key={s.id}>
                  <td>{s.plan === 'grupal' ? 'Grupo En Vivo' : 'Intensivo 1 a 1'}</td>
                  <td>${s.amount.toLocaleString('es-CL')}</td>
                  <td>{statusTxt[s.status] || s.status}</td>
                  <td>{s.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}
