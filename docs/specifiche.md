# Specifiche funzionali — ValueTech LMS

Piattaforma di formazione **ispirata a Moodle ma volutamente ridotta**: gestisce corsi,
iscrizioni e fruizione di contenuti **SCORM 1.2 / 2004** con tracciamento, accessibile come
**PWA** da desktop e mobile.

> Questo documento è la fonte di verità per la skill `/plan-change`.
> Ogni requisito ha un ID stabile; aggiornare la colonna **Stato** quando un piano viene implementato.

Legenda stato: ✅ implementato · 🟡 parziale · ⬜ da sviluppare durante il corso

## Attori

| Ruolo | Descrizione |
|-------|-------------|
| Amministratore | Gestisce utenti, corsi e configurazione della piattaforma |
| Docente | Crea e gestisce i propri corsi, carica i contenuti SCORM, consulta i report |
| Studente | Fruisce dei corsi a cui è iscritto, vede i propri progressi |

## Requisiti funzionali

| ID | Requisito | Stato |
|----|-----------|-------|
| RF-01 | Autenticazione degli utenti (login/logout, sessione sicura) | ⬜ — oggi esiste uno stub "utente demo" in `backend/app/api/deps.py` |
| RF-02 | Gestione utenti e ruoli (admin, docente, studente) | 🟡 — modello `User` presente, nessuna API |
| RF-03 | Creazione, modifica e pubblicazione di un corso | 🟡 — create/read/update presenti, manca eliminazione e controllo permessi |
| RF-04 | Iscrizione degli studenti ai corsi (manuale da parte del docente) | ⬜ |
| RF-05 | Caricamento di un pacchetto SCORM (.zip) in un corso, con validazione del manifest | ✅ |
| RF-06 | Fruizione di un pacchetto SCORM 1.2 nel player integrato | ✅ |
| RF-07 | Fruizione di un pacchetto SCORM 2004 (mono-SCO) nel player integrato | ✅ |
| RF-08 | Tracciamento e ripresa: stato, punteggio, tempo, `suspend_data` | ✅ |
| RF-09 | Navigazione tra più SCO dello stesso pacchetto (multi-SCO) | ⬜ |
| RF-10 | Report docente: avanzamento degli iscritti per corso, esportabile in CSV | ⬜ |
| RF-11 | Dashboard studente: corsi iscritti e percentuale di completamento | ⬜ |
| RF-12 | Attestato di completamento in PDF | ⬜ |

## Requisiti non funzionali

| ID | Requisito | Stato |
|----|-----------|-------|
| RNF-01 | Installabile come PWA (manifest, service worker, icone) | ✅ |
| RNF-02 | Catalogo corsi consultabile offline (dati in cache) | ✅ |
| RNF-03 | Database PostgreSQL con migrazioni versionate (Alembic) | ✅ |
| RNF-04 | Estrazione sicura dei pacchetti (zip slip, zip bomb, XXE) | ✅ |
| RNF-05 | Interfaccia in italiano, accessibile (WCAG 2.1 AA) | 🟡 |
| RNF-06 | Test automatici per ogni endpoint | 🟡 |
| RNF-07 | Avvio dell'intero stack con un comando (`docker compose up`) | ✅ |

## Fuori scope

Forum, chat, compiti con consegna di file, quiz nativi (i quiz arrivano dai pacchetti SCORM),
calendario, gradebook complesso, plugin di terze parti, xAPI/cmi5 (possibile evoluzione).
