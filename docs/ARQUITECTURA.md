# Arquitectura — Aula Site

## Principios
1. **Aula Site no certifica**: es apoyo pedagógico. El dominio no incluye
   "notas oficiales" ni "promoción"; incluye preparación, simulación y trazabilidad.
2. **Datos de menores**: acceso restringido por parentesco (apoderado → sus alumnos).
   RUN cifrado en aplicación. Cumplimiento Ley 19.628 y (en transición) Ley 21.719.
3. **API stateless** (JWT) para escalar horizontalmente detrás de un balanceador.

## Componentes
| Componente | Tecnología | Rol |
|---|---|---|
| API REST | FastAPI | Auth, usuarios, cursos, planificación, clases, exámenes, reportes |
| Base de datos | PostgreSQL 16 | Datos transaccionales |
| Frontend | React + Vite + Nginx | SPA responsive |
| Video en vivo | Jitsi Meet self-hosted | Salas determinísticas por curso |
| Grabaciones/materiales | MinIO (S3-compatible) | Almacenamiento + URLs firmadas |
| Cola de trabajos | Celery + Redis (fase 2) | Reportes masivos, procesamiento de video |
| CDN | CloudFront/Nginx cache (fase 2) | Escalar biblioteca a miles de usuarios |

## Escalabilidad
- Backend sin estado → réplicas múltiples + balanceador (ALB/Traefik).
- PostgreSQL en réplica de lectura para reportes.
- Contenido estático y video fuera del servidor de aplicación (S3 + CDN).
- WebSockets (fase 2) solo para presencia en clases en vivo; el resto es HTTP.

## Seguridad
- Contraseñas con bcrypt; sesiones con JWT de corta duración.
- Autorización por rol + verificación de parentesco en cada endpoint de menores.
- Rate limiting en login (fase 2, Kong/Traefik).
- HTTPS obligatorio; cookies `Secure; HttpOnly` si se migra el token a cookie.
- Auditoría: tabla `audit_log` recomendada para accesos a datos de alumnos.

## Módulos (estado)
| Módulo | Estado |
|---|---|
| Auth + roles | Funcional (MVP) |
| Gestión de usuarios y alumnos | Funcional (MVP) |
| Cursos + planificación anual/mensual/unidad/lección | Funcional (MVP) |
| Clases en vivo (enlace Jitsi) + biblioteca | Funcional (MVP) |
| Simulaciones de exámenes + evaluación automática | Funcional (MVP) |
| Reportes de progreso | Funcional (MVP) |
| Pagos (Webpay/Flow) | Fase 2 |
| Videoconferencia embebida + grabación automática | Fase 2 |
| Notificaciones (correo/push) | Fase 2 |
| App móvil | Fase 3 |
