# Registro open point

Decisioni aperte del progetto. Le voci vengono aggiunte dalla skill `/plan-change`
(formato in `.claude/skills/plan-change/templates/open-point-template.md`).

---

### OP-001 — Strategia di autenticazione

| Campo | Valore |
|-------|--------|
| Stato | APERTO |
| Priorità | ALTA |
| Tipo | Sicurezza |
| Aperto il | 2026-11-09 |
| Origine | Scaffold iniziale |
| Owner | da assegnare |

**Contesto:** il backend usa uno stub (`get_current_user`) che restituisce sempre un utente demo.

**Domanda:** come autentichiamo gli utenti?

**Opzioni:**
1. Sessione con cookie HttpOnly gestita dal backend — semplice, adatta alla PWA same-origin; meno adatta ad app native.
2. JWT access + refresh token — stateless; serve gestire revoca e storage sicuro lato client.
3. OIDC esterno (Keycloak, Google Workspace, Microsoft Entra ID) — SSO aziendale; dipendenza esterna.

**Assunzione corrente:** utente demo con ruolo admin.

**Decisione:** _(da compilare)_

---

### OP-002 — Supporto ai pacchetti multi-SCO

| Campo | Valore |
|-------|--------|
| Stato | APERTO |
| Priorità | MEDIA |
| Tipo | Requisito |
| Aperto il | 2026-11-09 |
| Origine | Scaffold iniziale |
| Owner | da assegnare |

**Contesto:** il player lancia solo il primo item lanciabile dell'organizzazione di default.
Il manifest completo è già salvato in `scorm_packages.manifest` (JSONB).

**Domanda:** serve la navigazione tra SCO (RF-09) e, per SCORM 2004, il sequencing?

**Opzioni:**
1. Menu laterale con l'albero degli item e un tentativo per SCO — copre la maggior parte dei casi.
2. Sequencing & Navigation SCORM 2004 completo — molto più complesso.

**Assunzione corrente:** solo pacchetti mono-SCO.

**Decisione:** _(da compilare)_

---

### OP-003 — Tracciamento SCORM offline

| Campo | Valore |
|-------|--------|
| Stato | APERTO |
| Priorità | BASSA |
| Tipo | Tecnico |
| Aperto il | 2026-11-09 |
| Origine | Scaffold iniziale |
| Owner | da assegnare |

**Contesto:** i contenuti SCORM vengono messi in cache dal service worker, ma i commit del
CMI richiedono la rete.

**Domanda:** vogliamo la fruizione completamente offline con sincronizzazione differita?

**Opzioni:**
1. `enableOfflineSupport` di scorm-again + coda dei commit — conflitti da gestire.
2. Workbox Background Sync sulle POST `/commit` — trasparente per il player.
3. Online-only per il tracciamento — semplice, è lo stato attuale.

**Assunzione corrente:** opzione 3.

**Decisione:** _(da compilare)_
