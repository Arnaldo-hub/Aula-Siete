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

MIGRACION_EMAIL_ADMIN = ("admin@aulasite.cl", "admin@aulasiete.cl")

def _migrar_email_admin(db: Session):
    """Alias del admin: la cuenta vieja (aulasite.cl) pasa a ser aulasiete.cl."""
    viejo, nuevo = MIGRACION_EMAIL_ADMIN
    if db.query(models.User).filter_by(email=nuevo).first():
        return
    u = db.query(models.User).filter_by(email=viejo).first()
    if u:
        u.email = nuevo
        db.commit()

def run_seed(db: Session) -> dict:
    _migrar_email_admin(db)
    admin = _user(db, "admin@aulasiete.cl", "Admin Aula Siete", "admin")
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


MEDIA_BANK = []
_historia_media = [
    ('¿Qué conflicto bélico enfrentó a Chile contra Bolivia y Perú entre 1879 y 1884?', ['Guerra del Pacífico', 'Guerra de independencia', 'Guerra civil chilena', 'Guerra hispano-americana'], 'Guerra del Pacífico', 'OA 1', 1),
    ('La Constitución chilena de 1925 estableció:', ['el parlamentarismo', 'la presidencia de la República con separación de poderes', 'el monopolio del Congreso', 'el voto calificado'], 'la presidencia de la República con separación de poderes', 'OA 2', 2),
    ('La crisis económica mundial de 1929 afectó a Chile principalmente por:', ['la caída del precio del salitre y el cobre', 'el fin de la agricultura', 'la invasión extranjera', 'el cierre de los bancos europeos en Chile'], 'la caída del precio del salitre y el cobre', 'OA 3', 2),
    ('El Frente Popular (1938) se caracterizó por:', ['el regreso de los militares', 'reformas sociales y el triunfo electoral de la centroizquierda', 'la abolición del Congreso', 'la privatización total'], 'reformas sociales y el triunfo electoral de la centroizquierda', 'OA 4', 2),
    ('El proceso de industrialización chilena del siglo XX concentró la producción en:', ['las regiones del norte grande', 'el área metropolitana de Santiago y Valparaíso', 'la Araucanía', 'Chiloé'], 'el área metropolitana de Santiago y Valparaíso', 'OA 5', 2),
    ('La reforma agraria de los años 1960-1973 buscó:', ['aumentar los latifundios', 'redistribuir la tierra y modernizar el campo', 'eliminar el trabajo rural', 'nacionalizar las mineras del cobre únicamente'], 'redistribuir la tierra y modernizar el campo', 'OA 6', 2),
    ('La Guerra Fría fue:', ['un conflicto armado directo entre EE.UU. y la URSS', 'un enfrentamiento ideológico, político y económico sin guerra directa', 'una alianza militar mundial', 'una guerra comercial europea'], 'un enfrentamiento ideológico, político y económico sin guerra directa', 'OA 7', 1),
    ('La descolonización de África y Asia ocurrió principalmente:', ['en el siglo XIX', 'después de la Segunda Guerra Mundial', 'en el siglo XXI', 'durante la Primera Guerra Mundial'], 'después de la Segunda Guerra Mundial', 'OA 8', 2),
    ('El golpe de Estado de 1973 en Chile derrocó al gobierno de:', ['Eduardo Frei Montalva', 'Salvador Allende', 'Jorge Alessandri', 'Michelle Bachelet'], 'Salvador Allende', 'OA 9', 1),
    ('Durante la dictadura militar (1973-1990) se caracterizó por:', ['la expansión de los derechos políticos', 'violaciones a los derechos humanos y restricción de libertades', 'la descentralización plena', 'el fin de la censura'], 'violaciones a los derechos humanos y restricción de libertades', 'OA 10', 1),
    ('La transición a la democracia en Chile se consolidó con:', ['el plebiscito de 1988 y las elecciones de 1989', 'una nueva guerra civil', 'la intervención de la ONU', 'la monarquía parlamentaria'], 'el plebiscito de 1988 y las elecciones de 1989', 'OA 11', 2),
    ('La globalización económica se refiere a:', ['el aislamiento de los países', 'la creciente interdependencia comercial, financiera y cultural mundial', 'el retorno al trueque', 'la desaparición de las fronteras políticas'], 'la creciente interdependencia comercial, financiera y cultural mundial', 'OA 12', 2)]
_ciencias_media = [
    ('La estructura básica del átomo está formada por:', ['protones, neutrones y electrones', 'solo protones', 'moléculas y células', 'iones y átomos'], 'protones, neutrones y electrones', 'OA 1', 1),
    ('En la tabla periódica, los elementos se ordenan según:', ['su color', 'su número atómico', 'su densidad', 'su estado físico'], 'su número atómico', 'OA 2', 1),
    ('El enlace químico que comparte electrones entre átomos es el enlace:', ['iónico', 'metálico', 'covalente', 'hidrógeno'], 'covalente', 'OA 3', 2),
    ('La fotosíntesis es un proceso realizado por:', ['todos los seres vivos', 'plantas y algunos microorganismos, que transforman luz en energía química', 'solo animales', 'hongos únicamente'], 'plantas y algunos microorganismos, que transforman luz en energía química', 'OA 4', 1),
    ('La respiración celular ocurre en:', ['el núcleo', 'las mitocondrias', 'la clorofila', 'la pared celular'], 'las mitocondrias', 'OA 5', 2),
    ('La genética estudia:', ['la clasificación de seres vivos', 'la herencia y la variación de los genes', 'el clima', 'las rocas'], 'la herencia y la variación de los genes', 'OA 6', 1),
    ('La teoría de la evolución de Darwin propone que las especies cambian por:', ['selección natural', 'mutaciones voluntarias', 'el clima únicamente', 'la intervención humana siempre'], 'selección natural', 'OA 7', 2),
    ('En un ecosistema, la relación depredador-presa forma parte de:', ['las cadenas y redes tróficas', 'el ciclo del agua', 'la fotosíntesis', 'la lluvia ácida'], 'las cadenas y redes tróficas', 'OA 8', 1),
    ('La velocidad de un móvil se calcula como:', ['distancia × tiempo', 'distancia / tiempo', 'tiempo / distancia', 'masa × aceleración'], 'distancia / tiempo', 'OA 9', 1),
    ('La Segunda Ley de Newton indica que la fuerza es igual a:', ['masa × aceleración', 'masa / aceleración', 'peso × velocidad', 'energía / tiempo'], 'masa × aceleración', 'OA 10', 2),
    ('La energía cinética es la energía que posee un cuerpo por:', ['su posición', 'su movimiento', 'su temperatura', 'su masa en reposo'], 'su movimiento', 'OA 11', 1),
    ('El pH de una sustancia ácida es:', ['mayor que 7', 'igual a 7', 'menor que 7', 'exactamente 14'], 'menor que 7', 'OA 12', 2)]
