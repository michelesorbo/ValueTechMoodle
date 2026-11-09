# Architettura

```
                ┌────────────────────── stesso origin ───────────────────────┐
 Browser/PWA ──▶│ nginx (prod) / Vite dev server (dev)                        │
                │   /               → app React (service worker Workbox)      │
                │   /api/*          → FastAPI                                 │
                │   /scorm-content/*→ FastAPI StaticFiles (pacchetti estratti)│
                └─────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
                                PostgreSQL 17 (JSONB per CMI e manifest)
```

## Stack

| Livello | Tecnologia | Perché |
|---------|------------|--------|
| Backend | Python 3.12+ · FastAPI · Pydantic v2 | OpenAPI automatico, tipizzazione forte, async |
| ORM / DB | SQLAlchemy 2.0 async · psycopg 3 · PostgreSQL 17 | JSONB per il CMI SCORM, vincoli e migrazioni robuste |
| Migrazioni | Alembic (autogenerate + naming convention) | Schema versionato, `downgrade` testabile |
| Frontend | React 19 · TypeScript · Vite · React Router · TanStack Query | Ecosistema maturo, ottimo supporto agli agenti AI |
| PWA | vite-plugin-pwa (Workbox, `registerType: prompt`) | Installabile, cache offline, update controllati |
| SCORM runtime | scorm-again (1.2 e 2004) | Implementazione completa e testata del data model CMI |
| Tooling | uv · ruff · mypy strict · pytest · oxlint · vitest | Feedback veloce, utile agli agenti AI per autoverificarsi |

## Flusso SCORM

1. **Upload** `POST /api/scorm/packages` → validazione zip (zip slip, symlink, zip bomb) →
   parsing di `imsmanifest.xml` con `defusedxml` → estrazione in `storage/scorm/<uuid>/`.
2. **Launch** `GET /api/scorm/packages/{id}/launch` → crea o riprende lo `ScormAttempt`
   dell'utente e restituisce URL di lancio, URL di commit e CMI salvato.
3. **Runtime**: il frontend crea `Scorm12API`/`Scorm2004API`, ricarica il CMI con
   `loadFromJSON`, lo espone su `window.API` / `window.API_1484_11` e solo dopo carica lo SCO
   nell'iframe.
4. **Commit**: scorm-again invia `{ cmi: {...} }` a `POST /api/scorm/attempts/{id}/commit`;
   il backend salva il CMI completo (JSONB) e denormalizza status/score/tempo per i report.

## Struttura delle cartelle

```
backend/app/
  api/routes/    endpoint HTTP (sottili: validazione + orchestrazione)
  api/deps.py    dipendenze FastAPI (sessione DB, utente corrente)
  core/          configurazione e accesso al DB
  models/        modelli SQLAlchemy
  schemas/       DTO Pydantic (contratti API)
  services/      logica di dominio (es. parsing ed estrazione SCORM)
backend/alembic/ migrazioni
frontend/src/
  api/           client HTTP tipizzato
  components/    componenti riusabili (ScormPlayer, PwaStatus)
  pages/         pagine collegate alle route
```

## Trade-off noti

- **FastAPI vs NestJS**: con NestJS si condividerebbero i tipi TS tra front e back; FastAPI
  ha meno boilerplate ed è più leggibile in aula. I tipi frontend potranno essere generati
  dall'OpenAPI (`/api/openapi.json`) — buon esercizio per il corso.
- **Contenuti SCORM serviti da FastAPI**: semplice in sviluppo; in produzione conviene farli
  servire direttamente da nginx o da un object storage dietro lo stesso dominio.
- **CMI in JSONB + colonne denormalizzate**: flessibilità sul data model completo, query
  veloci sui campi usati dai report.
