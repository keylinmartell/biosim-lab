# Plan de despliegue gratuito: Vercel + Supabase

Todo sin tarjeta de crédito:

| Capa | Servicio | Proyecto |
|---|---|---|
| Base de datos | Supabase (Free) | `biosim-lab` |
| Backend (FastAPI) | Vercel (Hobby, serverless) | Root Directory: `backend` |
| Frontend (Vue 3) | Vercel (Hobby) | Root Directory: `frontend` |

Los experimentos guardados viven **solo en la base de datos** (tabla `saved_experiments`). Ya no existe ningún JSON.

> Vercel detecta FastAPI automáticamente (`backend/index.py` expone `app`). No hace falta `mangum`.

---

## Fase 0. Antes de empezar

- [ ] Cuenta en GitHub con el repo subido (`git push`).
- [ ] Cuenta en Supabase (https://supabase.com) — entrar con GitHub.
- [ ] Cuenta en Vercel (https://vercel.com) — entrar con GitHub, plan **Hobby**.
- [ ] Confirmar que `backend/.env`, `node_modules` y `.venv` no están en el repo (revisar `.gitignore`).

---

## Fase 1. Supabase (base de datos)

1. **New project** → nombre `biosim-lab`, elige una región cercana (ej. `us-east-1`) y **guarda la contraseña** de la base de datos.
2. Espera a que el proyecto termine de crearse (~2 min).
3. Abre **SQL Editor → New query**, pega el contenido de `backend/sql/schema.sql` y pulsa **Run**.
   Esto crea la tabla `saved_experiments`. Se hace **una sola vez**.
4. Verifica en **Table Editor** que aparece `saved_experiments` (vacía).
5. Obtén la cadena de conexión: botón **Connect** (arriba) → **Transaction pooler** (puerto **6543**).
   Tiene esta forma:
   ```
   postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
6. Cámbiala al driver async, anteponiendo `+asyncpg`:
   ```
   postgresql+asyncpg://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
   > Si la contraseña tiene caracteres especiales (`@ # / :`), codifícalos en URL (`@` → `%40`).
   > Usa el **Transaction pooler**; la *Direct connection* usa IPv6 y suele fallar en Vercel.

---

## Fase 2. Backend en Vercel

1. En Vercel: **Add New → Project** → importa el repo.
2. Configura:
   - **Project Name:** `biosim-lab-api`
   - **Root Directory:** `backend`
   - **Framework Preset:** FastAPI (o *Other*, lo detecta solo)
3. **Environment Variables:**

   | Nombre | Valor |
   |---|---|
   | `DATABASE_URL` | la URL `postgresql+asyncpg://...:6543/postgres` de la Fase 1 |
   | `ALLOWED_ORIGINS` | *(se completa en la Fase 4)* |

   No definas `AUTO_CREATE_TABLES` en producción.
4. **Deploy**.
5. Prueba (reemplaza por tu URL):
   - `https://biosim-lab-api.vercel.app/health` → `{"status":"ok"}`
   - `https://biosim-lab-api.vercel.app/docs` → documentación Swagger
   - `https://biosim-lab-api.vercel.app/api/v1/dna/experiment/list` → `{"experiments":[],"total":0}`

Si `/experiment/list` devuelve error 500, revisa **Deployments → Logs** (casi siempre es `DATABASE_URL` mal escrita).

---

## Fase 3. Frontend en Vercel

1. **Add New → Project** → mismo repo.
2. Configura:
   - **Project Name:** `biosim-lab`
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite (build `npm run build`, output `dist`; ya definido en `frontend/vercel.json`)
3. **Environment Variables:**

   | Nombre | Valor |
   |---|---|
   | `VITE_API_BASE_URL` | `https://biosim-lab-api.vercel.app/api/v1` |

   > Debe incluir `/api/v1` al final: así lo usa [client.js](../frontend/src/api/client.js).
4. **Deploy** y abre `https://biosim-lab.vercel.app`.

---

## Fase 4. Cerrar el CORS

1. En el proyecto del **backend** → Settings → Environment Variables.
2. Define `ALLOWED_ORIGINS` = `https://biosim-lab.vercel.app` (varios dominios, separados por coma).
3. **Redeploy** el backend (Deployments → ⋯ → Redeploy).

---

## Fase 5. Verificación final

- [ ] La app carga y las operaciones de ADN (validar, complementar, mutar, reparar) responden.
- [ ] Guardar un experimento → aparece en **Supabase → Table Editor → saved_experiments**.
- [ ] Recargar la página → el experimento sigue en la lista.
- [ ] Hacer un redeploy → el experimento sigue ahí (persistencia real).

---

## Despliegues automáticos

Cada `git push` a `main` redespliega ambos proyectos de Vercel. Si cambias el esquema de la tabla, ejecuta el SQL correspondiente en Supabase.

---

## Desarrollo local

```bash
# Backend (con Postgres local o Supabase en backend/.env)
cd backend
pip install -r requirements.txt
set AUTO_CREATE_TABLES=1        # crea la tabla en tu BD local
uvicorn app.main:app --reload

# Frontend (el proxy de vite.config.js apunta a 127.0.0.1:8000)
cd frontend
npm install
npm run dev
```

---

## Límites y cosas a vigilar (planes gratuitos)

| Tema | Detalle |
|---|---|
| **Cold start** | Tras inactividad, la primera petición al backend tarda un poco más. |
| **Duración de función** | Hobby: hasta 300 s por petición; sobra para las simulaciones. |
| **Tamaño del bundle** | 500 MB; las dependencias del proyecto son ligeras. |
| **Supabase pausa el proyecto** | Tras ~1 semana sin actividad se pausa; se reactiva con un clic en el panel. Un ping periódico a `/api/v1/dna/experiment/list` (p. ej. UptimeRobot, gratis) lo evita. |
| **Base de datos** | 500 MB gratis; sobra para informes de texto/JSON. |
| **Log de eventos** | `/dna/events` es un registro **en memoria** por instancia serverless; no es persistente ni compartido. Solo los experimentos guardados van a la BD. |
| **Uso comercial** | El plan Hobby de Vercel es para uso personal/no comercial. |

> Los límites de los planes gratuitos cambian con frecuencia. Confírmalos en las páginas de precios de Vercel y Supabase antes de desplegar.

---

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `prepared statement ... already exists` | Falta desactivar el caché con pgbouncer | Ya resuelto en `backend/app/core/database.py`; asegúrate de usar el puerto 6543. |
| `Network is unreachable` / timeout a Supabase | Se usó *Direct connection* (IPv6) | Usar **Transaction pooler**. |
| `password authentication failed` | Contraseña incorrecta o sin codificar | Resetearla en Supabase y codificar caracteres especiales. |
| `relation "saved_experiments" does not exist` | No se ejecutó `schema.sql` | Ejecutarlo en el SQL Editor (Fase 1, paso 3). |
| El frontend recibe error CORS | `ALLOWED_ORIGINS` incorrecto | Debe ser exactamente el dominio del frontend, sin `/` final. |
| El frontend llama a `/api/v1` en su propio dominio y da 404 | Falta `VITE_API_BASE_URL` | Definirla en Vercel y **redeployar** el frontend (se inyecta en el build). |