_ingles_media = [
    ('Choose the correct form: "If it rains tomorrow, we ___ at home."', ['stay', 'will stay', 'stayed', 'staying'], 'will stay', 'OA 1', 2),
    ('The passive voice of "Shakespeare wrote Hamlet" is:', ['Hamlet was written by Shakespeare', 'Hamlet is written by Shakespeare', 'Hamlet wrote Shakespeare', 'Hamlet has written by Shakespeare'], 'Hamlet was written by Shakespeare', 'OA 2', 2),
    ("What does the modal verb 'must' express?", ['ability', 'obligation', 'possibility in the past', 'permission informal'], 'obligation', 'OA 3', 1),
    ('Select the correct reported speech: She said, "I am tired."', ['She said that she is tired', 'She said that she was tired', 'She said that I am tired', 'She said that she be tired'], 'She said that she was tired', 'OA 4', 3),
    ('"Although it was late, he continued working." The connector "although" expresses:', ['cause', 'contrast', 'addition', 'sequence'], 'contrast', 'OA 5', 2),
    ('Choose the word that best completes: "The ___ of the story was unexpected."', ['end', 'ending', 'ended', 'ends'], 'ending', 'OA 6', 2),
    ("What is the meaning of the phrasal verb 'look after'?", ['to search', 'to take care of', 'to watch TV', 'to find'], 'to take care of', 'OA 7', 2),
    ('Reading: "Anna has studied French for five years, but she has never visited France." What do we know about Anna?', ['She lives in France', 'She learned French but has not been to France', 'She hates French', 'She was born in France'], 'She learned French but has not been to France', 'OA 8', 3),
    ('Which sentence uses the present perfect correctly?', ['I have saw that movie', 'I have seen that movie', 'I has seen that movie', 'I seeing that movie'], 'I have seen that movie', 'OA 9', 2),
    ('The comparative of "intelligent" is:', ['intelligenter', 'more intelligent', 'most intelligent', 'intelligentest'], 'more intelligent', 'OA 10', 1),
    ("Choose the correct preposition: 'She is interested ___ science.'", ['in', 'on', 'at', 'for'], 'in', 'OA 11', 1),
    ("What does 'environment' mean?", ['a job interview', 'the natural world around us', 'a type of government', 'a school subject'], 'the natural world around us', 'OA 12', 1)]
for _lvl in ['MEDIA_1', 'MEDIA_2', 'MEDIA_3', 'MEDIA_4']:
    MEDIA_BANK.append(('Ciencias Naturales', _lvl, 'Diagnóstico Ciencias Naturales ' + _lvl[6] + '° Medio', 'diagnostico', _ciencias_media))
    MEDIA_BANK.append(('Historia', _lvl, 'Diagnóstico Historia y Cs. Sociales ' + _lvl[6] + '° Medio', 'diagnostico', _historia_media))
    MEDIA_BANK.append(('Ingles', _lvl, 'Diagnóstico Inglés ' + _lvl[6] + '° Medio', 'diagnostico', _ingles_media))


