import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Biblioteca() {
  const [recs, setRecs] = useState([])
  const [err, setErr] = useState('')
  useEffect(() => { api('/recordings').then(setRecs).catch(e => setErr(e.message)) }, [])

  return (
    <div>
      <h2 className="page-title">Biblioteca de clases grabadas</h2>
      {err && <div className="error">{err}</div>}
      <div className="grid">
        {recs.map(r => (
          <div className="card" key={r.id}>
            <h3>{r.title}</h3>
            <video controls src={r.video_url} />
          </div>
        ))}
      </div>
      {recs.length === 0 && !err && <div className="card muted">Aun no hay grabaciones publicadas.</div>}
    </div>
  )
}
