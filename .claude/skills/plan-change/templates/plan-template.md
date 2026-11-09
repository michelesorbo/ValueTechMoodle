# Piano NNNN — <Titolo della modifica>

| Campo | Valore |
|-------|--------|
| Stato | BOZZA · IN REVISIONE · APPROVATO · IMPLEMENTATO |
| Data | AAAA-MM-GG |
| Richiesta originale | "<testo della richiesta>" |
| Requisiti collegati | RF-xx, RNF-xx (da `docs/specifiche.md`) |
| Stima | S · M · L |

## 1. Obiettivo

Cosa deve essere vero, dal punto di vista dell'utente, a modifica completata (2-4 frasi).

## 2. Decisioni prese

| # | Domanda | Decisione | Fonte |
|---|---------|-----------|-------|
| D1 | ... | ... | Risposta utente · Assunzione · Specifica RF-xx |

## 3. Assunzioni

Default adottati in assenza di indicazioni. Ognuno deve essere reversibile e collegato a un open point.

- A1 — ... (→ OP-NNN)

## 4. Analisi d'impatto

| Area | File / componente | Tipo di modifica |
|------|-------------------|------------------|
| DB | `backend/app/models/...` + nuova migrazione Alembic | nuova tabella / colonna / indice |
| API | `backend/app/api/routes/...` | nuovo endpoint / modifica contratto |
| Frontend | `frontend/src/pages/...` | nuova pagina / componente |
| PWA | `frontend/vite.config.ts` (runtimeCaching) | cache / comportamento offline |
| SCORM | `backend/app/services/scorm/...` | versione 1.2 / 2004 |
| Test | `backend/tests/...`, `frontend/src/**/*.test.ts` | nuovi test |

## 5. Step di implementazione

Ogni step deve lasciare il progetto in stato verde (test e lint passano).

### Step 1 — <titolo>
- **File:** `path/esatto`
- **Modifica:** ...
- **Verifica:** comando o test che dimostra che lo step è corretto

### Step 2 — ...

## 6. Strategia di test

- Unit: ...
- Integrazione (API + PostgreSQL): ...
- Manuale / E2E: ...

## 7. Rischi e mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|

## 8. Rollback

Come si annulla la modifica (es. `alembic downgrade -1`, feature flag, revert del commit).

## 9. Definition of Done

- [ ] Tutti gli step completati
- [ ] `make test` e `make lint` verdi
- [ ] Migrazione con `downgrade` testato
- [ ] `docs/specifiche.md` aggiornato (stato dei requisiti)
- [ ] Open point collegati aggiornati

## 10. Open point collegati

- OP-NNN — <titolo>