BASICA_BANK = []
_MAT = {
'BASICA_1': [
    ('5 + 7 =', ['11', '12', '13', '10'], '12', 'OA 6', 1),
    ('10 - 4 =', ['5', '6', '7', '8'], '6', 'OA 7', 1),
    ('¿Qué número sigue? 3, 4, 5, ...', ['6', '7', '8', '5'], '6', 'OA 8', 1),
    ('¿Cuál es el número mayor?', ['8', '3', '9', '6'], '9', 'OA 4', 1),
    ('10 + 6 =', ['16', '15', '17', '14'], '16', 'OA 6', 1),
    ('La figura que tiene 3 lados es el:', ['círculo', 'triángulo', 'cuadrado', 'rectángulo'], 'triángulo', 'OA 17', 1),
    ('¿Cuántas decenas hay en 30?', ['2', '3', '4', '5'], '3', 'OA 5', 2),
    ('9 + 8 =', ['16', '17', '18', '15'], '17', 'OA 6', 1),
    ('¿Qué número es mayor que 15?', ['12', '14', '18', '10'], '18', 'OA 4', 1),
    ('2 decenas y 5 unidades forman el número:', ['25', '52', '20', '7'], '25', 'OA 5', 2),
    ('Tienes 4 manzanas y comes 1. ¿Cuántas quedan?', ['2', '3', '4', '5'], '3', 'OA 7', 1),
    ('¿Qué número sigue? 2, 4, 6, ...', ['7', '8', '9', '10'], '8', 'OA 8', 2)],
'BASICA_2': [
    ('23 + 14 =', ['37', '36', '38', '47'], '37', 'OA 6', 1),
    ('50 - 25 =', ['20', '25', '30', '35'], '25', 'OA 7', 1),
    ('3 × 4 =', ['7', '10', '12', '14'], '12', 'OA 9', 1),
    ('La mitad de 10 es:', ['4', '5', '6', '20'], '5', 'OA 10', 2),
    ('¿Qué número sigue? 5, 10, 15, ...', ['16', '18', '20', '25'], '20', 'OA 8', 1),
    ('7 × 2 =', ['14', '12', '9', '16'], '14', 'OA 9', 1),
    ('La figura con 4 lados iguales es el:', ['triángulo', 'cuadrado', 'círculo', 'hexágono'], 'cuadrado', 'OA 17', 1),
    ('100 es igual a ___ decenas.', ['1', '10', '100', '5'], '10', 'OA 5', 2),
    ('45 + 9 =', ['54', '55', '53', '64'], '54', 'OA 6', 2),
    ('El doble de 8 es:', ['12', '16', '4', '14'], '16', 'OA 10', 2),
    ('3 × 10 =', ['13', '30', '3', '33'], '30', 'OA 9', 1),
    ('60 - 18 =', ['42', '32', '52', '48'], '42', 'OA 7', 2)],
'BASICA_3': [
    ('7 × 6 =', ['42', '36', '48', '40'], '42', 'OA 9', 1),
    ('81 ÷ 9 =', ['8', '9', '7', '10'], '9', 'OA 10', 1),
    ('300 + 450 =', ['650', '750', '550', '700'], '750', 'OA 6', 1),
    ('La fracción 1/2 representa:', ['un cuarto', 'la mitad', 'un tercio', 'el doble'], 'la mitad', 'OA 11', 1),
    ('El perímetro de un cuadrado de lado 4 cm es:', ['8 cm', '12 cm', '16 cm', '20 cm'], '16 cm', 'OA 18', 2),
    ('9 × 4 =', ['32', '36', '45', '40'], '36', 'OA 9', 1),
    ('Redondea 47 a la decena más cercana:', ['40', '45', '50', '47'], '50', 'OA 3', 2),
    ('7 docenas son ___ unidades.', ['7', '72', '84', '14'], '84', 'OA 10', 3),
    ('240 ÷ 6 =', ['40', '30', '60', '24'], '40', 'OA 10', 2),
    ('¿Cuál es el número mayor?', ['999', '1000', '909', '990'], '1000', 'OA 4', 1),
    ('3/4 es mayor que:', ['1/4', '3/4', '1', '2/2'], '1/4', 'OA 11', 2),
    ('8 cajas con 12 lápices cada una. ¿Cuántos lápices hay?', ['20', '96', '84', '88'], '96', 'OA 12', 2)],
'BASICA_4': [
    ('23 × 4 =', ['82', '92', '72', '96'], '92', 'OA 9', 1),
    ('144 ÷ 12 =', ['10', '11', '12', '14'], '12', 'OA 10', 2),
    ('2/4 equivale a:', ['1/2', '1/4', '2/2', '3/4'], '1/2', 'OA 11', 1),
    ('0,5 es igual a:', ['1/2', '1/4', '1/10', '2/3'], '1/2', 'OA 13', 2),
    ('El área de un rectángulo de 5 × 3 es:', ['8', '15', '16', '12'], '15', 'OA 18', 1),
    ('3 metros son ___ centímetros.', ['30', '300', '3000', '3'], '300', 'OA 16', 1),
    ('25 × 5 =', ['100', '115', '125', '150'], '125', 'OA 9', 2),
    ('La suma de los ángulos internos de un triángulo es:', ['90°', '180°', '270°', '360°'], '180°', 'OA 17', 2),
    ('El promedio de 4, 6 y 8 es:', ['5', '6', '7', '8'], '6', 'OA 23', 2),
    ('720 ÷ 8 =', ['80', '90', '70', '85'], '90', 'OA 10', 2),
    ('1/3 + 1/3 =', ['1/6', '2/3', '2/6', '1'], '2/3', 'OA 11', 2),
    ('x + 15 = 40. Entonces x =', ['20', '25', '30', '35'], '25', 'OA 14', 3)],
'BASICA_5': [
    ('1/2 + 1/4 =', ['2/4', '3/4', '1/2', '1/4'], '3/4', 'OA 11', 2),
    ('0,75 equivale a:', ['3/4', '1/2', '7/5', '2/3'], '3/4', 'OA 13', 2),
    ('¿Cuál conjunto contiene todos los divisores de 12?', ['1, 2, 3, 4, 6, 12', '1 y 12', '2, 4 y 6', '1, 3 y 5'], '1, 2, 3, 4, 6, 12', 'OA 3', 2),
    ('El mínimo común múltiplo de 4 y 6 es:', ['8', '12', '24', '10'], '12', 'OA 4', 2),
    ('3² × 3³ =', ['3⁵', '3⁶', '9⁵', '6⁵'], '3⁵', 'OA 2', 3),
    ('20% de 150 =', ['15', '20', '30', '45'], '30', 'OA 12', 2),
    ('El volumen de un cubo de arista 3 es:', ['6', '9', '27', '18'], '27', 'OA 19', 2),
    ('7,25 + 3,5 =', ['10,30', '10,75', '11,30', '10,25'], '10,75', 'OA 13', 2),
    ('4/5 de 100 =', ['20', '40', '80', '60'], '80', 'OA 11', 3),
    ('¿Cuál de estos números es primo?', ['9', '11', '15', '21'], '11', 'OA 3', 1),
    ('2/3 ÷ 4/6 =', ['1', '8/12', '1/2', '2'], '1', 'OA 11', 3),
    ('El perímetro de un rectángulo de 8 × 5 es:', ['13', '26', '40', '25'], '26', 'OA 18', 2)],
'BASICA_6': [
    ('La razón entre 12 y 18 simplificada es:', ['2/3', '3/2', '4/6', '6/9'], '2/3', 'OA 5', 2),
    ('35% de 200 =', ['35', '60', '70', '80'], '70', 'OA 12', 2),
    ('(-3) + 7 =', ['4', '10', '-4', '-10'], '4', 'OA 1', 1),
    ('Si x = 4, ¿cuánto vale 3x - 2?', ['10', '12', '14', '8'], '10', 'OA 9', 2),
    ('El área de un triángulo de base 10 y altura 6 es:', ['16', '30', '60', '32'], '30', 'OA 18', 2),
    ('2,5 km son ___ metros.', ['25', '250', '2500', '25000'], '2500', 'OA 16', 2),
    ('El máximo común divisor de 18 y 24 es:', ['3', '6', '9', '12'], '6', 'OA 4', 2),
    ('3/4 ÷ 2/8 =', ['3', '3/2', '1/3', '12/16'], '3', 'OA 11', 3),
    ('2³ × 5 - 4 =', ['36', '40', '16', '30'], '36', 'OA 2', 3),
    ('Si 3/5 = x/15, entonces x =', ['3', '6', '9', '15'], '9', 'OA 6', 3),
    ('-8 - (-3) =', ['-11', '-5', '5', '11'], '-5', 'OA 1', 3),
    ('El promedio de 10, 20, 30 y 40 es:', ['20', '25', '30', '40'], '25', 'OA 23', 2)]}
