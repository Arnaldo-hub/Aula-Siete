# Aula Site — Plataforma de Apoyo Pedagógico para Exámenes Libres (Chile)

Aula Site opera como **institución de apoyo pedagógico** (no establecimiento
oficial Mineduc). Prepara a estudiantes que validan estudios mediante
**Exámenes Libres** administrados por el Ministerio de Educación de Chile.

## Despliegue en Render (recomendado, sin instalar nada en tu PC)

1. **Subir a GitHub**: crea un repositorio y sube todo el contenido de esta carpeta
   (backend/, frontend/, render.yaml, docs/...).

2. **En Render**: Dashboard → *New* → **Blueprint** → conecta tu repositorio GitHub.
   Render detecta `render.yaml` y crea automáticamente:
   - `aulasite-backend` (API FastAPI + seed de datos demo)
   - `aulasite-frontend` (sitio estático React)
   - `aulasite-db` (PostgreSQL gratis)

3. **Después del primer deploy**:
   - Copia la URL real del frontend (ej. https://aulasite-frontend.onrender.com)
     y ponla en el env var `CORS_ORIGINS` del backend (sin `*`), luego *Manual Deploy → Clear build cache & deploy*.
   - Si Render asignó otro nombre al backend, actualiza `VITE_API_URL` del frontend
     y redepliega.

4. **Probar**: entra a la URL del frontend con `apoderado@demo.cl` / `demo1234`.
   Documentación de la API en `https://<tu-backend>.onrender.com/docs`.

## Conectar tu dominio aulasiete.cl
- En Render → frontend → *Settings → Custom Domains* → agrega `aulasiete.cl`
  (y `www.aulasite.cl`). Render te da el registro DNS (CNAME) que debes crear
  en el panel de tu proveedor de dominio. HTTPS es automático y gratis.
- Recuerda actualizar `CORS_ORIGINS` del backend con https://aulasite.cl.

## Ejecutar en tu PC (opcional, para desarrollo)
Requisitos: Python 3.12+ y Node.js 20+.
```bat
cd backend
python -m venv venv && venv\Scriptsctivate
pip install -r requirements.txt && python seed.py
uvicorn app.main:app --reload
```
```bat
cd frontend
npm install && npm run dev
```
Frontend en http://localhost:5173, API en http://localhost:8000/docs.

## Documentación
- `docs/ARQUITECTURA.md` — diseño del sistema y escalabilidad
- `docs/CUMPLIMIENTO_MINEDUC.md` — marco legal y flujo de validación
- `docs/ROADMAP.md` — plan por fases hasta producción
