<div align="center">

# 🎧 AudioDex

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/yt--dlp-downloader-FF0000?logo=youtube&logoColor=white" alt="yt-dlp">
  <img src="https://img.shields.io/badge/FFmpeg-richiesto-007808?logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Rich-TUI-4EC820?logo=windowsterminal&logoColor=white" alt="Rich">
  <img src="https://img.shields.io/badge/Mutagen-tagging-3776AB?logo=python&logoColor=white" alt="Mutagen">
  <img src="https://img.shields.io/badge/LRCLIB-testi_karaoke-8B5CF6?logo=musicbrainz&logoColor=white" alt="LRCLIB">
  <img src="https://img.shields.io/badge/SQLite-WAL-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/m4a_·_mp3_·_opus-solo_audio-EC1C24?logo=itunes&logoColor=white" alt="Formati">
  <img src="https://img.shields.io/badge/License-PolyForm_Noncommercial-orange" alt="PolyForm Noncommercial License">
</p>

<p align="center">
  Cerca brani su <b>YouTube</b> e scaricane il <b>solo flusso audio</b> — o il <b>video intero</b>,<br>
  te lo chiede prima di partire: file di pochi MB, <b>qualità originale</b>, nessuna ricodifica.<br>
  Ogni traccia arriva già <b>taggata</b> (titolo, artista, album, copertina) e con il<br>
  <b>testo sincronizzato in stile karaoke</b> dentro il file, pronta da copiare sul telefono.<br>
  <b>Playlist intere</b> in una cartella ordinata, <b>download paralleli</b> con barre live.<br>
  <b>Niente account, niente pubblicità, niente limiti di durata.</b>
</p>

</div>

```bash
git clone https://github.com/Imkun-on/AudioDex.git
cd AudioDex
pip install -r requirements.txt

python AudioDex.py                                    # modalità interattiva
python AudioDex.py --url "https://www.youtube.com/playlist?list=..."
```

---

## 📖 Indice