_LENG = {
'BASICA_1': [
    ('Las vocales son:', ['a, e, i, o, u', 'b, c, d, f, g', 'a, b, c, d, e', 'm, n, ñ, o, p'], 'a, e, i, o, u', 'OA 3', 1),
    ('"Perro" tiene ___ sílabas.', ['1', '2', '3', '4'], '2', 'OA 4', 1),
    ('¿Cuál palabra empieza igual que "gato"?', ['gallo', 'perro', 'casa', 'luna'], 'gallo', 'OA 3', 1),
    ('Palabra que rima con "luna":', ['cuna', 'pan', 'sol', 'mesa'], 'cuna', 'OA 7', 1),
    ('"El ___ come." Elige el sustantivo.', ['niño', 'rápido', 'grande', 'azul'], 'niño', 'OA 5', 1),
    ('¿Cuántas letras tiene "casa"?', ['3', '4', '5', '6'], '4', 'OA 4', 1),
    ('"La ___ es roja." Elige la palabra adecuada.', ['manzana', 'correr', 'verde', 'saltar'], 'manzana', 'OA 5', 1),
    ('Una oración es:', ['un conjunto de palabras con sentido completo', 'una sola letra', 'un número', 'un dibujo'], 'un conjunto de palabras con sentido completo', 'OA 2', 2),
    ('"Gato" es un:', ['animal', 'fruta', 'color', 'número'], 'animal', 'OA 5', 1),
    ('¿Cuál de estas palabras es un nombre propio?', ['perro', 'Chile', 'casa', 'lápiz'], 'Chile', 'OA 5', 2),
    ('¿Cuál palabra es la más larga?', ['sol', 'mesa', 'uvas', 'abecedario'], 'abecedario', 'OA 4', 1),
    ('En "mesa", la letra que suena /m/ es:', ['s', 'm', 'e', 'a'], 'm', 'OA 3', 2)],
'BASICA_2': [
    ('Sinónimo de "feliz":', ['triste', 'contento', 'enojado', 'cansado'], 'contento', 'OA 8', 1),
    ('Antónimo de "grande":', ['enorme', 'gigante', 'pequeño', 'alto'], 'pequeño', 'OA 8', 1),
    ('"Elefante" se separa en sílabas:', ['e-le-fan-te', 'el-efa-n-te', 'ele-fan-te', 'e-lef-ante'], 'e-le-fan-te', 'OA 4', 1),
    ('Palabra escrita correctamente con "qu":', ['queso', 'keso', 'kasa', 'kilo'], 'queso', 'OA 12', 1),
    ('¿Cuál es una oración completa?', ['El perro grande', 'El perro ladra.', 'Ladrando el', 'Perro el'], 'El perro ladra.', 'OA 2', 2),
    ('"La niña ___ alta."', ['es', 'son', 'están', 'eran'], 'es', 'OA 9', 2),
    ('¿Qué signo va al final de una pregunta?', ['.', ',', '?', '!'], '?', 'OA 10', 1),
    ('"Médico" es una palabra:', ['aguda', 'llana', 'esdrújula', 'sin tilde'], 'esdrújula', 'OA 11', 2),
    ('"Brillante" en "el sol brillante" es un:', ['adjetivo', 'verbo', 'sustantivo', 'artículo'], 'adjetivo', 'OA 9', 2),
    ('¿Cuál palabra lleva tilde?', ['mesa', 'lápiz', 'casa', 'perro'], 'lápiz', 'OA 11', 1),
    ('Un cuento es un texto:', ['narrativo', 'instructivo', 'publicitario', 'científico'], 'narrativo', 'OA 14', 2),
    ('"¿Cuántos años tienes?" es:', ['una pregunta', 'un comando', 'una exclamación', 'un saludo'], 'una pregunta', 'OA 2', 1)],
'BASICA_3': [
    ('Sinónimo de "rápido":', ['veloz', 'lento', 'grande', 'fuerte'], 'veloz', 'OA 8', 1),
    ('"Había" se escribe con:', ['solo b', 'h y b', 'h y v', 'solo h'], 'h y b', 'OA 13', 2),
    ('Palabra aguda:', ['árbol', 'canción', 'lápiz', 'médico'], 'canción', 'OA 11', 2),
    ('El plural de "pez" es:', ['pezes', 'peces', 'pezs', 'pecesos'], 'peces', 'OA 6', 2),
    ('"Ayer comí pasta" está en tiempo:', ['presente', 'pasado', 'futuro', 'condicional'], 'pasado', 'OA 9', 1),
    ('En una noticia, el titular sirve para:', ['resumir la noticia principal', 'decorar la página', 'dar la opinión del autor', 'confundir al lector'], 'resumir la noticia principal', 'OA 16', 2),
    ('"Aunque llovía, salimos." El conector expresa:', ['oposición', 'causa', 'consecuencia', 'adición'], 'oposición', 'OA 21', 2),
    ('Diminutivo de "perro":', ['perrito', 'perrazo', 'perrero', 'perris'], 'perrito', 'OA 7', 1),
    ('Un párrafo es:', ['un grupo de oraciones sobre una misma idea', 'una palabra suelta', 'un título', 'un signo de puntuación'], 'un grupo de oraciones sobre una misma idea', 'OA 15', 2),
    ('"Escritor" pertenece a la familia de palabras de:', ['escribir', 'leer', 'libro', 'papel'], 'escribir', 'OA 7', 2),
    ('¿Cuál de estas palabras es un verbo?', ['correr', 'bonito', 'mesa', 'rápido'], 'correr', 'OA 9', 1),
    ('Polisemia significa que una palabra:', ['se escribe igual y tiene varios significados', 'rima con otra', 'es sinónima de otra', 'es antónima de otra'], 'se escribe igual y tiene varios significados', 'OA 8', 3)],
'BASICA_4': [
    ('Texto que narra hechos reales o imaginarios:', ['narrativo', 'expositivo', 'argumentativo', 'publicitario'], 'narrativo', 'OA 14', 1),
    ('"Las estrellas bailan en el cielo" es una:', ['personificación', 'comparación', 'enumeración', 'definición'], 'personificación', 'OA 17', 2),
    ('"Lunar" pertenece a la familia de palabras de:', ['luna', 'sol', 'mar', 'nube'], 'luna', 'OA 7', 2),
    ('Palabras homófonas suenan:', ['igual y se escriben distinto', 'distinto y se escriben igual', 'igual y se escriben igual', 'ninguna de las anteriores'], 'igual y se escriben distinto', 'OA 8', 2),
    ('En "Los niños juegan en el patio", el sujeto es:', ['Los niños', 'juegan', 'el patio', 'en el'], 'Los niños', 'OA 10', 2),
    ('La idea principal de un texto es:', ['la idea más importante que resume el contenido', 'la primera palabra', 'siempre el título', 'una cita textual'], 'la idea más importante que resume el contenido', 'OA 15', 2),
    ('Palabra con diptongo:', ['puerta', 'país', 'leer', 'caos'], 'puerta', 'OA 11', 3),
    ('"Sin embargo" es un conector de:', ['oposición', 'adición', 'tiempo', 'lugar'], 'oposición', 'OA 21', 2),
    ('¿Qué texto entrega instrucciones paso a paso?', ['una receta de cocina', 'un cuento', 'un poema', 'un anuncio'], 'una receta de cocina', 'OA 14', 1),
    ('"Relámpago" es una palabra:', ['esdrújula', 'aguda', 'llana', 'sin tilde'], 'esdrújula', 'OA 11', 2),
    ('La tilde de "sí" (afirmación) se llama tilde:', ['diacrítica', 'prosódica', 'enfática', 'ninguna'], 'diacrítica', 'OA 13', 3),
    ('Un diccionario sirve para:', ['buscar el significado de las palabras', 'contar historias', 'hacer cálculos', 'dibujar'], 'buscar el significado de las palabras', 'OA 18', 1)],
'BASICA_5': [
    ('El propósito de un texto argumentativo es:', ['convencer con razones', 'entretener', 'narrar sucesos', 'describir paisajes'], 'convencer con razones', 'OA 24', 2),
    ('Inferir significa:', ['sacar conclusiones de lo que se lee', 'copiar el texto', 'traducirlo', 'subrayarlo'], 'sacar conclusiones de lo que se lee', 'OA 16', 2),
    ('"Por consiguiente" indica:', ['consecuencia', 'causa', 'ejemplo', 'tiempo'], 'consecuencia', 'OA 21', 2),
    ('¿Cuál frase pertenece a un registro formal?', ['¿Cómo está usted?', '¿Cómo andai?', '¡Qué onda!', '¿Cómo estay?'], '¿Cómo está usted?', 'OA 23', 2),
    ('"Haber" (de "hay que estudiar") se escribe con:', ['v', 'b', 'h y v', 'h y b'], 'h y b', 'OA 13', 3),
    ('En "El libro que compré ayer es bueno", la parte "que compré ayer" es una oración:', ['subordinada', 'coordinada', 'principal', 'exclamativa'], 'subordinada', 'OA 10', 3),
    ('Sinónimo de "iniciar":', ['comenzar', 'terminar', 'seguir', 'dejar'], 'comenzar', 'OA 8', 1),
    ('Un texto coherente significa que:', ['las ideas se relacionan con orden y sentido', 'todas las oraciones son cortas', 'hay muchos adjetivos', 'el texto es muy largo'], 'las ideas se relacionan con orden y sentido', 'OA 21', 2),
    ('"Prudente" es un adjetivo que indica una:', ['cualidad', 'acción', 'lugar', 'tiempo'], 'cualidad', 'OA 9', 2),
    ('El texto expositivo busca:', ['informar y explicar', 'emocionar', 'vender un producto', 'narrar'], 'informar y explicar', 'OA 19', 1),
    ('"Ella vive ___ de su familia."', ['aparte', 'a parte', 'ambas sirven', 'ninguna sirve'], 'aparte', 'OA 13', 3),
    ('Paráfrasis es:', ['expresar una idea con otras palabras', 'copiar textualmente', 'resumir en una palabra', 'traducir a otro idioma'], 'expresar una idea con otras palabras', 'OA 16', 3)],
'BASICA_6': [
    ('El narrador que conoce los pensamientos de todos los personajes es:', ['omnisciente', 'protagonista', 'observador', 'lector'], 'omnisciente', 'OA 18', 2),
    ('"Tu sonrisa es un sol" es una:', ['metáfora', 'hipérbole', 'sinécdoque', 'metonimia'], 'metáfora', 'OA 17', 2),
    ('"Compró un Toyota" en lugar de "un auto" es una:', ['metonimia', 'metáfora', 'comparación', 'ironía'], 'metonimia', 'OA 17', 3),
    ('Los elementos de la comunicación son:', ['emisor, mensaje, receptor, código y canal', 'solo emisor y receptor', 'título y autor', 'verbo y sujeto'], 'emisor, mensaje, receptor, código y canal', 'OA 1', 1),
    ('Texto que defiende una tesis con argumentos:', ['argumentativo', 'poético', 'narrativo', 'instructivo'], 'argumentativo', 'OA 24', 1),
    ('"Antes de que llegaras, yo ya había salido" es una oración:', ['subordinada', 'yuxtapuesta', 'coordinada copulativa', 'exclamativa'], 'subordinada', 'OA 10', 3),
    ('La función poética del lenguaje se centra en:', ['el mensaje en sí', 'el emisor', 'el receptor', 'el canal'], 'el mensaje en sí', 'OA 1', 3),
    ('"Barro" (lodo) y "barro" (de barrer) son palabras:', ['homónimas', 'sinónimas', 'antónimas', 'parónimas'], 'homónimas', 'OA 8', 3),
    ('Un texto cohesivo utiliza:', ['conectores y referentes', 'solo oraciones largas', 'muchos signos de interrogación', 'mayúsculas siempre'], 'conectores y referentes', 'OA 21', 2),
    ('"A pesar de" expresa:', ['oposición o concesión', 'causa', 'finalidad', 'modo'], 'oposición o concesión', 'OA 21', 2),
    ('El estilo indirecto libre es propio de:', ['la narración literaria', 'el manual técnico', 'la factura', 'la receta de cocina'], 'la narración literaria', 'OA 18', 3),
    ('Resumir es:', ['expresar lo esencial de forma breve', 'copiar todo el texto', 'agregar opiniones', 'traducir el texto'], 'expresar lo esencial de forma breve', 'OA 16', 2)]}
