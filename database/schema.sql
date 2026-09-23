-- Aula Site — Esquema relacional
-- Rol de la plataforma: apoyo pedagógico (no certificación oficial).

CREATE TYPE user_role AS ENUM ('admin', 'profesor', 'apoderado', 'alumno');
CREATE TYPE level_code AS ENUM ('PREKINDER', 'KINDER', 'BASICA_1','BASICA_2','BASICA_3',
  'BASICA_4','BASICA_5','BASICA_6','BASICA_7','BASICA_8',
  'MEDIA_1','MEDIA_2','MEDIA_3','MEDIA_4');

CREATE TABLE users (
  id            BIGSERIAL PRIMARY KEY,
  email         CITEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name     TEXT NOT NULL,
  role          user_role NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE students (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT REFERENCES users(id) ON DELETE CASCADE,  -- cuenta alumno (opcional)
  guardian_id BIGINT NOT NULL REFERENCES users(id),           -- apoderado responsable
  run         TEXT UNIQUE,                                    -- RUN del menor (cifrado en app)
  birth_date  DATE,
  level       level_code NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE subjects (
  id   BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  level level_code NOT NULL
);

CREATE TABLE courses (
  id          BIGSERIAL PRIMARY KEY,
  subject_id  BIGINT NOT NULL REFERENCES subjects(id),
  level       level_code NOT NULL,
  teacher_id  BIGINT NOT NULL REFERENCES users(id),
  title       TEXT NOT NULL,
  description TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE enrollments (
  id         BIGSERIAL PRIMARY KEY,
  student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  course_id  BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE(student_id, course_id)
);

-- Planificación académica: año -> mes -> unidad -> sesión diaria
CREATE TABLE academic_plans (
  id         BIGSERIAL PRIMARY KEY,
  course_id  BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  year       INT NOT NULL,
  month      INT CHECK (month BETWEEN 1 AND 12),
  unit_title TEXT NOT NULL,
  objective  TEXT,
  order_idx  INT DEFAULT 0
);

CREATE TABLE lessons (
  id        BIGSERIAL PRIMARY KEY,
  plan_id   BIGINT NOT NULL REFERENCES academic_plans(id) ON DELETE CASCADE,
  title     TEXT NOT NULL,
  date      DATE NOT NULL,
  content   JSONB DEFAULT '{}'::jsonb,  -- material, links, actividades
  order_idx INT DEFAULT 0
);

-- Clases en vivo (videoconferencia)
CREATE TABLE live_classes (
  id         BIGSERIAL PRIMARY KEY,
  course_id  BIGINT NOT NULL REFERENCES courses(id),
  lesson_id  BIGINT REFERENCES lessons(id),
  title      TEXT NOT NULL,
  starts_at  TIMESTAMPTZ NOT NULL,
  ends_at    TIMESTAMPTZ NOT NULL,
  room_url   TEXT NOT NULL,             -- Jitsi/Daily
  status     TEXT DEFAULT 'scheduled'   -- scheduled | live | finished | cancelled
);

-- Biblioteca de grabaciones
CREATE TABLE recordings (
  id            BIGSERIAL PRIMARY KEY,
  live_class_id BIGINT REFERENCES live_classes(id),
  course_id     BIGINT NOT NULL REFERENCES courses(id),
  title         TEXT NOT NULL,
  duration_sec  INT,
  video_url     TEXT NOT NULL,          -- MinIO/S3 (firmado)
  is_public     BOOLEAN DEFAULT FALSE,
  uploaded_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE materials (
  id         BIGSERIAL PRIMARY KEY,
  course_id  BIGINT NOT NULL REFERENCES courses(id),
  lesson_id  BIGINT REFERENCES lessons(id),
  title      TEXT NOT NULL,
  file_url   TEXT NOT NULL,
  file_type  TEXT,                      -- pdf | docx | video | link
  uploaded_at TIMESTAMPTZ DEFAULT now()
);

-- Simulaciones de exámenes libres
CREATE TABLE exams (
  id          BIGSERIAL PRIMARY KEY,
  subject_id  BIGINT NOT NULL REFERENCES subjects(id),
  level       level_code NOT NULL,
  title       TEXT NOT NULL,
  time_limit_min INT NOT NULL DEFAULT 90,
  is_simulation BOOLEAN DEFAULT TRUE
);

CREATE TABLE questions (
  id       BIGSERIAL PRIMARY KEY,
  exam_id  BIGINT NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
  prompt   TEXT NOT NULL,
  options  JSONB NOT NULL,              -- ["A",...,"D"]
  answer   TEXT NOT NULL,               -- letra correcta
  skill    TEXT,                        -- OA asociado (currículum chileno)
  order_idx INT DEFAULT 0
);

CREATE TABLE exam_attempts (
  id         BIGSERIAL PRIMARY KEY,
  student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  exam_id    BIGINT NOT NULL REFERENCES exams(id),
  started_at TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ,
  score      NUMERIC(5,2),              -- porcentaje
  answers    JSONB DEFAULT '{}'::jsonb  -- {question_id: "letra"}
);

-- Progreso por lección (trazabilidad para apoderados)
CREATE TABLE progress (
  student_id BIGINT REFERENCES students(id) ON DELETE CASCADE,
  lesson_id  BIGINT REFERENCES lessons(id) ON DELETE CASCADE,
  status     TEXT DEFAULT 'pending',    -- pending | in_progress | completed
  updated_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (student_id, lesson_id)
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_live_classes_course ON live_classes(course_id, starts_at);
CREATE INDEX idx_recordings_course ON recordings(course_id);
CREATE INDEX idx_attempts_student ON exam_attempts(student_id);
