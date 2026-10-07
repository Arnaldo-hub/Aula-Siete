import { useEffect, useRef, useState } from 'react'
import { api } from '../api'

const LEVELS = [
  ['PREKINDER', 'Prekínder'], ['KINDER', 'Kínder'],
  ['BASICA_1', '1° Básico'], ['BASICA_2', '2° Básico'], ['BASICA_3', '3° Básico'],
  ['BASICA_4', '4° Básico'], ['BASICA_5', '5° Básico'], ['BASICA_6', '6° Básico'],
  ['BASICA_7', '7° Básico'], ['BASICA_8', '8° Básico'],
  ['MEDIA_1', '1° Medio'], ['MEDIA_2', '2° Medio'], ['MEDIA_3', '3° Medio'], ['MEDIA_4', '4° Medio'],
]
const nivelLabel = (lv) => (LEVELS.find(([k]) => k === lv) || [null, lv || '—'])[1]

const fld = { width: '100%', padding: '.6rem .8rem', borderRadius: '10px', border: '1.5px solid var(--border)', marginBottom: '.7rem', fontFamily: 'inherit' }

export default function Tutor() {
  const role = localStorage.getItem('role')
  const [tab, setTab] = useState('chat')
  const tabs = [['chat', '🤖 Tutor socrático']]
  if (role === 'profesor' || role === 'admin') tabs.push(['gen', '✨ Generador docente'])
  tabs.push(['essay', '✍️ Corrección de ensayo'])

  return (
    <div>
      <h2 className="page-title">Tutor IA — currículo chileno, 24/7</h2>
      <p className="muted" style={{ marginTop: '-1rem', marginBottom: '1.2rem' }}>
        No entrega respuestas listas: guía a tu hijo paso a paso con el método socrático, alineado a los OA del Mineduc.
      </p>
      <div style={{ display: 'flex', gap: '.4rem', flexWrap: 'wrap', marginBottom: '1.2rem' }}>
        {tabs.map(([k, label]) => (
          <button key={k} className="btn btn-sm" onClick={() => setTab(k)}
            style={tab === k ? { background: 'var(--primary)', color: '#fff' } : { background: '#fff', color: 'var(--ink)', border: '1px solid var(--border)' }}>
            {label}
          </button>
        ))}
      </div>
      {tab === 'chat' && <Chat />}
      {tab === 'gen' && <Generador />}
      {tab === 'essay' && <Ensayo />}
    </div>
  )
}

