<div align="center">

# AudioDex — Downloader Audio da YouTube

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/yt--dlp-2026+-FF0000?logo=youtube&logoColor=white" alt="yt-dlp">
  <img src="https://img.shields.io/badge/FFmpeg-richiesto-007808?logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Rich-13.0+-000000?logo=terminal&logoColor=white" alt="Rich">
  <img src="https://img.shields.io/badge/Mutagen-1.47+-3776AB?logo=python&logoColor=white" alt="Mutagen">
  <img src="https://img.shields.io/badge/SQLite-WAL-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Requests-2.31+-3776AB?logo=python&logoColor=white" alt="Requests">
</p>

<p align="center">
  Uno strumento CLI interattivo che cerca brani su <b>YouTube</b> e ne scarica il <b>solo flusso audio</b><br>
  (niente video: file piccoli, qualità massima), con <b>download paralleli</b>, barre di avanzamento live,<br>
  <b>tagging automatico dei metadati</b> (titolo, artista, album, copertina) e registrazione<br>
  di ogni download su un <b>database SQLite globale</b>.
</p>

</div>

```bash
git clone https://github.com/Imkun-on/Scraper_Audio.git
cd Scraper_Audio
pip install -r requirements.txt
python Scraper_Audio.py
```

---

## Indice

- [Caratteristiche](#caratteristiche)
- [Architettura del progetto](#architettura-del-progetto)
- [Requisiti e installazione](#requisiti-e-installazione)
- [Utilizzo ed esempi](#utilizzo-ed-esempi)
  - [Esempio 1: Modalità interattiva (ricerca per nome)](#esempio-1-modalità-interattiva-ricerca-per-nome)
  - [Esempio 2: Download diretto di una playlist](#esempio-2-download-diretto-di-una-playlist)
  - [Esempio 3: Uso da riga di comando](#esempio-3-uso-da-riga-di-comando)
- [Opzioni della riga di comando](#opzioni-della-riga-di-comando)
- [Come funziona il download](#come-funziona-il-download)
- [Tagging dei metadati](#tagging-dei-metadati)
- [Testi sincronizzati (karaoke)](#testi-sincronizzati-karaoke)
- [Database globale](#database-globale)
- [Gestione degli errori e tracce fallite](#gestione-degli-errori-e-tracce-fallite)
- [Formati di output](#formati-di-output)
- [Licenza e note](#licenza-e-note)

---

## Caratteristiche

- **Ricerca su YouTube per nome** di canzone o artista, con risultati in una tabella numerata (titolo, canale, durata) e selezione flessibile: numero singolo, intervallo (`1-5`), elenco (`1,3,7`) o `all`
- **Download diretto da URL** di video singoli, playlist e album (YouTube `playlist?list=`, link con `&list=`, e riconoscimento dei pattern playlist di Spotify/SoundCloud)
- **Solo audio, mai il video**: viene scaricato esclusivamente il flusso `bestaudio` e convertito nel formato scelto (`m4a`, `mp3`, `opus`) — un brano occupa pochi MB invece di centinaia
- **Download paralleli** con pool di thread configurabile (default 3) e **doppia barra di avanzamento live**: una complessiva sulle tracce e una per ogni file in corso, con velocità e tempo stimato
- **Tagging automatico dei metadati**: titolo, artista, album, numero traccia e **copertina** incorporata nel file (via mutagen)
- **Testi sincronizzati stile karaoke**: per ogni traccia viene cercato il testo con i timestamp su [LRCLIB](https://lrclib.net) e **incorporato nei tag del file audio** — un file unico che porta con sé anche il testo; i lettori compatibili lo mostrano riga per riga mentre il brano suona
- **Playlist organizzate**: ogni playlist/album viene scaricato in una sottocartella con il suo nome, con i numeri di traccia nell'ordine originale
- **Anti-duplicati**: le tracce già presenti su disco vengono saltate (`skip`), così si può rilanciare lo stesso download senza riscaricare nulla
- **Retry automatici** con backoff esponenziale e jitter (fino a 4 tentativi per traccia)
- **Database SQLite globale** che registra ogni download (titolo, artista, album, dimensione, durata, formato, data)
- **Esportazione delle tracce fallite** in `failed_tracks.txt` con gli URL pronti per ritentare
- **Arresto pulito con Ctrl+C**: i download in corso terminano, quelli in coda vengono annullati; un secondo Ctrl+C forza l'uscita
- **Controllo dello spazio disco** prima di iniziare, con richiesta di conferma sotto i 200 MB liberi

---

## Architettura del progetto

```
Scraper_Audio/
├── Scraper_Audio.py          # CLI principale: ricerca, selezione, download, UI Rich
├── Shared/
│   ├── __init__.py
│   ├── logger_setup.py       # Logger su file + tema/simboli Rich condivisi
│   └── http_client.py        # Utilità HTTP condivise (User-Agent, header, backoff retry)
├── Database_Globale/
│   ├── scraper_db.py         # Database SQLite globale dei download
│   └── scraper_metadata.db   # Il database (creato automaticamente, escluso da git)
├── download_audio/           # Cartella di output (creata automaticamente, esclusa da git)
├── logs/
│   └── scraper_audio.log     # Log dettagliato di ogni sessione (escluso da git)
├── requirements.txt          # Dipendenze Python
└── README.md
```

I moduli `Shared/` e `Database_Globale/` sono progettati per essere **condivisi tra più scraper** (audio, manga, anime): stesso tema grafico, stesso logging, stesso database con colonne specifiche per tipo.

---

## Requisiti e installazione

### Python

Richiede **Python 3.10+**.

### FFmpeg (obbligatorio)

FFmpeg è necessario per estrarre/convertire l'audio nel formato scelto. Su Windows:

```powershell
winget install Gyan.FFmpeg
```

oppure scaricalo da [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) e aggiungilo al `PATH`. Verifica con `ffmpeg -version`.

### Dipendenze Python

```bash
pip install -r requirements.txt
```

oppure manualmente:

```bash
pip install yt-dlp requests rich mutagen
```

| Libreria | Scopo |
|----------|-------|
| `yt-dlp` | Ricerca su YouTube ed estrazione/download del flusso audio |
| `requests` | Download della copertina (thumbnail) da incorporare nei tag |
| `rich` | Interfaccia CLI: tabelle, pannelli, barre di avanzamento live |
| `mutagen` | *(opzionale)* Scrittura dei metadati e della copertina nei file `.m4a` — senza, il download funziona ma i file restano senza tag |

> **Nota su yt-dlp:** YouTube cambia spesso le proprie API interne. Se ricerca o download smettono di funzionare, quasi sempre basta aggiornare yt-dlp: `pip install -U yt-dlp`

---

## Utilizzo ed esempi

```bash
python Scraper_Audio.py
```

### Flusso interattivo

1. **Avvio**: banner, controllo dello spazio disco, inizializzazione del database
2. **Cerca o incolla**: digita un nome di canzone/artista per cercare, oppure incolla direttamente un URL
3. **Selezione**: scegli quali risultati scaricare (numero, intervallo, elenco, `all`)
4. **Download**: le tracce vengono scaricate in parallelo con barre di avanzamento live
5. **Riepilogo**: pannello finale con scaricate / già presenti / fallite
6. Il loop riparte: nuova ricerca o `q` per uscire

---

### Esempio 1: Modalità interattiva (ricerca per nome)

```
╔══════════════════════════════════════════════════════════════════════════╗
║      ___             ___           _____                                  ║
║     /   | __  ______/ (_)___      / ___/______________ _____  ___  _____  ║
║    / /| |/ / / / __  / / __ \     \__ \/ ___/ ___/ __ `/ __ \/ _ \/ ___/  ║
║   / ___ / /_/ / /_/ / / /_/ /    ___/ / /__/ /  / /_/ / /_/ /  __/ /      ║
║  /_/  |_\__,_/\__,_/_/\____/____/____/\___/_/   \__,_/ .___/\___/_/       ║
║                           /_____/                   /_/                   ║
╚══════════════════════════════════════════════════════════════════════════╝

Modalita' interattiva
  • Digita un nome canzone/artista per cercare
  • Incolla un URL (video/playlist) per download diretto
  • Digita q per uscire

♫ Cerca o incolla URL > linkin park in the end

                        Risultati ricerca
╭──────┬───────────────────────────────────────────┬───────────────┬────────╮
│    # │ Titolo                                    │ Artista/Canale│ Durata │
├──────┼───────────────────────────────────────────┼───────────────┼────────┤
│    1 │ In The End [Official HD Music Video]      │ Linkin Park   │   3:54 │
│    2 │ In the End                                │ Linkin Park   │   3:36 │
│    3 │ Linkin Park - In The End (Audio)          │ YOUMUSIC      │   3:31 │
│  ... │                                           │               │        │
╰──────┴───────────────────────────────────────────┴───────────────┴────────╯

Seleziona: numero singolo (3), intervallo (1-5), multipli (1,3,7),
all per tutti, q per uscire

Scegli > 1

─────────────────────────── ⬇ Download audio ───────────────────────────
  Thread: 3  Tracce: 1

⠋ Tracce      ████████████████████████████████  100%  1/1  │ 0:00:05
⠋ #1 In The End [Official HD...  ██████████  100%  3.6/3.6 MB  2.1 MB/s

╔═════════════ ✅ Riepilogo ═════════════╗
║                                        ║
║   Tracce totali   1                    ║
║   ✓ Scaricate     1                    ║
║                                        ║
╚════════════════════════════════════════╝

♫ Cerca o incolla URL > q

Arrivederci!
```

---

### Esempio 2: Download diretto di una playlist

Incollando l'URL di una playlist (o di un video che appartiene a una playlist, tipo `watch?v=...&list=...`), il programma riconosce la playlist, mostra il riepilogo e chiede se scaricare tutto o selezionare le tracce:

```
♫ Cerca o incolla URL > https://www.youtube.com/playlist?list=OLAK5uy_kkk...

╭────────────────────────────────────────────╮
│ Molchat Doma - Etazhi                      │
│ Tracce: 9   Durata totale: 33:18           │
╰────────────────────────────────────────────╯

Scaricare tutte le 9 tracce? (s/n)
> s

─────────────────────────── ⬇ Download audio ───────────────────────────
  Thread: 3  Tracce: 9

⠋ Tracce      ██████████████████░░░░░░░░░░  6/9   │ 0:01:12 → 0:00:35
⠋ #7 Тоска           ██████████░░░░░  64%  2.1/3.3 MB  1.8 MB/s
⠋ #8 Клетка          ████░░░░░░░░░░░  28%  0.9/3.2 MB  2.0 MB/s
⠋ #9 Коммерсанты     ██░░░░░░░░░░░░░  11%  0.4/3.5 MB  1.7 MB/s
```

Le tracce finiscono in una **sottocartella con il nome dell'album** (`download_audio/Molchat Doma - Etazhi/`), taggate con album e numero di traccia nell'ordine della playlist. Rispondendo `n` alla domanda, si apre la selezione manuale (`1-5`, `1,3,7`, ecc.).

---

### Esempio 3: Uso da riga di comando

Per saltare la modalità interattiva:

```bash
# Ricerca una tantum (mostra i risultati e chiede la selezione)
python Scraper_Audio.py --search "daft punk get lucky"

# Download diretto di un video o di una playlist
python Scraper_Audio.py --url "https://www.youtube.com/watch?v=..."
python Scraper_Audio.py --url "https://www.youtube.com/playlist?list=..."

# In mp3, in una cartella personalizzata, con 5 download paralleli
python Scraper_Audio.py --url "https://..." --format mp3 --output "D:\Musica" --workers 5
```

---

## Opzioni della riga di comando

| Opzione | Abbreviazione | Default | Descrizione |
|---------|---------------|---------|-------------|
| `--search "testo"` | `-s` | — | Cerca per nome canzone/artista (alternativa a `--url`) |
| `--url <link>` | `-u` | — | URL diretto di video, playlist o album |
| `--output <cartella>` | `-o` | `download_audio/` | Cartella di destinazione dei file |
| `--format {m4a,mp3,opus}` | `-f` | `m4a` | Formato audio di output (solo audio, mai video) |
| `--workers <n>` | `-w` | `3` | Numero di download paralleli |
| `--max-results <n>` | — | `15` | Numero massimo di risultati di ricerca |
| `--no-lyrics` | — | disattivato | Non cercare i testi sincronizzati (`.lrc`) su LRCLIB |

Senza `--search` né `--url` si avvia la **modalità interattiva**.

---

## Come funziona il download

### 1. Ricerca

La ricerca usa il motore interno di yt-dlp con il prefisso `ytsearchN:<query>` e l'opzione `extract_flat`: vengono recuperati **solo i metadati** (titolo, canale, durata, URL) senza scaricare nulla. È la stessa tecnica usata per le playlist, dove `ignoreerrors` fa sì che i video privati o rimossi vengano saltati invece di far fallire l'intero elenco.

### 2. Normalizzazione degli URL playlist

Se si incolla l'URL di un video che fa parte di una playlist (`watch?v=...&list=...`), yt-dlp estrarrebbe solo quel video. Il programma estrae l'ID della playlist e lo converte nell'URL canonico `playlist?list=<ID>`, ottenendo l'elenco completo delle tracce.

### 3. Download del solo audio

Per ogni traccia yt-dlp viene configurato con:

```python
'format': 'bestaudio[ext=m4a]/bestaudio/best'   # mai la traccia video
'postprocessors': [{'key': 'FFmpegExtractAudio',
                    'preferredcodec': <formato scelto>,
                    'preferredquality': '0'}]    # qualità massima
```

Il flusso audio migliore disponibile viene scaricato e FFmpeg lo converte nel formato scelto (se il formato sorgente coincide, viene rimuxato senza ricodifica, quindi senza perdita di qualità).

### 4. Parallelismo e avanzamento

I download girano su un `ThreadPoolExecutor` (default 3 thread). Un *progress hook* di yt-dlp fa da ponte verso le barre Rich: ogni blocco scaricato aggiorna la barra del singolo file con i byte ricevuti, mentre la barra complessiva avanza al completamento di ogni traccia. I risultati vengono riordinati secondo l'ordine originale della playlist (i thread terminano in ordine sparso).

### 5. Anti-duplicati e retry

- Prima di scaricare, il titolo (sanificato dai caratteri vietati di Windows) viene confrontato con i file già presenti nella cartella: se esiste un file valido (>10 KB), la traccia è marcata `skip`.
- In caso di errore si riprova fino a **4 volte** con backoff esponenziale + jitter casuale (per non riprovare a raffica e non sincronizzare i retry dei vari thread).

---

## Tagging dei metadati

Dopo il download, ogni file `.m4a` viene taggato con **mutagen** usando i tag standard iTunes (i file `.m4a` usano il container MP4):

| Tag | Contenuto | Fonte |
|-----|-----------|-------|
| `©nam` | Titolo | Metadati YouTube |
| `©ART` | Artista | Campo `artist` o, in mancanza, il nome del canale |
| `©alb` | Album | Nome della playlist (o campo `album` di YouTube) |
| `trkn` | Numero traccia | Posizione nella playlist |
| `covr` | Copertina | Thumbnail del video, scaricata e incorporata (JPEG/PNG) |

Se mutagen non è installato il tagging viene semplicemente saltato: i file audio restano validi, solo senza metadati.

---

## Testi sincronizzati (karaoke)

Dopo ogni download riuscito, il programma interroga **[LRCLIB](https://lrclib.net)** (API gratuita, senza chiave) con artista, titolo e durata della traccia. Se il testo esiste, viene **incorporato direttamente nel tag `©lyr` del file m4a**, in formato LRC con i timestamp: il brano resta **un file unico** che porta con sé anche il testo, su PC come su telefono.

I lettori che leggono il testo dai tag (Musicolet, Oto Music, AIMP, Samsung Music su Android; MusicBee, foobar2000, AIMP su PC) lo mostrano **riga per riga in stile karaoke**; quelli più basilari lo mostrano come testo statico.

Dettagli del funzionamento:

- il titolo YouTube viene **ripulito** dalle decorazioni (`(Official Video)`, `[HD]`, `(Lyrics)`, ...) prima della ricerca, e i titoli nel formato `Artista - Brano` vengono separati nei due campi
- prima si tenta la **corrispondenza esatta** artista+titolo+durata, poi una ricerca libera scartando i risultati con durata troppo diversa (>10 s: probabilmente live o remix)
- il testo pesa **pochi KB** (~0,1% dell'audio): l'impatto sulla dimensione del file è trascurabile
- se il testo non esiste o la rete fallisce **non succede nulla**: i testi sono un extra, mai un motivo di fallimento del download
- il riepilogo finale mostra quante tracce hanno ottenuto il testo (`♫ Testi karaoke`)
- per disattivare la ricerca: `--no-lyrics`

Esempio del testo incorporato (formato LRC):

```
[00:18.98] We're no strangers to love
[00:22.55] You know the rules and so do I (do I)
[00:26.99] A full commitment's what I'm thinking of
```

---

## Database globale

Ogni download riuscito viene registrato in `Database_Globale/scraper_metadata.db`, un database SQLite **condiviso tra più scraper** (audio, manga, anime) con un'unica tabella `downloads`:

- **Campi comuni**: tipo di scraper, ID sorgente, titolo, URL, percorso file (relativo, così sopravvive agli spostamenti della cartella), dimensione, data ISO 8601
- **Campi audio**: artista, durata, formato, numero traccia, album

Dettagli tecnici:

- **Una connessione per thread** (`threading.local`): sqlite3 vieta di condividere la stessa connessione tra thread diversi, e le scritture arrivano dai thread di download
- **Modalità WAL**: letture e scritture concorrenti senza blocchi reciproci
- **`INSERT OR REPLACE`** sul vincolo `UNIQUE(scraper_type, source_id)`: riscaricare la stessa traccia aggiorna la riga esistente invece di duplicarla
- **Errori mai bloccanti**: il database è un registro accessorio — un suo problema viene loggato come warning e non interrompe mai i download

---

## Gestione degli errori e tracce fallite

- Ogni traccia fallita (dopo tutti i retry) finisce nel **riepilogo finale** con il motivo dell'errore nel log
- Titoli e URL delle tracce fallite vengono salvati in **`failed_tracks.txt`** nella cartella di output, pronti per ritentare con `python Scraper_Audio.py --url <URL>` senza rifare la ricerca
- Il log completo di ogni sessione è in `logs/scraper_audio.log` (il logger scrive **solo su file**: righe di log a video rovinerebbero le barre di avanzamento live)
- **Ctrl+C**: il primo avvia l'arresto pulito (finiscono i download in corso, si annullano quelli in coda), il secondo forza l'uscita immediata

---

## Formati di output

| Formato | Container | Note |
|---------|-----------|------|
| `m4a` *(default)* | MP4/AAC | Qualità nativa di YouTube, **nessuna ricodifica** (rimux), supporta tag e copertina via mutagen |
| `mp3` | MPEG | Massima compatibilità con dispositivi datati; richiede ricodifica (lieve perdita teorica) |
| `opus` | Ogg/Opus | Massima efficienza qualità/dimensione; supporto dispositivi meno diffuso |

> **Consiglio:** lascia `m4a` se non hai esigenze particolari — è il formato in cui YouTube serve l'audio, quindi non c'è alcuna conversione né perdita.

---

## Licenza e note

Questo progetto è destinato a **uso personale, educativo e di ricerca**. Il download di contenuti da YouTube è soggetto ai [Termini di Servizio di YouTube](https://www.youtube.com/t/terms): assicurati di scaricare solo contenuti di cui hai il diritto di fruire offline. Le librerie utilizzate (yt-dlp, Rich, mutagen, requests) sono distribuite con le rispettive licenze open source.
