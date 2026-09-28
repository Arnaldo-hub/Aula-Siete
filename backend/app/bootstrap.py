"""Carga de datos iniciales/demo. Idempotente: puede ejecutarse varias veces."""
from sqlalchemy.orm import Session
from . import models
from .security import hash_password

DEMO_PASSWORD = "demo1234"

def _user(db: Session, email: str, name: str, role: str):
    u = db.query(models.User).filter_by(email=email).first()
    if not u:
        u = models.User(email=email, full_name=name, role=role,
                        password_hash=hash_password(DEMO_PASSWORD))
        db.add(u); db.commit(); db.refresh(u)
    return u

def run_seed(db: Session) -> dict:
    admin = _user(db, "admin@aulasite.cl", "Admin Aula Site", "admin")
    prof = _user(db, "profesor@demo.cl", "Prof. Carolina Rojas", "profesor")
    guard = _user(db, "apoderado@demo.cl", "Maria Perez", "apoderado")

    subj = db.query(models.Subject).filter_by(name="Matematica", level="MEDIA_1").first()
    if not subj:
        subj = models.Subject(name="Matematica", level="MEDIA_1")
        db.add(subj); db.commit(); db.refresh(subj)

    course = db.query(models.Course).first()
    if not course:
        course = models.Course(subject_id=subj.id, level="MEDIA_1",
                               teacher_id=prof.id, title="Matematica 1 Medio",
                               description="Preparacion examen libre")
        db.add(course); db.commit(); db.refresh(course)

    exam = db.query(models.Exam).first()
    if not exam:
        exam = models.Exam(subject_id=subj.id, level="MEDIA_1",
                           title="Simulacion Examen Libre - Matematica 1 Medio")
        db.add(exam); db.commit(); db.refresh(exam)
        db.add_all([
            models.Question(exam_id=exam.id,
                            prompt="Cuanto es 3x + 2x cuando x=4?",
                            options=["20", "22", "24", "18"], answer="20",
                            skill="OA 7 - Algebra"),
            models.Question(exam_id=exam.id, prompt="Raiz cuadrada de 144:",
                            options=["10", "11", "12", "14"], answer="12",
                            skill="OA 3 - Numeros"),
        ])
        db.commit()

    # Alumno demo del apoderado (se crea aunque el seed parcial haya corrido antes)
    st = db.query(models.Student).filter_by(guardian_id=guard.id).first()
    if not st:
        st = models.Student(guardian_id=guard.id, level="MEDIA_1")
        db.add(st); db.flush()
    enr = db.query(models.Enrollment).filter_by(student_id=st.id, course_id=course.id).first()
    if not enr:
        db.add(models.Enrollment(student_id=st.id, course_id=course.id))
    db.commit()
    return {"ok": True, "admin_id": admin.id, "student_id": st.id,
            "course_id": course.id, "exam_id": exam.id}


