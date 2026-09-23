# Roadmap — De MVP a producción

## Fase 0 — MVP (este entregable): semanas 1-4
- [x] Backend completo: auth, usuarios, cursos, planificación, clases, exámenes, reportes
- [x] Frontend: login, panel del apoderado, biblioteca, simulaciones
- [x] Docker Compose: PostgreSQL + API + frontend
- [ ] Desplegar en servidor (VPS o AWS ECS), dominio + HTTPS (Caddy/Let's Encrypt)
- [ ] Poblar banco de preguntes alineado a currículum nacional (OA por asignatura/nivel)

## Fase 1 — Comercial: semanas 5-10
- [ ] Integración de pagos (Webpay Plus / Flow) y planes de suscripción
- [ ] Videoconferencia embebida propia (Jitsi self-hosted) + grabación automática a S3
- [ ] Notificaciones por correo (clases próximas, resultados de simulaciones)
- [ ] Panel administrativo (gestión de usuarios, matrículas, contenidos)
- [ ] Primeros 50-100 alumnos piloto + feedback de apoderados

## Fase 2 — Escala: meses 3-6
- [ ] Kubernetes o ECS con autoescala; réplica de lectura PostgreSQL
- [ ] Celery + Redis: reportes masivos, procesamiento de video (transcoding)
- [ ] CDN + URLs firmadas para contenido; streaming adaptativo (HLS)
- [ ] Analítica de aprendizaje: recomendación de contenido según desempeño
- [ ] Preparación formal Ley 21.719 (encargado de datos, DPIA)

## Fase 3 — Producto completo: meses 6-12
- [ ] App móvil (React Native) con modo offline de materiales
- [ ] Marketplace de docentes ( onboarding, pagos por hora)
- [ ] Acuerdos con colegios de referencia (no académicos: solo coordinación logística de exámenes)
- [ ] Meta: 1.000 alumnos activos, churn < 5%/mes