for _lvl in ['BASICA_1', 'BASICA_2', 'BASICA_3', 'BASICA_4', 'BASICA_5', 'BASICA_6']:
    BASICA_BANK.append(('Matematica', _lvl, 'Diagnóstico Matemática ' + _lvl[7] + '° Básica', 'diagnostico', _MAT[_lvl]))
    BASICA_BANK.append(('Lenguaje', _lvl, 'Diagnóstico Lenguaje ' + _lvl[7] + '° Básica', 'diagnostico', _LENG[_lvl]))


def seed_banco_preguntas(db: Session) -> dict:
    """Banco de preguntas: diagnosticos por nivel y asignatura.
    NOTA: los codigos OA son aproximados segun el programa de estudio;
    verificarlos contra el temario oficial de Ayuda Mineduc antes de produccion."""
    from .models import Exam, Question, Subject
    bank = [
    ('Matematica', 'BASICA_8', 'Diagnóstico Matemática 8° Básica', 'diagnostico', [
        ('¿Cuál es el valor de 3 elevado a -2?', ['-9', '-6', '1/9', '1/6'], '1/9', 'OA 1', 1),
        ('¿Cuál es la raíz cuadrada de 81?', ['7', '8', '9', '18'], '9', 'OA 3', 1),
        ('¿Cuánto es 20% de 450?', ['80', '85', '90', '95'], '90', 'OA 5', 2),
        ('Reduce los términos semejantes: 5x + 3x - 2x', ['6x', '5x', '7x', '8x'], '6x', 'OA 9', 2),
        ('Resuelve: 2x + 3 = 11', ['x = 3', 'x = 4', 'x = 5', 'x = 7'], 'x = 4', 'OA 10', 2),
        ('El ángulo complementario de 35° mide:', ['45°', '55°', '65°', '145°'], '55°', 'OA 16', 2),
        ('Factoriza: x² + 5x + 6', ['(x+1)(x+6)', '(x+2)(x+3)', '(x-2)(x-3)', '(x+5)(x+1)'], '(x+2)(x+3)', 'OA 11', 3),
        ('¿Cuánto es (2³)²?', ['12', '32', '64', '36'], '64', 'OA 2', 3),
        ('El promedio de 4, 8, 6 y 10 es:', ['6', '7', '8', '9'], '7', 'OA 23', 2),
        ('Un cuadrado de lado 5 cm tiene área:', ['20 cm²', '25 cm²', '10 cm²', '15 cm²'], '25 cm²', 'OA 18', 1),
        ('Si 3 libros cuestan $6.000, ¿cuánto cuestan 5 libros?', ['$8.000', '$9.000', '$10.000', '$12.000'], '$10.000', 'OA 6', 2),
        ('El máximo común divisor de 12 y 18 es:', ['2', '3', '6', '36'], '6', 'OA 3', 1)]),
    ('Lenguaje', 'BASICA_8', 'Diagnóstico Lenguaje 8° Básica', 'diagnostico', [
        ("En el texto: 'A pesar de la lluvia, el partido continuó', la conjunción subrayada expresa:", ['causa', 'consecuencia', 'oposición', 'condición'], 'oposición', 'OA 25', 1),
        ("Sinónimo de 'abundante':", ['escaso', 'copioso', 'raquítico', 'escaso'], 'copioso', 'OA 20', 1),
        ('¿Cuál es el propósito de un texto instructivo?', ['Entretener', 'Indicar pasos a seguir', 'Opinar', 'Narrar hechos'], 'Indicar pasos a seguir', 'OA 4', 2),
        ('Indica la palabra correctamente escrita:', ['hazienda', 'haser', 'hacer', 'hacerr'], 'hacer', 'OA 31', 1),
        ('En la comunicación, el receptor es:', ['quien emite el mensaje', 'quien lo decodifica', 'el canal', 'el código'], 'quien lo decodifica', 'OA 1', 2),
        ("'El viento susurraba entre los árboles' es un ejemplo de:", ['metáfora', 'personificación', 'hipérbole', 'símil'], 'personificación', 'OA 29', 2),
        ('La idea principal de un párrafo se encuentra generalmente:', ['al final siempre', 'al inicio o desarrollándose en el texto', 'en el título', 'nunca se explicita'], 'al inicio o desarrollándose en el texto', 'OA 7', 2),
        ('¿Qué conector indica consecuencia?', ['aunque', 'por lo tanto', 'sin embargo', 'mientras'], 'por lo tanto', 'OA 25', 2),
        ('El texto narrativo se caracteriza por:', ['presentar datos y gráficos', 'contar hechos reales o ficticios', 'dar instrucciones', 'definir conceptos'], 'contar hechos reales o ficticios', 'OA 3', 1),
        ('Palabra aguda correctamente acentuada:', ['rapido', 'canción', 'facil', 'habia'], 'canción', 'OA 31', 2),
        ('Inferir significa:', ['repetir lo que dice el texto', 'deducir información no explícita', 'copiar una cita', 'resumir el título'], 'deducir información no explícita', 'OA 8', 3),
        ('¿Cuál es el elemento que da las coordenadas de tiempo y lugar en un cuento?', ['el tema', 'la ambientación', 'el estilo', 'el narrador'], 'la ambientación', 'OA 28', 2)]),
    ('Ciencias Naturales', 'BASICA_8', 'Diagnóstico Ciencias Naturales 8° Básica', 'diagnostico', [
        ('¿Qué partícula subatómica posee carga eléctrica negativa?', ['Protón', 'Neutrón', 'Electrón', 'Núcleo'], 'Electrón', 'OA 10', 1),
        ('La fotosíntesis es el proceso mediante el cual las plantas:', ['absorben agua del suelo', 'transforman luz en energía química', 'respiran oxígeno de noche', 'eliminan desechos'], 'transforman luz en energía química', 'OA 13', 1),
        ('Un cambio químico se caracteriza por:', ['cambiar de estado', 'formar una o más sustancias nuevas', 'cambiar de forma sin alterarse', 'disolverse en agua'], 'formar una o más sustancias nuevas', 'OA 12', 2),
        ('¿Cuál es la mezcla homogénea?', ['Arena y agua', 'Agua y sal disuelta', 'Aceite y agua', 'Agua y tierra'], 'Agua y sal disuelta', 'OA 11', 2),
        ('La fuerza con que la Tierra atrae a los cuerpos se denomina:', ['fricción', 'peso', 'gravedad', 'inercia'], 'gravedad', 'OA 14', 1),
        ('La densidad de un cuerpo de masa 100 g y volumen 25 cm³ es:', ['2 g/cm³', '4 g/cm³', '25 g/cm³', '0,25 g/cm³'], '4 g/cm³', 'OA 15', 3),
        ('El órgano donde se produce la mayor absorción de nutrientes es:', ['el estómago', 'el intestino delgado', 'el hígado', 'el páncreas'], 'el intestino delgado', 'OA 13', 2),
        ('En una cadena alimenticia, los productores son:', ['los consumidores', 'las plantas', 'los hongos', 'los depredadores'], 'las plantas', 'OA 14', 1),
        ('El sistema encargado de transportar oxígeno y nutrientes a las células es el:', ['respiratorio', 'digestivo', 'circulatorio', 'excretor'], 'circulatorio', 'OA 13', 1),
        ('El paso directo de sólido a gas se denomina:', ['evaporación', 'condensación', 'sublimación', 'fusión'], 'sublimación', 'OA 10', 2),
        ('El gas de efecto invernadero que aumenta por la quema de combustibles fósiles es:', ['el oxígeno', 'el nitrógeno', 'el dióxido de carbono', 'el hidrógeno'], 'el dióxido de carbono', 'OA 17', 2),
        ('La clasificación de los seres vivos en reinos, filos, clases, etc., se denomina:', ['ecología', 'taxonomía', 'anatomía', 'genética'], 'taxonomía', 'OA 14', 3)]),
    ('Historia', 'BASICA_8', 'Diagnóstico Historia y Ciencias Sociales 8° Básica', 'diagnostico', [
        ('La Guerra del Pacífico (1879-1884) enfrentó a Chile contra:', ['Argentina y Uruguay', 'Bolivia y Perú', 'Ecuador y Colombia', 'Brasil y Paraguay'], 'Bolivia y Perú', 'OA 11', 1),
        ('El héroe naval del combate de Iquique fue:', ["Bernardo O'Higgins", 'Arturo Prat', 'Manuel Bulnes', 'José Miguel Carrera'], 'Arturo Prat', 'OA 11', 1),
        ('La República Parlamentaria en Chile (1891-1925) se caracterizó por:', ['el predominio del Congreso sobre el Presidente', 'el gobierno de los militares', 'la abolición del Congreso', 'el voto de los extranjeros'], 'el predominio del Congreso sobre el Presidente', 'OA 12', 2),
        ('El primer presidente de la República Parlamentaria fue:', ['José Manuel Balmaceda', 'Jorge Montt', 'Federico Errázuriz', 'Germán Riesco'], 'Jorge Montt', 'OA 12', 3),
        ('El Tratado de Ancón (1883) puso fin a la guerra entre Chile y:', ['Bolivia', 'Perú', 'Argentina', 'España'], 'Perú', 'OA 11', 2),
        ('El recurso principal disputado en la zona norte antes de la Guerra del Pacífico fue:', ['el cobre', 'el salitre', 'el carbón', 'el petróleo'], 'el salitre', 'OA 11', 2),
        ('La Constitución de 1833 estableció en Chile un sistema:', ['parlamentario', 'presidencialista', 'comunal', 'monárquico'], 'presidencialista', 'OA 10', 3),
        ('Diego Portales fue una figura clave en:', ['la independencia de 1810', 'la organización del Estado en la República Conservadora', 'la Guerra del Pacífico', 'el Parlamentarismo'], 'la organización del Estado en la República Conservadora', 'OA 10', 2),
        ('La colonización de la Araucanía se desarrolló principalmente en:', ['el siglo XVII', 'el siglo XIX', 'el siglo XXI', 'la colonia temprana'], 'el siglo XIX', 'OA 11', 2),
        ('La construcción de ferrocarriles en Chile durante el siglo XIX contribuyó a:', ['aislar las regiones', 'integrar el territorio y dinamizar la economía', 'detener el comercio exterior', 'eliminar los puertos'], 'integrar el territorio y dinamizar la economía', 'OA 13', 3),
        ('La economía chilena a fines del siglo XIX se basó principalmente en:', ['la industria tecnológica', 'la exportación de salitre y cobre', 'el turismo', 'la pesca artesanal'], 'la exportación de salitre y cobre', 'OA 13', 2),
        ('La "cuestión social" a comienzos del siglo XX se refirió a:', ['la disputa con Argentina', 'las demandas de obreros y condiciones de vida', 'el conflicto con el Vaticano', 'la privatización de minas'], 'las demandas de obreros y condiciones de vida', 'OA 13', 3)]),
    ('Ingles', 'BASICA_8', 'Diagnóstico Inglés 8° Básica', 'diagnostico', [
        ('Choose the correct sentence:', ['She go to school every day', 'She goes to school every day', 'She going to school every day', 'She gone to school every day'], 'She goes to school every day', 'OA 1', 1),
        ("What is the past tense of 'eat'?", ['eated', 'ate', 'eaten', 'eating'], 'ate', 'OA 2', 1),
        ("'There ___ many students in the classroom.'", ['is', 'are', 'am', 'be'], 'are', 'OA 3', 2),
        ('Select the comparative form of "big":', ['bigger', 'more big', 'biggest', 'most big'], 'bigger', 'OA 4', 2),
        ('Which word is a synonym of "happy"?', ['sad', 'glad', 'angry', 'tired'], 'glad', 'OA 5', 1),
        ("Complete: 'I ___ watching TV right now.'", ['am', 'is', 'are', 'be'], 'am', 'OA 6', 2),
        ("What does 'library' mean?", ['a place to buy food', 'a place with books to read', 'a place to play sports', 'a hospital'], 'a place with books to read', 'OA 7', 1),
        ("Choose the correct question:", ['Where you live?', 'Where do you live?', 'Where does you live?', 'Where living you?'], 'Where do you live?', 'OA 8', 2),
        ("'My birthday is ___ May.'", ['in', 'on', 'at', 'by'], 'in', 'OA 9', 2),
        ("Select the plural of 'child':", ['childs', 'childes', 'children', 'childrens'], 'children', 'OA 10', 2),
        ("Complete: 'She has lived here ___ 2015.'", ['for', 'since', 'from', 'at'], 'since', 'OA 11', 3),
        ("What is the opposite of 'ancient'?", ['old', 'modern', 'historic', 'antique'], 'modern', 'OA 12', 1)]),
    ('Ciencias Naturales', 'BASICA_7', 'Diagnóstico Ciencias Naturales 7° Básica', 'diagnostico', [
        ('La unidad básica de los seres vivos es:', ['el tejido', 'la célula', 'el órgano', 'el sistema'], 'la célula', 'OA 5', 1),
        ('El organelo donde ocurre la respiración celular es:', ['el núcleo', 'la mitocondria', 'la clorofila', 'la membrana'], 'la mitocondria', 'OA 5', 2),
        ('Al cambiar de sólido a líquido, la materia:', ['gana energía y sus partículas se separan', 'pierde energía', 'no cambia', 'se convierte en gas'], 'gana energía y sus partículas se separan', 'OA 2', 2),
        ('Una disolución está formada por:', ['dos líquidos que no se mezclan', 'soluto y solvente', 'sólidos únicamente', 'gases únicamente'], 'soluto y solvente', 'OA 3', 1),
        ('En un ecosistema, los descomponedores son:', ['las plantas', 'animales carnívoros', 'bacterias y hongos', 'los insectos'], 'bacterias y hongos', 'OA 8', 2),
        ('El ciclo del agua incluye los procesos de:', ['evaporación, condensación y precipitación', 'fusión y solidificación', 'solo lluvia', 'combustión y oxidación'], 'evaporación, condensación y precipitación', 'OA 8', 1),
        ('La energía que posee un cuerpo en movimiento es energía:', ['potencial', 'química', 'cinética', 'térmica'], 'cinética', 'OA 6', 1),
        ('La fuerza de rozamiento actúa:', ['a favor del movimiento siempre', 'contra el movimiento', 'solo en el agua', 'en el vacío'], 'contra el movimiento', 'OA 6', 2),
        ('El planeta conocido como "el planeta rojo" es:', ['Júpiter', 'Saturno', 'Marte', 'Venus'], 'Marte', 'OA 1', 1),
        ('Los nutrientes que aportan energía al cuerpo son:', ['vitaminas y minerales', 'proteínas, carbohidratos y grasas', 'solo agua', 'fibras'], 'proteínas, carbohidratos y grasas', 'OA 7', 2),
        ('El aparato que permite intercambiar gases en el sistema respiratorio es:', ['la tráquea', 'el pulmón', 'la faringe', 'el bronquio'], 'el pulmón', 'OA 7', 1),
        ('Una transformación química es:', ['derramar agua', 'quemar papel', 'romper un vidrio', 'cortar una cuerda'], 'quemar papel', 'OA 4', 3)]),
    ('Historia', 'BASICA_7', 'Diagnóstico Historia y Ciencias Sociales 7° Básica', 'diagnostico', [
        ('Los pueblos originarios que habitaban Chile antes de la llegada de los españoles eran:', ['mapuche, aymara y rapa nui', 'incas y aztecas', 'mayas y olmecas', 'araucanos y gauchos'], 'mapuche, aymara y rapa nui', 'OA 1', 1),
        ('La conquista de Chile fue encabezada por:', ['Hernán Cortés', 'Pedro de Valdivia', 'Francisco Pizarro', 'Diego de Almagro'], 'Pedro de Valdivia', 'OA 2', 1),
        ('La guerra araucana enfrentó a españoles con:', ['los incas', 'el pueblo mapuche', 'los aymaras', 'colonos ingleses'], 'el pueblo mapuche', 'OA 2', 1),
        ('La encomienda era un sistema que:', ['otorgaba tierras a los indígenas', 'obligaba a los indígenas a trabajar a cambio de "protección"', 'pagaba sueldos a los obreros', 'eliminaba los impuestos'], 'obligaba a los indígenas a trabajar a cambio de "protección"', 'OA 3', 2),
        ('La mita era:', ['un impuesto en dinero', 'una cuota de trabajo forzado en minas y obrajes', 'una fiesta religiosa', 'un tipo de comercio'], 'una cuota de trabajo forzado en minas y obrajes', 'OA 3', 2),
        ('La sociedad colonial se organizaba en estamentos; el grupo con más privilegios era:', ['los mestizos', 'los españoles peninsulares', 'los indígenas', 'los esclavos'], 'los españoles peninsulares', 'OA 4', 2),
        ('La evangelización tuvo como objetivo principal:', ['enseñar oficios a los indígenas', 'convertir a los indígenas al catolicismo', 'organizar elecciones', 'comerciar con Asia'], 'convertir a los indígenas al catolicismo', 'OA 5', 1),
        ('El mestizaje fue:', ['la mezcla de españoles y africanos únicamente', 'la unión de españoles e indígenas que dio origen a una nueva sociedad', 'la separación de razas', 'una ley comercial'], 'la unión de españoles e indígenas que dio origen a una nueva sociedad', 'OA 6', 2),
        ('El principal recurso extraído en la minería colonial fue:', ['el petróleo', 'el oro y la plata', 'el cobre refinado', 'el carbón'], 'el oro y la plata', 'OA 7', 1),
        ('Las reducciones eran:', ['poblaciones indígenas organizadas por los españoles para control y evangelización', 'mercados de esclavos', 'fortalezas militares', 'rutas comerciales'], 'poblaciones indígenas organizadas por los españoles para control y evangelización', 'OA 5', 3),
        ('El comercio colonial estaba controlado por:', ['los pueblos indígenas', 'España, mediante monopolio y casas de contratación', 'Inglaterra', 'comerciantes mapuches'], 'España, mediante monopolio y casas de contratación', 'OA 7', 2),
        ('A finales del siglo XVIII, las ideas de libertad e independencia difundidas fueron:', ['el iluminismo y la independencia de Estados Unidos', 'el feudalismo', 'la ilustración japonesa', 'la revolución industrial únicamente'], 'el iluminismo y la independencia de Estados Unidos', 'OA 8', 3)]),
    ('Ingles', 'BASICA_7', 'Diagnóstico Inglés 7° Básica', 'diagnostico', [
        ('Complete: "My mother ___ a teacher."', ['am', 'is', 'are', 'be'], 'is', 'OA 1', 1),
        ('What color is the sun?', ['blue', 'yellow', 'green', 'black'], 'yellow', 'OA 2', 1),
        ('Choose the correct sentence:', ['They plays soccer', 'They play soccer', 'They playing soccer', 'They is play soccer'], 'They play soccer', 'OA 3', 2),
        ("What is the plural of 'dog'?", ['doges', 'dogs', 'doggies only', 'dog'], 'dogs', 'OA 4', 1),
        ("Complete: '___ you like ice cream?'", ['Do', 'Does', 'Is', 'Are'], 'Do', 'OA 5', 2),
        ('Which of these is a fruit?', ['carrot', 'apple', 'potato', 'onion'], 'apple', 'OA 6', 1),
        ('"Good morning" se usa para saludar:', ['en la noche', 'en la mañana', 'al despedirse', 'para dormir'], 'en la mañana', 'OA 7', 1),
        ('Select the correct possessive adjective: "This is ___ book." (yo)', ['my', 'your', 'his', 'their'], 'my', 'OA 8', 2),
        ('How do you say "gato" in English?', ['dog', 'cat', 'bird', 'mouse'], 'cat', 'OA 9', 1),
        ('Complete: "She ___ to school by bus every day."', ['go', 'goes', 'going', 'gone'], 'goes', 'OA 10', 2),
        ("What day comes after Monday?", ['Sunday', 'Tuesday', 'Friday', 'Saturday'], 'Tuesday', 'OA 11', 1),
        ('Choose the correct negative: "He ___ like vegetables."', ["don't", "doesn't", "isn't", "aren't"], "doesn't", 'OA 12', 3)]),
    ('Matematica', 'MEDIA_4', 'PAES Matemática M1 — Simulacro 1', 'paes', [
        ('¿Cuál es el 15% de 200?', ['20', '25', '30', '35'], '30', 'OA 1', 1),
        ('Si f(x) = 2x + 1, entonces f(3) =', ['5', '6', '7', '9'], '7', 'OA 2 (Media)', 1),
        ('La pendiente de la recta y = 3x - 4 es:', ['-4', '3', '4', '1/3'], '3', 'OA 5 (Media)', 2),
        ('Desarrolla: (x + 2)²', ['x² + 4', 'x² + 4x + 4', 'x² + 2x + 4', 'x² - 4x + 4'], 'x² + 4x + 4', 'OA 8 (Media)', 2),
        ('Las soluciones de x² - 5x + 6 = 0 son:', ['1 y 6', '2 y 3', '-2 y -3', '5 y 1'], '2 y 3', 'OA 9 (Media)', 2),
        ('Un triángulo rectángulo tiene catetos 3 y 4. La hipotenusa mide:', ['5', '6', '7', '12'], '5', 'OA 12 (Media)', 1),
        ('Si sen α = 1/2, entonces α podría medir:', ['30°', '45°', '60°', '90°'], '30°', 'OA 13 (Media)', 2),
        ('Al lanzar un dado, la probabilidad de obtener un número par es:', ['1/6', '1/3', '1/2', '2/3'], '1/2', 'OA 30 (Media)', 2),
        ('¿Cuánto es 2⁻³?', ['-8', '-6', '1/8', '1/6'], '1/8', 'OA 2', 2),
        ('El promedio de 10, 20 y 30 es:', ['15', '20', '25', '30'], '20', 'OA 20 (Media)', 1),
        ('Si una máquina produce 120 piezas en 4 horas, ¿cuántas produce en 10 horas?', ['250', '280', '300', '320'], '300', 'OA 3', 2),
        ('El resultado de √(16 · 25) es:', ['20', '40', '9', '41'], '20', 'OA 4', 3)]),
    ('Lenguaje', 'MEDIA_4', 'PAES Lenguaje — Simulacro 1', 'paes', [
        ('La tesis de un texto argumentativo es:', ['un dato estadístico', 'la postura que se defiende', 'un ejemplo', 'una cita textual'], 'la postura que se defiende', 'OA 28 (Media)', 2),
        ('Conector que expresa oposición:', ['además', 'en consecuencia', 'no obstante', 'es decir'], 'no obstante', 'OA 26 (Media)', 1),
        ('Inferir es:', ['leer entre líneas', 'repetir el texto', 'copiar palabras', 'traducir'], 'leer entre líneas', 'OA 8 (Media)', 2),
        ("'Realizar' pertenece a un registro:", ['coloquial', 'formal', 'técnico', 'poético'], 'formal', 'OA 32 (Media)', 2),
        ('Indica la palabra correctamente escrita:', ['adevinar', 'huviera', 'caber', 'escrivir'], 'caber', 'OA 31 (Media)', 2),
        ('El propósito de un texto expositivo es:', ['opinar', 'narrar', 'informar y explicar', 'entretener'], 'informar y explicar', 'OA 6 (Media)', 1),
        ('Una metáfora consiste en:', ["comparar con 'como'", 'sustituir un término por otro por semejanza', 'exagerar', 'repetir sonidos'], 'sustituir un término por otro por semejanza', 'OA 29 (Media)', 2),
        ('La coherencia textual se logra mediante:', ['oraciones cortas', 'conectores y orden lógico de ideas', 'palabras difíciles', 'títulos llamativos'], 'conectores y orden lógico de ideas', 'OA 26 (Media)', 3),
        ('Una síntesis debe:', ['copiar el texto completo', 'expresar las ideas esenciales con palabras propias', 'agregar opinión personal', 'enumerar párrafos'], 'expresar las ideas esenciales con palabras propias', 'OA 10 (Media)', 2),
        ('La intención del autor se refiere a:', ['qué quería lograr con su texto', 'dónde nació', 'su profesión', 'el año de publicación'], 'qué quería lograr con su texto', 'OA 7 (Media)', 2),
        ("'Haber' y 'a ver' se diferencian en que:", ['son iguales', "'haber' es verbo y 'a ver' expresa observación", "'a ver' es verbo", 'ninguna es correcta'], "'haber' es verbo y 'a ver' expresa observación", 'OA 31 (Media)', 3),
        ('En un debate, un argumento de autoridad apela a:', ['las emociones', 'opiniones de expertos o fuentes confiables', 'datos numéricos', 'el humor'], 'opiniones de expertos o fuentes confiables', 'OA 30 (Media)', 3)])]
    bank = bank + MEDIA_BANK + BASICA_BANK

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
