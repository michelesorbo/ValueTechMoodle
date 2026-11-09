# Percorso di esercitazioni — AI agentiche nella programmazione

## Esercitazione 0 — Avvio del progetto

```bash
make db          # PostgreSQL in Docker
make migrate     # schema iniziale
make api         # terminale 1 → http://localhost:8000/api/docs
make web         # terminale 2 → http://localhost:5173
```

Crea un corso, carica `samples/demo-scorm12.zip`, avvia il contenuto e premi
"Completa lezione". Ricaricando il pacchetto, lo stato viene ripreso.

## Esercitazione 1 — Far conoscere il progetto all'agente: `/init`

Il repository **non contiene** un `CLAUDE.md`: generarlo è il primo esercizio.

1. Apri Claude Code nella root del progetto ed esegui `/init`.
2. Leggi con attenzione il `CLAUDE.md` generato e rispondi a queste domande:
   - Ha individuato i comandi corretti per test e lint (`make test`, `make lint`)?
   - Ha capito il vincolo "stesso origin" per i contenuti SCORM?
   - Cita `docs/specifiche.md` e la skill `/plan-change`?
3. Migliora il file **a mano**: aggiungi le convenzioni del team (lingua dei messaggi di
   commit, "ogni modifica allo schema richiede una migrazione Alembic", ecc.).
4. Discussione: cosa va nel `CLAUDE.md` e cosa invece in `docs/`? Cosa succede se il file
   diventa troppo lungo?

## Esercitazione 2 — Pianificare prima di scrivere codice: `/plan-change`

La skill si trova in `.claude/skills/plan-change/`. Leggi `SKILL.md` prima di usarla.

```
/plan-change aggiungere le iscrizioni degli studenti ai corsi
```

Osserva come l'agente:
1. legge specifiche, architettura e open point;
2. esplora il codice reale;
3. ti fa domande **solo** sui punti bloccanti;
4. registra gli open point in `docs/open-points.md`;
5. scrive il piano in `docs/plans/0001-....md` e **si ferma** in attesa di approvazione.

Rivedi il piano: gli step sono atomici? I file citati esistono? C'è la migrazione con
`downgrade`? Chiedi le correzioni necessarie, poi approva e fai implementare lo step 1.

## Esercitazione 3 — Migliorare la skill

Modifica la skill per il tuo team, per esempio:
- aggiungi una sezione "Stima in ore" al template del piano;
- fai generare anche un diagramma Mermaid del flusso;
- aggiungi alla checklist le domande per la rendicontazione dei fondi interprofessionali.

Ripeti `/plan-change` sulla stessa richiesta e confronta i due piani.

## Backlog suggerito per il corso

Ogni voce parte da un `/plan-change`. I riferimenti sono in `docs/specifiche.md`.

| # | Funzionalità | Requisiti | Difficoltà |
|---|--------------|-----------|------------|
| 1 | Iscrizioni ai corsi | RF-04 | ★☆☆ |
| 2 | Autenticazione e ruoli | RF-01, RF-02, OP-001 | ★★☆ |
| 3 | Dashboard studente | RF-11 | ★☆☆ |
| 4 | Report docente con export CSV | RF-10 | ★★☆ |
| 5 | Pacchetti multi-SCO | RF-09, OP-002 | ★★★ |
| 6 | Attestato PDF | RF-12 | ★★☆ |
| 7 | Tracciamento offline | OP-003 | ★★★ |