function Chat() {
  const [students, setStudents] = useState([])
  const [sid, setSid] = useState('')
  const [level, setLevel] = useState('MEDIA_4')
  const [msgs, setMsgs] = useState([
    { from: 'bot', text: 'Hola, soy tu tutor. Cuéntame qué tema estás estudiando (ej: ecuaciones, comprensión lectora) y partimos paso a paso.' }
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const boxRef = useRef(null)
  useEffect(() => { boxRef.current?.scrollTo(0, 99999) }, [msgs])
  useEffect(() => { api('/users/students').then(s => { setStudents(s); if (s[0]) setSid(String(s[0].id)) }).catch(() => {}) }, [])

  async function send(e) {
    e.preventDefault()
    const q = input.trim()
    if (!q || busy) return
    setInput(''); setBusy(true); setErr('')
    const history = [...msgs, { from: 'me', text: q }]
    setMsgs(history)
    try {
      const r = await api('/tutor/chat', { method: 'POST', body: {
        message: q, level, student_id: sid ? Number(sid) : null,
        history: msgs.slice(-10)
      }})
      setMsgs([...history, { from: 'bot', text: r.reply }])
    } catch (e2) {
      setErr(e2.message)
      setMsgs(history)
    }
    setBusy(false)
  }

  return (
    <section className="card">
      <div style={{ display: 'flex', gap: '.8rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <select value={sid} onChange={e => setSid(e.target.value)} style={{ ...fld, width: 'auto', margin: 0 }}>
          <option value="">Sin alumno asociado</option>
          {students.map(s => <option key={s.id} value={s.id}>{s.name} — {nivelLabel(s.level)}</option>)}
        </select>
        <select value={level} onChange={e => setLevel(e.target.value)} style={{ ...fld, width: 'auto', margin: 0 }}>
          {LEVELS.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      {err && <div className="error">{err}</div>}
      <div ref={boxRef} style={{ height: '380px', overflowY: 'auto', background: '#f8fafc', borderRadius: '12px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '.6rem' }}>
        {msgs.map((m, i) => (
          <div key={i} style={{
            maxWidth: '85%', padding: '.7rem .95rem', borderRadius: '14px', fontSize: '.92rem',
            lineHeight: 1.55, whiteSpace: 'pre-wrap',
            alignSelf: m.from === 'me' ? 'flex-end' : 'flex-start',
            background: m.from === 'me' ? 'var(--primary)' : '#fff',
            color: m.from === 'me' ? '#fff' : 'var(--ink)',
            border: m.from === 'me' ? 'none' : '1px solid var(--border)'
          }}>{m.text}</div>
        ))}
        {busy && <div className="muted" style={{ alignSelf: 'flex-start' }}>✍️ El tutor está pensando...</div>}
      </div>
      <form onSubmit={send} style={{ display: 'flex', gap: '.6rem', marginTop: '1rem' }}>
        <input style={{ ...fld, margin: 0, flex: 1 }} value={input} onChange={e => setInput(e.target.value)}
               placeholder="Escribe la duda de tu hijo (ej: no entiende cómo factorizar)..." />
        <button className="btn btn-primary" type="submit" disabled={busy}>Preguntar</button>
      </form>
    </section>
  )
}

function Generador() {
  const [f, setF] = useState({ subject: 'Matematica', level: 'BASICA_8', oa: '', topic: '', kind: 'guia' })
  const [out, setOut] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  async function gen(e) {
    e.preventDefault(); setBusy(true); setErr(''); setOut('')
    try {
      const r = await api('/ai/generate', { method: 'POST', body: f })
      setOut(r.content)
    } catch (e2) { setErr(e2.message) }
    setBusy(false)
  }
  return (
    <section className="card">
      <h3>Generador de material alineado al Mineduc</h3>
      {err && <div className="error">{err}</div>}
      <form onSubmit={gen} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '.6rem' }}>
        <select style={fld} value={f.subject} onChange={e => setF({ ...f, subject: e.target.value })}>
          <option>Matematica</option><option>Lenguaje</option><option>Historia</option><option>Ciencias</option><option>Ingles</option>
        </select>
        <select style={fld} value={f.level} onChange={e => setF({ ...f, level: e.target.value })}>
          {LEVELS.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select style={fld} value={f.kind} onChange={e => setF({ ...f, kind: e.target.value })}>
          <option value="guia">Guía de trabajo</option><option value="planificacion">Planificación de clase</option><option value="ejercicios">Set de ejercicios</option>
        </select>
        <input style={fld} placeholder="OA (ej: OA 11)" value={f.oa} onChange={e => setF({ ...f, oa: e.target.value })} />
        <input style={{ ...fld, gridColumn: '1 / 5' }} placeholder="Tema (ej: factorización de trinomios)" value={f.topic} onChange={e => setF({ ...f, topic: e.target.value })} required />
        <button className="btn btn-primary btn-sm" style={{ gridColumn: '1 / 5', justifySelf: 'start' }} disabled={busy}>
          {busy ? 'Generando...' : '✨ Generar material'}
        </button>
      </form>
      {out && <pre style={{ whiteSpace: 'pre-wrap', background: '#f8fafc', border: '1px solid var(--border)', borderRadius: '12px', padding: '1.2rem', marginTop: '1rem', fontFamily: 'inherit', fontSize: '.92rem', lineHeight: 1.6 }}>{out}</pre>}
    </section>
  )
}

function Ensayo() {
  const [text, setText] = useState('')
  const [level, setLevel] = useState('MEDIA_4')
  const [out, setOut] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  async function review(e) {
    e.preventDefault(); setBusy(true); setErr(''); setOut('')
    try {
      const r = await api('/ai/essay', { method: 'POST', body: { text, level } })
      setOut(r.feedback)
    } catch (e2) { setErr(e2.message) }
    setBusy(false)
  }
  return (
    <section className="card">
      <h3>Corrección de ensayo (formato PAES)</h3>
      <p className="muted">El alumno escribe su ensayo, la IA lo corrige con rúbrica PAES: comprensión, desarrollo, organización y lenguaje.</p>
      {err && <div className="error">{err}</div>}
      <select value={level} onChange={e => setLevel(e.target.value)} style={{ ...fld, width: 'auto' }}>
        {LEVELS.filter(([k]) => !['PREKINDER','KINDER','BASICA_1','BASICA_2','BASICA_3','BASICA_4','BASICA_5','BASICA_6'].includes(k)).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
      </select>
      <textarea style={{ ...fld, minHeight: '160px' }} value={text} onChange={e => setText(e.target.value)}
        placeholder="Pega aquí el texto del ensayo del alumno..." required />
      <button className="btn btn-primary btn-sm" onClick={review} disabled={busy}>{busy ? 'Corrigiendo...' : 'Corregir ensayo'}</button>
      {out && <pre style={{ whiteSpace: 'pre-wrap', background: '#f8fafc', border: '1px solid var(--border)', borderRadius: '12px', padding: '1.2rem', marginTop: '1rem', fontFamily: 'inherit', fontSize: '.92rem', lineHeight: 1.6 }}>{out}</pre>}
    </section>
  )
}
