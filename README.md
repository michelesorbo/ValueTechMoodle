# ValueTech LMS — progetto demo del corso "AI agentiche nella programmazione"

Gestionale per la formazione in stile Moodle, volutamente ridotto all'essenziale:
**corsi + contenuti SCORM 1.2/2004 con tracciamento**, fruibile come **PWA**.

Questo repository è il punto di partenza del corso: contiene una base funzionante e
testata, le specifiche dei requisiti ancora da sviluppare e una **skill personalizzata
di Claude Code** per pianificare le modifiche prima di implementarle.

## Stack

- **Backend:** Python · FastAPI · SQLAlchemy 2 (async) · Alembic · PostgreSQL 17
- **Frontend:** React 19 · TypeScript · Vite · React Router · TanStack Query · vite-plugin-pwa
- **SCORM:** parser del manifest lato server + runtime [scorm-again](https://github.com/jcputney/scorm-again) lato client

Dettagli e trade-off in [docs/architettura.md](docs/architettura.md).

## Avvio rapido

Prerequisiti: Docker, [uv](https://docs.astral.sh/uv/), Node.js 22+.

```bash
# Tutto in container → http://localhost:8080
make up

# Oppure sviluppo con hot-reload
make db && make migrate
make api   # http://localhost:8000/api/docs
make web   # http://localhost:5173
```

Pacchetti SCORM di prova: `samples/demo-scorm12.zip`, `samples/demo-scorm2004.zip`.

## Comandi

| Comando | Descrizione |
|---------|-------------|
| `make test` | pytest (con PostgreSQL) + vitest |
| `make lint` | ruff, mypy strict, oxlint, tsc |
| `make migrate` | applica le migrazioni |
| `cd backend && uv run alembic revision --autogenerate -m "..."` | nuova migrazione |

I test di integrazione del backend usano il database `lms_test` (creato in automatico da
docker compose). Per un altro DB: `DATABASE_URL=... uv run pytest`.

## Lavorare con Claude Code

| Cosa | Dove |
|------|------|
| Contesto per l'agente | `CLAUDE.md` → **da generare con `/init`** (esercitazione 1) |
| Skill di pianificazione | `.claude/skills/plan-change/` → `/plan-change <richiesta>` |
| Permessi condivisi | `.claude/settings.json` |
| Requisiti | `docs/specifiche.md` |
| Open point | `docs/open-points.md` |
| Piani | `docs/plans/` |

Il percorso guidato è in [docs/esercitazioni.md](docs/esercitazioni.md).

## Struttura

```
.
├── .claude/
│   ├── settings.json
│   └── skills/plan-change/      # skill personalizzata
│       ├── SKILL.md
│       ├── references/checklist-analisi.md
│       └── templates/{plan,open-point}-template.md
├── backend/                     # FastAPI + Alembic + test
├── frontend/                    # React PWA + player SCORM
├── docs/                        # specifiche, architettura, open point, piani
├── samples/                     # pacchetti SCORM di prova
├── docker-compose.yml
└── Makefile
```