**Capitolo 1 — [📋 Descrizione del progetto](#-descrizione-del-progetto)**

**Capitolo 2 — [🆚 Perché AudioDex e non i soliti convertitori online](#-perché-audiodex-e-non-i-soliti-convertitori-online)**

**Capitolo 3 — [✨ Caratteristiche](#-caratteristiche)**

**Capitolo 4 — [📦 Requisiti e installazione](#-requisiti-e-installazione)**
- 4.1 [Python](#python)
- 4.2 [FFmpeg (obbligatorio)](#ffmpeg-obbligatorio)
- 4.3 [Dipendenze Python](#dipendenze-python)

**Capitolo 5 — [🚀 Uso ed esempi](#-uso-ed-esempi)**
- 5.1 [Il flusso interattivo, passo per passo](#il-flusso-interattivo-passo-per-passo)
- 5.2 [Esempio 1 — Ricerca per nome](#esempio-1--ricerca-per-nome)
- 5.3 [Esempio 2 — Download di una playlist](#esempio-2--download-di-una-playlist)
- 5.4 [Esempio 3 — La scheda di un video singolo](#esempio-3--la-scheda-di-un-video-singolo)
- 5.5 [Esempio 4 — Uso da riga di comando](#esempio-4--uso-da-riga-di-comando)

**Capitolo 6 — [🔧 Opzioni della riga di comando](#-opzioni-della-riga-di-comando)**
- 6.1 [Playlist private](#playlist-private)

**Capitolo 7 — [🔀 Come funziona il download](#-come-funziona-il-download)**
- 7.1 [Ricerca](#1-ricerca)
- 7.2 [Normalizzazione degli URL playlist](#2-normalizzazione-degli-url-playlist)
- 7.3 [Download: audio o video](#3-download-audio-o-video)
- 7.4 [Parallelismo e avanzamento](#4-parallelismo-e-avanzamento)
- 7.5 [Anti-duplicati e retry](#5-anti-duplicati-e-retry)

**Capitolo 8 — [🔢 L'ordine delle tracce](#-lordine-delle-tracce)**
- 8.1 [Il problema](#il-problema)
- 8.2 [Come viene risolto](#come-viene-risolto)
- 8.3 [Selezioni parziali e playlist con buchi](#selezioni-parziali-e-playlist-con-buchi)
- 8.4 [Numerazione dei file già scaricati](#numerazione-dei-file-già-scaricati)

**Capitolo 9 — [🧾 Tagging dei metadati](#-tagging-dei-metadati)**

**Capitolo 10 — [🎵 Testi sincronizzati (karaoke)](#-testi-sincronizzati-karaoke)**

**Capitolo 11 — [💾 Formati di output](#-formati-di-output)**

**Capitolo 12 — [🧩 Architettura del progetto](#-architettura-del-progetto)**

**Capitolo 13 — [📊 Database globale](#-database-globale)**

**Capitolo 14 — [🧯 Gestione degli errori e tracce fallite](#-gestione-degli-errori-e-tracce-fallite)**

**Capitolo 15 — [📚 Librerie usate e perché](#-librerie-usate-e-perché)**

**Capitolo 16 — [📝 Changelog](#-changelog)**

**Capitolo 17 — [📜 Note legali](#-note-legali)**

**Capitolo 18 — [📄 Licenza](#-licenza)**

---

## 📋 Descrizione del progetto

**AudioDex** è uno strumento da terminale che trasforma un link YouTube in **file audio veri**: taggati, con copertina, con il testo dentro e ordinati come li vuoi tu.

L'idea nasce da un fastidio concreto: i convertitori online promettono "YouTube → MP3", ma poi ti servono tre clic su banner pubblicitari, il file esce senza titolo né copertina, e per un album da 12 tracce devi ripetere tutto 12 volte — ritrovandoti sul telefono una cartella di brani in ordine casuale. AudioDex fa lo stesso lavoro in un comando, per **una playlist intera**, e restituisce file già pronti per la libreria musicale.

Puoi scegliere **cosa** scaricare:

- 🔍 **cercando per nome**: digiti "linkin park in the end", scegli dai risultati in tabella;
- 📺 **un video singolo**, incollandone l'URL;
- 💿 **un'intera playlist o album**, che finisce in una **sottocartella con il suo nome**, con le tracce **numerate nell'ordine originale**.

E cosa ottieni per ogni brano:

- 🎚️ **la sola traccia audio** (`m4a`, `mp3` o `opus`): pochi MB invece di centinaia, a parità di qualità sonora — oppure il **video intero** (`mp4`, `mkv`) se lo chiedi;
- 🧾 **metadati completi**: titolo, artista, album, numero di traccia e **copertina** incorporata;
- 🎤 **il testo sincronizzato** in stile karaoke, dentro il file stesso (nessun `.lrc` sparso);
- 📱 **un nome file pulito**, senza emoji né caratteri strani: si copia sul telefono via USB senza errori.

Lo strumento è pensato per:

- 🎧 **Chi si costruisce una libreria musicale offline** ordinata e taggata come si deve
- 📱 **Chi ascolta dal telefono** senza abbonamento e senza connessione
- 💿 **Chi scarica album e playlist interi** e vuole ritrovarli nell'ordine giusto

---

## 🆚 Perché AudioDex e non i soliti convertitori online

I siti "YouTube to MP3" sono gratuiti solo in apparenza. Nella pratica:

- ti fanno cliccare su **pubblicità travestite** da pulsante di download;
- impongono un **tetto di durata** (spesso 10-20 minuti) o **una traccia alla volta**;
- restituiscono file **senza tag e senza copertina**, chiamati `video_1.mp3`;
- **ricodificano** l'audio in 128 kbps, peggiorandolo rispetto all'originale;
- per una playlist ti chiedono l'**account** o il piano **premium**.

AudioDex nasce per togliere di mezzo tutto questo:

| | Tipico convertitore online | **AudioDex** |
|---|---|---|
| **Costo reale** | gratis → poi premium / pubblicità invasiva | **gratis davvero**, gira sul tuo PC |
| **Playlist intere** | a pagamento o assenti | **sì**, in una cartella ordinata |
| **Durata massima** | spesso 10-20 min | **nessun limite** |
| **Qualità audio** | ricodifica a 128 kbps | **flusso originale**, `m4a` senza ricodifica |
| **Tag e copertina** | quasi mai | **sempre** (titolo, artista, album, traccia, cover) |
| **Testo del brano** | no | **sincronizzato, dentro il file** |
| **Ordine delle tracce** | casuale | **quello della playlist**, numerato |
| **Account obbligatorio** | frequente | **no** |
| **Download paralleli** | no | **sì** (3 di default, configurabili) |
| **Open source** | mai | **sì** |

In breve: **lo controlli tu**, gira sul **tuo computer**, e i file che ottieni sono quelli che avresti comprato.

---

## ✨ Caratteristiche

- 🔍 **Ricerca su YouTube per nome** di canzone o artista, con risultati in tabella numerata e selezione flessibile: numero singolo, intervallo (`1-5`), elenco (`1,3,7`) o `all`. Le colonne separano **titolo** e **artista** (ricavato dal formato `Artista - Brano` o dal canale), con durata e views quando disponibili
- 🎬 **Scheda del video prima di scaricare**: incollando l'URL di un video singolo compare un pannello con canale, **visualizzazioni, mi piace, iscritti**, categoria, lingua, data di pubblicazione, durata e numero di capitoli — poi ti viene chiesta conferma
- 💿 **Scheda della playlist**: canale, numero di tracce, durata totale, visualizzazioni complessive, data dell'ultimo aggiornamento e visibilità (pubblica / non in elenco), più l'avviso di quanti video sono **privati o rimossi**
- 📋 **Elenco completo delle tracce di una playlist** prima della conferma, con le stesse colonne della ricerca
- 🔗 **Download diretto da URL** di video singoli, playlist e album (YouTube `playlist?list=`, link con `&list=`, e riconoscimento dei pattern playlist di Spotify/SoundCloud)
- 🎚️ **Audio o video, lo scegli tu**: di default viene scaricato il solo flusso `bestaudio` e convertito nel formato scelto (`m4a`, `mp3`, `opus`) — un brano occupa pochi MB invece di centinaia. Serve il video intero? In modalità interattiva il programma **te lo chiede** prima di partire, e da riga di comando c'è `--media video` (`mp4` o `mkv`)
- ⚡ **Download paralleli** con pool di thread configurabile (default 3) e **avanzamento live su tre livelli**: una barra complessiva sulle tracce, **una barra per ciascuna delle quattro fasi** (Download, Conversione, Testi, Tag) e una barra per ogni file in corso con velocità e tempo stimato
- 🧾 **Tagging automatico dei metadati**: titolo, artista, album, numero traccia e **copertina** incorporata nel file (via mutagen)
- 🎤 **Testi sincronizzati stile karaoke**: per ogni traccia viene cercato il testo con i timestamp su [LRCLIB](https://lrclib.net) e **incorporato nei tag del file audio** — un file unico che porta con sé anche il testo; i lettori compatibili lo mostrano riga per riga mentre il brano suona
- 🔢 **Ordine della playlist rispettato**: i file vengono salvati con il **numero di traccia in testa al nome** (`01 - Brano.m4a`), così sul disco e sul telefono restano nell'ordine originale anche se i download finiscono in ordine sparso (vedi il [capitolo 8](#-lordine-delle-tracce))
- 💿 **Playlist organizzate**: ogni playlist/album finisce in una sottocartella con il suo nome
- ♻️ **Anti-duplicati**: le tracce già presenti su disco vengono saltate (`skip`), così si può rilanciare lo stesso download senza riscaricare nulla
- 🔁 **Retry automatici** con backoff esponenziale e jitter (fino a 4 tentativi per traccia)
- 📱 **Nomi file compatibili con i telefoni**: niente emoji né caratteri Unicode a tutta larghezza (`⧸ ： ｜`), che fanno fallire la copia via cavo USB
- 📊 **Database SQLite globale** che registra ogni download (titolo, artista, album, dimensione, durata, formato, data)
- 📄 **Esportazione delle tracce fallite** in `failed_tracks.txt` con gli URL pronti per ritentare
- 🛑 **Arresto pulito con Ctrl+C**: i download in corso terminano, quelli in coda vengono annullati; un secondo Ctrl+C forza l'uscita
- 💽 **Controllo dello spazio disco** prima di iniziare, con richiesta di conferma sotto i 200 MB liberi

---

## 📦 Requisiti e installazione

### Python

Richiede **Python 3.10+**.

### FFmpeg (obbligatorio)

FFmpeg estrae e converte l'audio nel formato scelto: senza, il download non può completarsi. Su Windows:

```powershell
winget install Gyan.FFmpeg
```

```bash
# macOS
brew install ffmpeg
# Linux (Debian/Ubuntu)
sudo apt install ffmpeg
```

In alternativa scaricalo da [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) e aggiungilo al `PATH`. Verifica con `ffmpeg -version`.

### Dipendenze Python

```bash
pip install -r requirements.txt
```

oppure manualmente:

```bash
pip install yt-dlp requests rich mutagen
```

> ⚠️ **Nota su yt-dlp:** YouTube cambia spesso le proprie API interne. Se ricerca o download smettono di funzionare, quasi sempre basta aggiornare: `pip install -U yt-dlp`

---

## 🚀 Uso ed esempi

```bash
python AudioDex.py
```

### Il flusso interattivo, passo per passo

1. **Avvio**: banner, controllo dello spazio disco, inizializzazione del database
2. **Cerca o incolla**: digita un nome di canzone/artista per cercare, oppure incolla direttamente un URL
3. **Selezione**: scegli quali risultati scaricare (numero, intervallo, elenco, `all`)
4. **Download**: le tracce vengono scaricate in parallelo con barre di avanzamento live; ogni file viene taggato (titolo, artista, album, copertina) e arricchito del testo sincronizzato se disponibile
5. **Riepilogo**: pannello finale con scaricate / già presenti / fallite
6. Il loop riparte: nuova ricerca oppure `q` per uscire

### Esempio 1 — Ricerca per nome

```
╔═════════════════════════════════════════════════╗
║                                                 ║
║      ___             ___       ____             ║
║     /   | __  ______/ (_)___  / __ \___  _  __  ║
║    / /| |/ / / / __  / / __ \/ / / / _ \| |/_/  ║
║   / ___ / /_/ / /_/ / / /_/ / /_/ /  __/>  <    ║
║  /_/  |_\__,_/\__,_/_/\____/_____/\___/_/|_|    ║
║                                                 ║
╚═════════════════════════════════════════════════╝

Modalita' interattiva
  • Digita un nome canzone/artista per cercare
  • Incolla un URL (video/playlist) per download diretto
  • Digita q per uscire

♫ Cerca o incolla URL > linkin park in the end

                            Risultati ricerca
╭──────┬───────────────────────────────┬──────────────┬────────┬─────────╮
│    # │ Titolo                        │ Artista      │ Durata │   Views │
├──────┼───────────────────────────────┼──────────────┼────────┼─────────┤
│    1 │ In The End                    │ Linkin Park  │   3:54 │ 290 Mln │
│    2 │ In the End                    │ Linkin Park  │   3:36 │ 1.2 Mrd │
│    3 │ In The End                    │ Linkin Park  │   3:31 │  45 Mln │
│  ... │                               │              │        │         │
╰──────┴───────────────────────────────┴──────────────┴────────┴─────────╯

Seleziona: numero singolo (3), intervallo (1-5), multipli (1,3,7),
all per tutti, q per uscire

Scegli > 1

─────────────────────────── ⬇ Download audio ───────────────────────────
  Thread: 3  Tracce: 1

⠋ Tracce      ████████████████████████████████  100%  1/1  │ 0:00:05
⠋ Download    ████████████████████████████████  1/1
⠋ Conversione ████████████████████████████████  1/1
⠋ Testi       ████████████████████████████████  1/1
⠋ Tag         ████████████████████████████████  1/1
──────────────────────────────────────────────
⠋ #1 In The End [Official HD...  ██████████  100%  3.6/3.6 MB  2.1 MB/s

╔═════════════ ✅ Riepilogo ═════════════╗
║                                        ║
║   Tracce totali   1                    ║
║   ✓ Scaricate     1                    ║
║   ♫ Testi karaoke 1                    ║
║                                        ║
╚════════════════════════════════════════╝

♫ Cerca o incolla URL > q

Arrivederci!
```

### Esempio 2 — Download di una playlist

Incollando l'URL di una playlist (o di un video che le appartiene, tipo `watch?v=...&list=...`), il programma la riconosce, mostra il riepilogo e chiede se scaricare tutto o selezionare le tracce:

```
♫ Cerca o incolla URL > https://www.youtube.com/playlist?list=OLAK5uy_kkk...

┌──────── 💿 Molchat Doma - Etazhi ────────┐
│                                          │
│    📺  Canale            Molchat Doma    │
│    🎵  Tracce            9               │
│    ⏱  Durata totale      33:18           │
│    👁  Visualizzazioni    2.4 Mln         │
│    📅  Aggiornata        14/03/2024      │
│    🔓  Visibilità        Pubblica        │
│                                          │
└──────────────────────────────────────────┘

                Tracce della playlist
╭──────┬─────────────────────────┬──────────────┬────────╮
│    # │ Titolo                  │ Artista      │ Durata │
├──────┼─────────────────────────┼──────────────┼────────┤
│    1 │ Na Dne                  │ Molchat Doma │   3:31 │
│    2 │ Tantsevat               │ Molchat Doma │   3:33 │
│    3 │ Volny                   │ Molchat Doma │   3:25 │
│  ... │                         │              │        │
╰──────┴─────────────────────────┴──────────────┴────────╯

Scaricare tutte le 9 tracce? (s/n)
> s

─────────────────────────── ⬇ Download audio ───────────────────────────
  Thread: 3  Tracce: 9

⠋ Tracce      ██████████████████░░░░░░░░░░  67%  6/9  │ 0:01:12 → 0:00:35
⠋ Download    ████████████████████████░░░░  8/9
⠋ Conversione ██████████████████████░░░░░░  7/9
⠋ Testi       ████████████████████░░░░░░░░  6/9
⠋ Tag         ████████████████████░░░░░░░░  6/9
──────────────────────────────────────────────
⠋ #7 Тоска           ██████████░░░░░  64%  2.1/3.3 MB  1.8 MB/s
⠋ #8 Клетка          ████░░░░░░░░░░░  28%  0.9/3.2 MB  2.0 MB/s
⠋ #9 Коммерсанты     ██░░░░░░░░░░░░░  11%  0.4/3.5 MB  1.7 MB/s
```

Le **quattro barre di fase** raccontano cosa sta succedendo davvero: scaricare un brano non è un passaggio solo, e senza di esse un file restava apparentemente fermo al 100% mentre in realtà stava ancora convertendo, cercando il testo o scrivendo i tag.

| Fase | Cosa fa |
|---|---|
| **Download** | trasferimento del flusso audio da YouTube (l'unica con i byte noti, mostrati sotto) |
| **Conversione** | FFmpeg estrae/rimuxa nel formato scelto |
| **Testi** | interrogazione di LRCLIB per il testo sincronizzato |
| **Tag** | scrittura di metadati e copertina nel file |

> Una traccia **già presente** o **fallita** non attraversa tutte le fasi: le barre vengono comunque completate a fine lavorazione, così arrivano in fondo insieme al lavoro invece di restare indietro per sempre.

Le tracce finiscono in una **sottocartella con il nome dell'album**, **numerate nell'ordine della playlist**:

```
download_audio/Molchat Doma - Etazhi/
├── 01 - Na Dne.m4a
├── 02 - Tantsevat.m4a
├── 03 - Volny.m4a
└── ...
```

Rispondendo `n` alla domanda si apre la selezione manuale (`1-5`, `1,3,7`, ecc.) usando i numeri della tabella.

> ℹ️ Nelle playlist la colonna **Views** non compare: YouTube non fornisce quel dato nell'elenco delle tracce (solo titolo e durata). L'artista viene ricavato dal titolo `Artista - Brano`; dove il formato manca compare `??`.

### Esempio 3 — La scheda di un video singolo

Incollando l'URL di un **video singolo** (senza `list=`), prima di scaricare compare la sua scheda:

```
♫ Cerca o incolla URL > https://www.youtube.com/watch?v=...

Recupero le informazioni del video...

┌─ 🎬 But what is a neural network? | Deep learning chapter 1 ─┐
│                                                              │
│    📺  Canale            3Blue1Brown                         │
│    👁  Visualizzazioni    23.7 Mln                            │
│    👍  Mi piace          553 K                               │
│    👥  Iscritti          8.5 Mln                             │
│    🏷  Categoria          Education                           │
│    🗣  Lingua             Inglese                             │
│    📅  Pubblicato        05/10/2017                          │
│    ⏱  Durata             18:40                               │
│    📑  Capitoli          12 sezioni                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘

Procedo con il download di questo video? (s/n):
```

Serve a capire a colpo d'occhio se è il video giusto prima di consumare banda. I campi che YouTube non espone vengono **omessi**, non mostrati vuoti.

> ℹ️ **Perché solo per i video singoli.** La scheda richiede l'estrazione **completa** dei metadati (`extract_flat` disattivato): è l'unica che riporta mi piace, iscritti, categoria e lingua, ma costa un paio di secondi. Per un video è tempo ben speso; su una playlist da 50 tracce sarebbero minuti di attesa, quindi lì resta l'estrazione veloce e la tabella riassuntiva.

> Con `--url` la scheda viene comunque **mostrata**, ma senza chiedere conferma: da riga di comando hai già dichiarato cosa vuoi scaricare, e un prompt bloccherebbe gli script.

### Esempio 4 — Uso da riga di comando

Per saltare la modalità interattiva:

```bash
# Ricerca una tantum (mostra i risultati e chiede la selezione)
python AudioDex.py --search "daft punk get lucky"

# Download diretto di un video o di una playlist
python AudioDex.py --url "https://www.youtube.com/watch?v=..."
python AudioDex.py --url "https://www.youtube.com/playlist?list=..."

# In mp3, in una cartella personalizzata, con 5 download paralleli
python AudioDex.py --url "https://..." --format mp3 --output "D:\Musica" --workers 5

# Video intero invece del solo audio (mp4)
python AudioDex.py --url "https://..." --media video
python AudioDex.py --url "https://..." --format mkv     # --media video implicito
```

> Con `--search`/`--url` il default resta **audio**: la domanda non viene posta, così gli script non restano appesi a un prompt.

---

## 🔧 Opzioni della riga di comando

| Opzione | Abbrev. | Default | Descrizione |
|---|---|---|---|
| `--search "testo"` | `-s` | — | Cerca per nome canzone/artista (alternativa a `--url`) |
| `--url <link>` | `-u` | — | URL diretto di video, playlist o album |
| `--output <cartella>` | `-o` | `download_audio/` | Cartella di destinazione dei file |
| `--media {audio,video}` | `-m` | *(chiesto)* | Scarica solo l'audio o il video intero. Se omesso: in modalità interattiva viene **chiesto**, con `--search`/`--url` il default è `audio` |
| `--format {m4a,mp3,opus,mp4,mkv}` | `-f` | `m4a` / `mp4` | Formato di output. I primi tre sono audio, gli ultimi due video: indicarne uno **implica** il `--media` corrispondente |
| `--workers <n>` | `-w` | `3` | Numero di download paralleli |
| `--max-results <n>` | — | `15` | Numero massimo di risultati di ricerca |
| `--no-lyrics` | — | disattivato | Non cercare i testi sincronizzati su LRCLIB |
| `--cookies-from-browser <browser>` | — | — | Usa i cookie del browser (`firefox`, `chrome`, `edge`, …) per accedere a playlist e video **privati** |

> Senza `--search` né `--url` si avvia la **modalità interattiva**.

### Playlist private

Se incolli l'URL di una tua playlist **privata**, YouTube risponde *"The playlist does not exist"*: senza autenticazione la playlist è invisibile. Due soluzioni:

1. ⭐ **Consigliata:** su YouTube imposta la playlist su **"Non in elenco"** — non diventa pubblica (è visibile solo a chi ha il link) e l'URL funziona subito, senza altre opzioni.
2. Per tenerla **privata**: avvia con `--cookies-from-browser firefox` (o il tuo browser) — yt-dlp legge i cookie e si presenta a YouTube autenticato come te.

> 🪟 **Nota per Windows:** con Chrome/Edge la lettura dei cookie può fallire per la cifratura recente del browser (prova a chiuderlo prima); con **Firefox** funziona in modo affidabile.

---

## 🔀 Come funziona il download

### 1. Ricerca

La ricerca usa il motore interno di yt-dlp con il prefisso `ytsearchN:<query>` e l'opzione `extract_flat`: vengono recuperati **solo i metadati** (titolo, canale, durata, URL) senza scaricare nulla. È la stessa tecnica usata per le playlist, dove `ignoreerrors` fa sì che i video privati o rimossi vengano saltati invece di far fallire l'intero elenco.

### 2. Normalizzazione degli URL playlist

Se si incolla l'URL di un video che fa parte di una playlist (`watch?v=...&list=...`), yt-dlp estrarrebbe **solo quel video**. Il programma estrae l'ID della playlist e lo converte nell'URL canonico `playlist?list=<ID>`, ottenendo l'elenco completo delle tracce.

### 3. Download: audio o video

**Solo audio** (default). yt-dlp viene configurato così:

```python
'format': 'bestaudio[ext=m4a]/bestaudio/best'   # niente traccia video
'postprocessors': [{'key': 'FFmpegExtractAudio',
                    'preferredcodec': <formato scelto>,
                    'preferredquality': '0'}]    # qualità massima
```

Il flusso audio migliore disponibile viene scaricato e FFmpeg lo converte nel formato scelto. Se il formato sorgente coincide (il caso di `m4a`), viene **rimuxato senza ricodifica**: nessuna perdita di qualità.

**Video intero** (`--media video`). YouTube serve video e audio come **flussi separati** — le risoluzioni alte non hanno l'audio incorporato — quindi si prende il meglio di entrambi e FFmpeg li unisce nel container scelto:

```python
'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
'merge_output_format': 'mp4'    # oppure 'mkv'
```

Il fallback `best` in coda copre i video serviti a flusso unico.

**Anche i video vengono taggati**, con la stessa cura dell'audio — cambia solo lo strumento, perché i due container usano sistemi di metadati diversi:

| | `mp4` | `mkv` |
|---|---|---|
| **Titolo, artista, album, n. traccia** | ✅ mutagen (tag iTunes) | ✅ FFmpeg |
| **Copertina** | ✅ incorporata da mutagen | ✅ allegata da yt-dlp |
| **Capitoli del video** | ✅ FFmpeg | ✅ FFmpeg |
| **Testo karaoke** | ✅ nel tag `©lyr` | ❌ il Matroska non ha un campo equivalente |

Nel dettaglio: il postprocessor `FFmpegMetadata` scrive titolo, autore, data e capitoli durante il merge — l'unica via per il Matroska, che mutagen non sa taggare. **Album e numero di traccia** non stanno nell'info di yt-dlp (li ricaviamo noi dalla playlist), quindi vengono passati a ffmpeg come argomenti espliciti: senza, un video di playlist perderebbe proprio i due campi che tengono insieme una raccolta. Per l'`mp4` interviene poi `_tag_m4a` come per l'audio, aggiungendo copertina e testo.

> ⚠️ **Attenzione allo spazio**: un video pesa da **20 a 100 volte** più del solo audio. Una playlist da 20 brani passa da ~70 MB a diversi GB.

### 4. Parallelismo e avanzamento

I download girano su un `ThreadPoolExecutor` (default 3 thread). Un *progress hook* di yt-dlp fa da ponte verso le barre Rich: ogni blocco scaricato aggiorna la barra del singolo file con i byte ricevuti, mentre la barra complessiva avanza al completamento di ogni traccia. I risultati vengono ricomposti nell'ordine originale delle entry (i thread terminano in ordine sparso).

### 5. Anti-duplicati e retry

- Prima di scaricare, il titolo — sanificato dai caratteri vietati di Windows, dai "sosia" Unicode che yt-dlp usa al loro posto e dalle emoji — viene confrontato con i file già presenti nella cartella: se esiste un file valido (>10 KB), la traccia è marcata `skip`. Il confronto avviene **tra formati dello stesso tipo**: un `.m4a` già scaricato non fa saltare lo stesso titolo richiesto in video, e viceversa.
- Il nome del file scaricato viene poi ripulito allo stesso modo: niente emoji né caratteri a tutta larghezza (es. `⧸ ： ｜`), così i brani si copiano sul telefono via cavo USB senza errori.
- In caso di errore si riprova fino a **4 volte** con backoff esponenziale + jitter casuale, per non riprovare a raffica e non sincronizzare i retry dei vari thread.

---

## 🔢 L'ordine delle tracce

### Il problema

I download partono in parallelo su più thread e finiscono in **ordine sparso**: la traccia 7, più leggera, può completarsi prima della 2. Se i file venissero salvati con il solo titolo, la cartella li mostrerebbe in **ordine alfabetico** — e un album ascoltato dal telefono partirebbe da un brano a caso.

Il tag `trkn` (numero di traccia) da solo non basta: molti lettori da telefono, e la semplice esplorazione della cartella via USB, ordinano **per nome file**.

### Come viene risolto

Per le playlist il numero di traccia entra **nel nome del file**, zero-padded:

```
download_audio/Molchat Doma - Etazhi/
├── 01 - Na Dne.m4a
├── 02 - Tantsevat.m4a
├── 03 - Volny.m4a
└── ...
```

Così l'ordine alfabetico **coincide** con quello della playlist, ovunque tu apra la cartella. Le cifre si adattano alla dimensione della playlist: una raccolta da 150 brani usa tre cifre (`007 - …`), così anche lì l'ordinamento resta corretto.

> Il prefisso viene aggiunto **solo alle playlist**. Un video singolo o una selezione da ricerca non hanno un "ordine" da preservare, quindi conservano il nome pulito.

### Selezioni parziali e playlist con buchi

Il numero usato è quello della **playlist di origine**, non la posizione nella lista scaricata:

- scarichi solo le tracce **5-8** di un album → i file escono `05`, `06`, `07`, `08`, non `01`-`04`, e si incastrano con quelli già in cartella;
- la playlist contiene un video **privato o rimosso** → viene saltato, ma le tracce successive **non scalano** di posizione: la numerazione resta fedele all'originale.

### Numerazione dei file già scaricati

Il controllo anti-duplicati riconosce lo stesso brano anche se sul disco è **senza numero**, perché scaricato con una versione precedente del programma. In quel caso il file viene semplicemente **rinominato**, non riscaricato:

```
Na Dne.m4a  →  01 - Na Dne.m4a
```

Rilanciando lo stesso comando su una vecchia cartella, quindi, la numerazione si allinea **senza consumare banda**.

> ⚠️ **Un file che ha già un numero non viene mai rinominato**, nemmeno se la playlist è stata riordinata: in quel caso la traccia viene riscaricata con il numero nuovo e il vecchio file resta lì (puoi cancellarlo a mano).
>
> Il motivo è che una playlist può contenere **due tracce con lo stesso titolo** — succede spesso, es. lo stesso brano in versione singolo e in versione album. Riconoscendo "stesso titolo, numero qualsiasi", le due tracce si contenderebbero **lo stesso file**, rinominandolo a vicenda: ne resterebbe uno solo e la seconda non verrebbe mai scaricata. Meglio un file di troppo che una traccia persa.

---

## 🧾 Tagging dei metadati

Dopo il download, ogni file `.m4a` viene taggato con **mutagen** usando i tag standard iTunes (i file `.m4a` usano il container MP4):

| Tag | Contenuto | Fonte |
|---|---|---|
| `©nam` | Titolo | Metadati YouTube |
| `©ART` | Artista | Campo `artist` o, in mancanza, il nome del canale |
| `©alb` | Album | Nome della playlist (o campo `album` di YouTube) |
| `trkn` | Numero traccia | Posizione nella playlist di origine |
| `covr` | Copertina | Thumbnail del video, scaricata e incorporata (JPEG/PNG) |
| `©lyr` | Testo | LRCLIB, formato LRC con timestamp (vedi capitolo 10) |

Gli stessi tag vengono scritti nei video **`.mp4`**, che condividono il container MP4 con l'`.m4a`. Per i **`.mkv`** i metadati li scrive FFmpeg durante il merge (vedi [7.3](#3-download-audio-o-video)).

> Se mutagen non è installato il tagging viene semplicemente saltato: i file restano validi, solo senza metadati.

---

## 🎵 Testi sincronizzati (karaoke)

Dopo ogni download riuscito, il programma interroga **[LRCLIB](https://lrclib.net)** (API gratuita, senza chiave) con artista, titolo e durata della traccia. Se il testo esiste, viene **incorporato direttamente nel tag `©lyr` del file m4a**, in formato LRC con i timestamp: il brano resta **un file unico** che porta con sé anche il testo, su PC come su telefono.

I lettori che leggono il testo dai tag (**Musicolet**, **Oto Music**, **AIMP**, **Samsung Music** su Android; **MusicBee**, **foobar2000**, **AIMP** su PC) lo mostrano **riga per riga in stile karaoke**; quelli più basilari lo mostrano come testo statico.

Esempio del testo incorporato:

```
[00:18.98] We're no strangers to love
[00:22.55] You know the rules and so do I (do I)
[00:26.99] A full commitment's what I'm thinking of
```

Dettagli del funzionamento:

- il titolo YouTube viene **ripulito** dalle decorazioni (`(Official Video)`, `[HD]`, `(Lyrics)`, …) prima della ricerca, e i titoli nel formato `Artista - Brano` vengono separati nei due campi;
- prima si tenta la **corrispondenza esatta** artista + titolo + durata, poi una ricerca libera scartando i risultati con durata troppo diversa (>10 s: probabilmente live o remix);
- il testo pesa **pochi KB** (~0,1% dell'audio): l'impatto sulla dimensione del file è trascurabile;
- se il testo non esiste o la rete fallisce **non succede nulla**: i testi sono un extra, mai un motivo di fallimento del download;
- il riepilogo finale mostra quante tracce hanno ottenuto il testo (`♫ Testi karaoke`);
- per disattivare la ricerca: `--no-lyrics`.

---

## 💾 Formati di output

| Formato | Container | Note |
|---|---|---|
| `m4a` ⭐ *(default)* | MP4/AAC | Qualità nativa di YouTube, **nessuna ricodifica** (rimux), supporta tag e copertina via mutagen |
| `mp3` | MPEG | Massima compatibilità con dispositivi datati; richiede ricodifica (lieve perdita teorica) |
| `opus` | Ogg/Opus | Massima efficienza qualità/dimensione; supporto dispositivi meno diffuso |
| `mp4` ⭐ *(video)* | MP4/H.264 | Il default per `--media video`: nessuna ricodifica e **tag completi** (titolo, artista, album, traccia, copertina, testo) come l'`m4a` |
| `mkv` *(video)* | Matroska | Container più permissivo, utile quando i flussi migliori non stanno in un mp4. Tag e copertina ci sono, scritti da FFmpeg; manca solo il **testo karaoke**, che nel Matroska non ha un campo equivalente |

> 💡 **Consiglio:** lascia `m4a` se non hai esigenze particolari — è il formato in cui YouTube serve l'audio, quindi non c'è alcuna conversione né perdita. Per il video vale lo stesso con `mp4`.

---

## 🧩 Architettura del progetto

```
AudioDex/
├── AudioDex.py          # CLI principale: ricerca, selezione, download, UI Rich
├── Shared/
│   ├── __init__.py
│   ├── logger_setup.py       # Logger su file + tema/simboli Rich condivisi
│   └── http_client.py        # Utilità HTTP condivise (User-Agent, header, backoff retry)
├── Database_Globale/
│   ├── scraper_db.py         # Database SQLite globale dei download
│   └── scraper_metadata.db   # Il database (creato automaticamente, escluso da git)
├── download_audio/           # Cartella di output (creata automaticamente, esclusa da git)
├── logs/
│   └── audiodex.log     # Log dettagliato di ogni sessione (escluso da git)
├── requirements.txt          # Dipendenze Python
└── README.md
```

I moduli `Shared/` e `Database_Globale/` sono progettati per essere **condivisi tra più scraper** (audio, manga, anime): stesso tema grafico, stesso logging, stesso database con colonne specifiche per tipo.

---

## 📊 Database globale

Ogni download riuscito viene registrato in `Database_Globale/scraper_metadata.db`, un database SQLite **condiviso tra più scraper** con un'unica tabella `downloads`:

- **Campi comuni**: tipo di scraper, tipo di media (`audio`/`video`), ID sorgente, titolo, URL, percorso file (relativo, così sopravvive agli spostamenti della cartella), dimensione, data ISO 8601
- **Campi audio**: artista, durata, formato, numero traccia, album

Dettagli tecnici:

- 🧵 **Una connessione per thread** (`threading.local`): sqlite3 vieta di condividere la stessa connessione tra thread diversi, e le scritture arrivano dai thread di download
- ⚡ **Modalità WAL**: letture e scritture concorrenti senza blocchi reciproci
- ♻️ **`INSERT OR REPLACE`** sul vincolo `UNIQUE(scraper_type, source_id, media_kind)`: riscaricare la stessa traccia **nello stesso formato** aggiorna la riga esistente invece di duplicarla, mentre la versione **audio** e quella **video** dello stesso video YouTube convivono come due righe — sono due file distinti sul disco
- 🔄 **Migrazione automatica**: i database creati prima dell'arrivo del download video hanno la vecchia chiave `UNIQUE(scraper_type, source_id)`, che SQLite non sa modificare con un `ALTER TABLE`. Al primo avvio la tabella viene **ricostruita** e i dati ricopiati, dentro un'unica transazione e dopo una **copia di sicurezza** del file (`scraper_metadata.db.backup-pre-media-kind`). Le righe storiche vengono etichettate come `audio`. Se qualcosa va storto la migrazione si annulla e i dati restano intatti
- 🛡️ **Errori mai bloccanti**: il database è un registro accessorio — un suo problema viene loggato come warning e non interrompe mai i download

---

## 🧯 Gestione degli errori e tracce fallite

- Ogni traccia fallita (dopo tutti i retry) finisce nel **riepilogo finale**, con il motivo dell'errore nel log
- Titoli e URL delle tracce fallite vengono salvati in **`failed_tracks.txt`** nella cartella di output, pronti per ritentare con `python AudioDex.py --url <URL>` senza rifare la ricerca
- Il log completo di ogni sessione è in `logs/audiodex.log` — il logger scrive **solo su file**: righe di log a video rovinerebbero le barre di avanzamento live
- 🛑 **Ctrl+C**: il primo avvia l'arresto pulito (finiscono i download in corso, si annullano quelli in coda), il secondo forza l'uscita immediata

---

## 📚 Librerie usate e perché

| Libreria | A cosa serve | Perché proprio questa |
|---|---|---|
| `yt-dlp` | Ricerca su YouTube ed estrazione/download del flusso audio | Lo standard de facto: gestisce stream, playlist, resume e metadati |
| `requests` | Download della copertina e chiamate a LRCLIB | Semplice e onnipresente; qui bastano due GET |
| `rich` | Interfaccia da terminale: tabelle, pannelli, barre live | Trasforma la CLI in un'esperienza curata (`Table`, `Progress`, `Live`) |
| `mutagen` | *(opzionale)* Metadati e copertina nei file `.m4a` | Pure-python, legge/scrive i tag MP4 (iTunes) senza dipendenze esterne |

### Strumento esterno (non pip)

| Strumento | A cosa serve | Note |
|---|---|---|
| **[FFmpeg](https://ffmpeg.org)** | Estrazione e conversione dell'audio | **Obbligatorio**, da installare una volta. Con `m4a` non ricodifica: si limita al rimux |

### Servizio esterno (nessuna chiave)

| Servizio | A cosa serve | Note |
|---|---|---|
| **[LRCLIB](https://lrclib.net)** | Testi sincronizzati (LRC) | API pubblica e gratuita, **senza registrazione né chiave**. Se non risponde, il download prosegue lo stesso |

### Libreria standard (nessuna installazione)

`os`, `re`, `json`, `shutil`, `signal`, `time`, `random`, `threading`, `sqlite3`, `concurrent.futures`: percorsi e file, regex, spazio disco, gestione Ctrl+C, backoff dei retry, pool di thread e database.

---

## 📝 Changelog

### 2026-07-19

**Nuove funzionalità**

- 🔢 **Ordine della playlist rispettato sul disco**: i file delle playlist vengono salvati con il numero di traccia in testa al nome (`01 - Brano.m4a`), zero-padded sulla dimensione della playlist. Il numero è quello della **playlist di origine**: una selezione parziale (tracce 5-8) mantiene `05`-`08`, e un video rimosso non fa scalare le tracce successive
- ♻️ **Numerazione dei file già scaricati**: i brani già presenti **senza numero** (scaricati con una versione precedente) vengono **rinominati** invece che riscaricati — rilanciare il download su una vecchia cartella allinea la numerazione a costo zero
- 📊 **Barre di avanzamento per fase**: quattro barre (Download, Conversione, Testi, Tag) mostrano quante tracce hanno superato ciascun passaggio. Prima esisteva solo la barra dei byte, che restava al 100% mentre la traccia stava ancora convertendo, cercando il testo o scrivendo i tag — sembrava piantata
- 🎬 **Download del video intero**, oltre al solo audio: in modalità interattiva viene **chiesto** prima di partire, da riga di comando c'è `--media video` (o direttamente `--format mp4`/`mkv`). Anche i video vengono **taggati come l'audio** (titolo, artista, album, numero di traccia, copertina, capitoli): nell'`mp4` con mutagen, nell'`mkv` con FFmpeg. L'anti-duplicati ora distingue i formati audio da quelli video, così lo stesso brano può esistere in entrambe le versioni
- 🎬 **Scheda del video prima del download**: incollando l'URL di un video singolo compare un pannello con canale, visualizzazioni, mi piace, iscritti, categoria, lingua, data e capitoli, seguito da una richiesta di conferma. Prima un URL di video singolo faceva partire il download **senza mostrare nulla**
- 💿 **Scheda della playlist arricchita**: al riepilogo si aggiungono canale, visualizzazioni complessive, data dell'ultimo aggiornamento, visibilità e il numero di video **non disponibili**. Erano dati che yt-dlp già restituiva nella stessa chiamata e che venivano scartati: **nessuna richiesta di rete in più**
- 🗄️ **Database: audio e video convivono**. La chiave univoca comprende il **tipo di media**, quindi scaricare lo stesso video prima in audio e poi in video non sovrascrive più la riga precedente. I database esistenti vengono **migrati automaticamente** al primo avvio, con copia di sicurezza

**Correzioni**

- 🐛 **«Fallite» che erano in realtà tracce già presenti**: nel ramo «già scaricato» si leggeva `progress.tasks[task_id]`, ma `Progress.tasks` di Rich è una **lista posizionale**, non indicizzata per `TaskID`. Poiché le barre dei file completati vengono rimosse man mano, gli indici scalavano e partiva un `IndexError`, che `download_batch` catturava marcando la traccia come **fallita** — pur avendo il file sano su disco. Su una playlist tutta già scaricata il riepilogo mostrava metà tracce «Fallite»
- 🐛 **Tracce omonime che si contendevano lo stesso file**: con due brani dallo stesso titolo nella stessa playlist (es. versione singolo e versione album), la rinumerazione riconosceva «stesso titolo, numero qualsiasi» e le due tracce si rinominavano il file a vicenda, lasciandone scaricare una sola. Ora un file **già numerato non viene mai rinominato**
- 🐛 **Ordine dei risultati nel riepilogo**: il riordino finale confrontava i **titoli**, quindi due tracce omonime (o un titolo cambiato da yt-dlp) finivano fuori posto o in fondo. Ora i risultati sono ricomposti dalla **posizione della traccia**

### 2026-06-11

**Correzioni**

- **Ricerca YouTube riparata**: l'opzione `default_search` di yt-dlp restituiva sempre 0 risultati con le versioni recenti — ora la ricerca usa il prefisso esplicito `ytsearchN:`. Aggiornato anche yt-dlp alla 2026.6.9 e vincolata come versione minima in `requirements.txt`
- **Import compatibile con gli IDE**: `scraper_db` viene importato come `from Database_Globale import scraper_db` invece che tramite manipolazione di `sys.path`, così Pylance/VS Code lo risolvono senza falsi errori
- **Fallback artista/canale**: i campi `uploader`/`channel` con valore `None` non producono più "None" nelle tabelle
- **Nomi dei file compatibili con i telefoni**: `_sanitize_filename` ora converte in `_` i "sosia" Unicode a tutta larghezza che yt-dlp usa al posto dei caratteri vietati (`/ : | ? * " < >` → `⧸ ： ｜ …`) e rimuove le emoji; dopo il download il file viene rinominato di conseguenza. Questi caratteri facevano fallire la copia delle tracce verso il telefono tramite cavo USB

**Modifiche**

- **Solo audio**: rimosso del tutto il percorso di download video. Il default è passato da `mp4` (video completo) a `m4a` (solo traccia audio): file di pochi MB invece di centinaia, a parità di qualità sonora. Formati disponibili: `m4a`, `mp3`, `opus`
- **Documentazione del codice in italiano**: ogni funzione, classe e modulo ha una docstring che spiega cosa fa e perché esiste; commenti mirati sulle parti non ovvie (opzioni yt-dlp, threading, database)

**Nuove funzionalità**

- **Testi sincronizzati stile karaoke**: dopo ogni download il testo con i timestamp viene cercato su LRCLIB e incorporato nei tag del file audio (formato LRC) — un file unico con dentro anche il testo. Riepilogo con conteggio `♫ Testi karaoke`; disattivabile con `--no-lyrics`
- **Playlist e video privati**: nuova opzione `--cookies-from-browser <browser>` che autentica yt-dlp con i cookie del browser; documentata anche l'alternativa più semplice (playlist "Non in elenco")
- **Tabella delle tracce di una playlist** mostrata prima della conferma di download, e colonna **Views** (formato compatto: `2.1 Mrd`, `45 Mln`, `350 K`) dove YouTube fornisce il dato — nelle playlist non lo espone, quindi lì la colonna è nascosta. I like non sono mostrati: recuperarli costerebbe ~5 s per traccia
- **Colonne Titolo e Artista separate**: l'artista viene ricavato dal titolo (`Artista - Brano`) o dal nome del canale, e il titolo viene ripulito dalle decorazioni (`(Official Video)`, `(Lyrics)`, …)
- **`requirements.txt`** con versioni minime e note su FFmpeg e sull'aggiornamento frequente di yt-dlp
- **Repository GitHub** con `.gitignore` che esclude contenuti scaricati, database locale e log

---

## 📜 Note legali

AudioDex scarica contenuti da YouTube. L'uso potrebbe essere soggetto ai [Termini di Servizio di YouTube](https://www.youtube.com/t/terms) e alle norme sul **diritto d'autore** della tua giurisdizione. È pensato per uso **personale ed educativo** (es. ascoltare offline musica di cui hai i diritti): usalo in modo responsabile e solo per contenuti di cui hai il diritto di fruire.

Le librerie utilizzate (yt-dlp, Rich, mutagen, requests) sono distribuite con le rispettive licenze open source.

---

## 📄 Licenza

Rilasciato sotto **[PolyForm Noncommercial License 1.0.0](LICENSE)**.

In breve — **non è un riassunto legale, fa fede il testo della licenza**:

- ✅ **Puoi** usare, studiare, modificare e ridistribuire AudioDex per **scopi non commerciali**: uso personale, ricerca, progetti hobbistici, e uso da parte di **enti caritatevoli o educativi** (scuole, università).
- ❌ **Non puoi** usarlo per scopi commerciali: venderlo, offrirlo come servizio a pagamento, o usarlo nell'attività di un'azienda.
- 📎 Se lo ridistribuisci, devi **allegare la licenza** (o il suo URL) e mantenere la riga `Required Notice:`.

> Serve un uso commerciale? Scrivimi: una licenza separata è negoziabile.
