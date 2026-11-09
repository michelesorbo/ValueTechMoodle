# Checklist di analisi — ValueTech LMS

Scorri la checklist e tieni solo le voci pertinenti alla richiesta. Ogni voce senza
risposta chiara (né nelle specifiche, né nel codice) diventa una **domanda** (se
bloccante) o un **open point** (se non bloccante).

## Dominio e requisiti
- Quali ruoli sono coinvolti (admin, docente, studente)? Chi può fare cosa?
- La funzionalità è già descritta in `docs/specifiche.md`? Con quale ID?
- Ci sono vincoli normativi? (GDPR sui dati degli studenti, conservazione dei tracciamenti
  per la rendicontazione dei fondi interprofessionali, accessibilità WCAG 2.1 AA)
- Quali sono i casi limite? (corso senza contenuti, utente non iscritto, pacchetto rimosso
  mentre uno studente lo sta fruendo)

## Dati (PostgreSQL)
- Nuove entità o relazioni? Cardinalità?
- Vincoli di unicità, `ON DELETE` (CASCADE vs RESTRICT vs soft delete)?
- Indici necessari per le query previste (FK, filtri, ordinamenti)?
- Serve JSONB o è meglio una colonna strutturata/indicizzabile?
- Migrazione su dati esistenti: serve un backfill? Il `downgrade` è sicuro?

## API (FastAPI)
- Contratto: path, metodo, payload, codici di risposta, paginazione.
- Autorizzazione: quale dipendenza controlla i permessi?
- Il cambio è retro-compatibile con il frontend già distribuito (PWA in cache!)?
- Idempotenza e concorrenza (due commit SCORM ravvicinati, doppio click).

## Frontend (React PWA)
- Nuove route? Va caricata in lazy loading?
- Stato server via TanStack Query: chiavi di query e invalidazioni.
- Comportamento offline: la funzione deve funzionare offline? Cosa vede l'utente?
- Va aggiornato il `runtimeCaching` del service worker? Rischio di dati obsoleti?
- Mobile first e accessibilità (focus, label, contrasto).

## SCORM
- Versione: 1.2, 2004 o entrambe?
- Pacchetti mono-SCO o multi-SCO? Serve la navigazione tra item (sequencing 2004)?
- Quali campi CMI servono per la reportistica (status, score, tempo, interactions)?
- Nuovo tentativo vs ripresa del tentativo esistente: chi lo decide?
- Contenuti serviti dallo stesso origin? (requisito per `window.parent.API`)

## Qualità e operatività
- Quali test dimostrano che la modifica funziona?
- Serve un dato demo / seed per provarla?
- Impatto su performance, storage (dimensione dei pacchetti), log.
- Cosa va documentato (README, specifiche, CLAUDE.md)?
