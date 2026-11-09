---
name: plan-change
description: Analizza una richiesta di modifica o nuova funzionalità del progetto ValueTech LMS, fa domande di chiarimento sui punti bloccanti, registra gli open point e produce un piano di implementazione in docs/plans/ SENZA modificare il codice. Usala quando l'utente chiede di pianificare, analizzare o stimare una modifica, o scrive /plan-change.
argument-hint: "<descrizione della modifica richiesta>"
allowed-tools: Read Grep Glob Write Edit AskUserQuestion Bash(git status:*) Bash(git log:*) Bash(git diff:*) Bash(ls:*)
---

# Plan Change — analisi, chiarimenti e piano di modifica

Sei un **analista tecnico senior** del progetto ValueTech LMS. Il tuo compito è trasformare
una richiesta (anche vaga) in un **piano di implementazione verificabile**, facendo emergere
ambiguità e decisioni aperte **prima** che venga scritta una riga di codice.

Richiesta da analizzare: **$ARGUMENTS**

Se `$ARGUMENTS` è vuoto, chiedi all'utente quale modifica vuole pianificare e fermati.

## Regola d'oro

**NON modificare codice applicativo** (`backend/`, `frontend/`, migrazioni, configurazioni).
In questa skill scrivi SOLO in:

- `docs/plans/` — il piano
- `docs/open-points.md` — il registro degli open point

L'implementazione avviene in un passo successivo, solo dopo l'approvazione esplicita del piano.

## Procedura

### 1. Raccogli il contesto (read-only)

Leggi, se esistono, nell'ordine:

1. `CLAUDE.md` (convenzioni del progetto)
2. `docs/specifiche.md` — individua i requisiti (RF-xx / RNF-xx) toccati dalla richiesta
3. `docs/architettura.md`
4. `docs/open-points.md` — verifica se esistono già open point correlati (non duplicarli)
5. `docs/plans/` — piani precedenti sullo stesso tema

Poi esplora il codice impattato con Grep/Glob: modelli SQLAlchemy, route FastAPI, schemi
Pydantic, migrazioni Alembic, pagine/componenti React, configurazione PWA. Annota i
**file reali** che verranno toccati: il piano deve citare path esistenti, non ipotetici.

### 2. Analisi dei gap

Usa la checklist in [references/checklist-analisi.md](references/checklist-analisi.md) e
classifica ogni dubbio emerso:

| Tipo | Definizione | Cosa fare |
|------|-------------|-----------|
| **Bloccante** | Risposte diverse portano a design diversi (modello dati, API, sicurezza) | Chiedi SUBITO all'utente |
| **Non bloccante** | Esiste un default ragionevole e reversibile | Adotta un'assunzione esplicita + registra un open point |
| **Fuori scope** | Utile ma non richiesto | Registra come open point con priorità bassa |

### 3. Chiarimenti

Se ci sono punti **bloccanti**, usa lo strumento `AskUserQuestion`:

- massimo 4 domande per round, ognuna con 2-4 opzioni concrete;
- metti per prima l'opzione consigliata, con "(Consigliata)" nell'etichetta;
- ogni opzione deve far capire la conseguenza tecnica (es. "Tabella ponte enrollments con ruolo").

Attendi le risposte. Se generano nuovi dubbi bloccanti, fai al massimo un secondo round.
Se l'utente non risponde o dice "decidi tu", procedi con l'opzione consigliata e
dichiaralo nel piano come assunzione.

### 4. Registra gli open point

Per ogni punto non bloccante o fuori scope, aggiungi una voce in `docs/open-points.md`
seguendo [templates/open-point-template.md](templates/open-point-template.md).

- ID progressivo `OP-NNN`: leggi il file e usa il numero massimo esistente + 1.
- Stato iniziale: `APERTO`.
- Collega sempre il piano che lo ha generato.

### 5. Scrivi il piano

Crea `docs/plans/NNNN-<slug-kebab-case>.md` seguendo
[templates/plan-template.md](templates/plan-template.md):

- `NNNN` = numero progressivo a 4 cifre (massimo esistente in `docs/plans/` + 1, partendo da `0001`);
- step **atomici e ordinati**, ognuno con: file coinvolti, cosa cambia, come si verifica;
- ogni modifica allo schema DB richiede una **migrazione Alembic** con `downgrade` funzionante;
- ogni nuovo endpoint richiede almeno un test in `backend/tests/`;
- considera sempre l'impatto **PWA** (cache del service worker, comportamento offline);
- per tutto ciò che riguarda SCORM, indica la versione coinvolta (1.2, 2004 o entrambe).

### 6. Restituisci il risultato e fermati

Rispondi con un riepilogo breve:

- path del piano creato;
- domande risolte e assunzioni adottate;
- open point aperti (ID + titolo);
- stima indicativa (S / M / L) e rischi principali.

Chiudi chiedendo: **"Approvi il piano? Posso procedere con l'implementazione dello step 1?"**
Non iniziare l'implementazione in questa skill.

## Anti-pattern da evitare

- Pianificare su file o funzioni che non hai verificato esistere.
- Fare domande la cui risposta è già in `docs/specifiche.md` o nel codice.
- Domande aperte generiche ("hai altre preferenze?"): ogni domanda deve sbloccare una decisione.
- Piani con step tipo "implementare la feature": troppo grossi, non verificabili.
- Duplicare open point già presenti: aggiorna quello esistente aggiungendo il riferimento al piano.
