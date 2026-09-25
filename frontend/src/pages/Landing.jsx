import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BASE } from '../api'
import Logo from '../Logo'
import Chatbot from '../Chatbot'

const WSP = 'https://wa.me/56954690241?text=Hola%2C%20quiero%20informaci%C3%B3n%20sobre%20Aula%20Site'

export default function Landing() {
  const [stats, setStats] = useState(null)
  useEffect(() => {
    fetch(`${BASE}/stats`).then(r => r.json()).then(setStats).catch(() => {})
  }, [])

  const s = k => stats ? stats[k] : '—'

  return (
    <div>
      <nav className="nav">
        <Link to="/" className="logo" style={{display:'flex',alignItems:'center',gap:'.5rem'}}><Logo size={32} />Aula<span>Site</span></Link>
        <div className="nav-links">
          <a href="#segmentos">Para quien es</a>
          <a href="#planes">Planes</a>
          <a href="#faq">Preguntas</a>
        </div>
        <Link to="/login" className="btn btn-primary btn-sm" style={{marginLeft:'1rem'}}>Ingresar</Link>
      </nav>

      <header className="hero">
        <span className="badge">Apoyo pedagogico · Examenes Libres · Chile</span>
        <h1>Prepara a tu hijo para los <em>Examenes Libres</em> con clases online en vivo</h1>
        <p>Clases en vivo en grupos reducidos, biblioteca de grabaciones, simulaciones de examen y reportes para el apoderado. La certificacion oficial la emite el Mineduc; nosotros preparamos para aprobar.</p>
        <div className="hero-cta">
          <a href={WSP} target="_blank" rel="noreferrer" className="btn btn-accent">Agenda una clase de prueba gratis</a>
          <a href="#planes" className="btn btn-outline">Ver planes</a>
        </div>
        <div className="stats">
          <div><strong>{s('courses')}</strong><span>Cursos activos</span></div>
          <div><strong>{s('questions')}</strong><span>Preguntas de practica</span></div>
          <div><strong>{s('recordings')}</strong><span>Clases grabadas</span></div>
          <div><strong>{s('attempts')}</strong><span>Simulaciones rendidas</span></div>
        </div>
      </header>

      <section>
        <h2 className="section-title">Todo lo que necesita para aprobar</h2>
        <p className="section-sub">Un solo lugar para estudiar, practicar y medir el progreso real antes de rendir.</p>
        <div className="features">
          <div className="feature"><div className="ico">🎥</div><h3>Clases en vivo, grupos reducidos</h3><p>Maximo 10 estudiantes por sala, con camara y microfono: participacion real, no una flecha mas.</p></div>
          <div className="feature"><div className="ico">📼</div><h3>Biblioteca de grabaciones</h3><p>Todas las clases quedan grabadas y disponibles para repasar cuando quiera.</p></div>
          <div className="feature"><div className="ico">📝</div><h3>Simulaciones de examen</h3><p>Pruebas de practica con evaluacion automatica, alineadas al formato de los Examenes Libres.</p></div>
          <div className="feature"><div className="ico">📈</div><h3>Reportes para apoderados</h3><p>Progreso por lecciones y promedio en simulaciones, siempre visible para la familia.</p></div>
        </div>
      </section>

      <section id="segmentos" style={{background:'#fff'}}>
        <h2 className="section-title">Para quien es Aula Site</h2>
        <p className="section-sub">Dos caminos, una misma meta: aprobar y validar estudios oficialmente.</p>
        <div className="segments">
          <div className="segment">
            <h3>🎯 Voy a rendir Examen Libre</h3>
            <p>Tu hijo estudiara por cuenta propia o en otro establecimiento y necesita preparacion enfocada: clases por asignatura evaluada, simulaciones del formato real y seguimiento hasta el dia del examen presencial.</p>
            <a className="btn btn-primary" href={WSP} target="_blank" rel="noreferrer">Quiero prepararme</a>
          </div>
          <div className="segment">
            <h3>🏠 Educamos en casa (homeschool)</h3>
            <p>Familias que educan en casa y validan el ano mediante Examenes Libres. Plan anual con planificacion, clases y evidencia de progreso para rendir con confianza.</p>
            <a className="btn btn-outline" href={WSP} target="_blank" rel="noreferrer">Conocer el plan anual</a>
          </div>
        </div>
      </section>

      <section id="planes">
        <h2 className="section-title">Planes</h2>
        <p className="section-sub">Precios de lanzamiento. Cupos limitados por sala para mantener grupos reducidos.</p>
        <div className="plans">
          <div className="plan">
            <h3>Plan Grupo En Vivo</h3>
            <div className="price">$49.900</div>
            <div className="per">por mes · por estudiante</div>
            <ul>
              <li>2 clases en vivo semanales (grupo max. 10)</li>
              <li>Biblioteca de grabaciones ilimitada</li>
              <li>Simulaciones de examen ilimitadas</li>
              <li>Reporte mensual de progreso</li>
              <li>Reunion de seguimiento con apoderado</li>
            </ul>
            <a className="btn btn-primary" href={WSP} target="_blank" rel="noreferrer">Reservar cupo</a>
          </div>
          <div className="plan featured">
            <span className="tag">RECOMENDADO</span>
            <h3>Plan Intensivo 1 a 1</h3>
            <div className="price">$119.900</div>
            <div className="per">por mes · por estudiante</div>
            <ul>
              <li>Todo lo del Plan Grupo En Vivo</li>
              <li>2 clases particulares semanales</li>
              <li>Plan de estudio personalizado</li>
              <li>Dudas express con docente entre clases</li>
              <li>Preparacion por asignatura evaluada</li>
            </ul>
            <a className="btn btn-accent" href={WSP} target="_blank" rel="noreferrer">Reservar cupo</a>
          </div>
        </div>
      </section>

      <section style={{background:'#fff'}}>
        <h2 className="section-title">Como funciona la validacion de estudios</h2>
        <p className="section-sub">Aula Site es una institucion de apoyo pedagogico. La certificacion oficial la emite el Ministerio de Educacion mediante Examenes Libres presenciales.</p>
        <div className="steps">
          <div className="step"><h3>Apoyo online</h3><p>El estudiante toma clases en vivo, grabaciones y simulaciones en nuestra plataforma.</p></div>
          <div className="step"><h3>Inscripcion oficial</h3><p>El apoderado inscribe al alumno en el portal Ayuda Mineduc para rendir Examenes Libres.</p></div>
          <div className="step"><h3>Evaluacion presencial</h3><p>El Mineduc asigna un colegio donde el alumno rinde las pruebas obligatorias.</p></div>
          <div className="step"><h3>Certificacion</h3><p>Aprobado el examen, el Mineduc emite el certificado de estudios con validez legal.</p></div>
        </div>
      </section>

      <section id="faq">
        <h2 className="section-title">Preguntas frecuentes</h2>
        <p className="section-sub">Lo que toda familia nos pregunta antes de partir.</p>
        <div className="faq">
          <details><summary>¿Es Aula Site un colegio?</summary><p>No. Somos una plataforma de apoyo pedagogico. En Chile el Mineduc no reconoce colegios 100% virtuales; la validacion de estudios se hace mediante Examenes Libres presenciales, y eso es exactamente para lo que preparamos a tu hijo.</p></details>
          <details><summary>¿Ustedes emiten el certificado de estudios?</summary><p>No, y desconfia de quien lo prometa. El certificado con validez legal lo emite exclusivamente el Ministerio de Educacion despues de aprobar los Examenes Libres. Nosotros entregamos clases, simulaciones y reportes de preparacion.</p></details>
          <details><summary>¿Como inscribo a mi hijo en los Examenes Libres?</summary><p>La inscripcion la realiza el apoderado en el portal Ayuda Mineduc. Nosotros te orientamos paso a paso con las fechas y asignaturas que corresponden segun el nivel de tu hijo.</p></details>
          <details><summary>¿Que necesita mi hijo para tomar las clases?</summary><p>Un computador, tablet o celular con internet, y una cuenta de apoderado en nuestra plataforma. Las clases en vivo se realizan por videollamada con camara y microfono.</p></details>
          <details><summary>¿Las clases quedan grabadas?</summary><p>Si. Todas las clases en vivo quedan en la biblioteca para repasar las veces que sea necesario.</p></details>
          <details><summary>¿Puedo pausar mi suscripcion?</summary><p>Si. Los meses pagados y no utilizados se congelan y puedes reanudarlos cuando lo necesites. Escríbenos por WhatsApp para gestionarlo.</p></details>
        </div>
      </section>

      <section>
        <h2 className="section-title">Cobertura completa</h2>
        <p className="section-sub">Desde educacion parvularia hasta cuarto medio.</p>
        <div className="levels">
          <span className="chip">Prekinder</span><span className="chip">Kinder</span>
          <span className="chip">1° a 8° Basica</span><span className="chip">1° a 4° Media</span>
        </div>
      </section>

      <section style={{paddingTop:0}}>
        <div className="cta-final">
          <h2>La primera clase de prueba es gratis</h2>
          <p>Crea tu cuenta como apoderado, registra a tu hijo y mira como rinde su primera simulacion.</p>
          <a className="btn btn-accent" href={WSP} target="_blank" rel="noreferrer">Agendar clase de prueba</a>
        </div>
      </section>

      <footer>
        <strong>AulaSite</strong> · Apoyo pedagogico para Examenes Libres · Chile
        <p className="legal">Aula Site es una plataforma de apoyo pedagogico y no un establecimiento educacional reconocido por el Ministerio de Educacion de Chile. No emitimos certificados de estudios ni promocion de alumnos. La validacion oficial de estudios se realiza exclusivamente mediante los Examenes Libres administrados por el Mineduc, con inscripcion del apoderado en el portal Ayuda Mineduc y evaluacion presencial en un establecimiento designado por el ministerio.</p>
      </footer>

      <Chatbot />
    </div>
  )
}
