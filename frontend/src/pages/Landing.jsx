import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div>
      <nav className="nav">
        <Link to="/" className="logo">Aula<span>Site</span></Link>
        <div className="nav-links">
          <a href="#como-funciona">Como funciona</a>
          <a href="#niveles">Niveles</a>
          <a href="#contacto">Contacto</a>
        </div>
        <Link to="/login" className="btn btn-primary btn-sm" style={{marginLeft:'1rem'}}>Ingresar</Link>
      </nav>

      <header className="hero">
        <span className="badge">Apoyo pedagogico · Examenes Libres · Chile</span>
        <h1>Prepara a tu hijo para los <em>Examenes Libres</em> con clases online en vivo</h1>
        <p>Plataforma de apoyo pedagogico con clases en vivo, biblioteca de grabaciones, simulaciones de examen y reportes de progreso para el apoderado. La certificacion oficial la emite el Mineduc; nosotros preparamos para aprobar.</p>
        <div className="hero-cta">
          <Link to="/login" className="btn btn-accent">Comenzar ahora</Link>
          <a href="#como-funciona" className="btn btn-outline">Como funciona</a>
        </div>
        <div className="stats">
          <div><strong>14</strong><span>Niveles educativos</span></div>
          <div><strong>100%</strong><span>Clases online en vivo</span></div>
          <div><strong>24/7</strong><span>Biblioteca de grabaciones</span></div>
        </div>
      </header>

      <section>
        <h2 className="section-title">Todo lo que necesita para aprobar</h2>
        <p className="section-sub">Un solo lugar para estudiar, practicar y medir el progreso real antes de rendir.</p>
        <div className="features">
          <div className="feature"><div className="ico">🎥</div><h3>Clases en vivo con docentes</h3><p>Sesiones online interactivas por nivel y asignatura, con link directo desde la plataforma.</p></div>
          <div className="feature"><div className="ico">📼</div><h3>Biblioteca de grabaciones</h3><p>Todas las clases quedan grabadas y disponibles para repasar cuando quiera.</p></div>
          <div className="feature"><div className="ico">📝</div><h3>Simulaciones de examen</h3><p>Pruebas de practica con evaluacion automatica, alineadas al formato de los Examenes Libres.</p></div>
          <div className="feature"><div className="ico">📈</div><h3>Reportes para apoderados</h3><p>Progreso por lecciones y promedio en simulaciones, siempre visible para la familia.</p></div>
        </div>
      </section>

      <section id="como-funciona" style={{background:'#fff'}}>
        <h2 className="section-title">Como funciona la validacion de estudios</h2>
        <p className="section-sub">Aula Site es una institucion de apoyo pedagogico. La certificacion oficial la emite el Ministerio de Educacion mediante Examenes Libres presenciales.</p>
        <div className="steps">
          <div className="step"><h3>Apoyo online</h3><p>El estudiante toma clases en vivo, grabaciones y simulaciones en nuestra plataforma.</p></div>
          <div className="step"><h3>Inscripcion oficial</h3><p>El apoderado inscribe al alumno en el portal Ayuda Mineduc para rendir Examenes Libres.</p></div>
          <div className="step"><h3>Evaluacion presencial</h3><p>El Mineduc asigna un colegio donde el alumno rinde las pruebas obligatorias.</p></div>
          <div className="step"><h3>Certificacion</h3><p>Aprobado el examen, el Mineduc emite el certificado de estudios con validez legal.</p></div>
        </div>
      </section>

      <section id="niveles">
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
          <Link to="/login" className="btn btn-accent">Crear cuenta gratis</Link>
        </div>
      </section>

      <footer id="contacto">
        <strong>AulaSite</strong> · Apoyo pedagogico para Examenes Libres · Chile
        <p className="legal">Aula Site es una plataforma de apoyo pedagogico y no un establecimiento educacional reconocido por el Ministerio de Educacion de Chile. No emitimos certificados de estudios ni promocion de alumnos. La validacion oficial de estudios se realiza exclusivamente mediante los Examenes Libres administrados por el Mineduc, con inscripcion del apoderado en el portal Ayuda Mineduc y evaluacion presencial en un establecimiento designado por el ministerio.</p>
      </footer>
    </div>
  )
}
