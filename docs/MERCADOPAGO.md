# Pagos con Mercado Pago — Configuración (15 minutos)

## 1. Crear la aplicación en Mercado Pago
1. Entra a https://www.mercadopago.cl/developers (con tu cuenta MP).
2. "Tus aplicaciones" → **Crear aplicación** → nombre: `Aula Siete`.
3. En la aplicación: pestaña **Credenciales** → copia el **Access Token de PRODUCCIÓN**
   (empieza con `APP_USR-...`). Ese es el único dato que va en Render.

## 2. Variables en Render
Render → `aulasite-backend` → Environment:
| Key | Value |
|---|---|
| `MP_ACCESS_TOKEN` | tu Access Token de producción |
| `PUBLIC_BASE_URL` | `https://aulasiete.cl` |

Save Changes.

## 3. Webhook (para confirmar pagos automáticamente)
En la aplicación de MP → **Webhooks** → agregar:
- URL: `https://aulasite-backend.onrender.com/api/payments/webhook`
- Evento: `subscription_preapproval` (suscripciones)

Si no configuras el webhook, la suscripción igual se crea; el estado se puede
revisar manualmente, pero el webhook mantiene todo actualizado solo.

## 4. Activar suscripciones en tu cuenta MP
Las suscripciones automáticas (preapproval) requieren que tu cuenta MP tenga
medio de cobro configururado y, en algunos casos, aprobación de MP.
Si MP rechaza una suscripción de prueba, revisar en el panel de MP:
Mercado Pago → Configuración → Suscripciones.

## 5. Flujo que vive el apoderado
1. Panel → 💳 Suscripción → elige plan → "Suscribirse".
2. Se abre Mercado Pago → autoriza el débito mensual con tarjeta.
3. Vuelve a la plataforma y ve su suscripción "✅ Activa".
4. Cada mes MP cobra automático; si cancela, el webhook actualiza el estado.

## Notas
- Precios en CLP, cobro mensual, sin IVA agregado (MP cobra comisión por transacción ~3-4%).
- Para cambiar precios: editar PLANS en `backend/app/routers/payments.py`.
