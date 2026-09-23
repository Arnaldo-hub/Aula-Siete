import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Biblioteca() {
  const [recs, setRecs] = useState([])
  useEffect(() => { api('/recordings').then(setRecs).catch(() => {}) }, [])
  return (
    <main className="container">
      <h2>Biblioteca de clases grabadas</h2>
      <div className="grid">
        {recs.map(r => (
          <div className="card" key={r.id}>
            <h4>{r.title}</h4>
            <video controls src={r.video_url} style={{ width: '100%' }} />
          </div>
        ))}
        {recs.length === 0 && <p className="muted">No hay grabaciones publicadas aún.</p>}
      </div>
    </main>
  )
}
