import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

const LEVELS = [
  ['PREKINDER', 'Prekínder'], ['KINDER', 'Kínder'],
  ['BASICA_1', '1° Básico'], ['BASICA_2', '2° Básico'], ['BASICA_3', '3° Básico'],
  ['BASICA_4', '4° Básico'], ['BASICA_5', '5° Básico'], ['BASICA_6', '6° Básico'],
  ['BASICA_7', '7° Básico'], ['BASICA_8', '8° Básico'],
  ['MEDIA_1', '1° Medio'], ['MEDIA_2', '2° Medio'], ['MEDIA_3', '3° Medio'], ['MEDIA_4', '4° Medio'],
]
const nivelLabel = (lv) => (LEVELS.find(([k]) => k === lv) || [null, lv || '—'])[1]

const subStatus = {
  pending: '⏳ Pendiente de confirmación',
  authorized: '✅ Activa',
  paused: '⏸ Pausada (pago fallido)',
  cancelled: '❌ Cancelada',
}

export default function Suscripcion() {
  const [students, setStudents] = useState([])
  const [sel, setSel] = useState('')
  const [estado, setEstado] = useState(null)
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')

  function load() {
    api('/users/students').then((rows) => {
      setStudents(rows)
      if (rows.length && !sel) setSel(String(rows[0].id))
    }).catch(() => {})
  }
  useEffect(() => { load() }, [])

  useEffect(() => {
    if (!sel) { setEstado(null); return }
    api('/payments/my-status?student_id=' + sel).then(setEstado).catch(() => setEstado(null))
  }, [sel])

  async function subscribe(plan) {
    setErr(''); setMsg('')
    if (!sel) { setErr('Primero selecciona el alumno a inscribir.'); return }
    try {
      const r = await api('/payments/subscribe?plan=' + plan + '&student_id=' + sel, { method: 'POST' })
      if (r.init_point) window.location.href = r.init_point
    } catch (e2) { setErr(e2.message) }
  }

  const selStudent = students.find((s) => String(s.id) === String(sel))

  return (
    <div>
      <h2 className="page-title">Suscripción</h2>
      {msg && <div className="card ok">{msg}</div>}
      {err && <div className="error">{err}</div>}

      {students.length === 0 ? (
        <div className="card">
          <h3>Primero registra a tu alumno</h3>
          <p>Para contratar un plan necesitas registrar al menos un alumno con su nivel.
            Hazlo desde el <Link to="/app"><strong>Panel → Registrar alumno</strong></Link> y vuelve aquí.</p>
        </div>
      ) : (
        <div className="card">
          <h3>Alumno a inscribir</h3>
          <select value={sel} onChange={(e) => setSel(e.target.value)}
            style={{ width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', fontFamily: 'inherit' }}>
            {students.map((s) => <option key={s.id} value={s.id}>{s.name} — {nivelLabel(s.level)}</option>)}
          </select>
          {estado && (
            <p style={{ marginTop: '.8rem' }}>
              Estado del plan: <strong>{subStatus[estado.status] || estado.status}</strong>
              {estado.status !== 'authorized' && (
                <span className="muted"> — el botón Suscribirse de abajo reactiva o crea el cobro.</span>
              )}
            </p>
          )}
        </div>
      )}

      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Plan Grupo En Vivo</h3>
          <p style={{ fontSize: '1.7rem', fontWeight: 800, color: 'var(--primary)', margin: '.4rem 0' }}>
            $49.900 <small style={{ fontSize: '.95rem' }}>CLP/mes</small></p>
          <p className="muted">Cobro mensual automático con Mercado Pago. Cancela cuando quieras.</p>
          <button className="btn btn-primary" disabled={students.length === 0}
            onClick={() => subscribe('grupal')}>Suscribirse</button>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Plan Intensivo 1 a 1</h3>
          <p style={{ fontSize: '1.7rem', fontWeight: 800, color: 'var(--primary)', margin: '.4rem 0' }}>
            $119.900 <small style={{ fontSize: '.95rem' }}>CLP/mes</small></p>
          <p className="muted">Cobro mensual automático con Mercado Pago. Cancela cuando quieras.</p>
          <button className="btn btn-primary" disabled={students.length === 0}
            onClick={() => subscribe('intensivo')}>Suscribirse</button>
        </div>
      </div>

      <div className="card">
        <h3>¿Cómo funciona el cobro?</h3>
        <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
          <li>Al suscribirte, Mercado Pago te cobra <strong>automáticamente cada mes</strong> con tu medio de pago.</li>
          <li>Si un cobro falla, MP reintenta; si sigue fallando el plan se pausa y el acceso se corta temporalmente.</li>
          <li>Para reactivar, vuelve a esta página y aprieta <strong>Suscribirse</strong> (se crea el cobro de nuevo).</li>
          <li>Para cancelar definitivamente, hazlo desde tu cuenta de Mercado Pago (sección Suscripciones) o escríbenos por WhatsApp.</li>
        </ul>
      </div>
    </div>
  )
}
