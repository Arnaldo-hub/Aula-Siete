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

export default function Ruta() {
  const [students, setStudents] = useState([])
  const [sid, setSid] = useState('')
  const [items, setItems] = useState([])
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/users/students').then(s => { setStudents(s); if (s[0]) setSid(String(s[0].id)) }).catch(e => setErr(e.message))
  }, [])

  useEffect(() => {
    if (!sid) return
    api(`/exams/path/${sid}`).then(setItems).catch(e => setErr(e.message))
  }, [sid])

  async function markDone(id) {
    await api(`/exams/path/${id}/done`, { method: 'POST', body: {} })
    setItems(items.map(i => i.id === id ? { ...i, status: 'completed' } : i))
  }

  const pending = items.filter(i => i.status !== 'completed')
  const done = items.filter(i => i.status === 'completed')

  return (
    <div>
      <h2 className="page-title">Mi ruta personalizada</h2>
      <p className="muted" style={{ marginTop: '-1rem', marginBottom: '1.2rem' }}>
        Generada automaticamente segun los OA debiles detectados en el ultimo diagnostico.
      </p>
      {err && <div className="error">{err}</div>}

      <section className="card" style={{ background: 'var(--bg-soft)' }}>
        <h3>¿Cómo funciona la ruta?</h3>
        <p className="muted" style={{ margin: 0 }}>
          Cuando tu hijo rinde un diagnóstico en <strong>Simulaciones</strong>, el sistema detecta
          los objetivos de aprendizaje (OA) que falló y crea aquí tareas de refuerzo a medida.
          Cuando las complete, aprieta <strong>"Marcar completado"</strong> y la ruta se actualiza.
        </p>
        <Link className="btn btn-primary btn-sm" to="/simulaciones" style={{ marginTop: '.7rem', display: 'inline-block' }}>📝 Rendir un diagnóstico ahora</Link>
      </section>

      {students.length > 1 && (
        <section className="card">
          <label style={{ fontSize: '.85rem', fontWeight: 600 }}>Alumno</label>
          <select value={sid} onChange={e => setSid(e.target.value)} style={{ width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)' }}>
            {students.map(s => <option key={s.id} value={s.id}>{s.name} — {nivelLabel(s.level)}</option>)}
          </select>
        </section>
      )}

      <section className="card">
        <h3>Pendientes ({pending.length})</h3>
        {pending.length === 0 && <p className="muted">Sin tareas pendientes. Rinde un diagnostico de tu nivel para generar tu ruta.</p>}
        {pending.map(i => (
          <div key={i.id} className="doubt" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
            <div>
              <strong>{i.oa}</strong> — {i.title}
              {i.material_id && <p className="muted" style={{ fontSize: '.8rem', margin: '.2rem 0 0' }}>Material disponible en el curso</p>}
            </div>
            <button className="btn btn-primary btn-sm" onClick={() => markDone(i.id)}>Marcar completado</button>
          </div>
        ))}
      </section>

      {done.length > 0 && (
        <section className="card">
          <h3>Completados ({done.length})</h3>
          {done.map(i => (
            <div key={i.id} className="doubt" style={{ opacity: .65 }}>
              <span style={{ textDecoration: 'line-through' }}>{i.oa} — {i.title}</span>
            </div>
          ))}
        </section>
      )}
    </div>
  )
}