def seed_banco_preguntas(db: Session) -> dict:
    """Banco Fase A: diagnosticos 8 Basica y simulacros PAES 4 Media."""
    from .models import Exam, Question, Subject
    bank = [('Matematica', 'BASICA_8', 'Diagnóstico Matemática 8° Básica', 'diagnostico', [('¿Cuál es el valor de 3 elevado a -2?', ['-9', '-6', '1/9', '1/6'], '1/9', 'OA 1', 1), ('¿Cuál es la raíz cuadrada de 81?', ['7', '8', '9', '18'], '9', 'OA 3', 1), ('¿Cuánto es 20% de 450?', ['80', '85', '90', '95'], '90', 'OA 5', 2), ('Reduce los términos semejantes: 5x + 3x - 2x', ['6x', '5x', '7x', '8x'], '6x', 'OA 9', 2), ('Resuelve: 2x + 3 = 11', ['x = 3', 'x = 4', 'x = 5', 'x = 7'], 'x = 4', 'OA 10', 2), ('El ángulo complementario de 35° mide:', ['45°', '55°', '65°', '145°'], '55°', 'OA 16', 2), ('Factoriza: x² + 5x + 6', ['(x+1)(x+6)', '(x+2)(x+3)', '(x-2)(x-3)', '(x+5)(x+1)'], '(x+2)(x+3)', 'OA 11', 3), ('¿Cuánto es (2³)²?', ['12', '32', '64', '36'], '64', 'OA 2', 3), ('El promedio de 4, 8, 6 y 10 es:', ['6', '7', '8', '9'], '7', 'OA 23', 2), ('Un cuadrado de lado 5 cm tiene área:', ['20 cm²', '25 cm²', '10 cm²', '15 cm²'], '25 cm²', 'OA 18', 1), ('Si 3 libros cuestan $6.000, ¿cuánto cuestan 5 libros?', ['$8.000', '$9.000', '$10.000', '$12.000'], '$10.000', 'OA 6', 2), ('El máximo común divisor de 12 y 18 es:', ['2', '3', '6', '36'], '6', 'OA 3', 1)]), ('Lenguaje', 'BASICA_8', 'Diagnóstico Lenguaje 8° Básica', 'diagnostico', [("En el texto: 'A pesar de la lluvia, el partido continuó', la conjunción subrayada expresa:", ['causa', 'consecuencia', 'oposición', 'condición'], 'oposición', 'OA 25', 1), ("Sinónimo de 'abundante':", ['escaso', 'copioso', 'raquítico', 'escaso'], 'copioso', 'OA 20', 1), ('¿Cuál es el propósito de un texto instructivo?', ['Entretener', 'Indicar pasos a seguir', 'Opinar', 'Narrar hechos'], 'Indicar pasos a seguir', 'OA 4', 2), ('Indica la palabra correctamente escrita:', ['hazienda', 'haser', 'hacer', 'hacerr'], 'hacer', 'OA 31', 1), ('En la comunicación, el receptor es:', ['quien emite el mensaje', 'quien lo decodifica', 'el canal', 'el código'], 'quien lo decodifica', 'OA 1', 2), ("'El viento susurraba entre los árboles' es un ejemplo de:", ['metáfora', 'personificación', 'hipérbole', 'símil'], 'personificación', 'OA 29', 2), ('La idea principal de un párrafo se encuentra generalmente:', ['al final siempre', 'al inicio o desarrollándose en el texto', 'en el título', 'nunca se explicita'], 'al inicio o desarrollándose en el texto', 'OA 7', 2), ('¿Qué conector indica consecuencia?', ['aunque', 'por lo tanto', 'sin embargo', 'mientras'], 'por lo tanto', 'OA 25', 2), ('El texto narrativo se caracteriza por:', ['presentar datos y gráficos', 'contar hechos reales o ficticios', 'dar instrucciones', 'definir conceptos'], 'contar hechos reales o ficticios', 'OA 3', 1), ('Palabra aguda correctamente acentuada:', ['rapido', 'canción', 'facil', 'habia'], 'canción', 'OA 31', 2), ('Inferir significa:', ['repetir lo que dice el texto', 'deducir información no explícita', 'copiar una cita', 'resumir el título'], 'deducir información no explícita', 'OA 8', 3), ('¿Cuál es el elemento que da las coordenadas de tiempo y lugar en un cuento?', ['el tema', 'la ambientación', 'el estilo', 'el narrador'], 'la ambientación', 'OA 28', 2)]), ('Matematica', 'MEDIA_4', 'PAES Matemática M1 — Simulacro 1', 'paes', [('¿Cuál es el 15% de 200?', ['20', '25', '30', '35'], '30', 'OA 1', 1), ('Si f(x) = 2x + 1, entonces f(3) =', ['5', '6', '7', '9'], '7', 'OA 2 (Media)', 1), ('La pendiente de la recta y = 3x - 4 es:', ['-4', '3', '4', '1/3'], '3', 'OA 5 (Media)', 2), ('Desarrolla: (x + 2)²', ['x² + 4', 'x² + 4x + 4', 'x² + 2x + 4', 'x² - 4x + 4'], 'x² + 4x + 4', 'OA 8 (Media)', 2), ('Las soluciones de x² - 5x + 6 = 0 son:', ['1 y 6', '2 y 3', '-2 y -3', '5 y 1'], '2 y 3', 'OA 9 (Media)', 2), ('Un triángulo rectángulo tiene catetos 3 y 4. La hipotenusa mide:', ['5', '6', '7', '12'], '5', 'OA 12 (Media)', 1), ('Si sen α = 1/2, entonces α podría medir:', ['30°', '45°', '60°', '90°'], '30°', 'OA 13 (Media)', 2), ('Al lanzar un dado, la probabilidad de obtener un número par es:', ['1/6', '1/3', '1/2', '2/3'], '1/2', 'OA 30 (Media)', 2), ('¿Cuánto es 2⁻³?', ['-8', '-6', '1/8', '1/6'], '1/8', 'OA 2', 2), ('El promedio de 10, 20 y 30 es:', ['15', '20', '25', '30'], '20', 'OA 20 (Media)', 1), ('Si una máquina produce 120 piezas en 4 horas, ¿cuántas produce en 10 horas?', ['250', '280', '300', '320'], '300', 'OA 3', 2), ('El resultado de √(16 · 25) es:', ['20', '40', '9', '41'], '20', 'OA 4', 3)]), ('Lenguaje', 'MEDIA_4', 'PAES Lenguaje — Simulacro 1', 'paes', [('La tesis de un texto argumentativo es:', ['un dato estadístico', 'la postura que se defiende', 'un ejemplo', 'una cita textual'], 'la postura que se defiende', 'OA 28 (Media)', 2), ('Conector que expresa oposición:', ['además', 'en consecuencia', 'no obstante', 'es decir'], 'no obstante', 'OA 26 (Media)', 1), ('Inferir es:', ['leer entre líneas', 'repetir el texto', 'copiar palabras', 'traducir'], 'leer entre líneas', 'OA 8 (Media)', 2), ("'Realizar' pertenece a un registro:", ['coloquial', 'formal', 'técnico', 'poético'], 'formal', 'OA 32 (Media)', 2), ('Indica la palabra correctamente escrita:', ['adevinar', 'huviera', 'caber', 'escrivir'], 'caber', 'OA 31 (Media)', 2), ('El propósito de un texto expositivo es:', ['opinar', 'narrar', 'informar y explicar', 'entretener'], 'informar y explicar', 'OA 6 (Media)', 1), ('Una metáfora consiste en:', ["comparar con 'como'", 'sustituir un término por otro por semejanza', 'exagerar', 'repetir sonidos'], 'sustituir un término por otro por semejanza', 'OA 29 (Media)', 2), ('La coherencia textual se logra mediante:', ['oraciones cortas', 'conectores y orden lógico de ideas', 'palabras difíciles', 'títulos llamativos'], 'conectores y orden lógico de ideas', 'OA 26 (Media)', 3), ('Una síntesis debe:', ['copiar el texto completo', 'expresar las ideas esenciales con palabras propias', 'agregar opinión personal', 'enumerar párrafos'], 'expresar las ideas esenciales con palabras propias', 'OA 10 (Media)', 2), ('La intención del autor se refiere a:', ['qué quería lograr con su texto', 'dónde nació', 'su profesión', 'el año de publicación'], 'qué quería lograr con su texto', 'OA 7 (Media)', 2), ("'Haber' y 'a ver' se diferencian en que:", ['son iguales', "'haber' es verbo y 'a ver' expresa observación", "'a ver' es verbo", 'ninguna es correcta'], "'haber' es verbo y 'a ver' expresa observación", 'OA 31 (Media)', 3), ('En un debate, un argumento de autoridad apela a:', ['las emociones', 'opiniones de expertos o fuentes confiables', 'datos numéricos', 'el humor'], 'opiniones de expertos o fuentes confiables', 'OA 30 (Media)', 3)])]
    created = 0
    for subject_name, level, title, kind, qs in bank:
        if db.query(Exam).filter_by(title=title).first():
            continue
        subj = db.query(Subject).filter_by(name=subject_name, level=level).first()
        if not subj:
            subj = Subject(name=subject_name, level=level)
            db.add(subj); db.commit(); db.refresh(subj)
        exam = Exam(subject_id=subj.id, level=level, title=title,
                    time_limit_min=45 if kind == "diagnostico" else 90,
                    is_simulation=True, kind=kind)
        db.add(exam); db.commit(); db.refresh(exam)
        for i, (prompt, options, answer, oa, diff) in enumerate(qs):
            db.add(Question(exam_id=exam.id, prompt=prompt, options=options,
                            answer=answer, skill=oa, oa=oa, difficulty=diff,
                            order_idx=i))
        created += 1
    db.commit()
    return {"exams_created": created}
