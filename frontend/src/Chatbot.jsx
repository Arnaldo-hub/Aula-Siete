import { useState, useRef, useEffect } from 'react'

const WSP = 'https://wa.me/56954690241?text=Hola%2C%20tengo%20una%20consulta%20sobre%20Aula%20Site'

// Base de conocimiento: palabra clave -> respuesta
const KB = [
  { k: ['precio', 'plan', 'cuanto', 'cuesta', 'valor', 'pago', 'pagar'],
    a: 'Tenemos dos planes: Grupo En Vivo $49.900/mes y Plan Intensivo 1 a 1 $119.900/mes. Incluyen clases en vivo, grabaciones, simulaciones ilimitadas y reporte mensual. La primera clase de prueba es gratis. ¿Quieres que te contactemos por WhatsApp?' },
  { k: ['examen libre', 'examenes libres', 'mineduc', 'certificado', 'validar', 'validacion'],
    a: 'La certificacion oficial la emite el Mineduc mediante Examenes Libres presenciales. El apoderado inscribe al alumno en el portal Ayuda Mineduc. Nosotros preparamos con clases y simulaciones; no emitimos certificados (desconfia de quien lo prometa).' },
  { k: ['inscripcion', 'inscribir', 'inscribo', 'ayuda mineduc', 'matricula'],
    a: 'La inscripcion a Examenes Libres la realiza el apoderado en ayudamineduc.cl. Te guiamos con las fechas y asignaturas segun el nivel de tu hijo. Agenda una clase de prueba gratis y partimos.' },
  { k: ['clase', 'clases', 'vivo', 'horario', 'cuando'],
    a: 'Las clases son online en vivo, en grupos de maximo 10 estudiantes con camara y microfono, y quedan grabadas en la biblioteca para repasar cuando quieras. Los horarios se coordinan segun el nivel.' },
  { k: ['nivel', 'niveles', 'basica', 'media', 'prekinder', 'kinder', 'octavo', 'cuarto'],
    a: 'Cubrimos Prekinder, Kinder, Basica 1° a 8° y Media 1° a 4°. La preparacion para Examenes Libres se concentra en 8° Basica y 4° Media.' },
  { k: ['prueba', 'gratis', 'demo', 'probar'],
    a: 'La primera clase de prueba es gratis. Escribenos por WhatsApp al +56 9 5469 0241 y agendamos.' },
  { k: ['simulacion', 'simulaciones', 'ensayo', 'practica'],
    a: 'Las simulaciones replican el formato de los Examenes Libres con evaluacion automatica e instantanea. El apoderado ve el puntaje y progreso en su panel.' },
  { k: ['profesor', 'profesores', 'docente', 'docentes'],
    a: 'Nuestros docentes dan clases en vivo en grupos reducidos y responden dudas entre clases. Todos los profesores son especialistas por asignatura y nivel.' },
  { k: ['requisito', 'necesito', 'internet', 'computador', 'tablet', 'celular'],
    a: 'Solo se necesita un computador, tablet o celular con internet. Las clases en vivo usan videollamada con camara y microfono.' },
  { k: ['pausar', 'congelar', 'suspender', 'reanudar'],
    a: 'Puedes pausar tu suscripcion cuando lo necesites: los meses pagados y no utilizados se congelan. Lo gestionas por WhatsApp.' },
  { k: ['contacto', 'whatsapp', 'telefono', 'llamar', 'correo', 'email'],
    a: 'Puedes escribirnos por WhatsApp al +56 9 5469 0241 o al correo de contacto. Te respondemos rapidamente.' },
]

function answer(text) {
  const t = text.toLowerCase()
  for (const item of KB) {
    if (item.k.some(k => t.includes(k))) return item.a
  }
  return null
}

export default function Chatbot() {
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState([
    { from: 'bot', text: 'Hola, soy el asistente de Aula Site. Preguntame por precios, clases, Examenes Libres o niveles.' }
  ])
  const [input, setInput] = useState('')
  const boxRef = useRef(null)

  useEffect(() => { boxRef.current?.scrollTo(0, 9999) }, [msgs, open])

  function send(e) {
    e.preventDefault()
    const q = input.trim()
    if (!q) return
    setInput('')
    const a = answer(q)
    setMsgs(m => [...m, { from: 'me', text: q }])
    setTimeout(() => {
      setMsgs(m => [...m, a
        ? { from: 'bot', text: a }
        : { from: 'bot', text: 'No tengo una respuesta segura para eso. Te derivamos con un asesor por WhatsApp:', wsp: true }])
    }, 500)
  }

  return (
    <div className="chat-wrap">
      {open && (
        <div className="chat-panel">
          <div className="chat-head">
            <strong>Asistente Aula Site</strong>
            <button onClick={() => setOpen(false)} aria-label="Cerrar">✕</button>
          </div>
          <div className="chat-body" ref={boxRef}>
            {msgs.map((m, i) => (
              <div key={i} className={'bubble ' + (m.from === 'me' ? 'me' : 'bot')}>
                {m.text}
                {m.wsp && <a className="btn btn-accent btn-sm" style={{marginTop:'.6rem'}} href={WSP} target="_blank" rel="noreferrer">Continuar por WhatsApp</a>}
              </div>
            ))}
          </div>
          <form className="chat-input" onSubmit={send}>
            <input value={input} onChange={e => setInput(e.target.value)}
                   placeholder="Escribe tu consulta..." />
            <button type="submit" className="btn btn-primary btn-sm">Enviar</button>
          </form>
        </div>
      )}
      <button className="chat-fab" onClick={() => setOpen(!open)} title="Asistente virtual">
        {open ? '✕' : '💬'}
      </button>
    </div>
  )
}
