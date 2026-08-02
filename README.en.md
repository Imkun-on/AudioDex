<div align="center">

# 🎧 AudioDex

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/yt--dlp-downloader-FF0000?logo=youtube&logoColor=white" alt="yt-dlp">
  <img src="https://img.shields.io/badge/FFmpeg-required-007808?logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Rich-TUI-4EC820?logo=windowsterminal&logoColor=white" alt="Rich">
  <img src="https://img.shields.io/badge/Mutagen-tagging-3776AB?logo=python&logoColor=white" alt="Mutagen">
  <img src="https://img.shields.io/badge/Requests-HTTP-2C5BB4?logo=curl&logoColor=white" alt="Requests">
  <img src="https://img.shields.io/badge/LRCLIB-karaoke_lyrics-8B5CF6?logo=musicbrainz&logoColor=white" alt="LRCLIB">
  <img src="https://img.shields.io/badge/SQLite-WAL-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/m4a_·_mp3_·_opus-audio_only-EC1C24?logo=itunes&logoColor=white" alt="Formats">
  <img src="https://img.shields.io/badge/License-PolyForm_Noncommercial-orange" alt="PolyForm Noncommercial License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/BurnDex-audio_CD-BD10E0?logo=compactdisc&logoColor=white" alt="BurnDex">
  <img src="https://img.shields.io/badge/IMAPI2-native_COM-0078D4?logo=windows&logoColor=white" alt="IMAPI2">
  <img src="https://img.shields.io/badge/pywin32-COM_bridge-3776AB?logo=python&logoColor=white" alt="pywin32">
  <img src="https://img.shields.io/badge/Red_Book-CD--DA_44.1kHz_16bit-C0392B?logo=audiomack&logoColor=white" alt="Red Book">
  <img src="https://img.shields.io/badge/Windows-burning_only-0078D4?logo=windows11&logoColor=white" alt="Windows">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AudioDexGUI-desktop_UI-06B6D4?logo=materialdesign&logoColor=white" alt="AudioDexGUI">
  <img src="https://img.shields.io/badge/Flet-0.86-02569B?logo=flutter&logoColor=white" alt="Flet">
  <img src="https://img.shields.io/badge/Flutter-rendering_engine-42A5F5?logo=flutter&logoColor=white" alt="Flutter">
  <img src="https://img.shields.io/badge/flet--video-looping_background-8E44AD?logo=vlcmediaplayer&logoColor=white" alt="flet-video">
  <img src="https://img.shields.io/badge/Theme-dark_cyberpunk-EC4899?logo=neovim&logoColor=white" alt="Dark theme">
  <img src="https://img.shields.io/badge/i18n-🇮🇹_IT_·_🇬🇧_EN-16A34A" alt="i18n">
</p>

<p align="center">
  Search <b>YouTube</b> and download the <b>audio stream only</b> — or the <b>full video</b>,<br>
  it asks you first: a few MB per track, <b>original quality</b>, no re-encoding.<br>
  Every track arrives already <b>tagged</b> (title, artist, album, cover art) and with<br>
  <b>time-synced karaoke lyrics</b> inside the file, ready to copy to your phone.<br>
  <b>Entire playlists</b> in a tidy folder, <b>parallel downloads</b> with live progress bars.<br>
  <b>No account, no ads, no duration limits.</b>
</p>

<p align="center">
  <b>And when you listen in the car</b>, <code>BurnDex.py</code> turns a downloaded collection into a<br>
  <b>real audio CD</b> (Red Book CD-DA) that any car stereo or ageing hi-fi can read:<br>
  native Windows APIs, no third-party burning software.
</p>

<p align="center">
  <a href="README.md">🇮🇹 Italiano</a>  ·  🇬🇧 <b>English</b>
</p>

</div>

**Install** — this block is safe to paste as a whole:

```bash
git clone https://github.com/Imkun-on/AudioDex.git
cd AudioDex
pip install -r requirements.txt
```

**Usage** — these lines are alternatives: run **one** at a time.

```bash
python AudioDex.py                                    # interactive mode
python AudioDex.py --url "https://www.youtube.com/playlist?list=..."
```

```bash
python BurnDex.py --info                              # what's in the drive
python BurnDex.py                                     # burn a collection to an audio CD
```

```bash
python AudioDexGUI.py                                 # both tools, graphical interface
```

> 🎞️ **The GUI background video is not in the repository** (74 MB would slow down every
> `git clone`): it lives as an attachment of the [`assets-v1` Release](https://github.com/Imkun-on/AudioDex/releases/tag/assets-v1)
> and is downloaded **once, on first launch**, in the background. The window opens right away:
> until the download finishes — or if it fails — the background is a dark purple gradient.

> 🌍 **A note on the screenshots.** Both tools speak **English or Italian** — they ask
> which one you want on first launch, see [Interface language](#-interface-language).
> The terminal transcripts throughout this document were captured before the English
> interface existed, so they show the Italian output verbatim; the layout is identical
> in English, only the words differ.

---

## 📖 Table of contents

**Chapter 1 — [📋 Project description](#-project-description)**

**Chapter 2 — [🆚 Why AudioDex instead of the usual online converters](#-why-audiodex-instead-of-the-usual-online-converters)**

**Chapter 3 — [✨ Features](#-features)**

**Chapter 4 — [📦 Requirements and installation](#-requirements-and-installation)**
- 4.1 [Python](#python)
- 4.2 [FFmpeg (required)](#ffmpeg-required)
- 4.3 [Python dependencies](#python-dependencies)
- 4.4 [🌍 Interface language](#-interface-language)

**Chapter 5 — [🚀 Usage and examples](#-usage-and-examples)**
- 5.1 [The interactive flow, step by step](#the-interactive-flow-step-by-step)
- 5.2 [Example 1 — Search by name](#example-1--search-by-name)
- 5.3 [Example 2 — Downloading a playlist](#example-2--downloading-a-playlist)
- 5.4 [Example 3 — The single-video card](#example-3--the-single-video-card)
- 5.5 [Example 4 — Command-line usage](#example-4--command-line-usage)

**Chapter 6 — [🔧 Command-line options](#-command-line-options)**
- 6.1 [Private playlists](#private-playlists)

**Chapter 7 — [🔀 How downloading works](#-how-downloading-works)**
- 7.1 [Search](#1-search)
- 7.2 [Playlist URL normalisation](#2-playlist-url-normalisation)
- 7.3 [Download: audio or video](#3-download-audio-or-video)
- 7.4 [Parallelism and progress](#4-parallelism-and-progress)
- 7.5 [Duplicate detection and retries](#5-duplicate-detection-and-retries)

**Chapter 8 — [🔢 Track ordering](#-track-ordering)**
- 8.1 [The problem](#the-problem)
- 8.2 [How it is solved](#how-it-is-solved)
- 8.3 [Partial selections and playlists with gaps](#partial-selections-and-playlists-with-gaps)
- 8.4 [Numbering already-downloaded files](#numbering-already-downloaded-files)

**Chapter 9 — [🧾 Metadata tagging](#-metadata-tagging)**

**Chapter 10 — [🎵 Synced lyrics (karaoke)](#-synced-lyrics-karaoke)**

**Chapter 11 — [💾 Output formats](#-output-formats)**

**Chapter 12 — [💿 BurnDex — burning an audio CD](#-burndex--burning-an-audio-cd)**
- 12.1 [What it is for, and why an audio CD](#what-it-is-for-and-why-an-audio-cd)
- 12.2 [Additional requirements](#additional-requirements)
- 12.3 [The four-step flow](#the-four-step-flow)
- 12.4 [Command-line options](#command-line-options-burndex)
- 12.5 [Track order on the disc](#track-order-on-the-disc)
- 12.6 [Recognised disc types](#recognised-disc-types)
- 12.7 [System detection](#system-detection)
- 12.8 [How writing works (IMAPI2)](#how-writing-works-imapi2)
- 12.9 [Audio CD limits](#audio-cd-limits)
- 12.10 [Error diagnosis](#error-diagnosis)

**Chapter 13 — [🧩 Project architecture](#-project-architecture)**

**Chapter 14 — [📊 Global database](#-global-database)**

**Chapter 15 — [🧯 Error handling and failed tracks](#-error-handling-and-failed-tracks)**

**Chapter 16 — [📚 Libraries used, and why](#-libraries-used-and-why)**

**Chapter 17 — [📝 Changelog](#-changelog)**

**Chapter 18 — [📜 Legal notes](#-legal-notes)**

**Chapter 19 — [📄 Licence](#-licence)**

---

## 📋 Project description

**AudioDex** is a terminal tool that turns a YouTube link into **real audio files**: tagged, with cover art, with the lyrics inside, and ordered the way you want them.

The idea comes from a concrete annoyance: online converters promise "YouTube → MP3", but then you need three clicks on ad banners, the file comes out with no title and no cover art, and for a 12-track album you have to repeat everything 12 times — ending up with a folder of randomly ordered songs on your phone. AudioDex does the same job in one command, for **an entire playlist**, and hands back files that are already ready for your music library.

You can choose **what** to download:

- 🔍 **by searching a name**: you type "linkin park in the end" and pick from a results table;
- 📺 **a single video**, by pasting its URL;
- 💿 **a whole playlist or album**, which lands in a **subfolder named after it**, with tracks **numbered in the original order**.

And what you get for each song:

- 🎚️ **the audio track only** (`m4a`, `mp3` or `opus`): a few MB instead of hundreds, at identical sound quality — or the **full video** (`mp4`, `mkv`) if you ask for it;
- 🧾 **complete metadata**: title, artist, album, track number and embedded **cover art**;
- 🎤 **time-synced lyrics** in karaoke style, inside the file itself (no scattered `.lrc` files);
- 📱 **a clean filename**, without emoji or odd characters: it copies to a phone over USB without errors.

The tool is aimed at:

- 🎧 **People building an offline music library** that is properly ordered and tagged
- 📱 **People who listen from a phone** without a subscription and without a connection
- 💿 **People who download whole albums and playlists** and want them in the right order

---

## 🆚 Why AudioDex instead of the usual online converters

"YouTube to MP3" sites are only free on the surface. In practice they:

- make you click **ads disguised** as a download button;
- impose a **duration cap** (often 10-20 minutes) or **one track at a time**;
- hand back files **with no tags and no cover art**, named `video_1.mp3`;
- **re-encode** the audio to 128 kbps, making it worse than the original;
- ask for an **account** or a **premium** plan for playlists.

AudioDex exists to get all of that out of the way:

| | Typical online converter | **AudioDex** |
|---|---|---|
| **Real cost** | free → then premium / invasive ads | **genuinely free**, runs on your PC |
| **Whole playlists** | paid or absent | **yes**, in a tidy folder |
| **Maximum duration** | often 10-20 min | **no limit** |
| **Audio quality** | re-encoded to 128 kbps | **original stream**, `m4a` with no re-encoding |
| **Tags and cover art** | almost never | **always** (title, artist, album, track, cover) |
| **Song lyrics** | no | **time-synced, inside the file** |
| **Track order** | random | **the playlist's**, numbered |
| **Account required** | often | **no** |
| **Parallel downloads** | no | **yes** (3 by default, configurable) |
| **Open source** | never | **yes** |

In short: **you are in control**, it runs on **your computer**, and the files you get are the ones you would have bought.

---

## ✨ Features

- 🔍 **Search YouTube by song or artist name**, with results in a numbered table and flexible selection: single number, range (`1-5`), list (`1,3,7`) or `all`. Columns separate **title** and **artist** (derived from the `Artist - Song` format or from the channel), with duration and view count where available
- 🎬 **A video card before downloading**: pasting a single video's URL brings up a panel with channel, **views, likes, subscribers**, category, language, publication date, duration and chapter count — then it asks for confirmation
- 💿 **A playlist card**: channel, track count, total duration, aggregate views, last-updated date and visibility (public / unlisted), plus a warning about how many videos are **private or removed**
- 📋 **The full track list of a playlist** before confirming, with the same columns as the search
- 🔗 **Direct download from a URL** for single videos, playlists and albums (YouTube `playlist?list=`, links with `&list=`, and recognition of Spotify/SoundCloud playlist patterns)
- 🎚️ **Audio or video, your choice**: by default only the `bestaudio` stream is downloaded and converted to the chosen format (`m4a`, `mp3`, `opus`) — a song takes a few MB instead of hundreds. Need the full video? In interactive mode the program **asks you** before starting, and from the command line there is `--media video` (`mp4` or `mkv`)
- ⚡ **Parallel downloads** with a configurable thread pool (3 by default) and **live progress at three levels**: an overall bar across tracks, **one bar for each of the four phases** (Download, Conversion, Lyrics, Tags) and one bar per file in flight with speed and ETA
- 🧾 **Automatic metadata tagging**: title, artist, album, track number and embedded **cover art** (via mutagen)
- 🎤 **Karaoke-style synced lyrics**: for each track the timestamped lyrics are looked up on [LRCLIB](https://lrclib.net) and **embedded in the audio file's tags** — a single file that carries its own lyrics; compatible players show them line by line as the song plays
- 🔢 **Playlist order preserved**: files are saved with the **track number at the front of the name** (`01 - Song.m4a`), so on disk and on your phone they stay in the original order even though downloads finish out of order (see [chapter 8](#-track-ordering))
- 💿 **Organised playlists**: each playlist/album lands in a subfolder named after it
- ♻️ **Duplicate detection**: tracks already on disk are skipped (`skip`), so you can re-run the same download without fetching anything again
- 🔁 **Automatic retries** with exponential backoff and jitter (up to 4 attempts per track)
- 📱 **Phone-friendly filenames**: no emoji, no full-width Unicode characters (`⧸ ： ｜`), which break copying over a USB cable
- 📊 **A global SQLite database** recording every download (title, artist, album, size, duration, format, date)
- 📄 **Export of failed tracks** to `failed_tracks.txt` with URLs ready for a retry
- 🛑 **Clean shutdown with Ctrl+C**: downloads in flight finish, queued ones are cancelled; a second Ctrl+C forces the exit
- 💽 **Disk-space check** before starting, asking for confirmation below 200 MB free
- 💿 **Audio CD burning** with [BurnDex](#-burndex--burning-an-audio-cd): a downloaded collection becomes a **CD-DA** readable by any car stereo, through native Windows APIs. It recognises the type of disc inserted, tells internal drives from USB ones, and with `--dry-run` rehearses everything without consuming a CD-R

---

## 📦 Requirements and installation

### Python

Python **3.10 or later** (the code uses the `X | Y` type-union syntax).

### FFmpeg (required)

FFmpeg extracts and converts the audio into the chosen format: without it a download cannot complete. On Windows:

```powershell
winget install Gyan.FFmpeg
```

On macOS:

```bash
brew install ffmpeg
```

On Linux (Debian/Ubuntu):

```bash
sudo apt install ffmpeg
```

Alternatively download it from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add it to your `PATH`. Verify with `ffmpeg -version`.

### Python dependencies

```bash
pip install -r requirements.txt
```

or manually:

```bash
pip install yt-dlp requests rich mutagen
pip install pywin32          # BurnDex only (CD burning, Windows)
```

> ⚠️ **A note on yt-dlp:** YouTube changes its internal APIs often. If search or downloads stop working, updating almost always fixes it: `pip install -U yt-dlp`

> 💿 **`pywin32` is only needed by BurnDex**, and only on Windows. AudioDex works without it. If it is missing, `BurnDex.py --dry-run` still runs every check on the track list and simply skips querying the drive.

### 🌍 Interface language

**Italian or English.** On first launch, both AudioDex and BurnDex ask which language you want to work in. The question is asked **in English**, because it is the one language anyone who does not speak Italian can certainly read:

```
┌───────┬────────────┐
│    1  │  English   │
│    2  │  Italiano  │
└───────┴────────────┘

Language / Lingua (1-2, Enter = English):
```

Choose `1` and **everything** switches to English: prompts, tables, panels, progress bars, summaries, error messages and the `--help` texts. Nothing is left half-translated.

The answer is **remembered** in `settings.json`, next to the scripts, and is not asked again on later runs. To change it:

```bash
python AudioDex.py --lang ask     # asks again and re-saves the answer
```

For a single run, without touching the stored preference:

```bash
python AudioDex.py --lang en --url "https://..."
python BurnDex.py -l en --info
```

**What is not translated.** The log files in `logs/` and the code comments stay in Italian: they are for whoever maintains the program, not for whoever uses it.

> ⚙️ **The question is not asked in non-interactive runs.** With `--url`, `--search` or `--yes` there is nobody there to answer, and hanging on a prompt would block a script: the stored preference applies, or Italian if there is not one yet. To pin the language inside a script, use `--lang`.

> 🗣 **Answers work in both languages.** Both `s` and `y` count as confirmation, `q` and `esci` as quit, whichever language you picked: someone running the English interface who types `s` out of habit does not get the operation cancelled.

---

## 🚀 Usage and examples

```bash
python AudioDex.py
```

### The interactive flow, step by step

1. **Startup**: banner, disk-space check, database initialisation
2. **Search or paste**: type a song/artist name to search, or paste a URL directly
3. **Selection**: choose which results to download (number, range, list, `all`)
4. **Download**: tracks are downloaded in parallel with live progress bars; each file is tagged (title, artist, album, cover art) and enriched with synced lyrics when available
5. **Summary**: a final panel with downloaded / already present / failed
6. The loop starts again: a new search, or `q` to quit

### Example 1 — Search by name

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

### Example 2 — Downloading a playlist

Paste a playlist URL (or the URL of a video belonging to one, e.g. `watch?v=...&list=...`) and the program recognises it, shows the summary and asks whether to download everything or select tracks:

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

The **four phase bars** tell you what is actually happening: downloading a song is not a single step, and without them a file would appear stuck at 100% while it was in fact still converting, looking up lyrics or writing tags.

| Phase | What it does |
|---|---|
| **Download** (*Download*) | transferring the audio stream from YouTube (the only phase with known byte counts, shown below) |
| **Conversion** (*Conversione*) | FFmpeg extracts/remuxes into the chosen format |
| **Lyrics** (*Testi*) | querying LRCLIB for synced lyrics |
| **Tags** (*Tag*) | writing metadata and cover art into the file |

> A track that is **already present** or has **failed** does not go through every phase: the bars are completed anyway at the end of processing, so they reach the end together with the work rather than lagging behind forever.

Tracks land in a **subfolder named after the album**, **numbered in playlist order**:

```
download_audio/Molchat Doma - Etazhi/
├── 01 - Na Dne.m4a
├── 02 - Tantsevat.m4a
├── 03 - Volny.m4a
└── ...
```

Answering `n` opens manual selection (`1-5`, `1,3,7`, and so on) using the table's numbers.

> ℹ️ In playlists the **Views** column does not appear: YouTube does not supply that figure in a track listing (only title and duration). The artist is derived from an `Artist - Song` title; where that format is missing, `??` is shown.

### Example 3 — The single-video card

Pasting the URL of a **single video** (with no `list=`) shows its card before downloading:

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

It exists so you can tell at a glance whether this is the right video before spending bandwidth. Fields YouTube does not expose are **omitted**, not shown blank.

> ℹ️ **Why only for single videos.** The card requires **full** metadata extraction (`extract_flat` disabled): it is the only path that reports likes, subscribers, category and language, but it costs a couple of seconds. For one video that is time well spent; on a 50-track playlist it would mean minutes of waiting, so there the fast extraction and the summary table remain.

> With `--url` the card is still **shown**, but without asking for confirmation: on the command line you have already declared what you want, and a prompt would block scripts.

### Example 4 — Command-line usage

To skip interactive mode. Again, these are alternative examples — run one at a time:

```bash
# One-off search (shows results and asks for a selection)
python AudioDex.py --search "daft punk get lucky"

# Direct download of a video or a playlist
python AudioDex.py --url "https://www.youtube.com/watch?v=..."
python AudioDex.py --url "https://www.youtube.com/playlist?list=..."

# As mp3, into a custom folder, with 5 parallel downloads
python AudioDex.py --url "https://..." --format mp3 --output "D:\Music" --workers 5

# Full video instead of audio only (mp4)
python AudioDex.py --url "https://..." --media video
python AudioDex.py --url "https://..." --format mkv     # --media video implied
```

> With `--search`/`--url` the default stays **audio**: the question is not asked, so scripts do not hang on a prompt.

---

## 🔧 Command-line options

| Option | Short | Default | Description |
|---|---|---|---|
| `--search "text"` | `-s` | — | Search by song/artist name (alternative to `--url`) |
| `--url <link>` | `-u` | — | Direct URL of a video, playlist or album |
| `--output <folder>` | `-o` | `download_audio/` | Destination folder for the files |
| `--media {audio,video}` | `-m` | *(asked)* | Download audio only or the full video. If omitted: in interactive mode you are **asked**, with `--search`/`--url` the default is `audio` |
| `--format {m4a,mp3,opus,mp4,mkv}` | `-f` | `m4a` / `mp4` | Output format. The first three are audio, the last two video: choosing one **implies** the matching `--media` |
| `--workers <n>` | `-w` | `3` | Number of parallel downloads |
| `--max-results <n>` | — | `15` | Maximum number of search results |
| `--no-lyrics` | — | off | Do not look up synced lyrics on LRCLIB |
| `--cookies-from-browser <browser>` | — | — | Use browser cookies (`firefox`, `chrome`, `edge`, …) to reach **private** playlists and videos |
| `--lang {it,en,ask}` | `-l` | *(remembered)* | Interface language for this run. With `ask` the question is asked again and the answer re-saved — see [Interface language](#-interface-language) |

> Without `--search` or `--url`, **interactive mode** starts.

### Private playlists

If you paste the URL of one of your **private** playlists, YouTube answers *"The playlist does not exist"*: without authentication the playlist is invisible. Two solutions:

1. ⭐ **Recommended:** set the playlist to **"Unlisted"** on YouTube — it does not become public (only people with the link can see it) and the URL works immediately, with no extra options.
2. To keep it **private**: start with `--cookies-from-browser firefox` (or your browser) — yt-dlp reads the cookies and presents itself to YouTube as you.

> 🪟 **Windows note:** with Chrome/Edge, reading cookies can fail because of the browser's recent encryption (try closing it first); with **Firefox** it works reliably.

---

## 🔀 How downloading works

### 1. Search

Search uses yt-dlp's internal engine with the `ytsearchN:<query>` prefix and the `extract_flat` option: **only metadata** is retrieved (title, channel, duration, URL), nothing is downloaded. It is the same technique used for playlists, where `ignoreerrors` makes private or removed videos get skipped instead of failing the whole listing.

### 2. Playlist URL normalisation

If you paste the URL of a video that belongs to a playlist (`watch?v=...&list=...`), yt-dlp would extract **only that video**. The program pulls out the playlist ID and rewrites it as the canonical `playlist?list=<ID>` URL, obtaining the full track listing.

### 3. Download: audio or video

**Audio only** (default). yt-dlp is configured like this:

```python
'format': AUDIO_SOURCE_FORMATS[<chosen format>]   # no video stream
'postprocessors': [{'key': 'FFmpegExtractAudio',
                    'preferredcodec': <chosen format>,
                    'preferredquality': '0'}]      # maximum quality
```

The stream requested depends on the output format, so that source and destination match and FFmpeg can simply **remux** instead of re-encoding:

```python
AUDIO_SOURCE_FORMATS = {
    'm4a':  'bestaudio[ext=m4a]/bestaudio[acodec^=mp4a]/bestaudio/best',   # AAC, itag 140
    'opus': 'bestaudio[acodec=opus]/bestaudio[ext=webm]/bestaudio/best',   # Opus, itag 251
    'mp3':  'bestaudio/best',      # YouTube never serves mp3: conversion is unavoidable
}
```

Each entry ends with progressive fallbacks, for videos that do not expose the preferred codec.

**Full video** (`--media video`). YouTube serves video and audio as **separate streams** — high resolutions have no embedded audio — so the best of each is fetched and FFmpeg muxes them into the chosen container:

```python
'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
'merge_output_format': 'mp4'    # or 'mkv'
```

The trailing `best` fallback covers videos served as a single stream.

**Videos get tagged too**, with the same care as audio — only the tool changes, because the two containers use different metadata systems:

| | `mp4` | `mkv` |
|---|---|---|
| **Title, artist, album, track no.** | ✅ mutagen (iTunes atoms) | ✅ FFmpeg |
| **Cover art** | ✅ embedded by mutagen | ✅ attached by yt-dlp |
| **Video chapters** | ✅ FFmpeg | ✅ FFmpeg |
| **Karaoke lyrics** | ✅ in the `©lyr` atom | ❌ Matroska has no equivalent field |

In detail: the `FFmpegMetadata` postprocessor writes title, author, date and chapters during the merge — the only route for Matroska, which mutagen cannot tag. **Album and track number** are not in yt-dlp's info (we derive them from the playlist), so they are passed to ffmpeg as explicit arguments: without them, a playlist video would lose exactly the two fields that hold a collection together. For `mp4`, `_tag_m4a` then steps in as it does for audio, adding cover art and lyrics.

> ⚠️ **Mind the disk space**: a video weighs **20 to 100 times** more than audio alone. A 20-song playlist goes from ~70 MB to several GB.

### 4. Parallelism and progress

Downloads run on a `ThreadPoolExecutor` (3 threads by default). A yt-dlp *progress hook* bridges to the Rich bars: each downloaded chunk updates the per-file bar with received bytes, while the overall bar advances as each track completes. Results are reassembled in the original entry order (threads finish out of order).

### 5. Duplicate detection and retries

- Before downloading, the title — sanitised of Windows-forbidden characters, of the Unicode look-alikes yt-dlp substitutes for them, and of emoji — is compared against the files already in the folder: if a valid file exists (>10 KB), the track is marked `skip`. The comparison happens **within the same media type**: an already-downloaded `.m4a` does not suppress the same title requested as video, and vice versa.
- The downloaded file's name is then cleaned the same way: no emoji, no full-width characters (e.g. `⧸ ： ｜`), so songs copy to a phone over USB without errors.
- On error it retries up to **4 times** with exponential backoff plus random jitter, so retries neither hammer the server nor synchronise across threads.

---

## 🔢 Track ordering

### The problem

Downloads start in parallel across several threads and finish **out of order**: track 7, being lighter, may complete before track 2. If files were saved with only the title, the folder would list them **alphabetically** — and an album played from a phone would start on a random song.

The `trkn` tag (track number) alone is not enough: many phone players, and simply browsing the folder over USB, sort **by filename**.

### How it is solved

For playlists the track number goes **into the filename**, zero-padded:

```
download_audio/Molchat Doma - Etazhi/
├── 01 - Na Dne.m4a
├── 02 - Tantsevat.m4a
├── 03 - Volny.m4a
└── ...
```

That way alphabetical order **coincides** with playlist order, wherever you open the folder. The digit count adapts to the playlist size: a 150-song collection uses three digits (`007 - …`), so sorting stays correct there too.

> The prefix is added **only for playlists**. A single video or a selection from a search has no "order" to preserve, so it keeps a clean name.

### Partial selections and playlists with gaps

The number used is the one from the **source playlist**, not the position in the downloaded list:

- you download only tracks **5-8** of an album → the files come out `05`, `06`, `07`, `08`, not `01`-`04`, and slot in alongside those already in the folder;
- the playlist contains a **private or removed** video → it is skipped, but the following tracks **do not shift up**: the numbering stays faithful to the original.

### Numbering already-downloaded files

Duplicate detection recognises the same song even if it is on disk **without a number**, because it was downloaded with an earlier version of the program. In that case the file is simply **renamed**, not re-downloaded:

```
Na Dne.m4a  →  01 - Na Dne.m4a
```

Re-running the same command on an old folder therefore aligns the numbering **without using bandwidth**.

> ⚠️ **A file that already has a number is never renamed**, not even if the playlist has been reordered: in that case the track is re-downloaded with the new number and the old file stays where it is (you can delete it by hand).
>
> The reason is that a playlist can contain **two tracks with the same title** — it happens often, e.g. the same song in single and album versions. By matching "same title, any number", the two tracks would fight over **the same file**, renaming it back and forth: only one would survive and the second would never be downloaded. Better one file too many than one track lost.

---

## 🧾 Metadata tagging

After downloading, every `.m4a` file is tagged with **mutagen** using standard iTunes atoms (`.m4a` files use the MP4 container):

| Tag | Content | Source |
|---|---|---|
| `©nam` | Title | YouTube metadata |
| `©ART` | Artist | The `artist` field or, failing that, the channel name |
| `©alb` | Album | Playlist name (or YouTube's `album` field) |
| `trkn` | Track number | Position in the source playlist |
| `covr` | Cover art | The video thumbnail, downloaded and embedded (JPEG/PNG) |
| `©lyr` | Lyrics | LRCLIB, LRC format with timestamps (see chapter 10) |

The same atoms are written into **`.mp4`** videos, which share the MP4 container with `.m4a`. For **`.mkv`** the metadata is written by FFmpeg during the merge (see [7.3](#3-download-audio-or-video)).

> If mutagen is not installed, tagging is simply skipped: the files remain valid, just without metadata.

---

## 🎵 Synced lyrics (karaoke)

After each successful download the program queries **[LRCLIB](https://lrclib.net)** (a free API, no key required) with the track's artist, title and duration. If lyrics exist, they are **embedded directly into the m4a file's `©lyr` atom**, in LRC format with timestamps: the song stays **a single file** that carries its own lyrics, on a PC as on a phone.

Players that read lyrics from tags (**Musicolet**, **Oto Music**, **AIMP**, **Samsung Music** on Android; **MusicBee**, **foobar2000**, **AIMP** on PC) display them **line by line, karaoke style**; more basic ones show them as static text.

An example of the embedded lyrics:

```
[00:18.98] We're no strangers to love
[00:22.55] You know the rules and so do I (do I)
[00:26.99] A full commitment's what I'm thinking of
```

How it works:

- the YouTube title is **cleaned** of decorations (`(Official Video)`, `[HD]`, `(Lyrics)`, …) before the lookup, and titles in `Artist - Song` form are split into the two fields;
- an **exact match** on artist + title + duration is tried first, then a free search discarding results whose duration differs too much (>10 s: probably a live version or a remix);
- lyrics weigh **a few KB** (~0.1% of the audio): the impact on file size is negligible;
- if the lyrics do not exist or the network fails **nothing happens**: lyrics are a bonus, never a reason for a download to fail;
- the final summary shows how many tracks got lyrics (`♫ Testi karaoke`);
- to disable the lookup: `--no-lyrics`.

---

## 💾 Output formats

| Format | Container | Notes |
|---|---|---|
| `m4a` ⭐ *(default)* | MP4/AAC | YouTube's native quality, **no re-encoding** (remux), supports tags and cover art via mutagen |
| `mp3` | MPEG | Maximum compatibility with older devices; requires re-encoding (slight theoretical loss) |
| `opus` | Ogg/Opus | Best quality-to-size efficiency; less widespread device support |
| `mp4` ⭐ *(video)* | MP4/H.264 | The default for `--media video`: no re-encoding and **full tags** (title, artist, album, track, cover art, lyrics) just like `m4a` |
| `mkv` *(video)* | Matroska | A more permissive container, useful when the best streams do not fit in an mp4. Tags and cover art are there, written by FFmpeg; only the **karaoke lyrics** are missing, as Matroska has no equivalent field |

> 💡 **Advice:** leave it on `m4a` unless you have a specific need — it is the format YouTube serves audio in, so there is no conversion and no loss. The same goes for `mp4` on the video side.

> 🔎 **The stream downloaded depends on the format requested.** The `AUDIO_SOURCE_FORMATS` table maps each output format to the codec to ask YouTube for: `m4a` → AAC (itag 140), `opus` → Opus (itag 251), `mp3` → the best stream available. When source and destination match, FFmpeg only changes the container and **copies the audio byte for byte**. Previously AAC was always downloaded: asking for `--format opus` meant fetching AAC and then recompressing it to Opus, i.e. **two lossy compressions in a row**.

---

## 💿 BurnDex — burning an audio CD

`BurnDex.py` is a **companion tool** that lives in the same folder and reads AudioDex's downloaded collections directly, turning them into a real **audio CD**.

### What it is for, and why an audio CD

You cannot just "put an `.m4a` on a CD" and expect a car stereo to play it. There are two different ways to write a disc, and only one works everywhere:

| | What it holds | Where it plays |
|---|---|---|
| **Audio CD** (CD-DA) | Raw PCM tracks, no files, no metadata | 🚗 Any CD player, car stereo, 1990s hi-fi |
| **Data CD** | The `.m4a`/`.mp3` files copied as they are | Only recent players that can decode those codecs |

BurnDex produces **audio CDs**, i.e. the **Red Book (CD-DA)** standard: PCM 44.1 kHz, 16 bit, stereo, about 80 minutes maximum. It is the only format that in 2026 still plays in virtually any device.

> ⚠️ **An audio CD has no metadata.** Titles and artists do not exist in the CD-DA format: what you sometimes see on a car stereo display comes from an online database. It is the price of universal compatibility.

### Additional requirements

| Requirement | Notes |
|---|---|
| **Windows** | Burning uses **IMAPI2**, the native Windows COM API. AudioDex stays cross-platform; only BurnDex is tied to Windows |
| **pywin32** | Already in `requirements.txt`. Needed only by BurnDex: without it, `--dry-run` still works and burning stops with a clear message |
| **FFmpeg** | The same one AudioDex uses, here to decode audio into PCM |
| **A burner** | Internal or external USB — BurnDex tells the two apart, see [System detection](#system-detection) |

No third-party burning software: no Nero, ImgBurn or CDBurnerXP.

### The four-step flow

Running `python BurnDex.py` with no arguments starts a wizard with **four numbered steps**, each of which can be cancelled:

```
 Passo 1/4   RACCOLTA   ────────────────────────────────────────────

┌────┬────────────────────────────────────────┬────────┬───────────┐
│  # │ Raccolta                               │ Tracce │    Durata │
├────┼────────────────────────────────────────┼────────┼───────────┤
│  1 │ Molchat Doma - Etazhi                  │      9 │  33.6 min │
└────┴────────────────────────────────────────┴────────┴───────────┘

💿 Quale raccolta? (numero, invio per uscire) > 1
```

**1 — Collection.** Lists the folders under `download_audio/` with track count and **total duration**, in yellow if it exceeds the disc limit: you choose already knowing what fits.

```
 Passo 2/4   SCALETTA   ────────────────────────────────────────────

                       Molchat Doma - Etazhi
┌────┬─────────────────────────────────────────────────┬───────────┐
│  # │ Traccia                                         │    Durata │
├────┼─────────────────────────────────────────────────┼───────────┤
│  1 │ 01 - На Дне.m4a                                 │      4:07 │
│  2 │ 02 - Танцевать.m4a                              │      3:22 │
│  …                                                                │
├────┼─────────────────────────────────────────────────┼───────────┤
│    │ 9 tracce                                        │  33.6 min │
└────┴─────────────────────────────────────────────────┴───────────┘
██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  33.6 / 80 min
Ordine: numero di traccia nel nome  ·  stacchi da 2 s inclusi nel totale
```

**2 — Track list.** The exact sequence that will end up on the disc, with a total row and a **capacity bar** (green up to 85%, yellow beyond, red past 79 minutes). Underneath, the **criterion** used to decide the order is always stated. You can select a subset with the same syntax as AudioDex — `3`, `1-5`, `1,3,7`, Enter for all — and the list is **reprinted** with the new numbering.

**3 — Disc and speed.** A card for the drive and the disc inserted, then the write-speed choice built from the **real values** the burner declares:

```
┌─────┬────────────┬───────────────────────────────────────────────┐
│   # │ Velocita'  │ Resa                                          │
├─────┼────────────┼───────────────────────────────────────────────┤
│   1 │ 8x ★       │ consigliata — incisione piu' netta, la piu'    │
│     │            │ sicura per autoradio e stereo datati          │
│   2 │ 24x        │ la piu' rapida, ma qualche lettore vecchio     │
│     │            │ puo' faticare                                 │
└─────┴────────────┴───────────────────────────────────────────────┘
```

> 💡 **Speed does not change audio quality.** At 8x and at 24x the very same bits end up on the disc. What changes is the **physical precision** of the burn: going slowly gives the pits sharper edges, and worn players make fewer errors. The result is not "worse sound", it is all-or-nothing — the disc either reads or stumbles.

**4 — Burning.** All tracks are decoded, then a final confirmation card, then the write.

```
╔═══════════════════ 💿  Pronto a masterizzare ════════════════════╗
║   Unita'            MATSHITA DVD+-RW UJ8E2                       ║
║   Disco             CD-R vuoto                                   ║
║   Velocita'         8x                                           ║
║   Tracce            9                                            ║
║   Durata            33.6 min  (46.4 min liberi dopo)             ║
║       ███████████████░░░░░░░░░░░░░░░░░░░░░  33.6 / 80 min        ║
╚═════════════ la scrittura su CD-R e' irreversibile ══════════════╝
```

> 🛡️ **Decoding happens entirely before `PrepareMedia()`**, not on the fly during the write. Once the laser starts burning, a slow FFmpeg or a corrupt file would ruin the disc halfway through: this way the only possible error during writing is a hardware fault.

### Command-line options (BurnDex)

| Option | Description |
|---|---|
| `--dir`, `-d` | Folder to burn. If omitted, you pick it from a list |
| `--base`, `-b` | Collections folder (default: `AudioDex/download_audio`) |
| `--speed`, `-s` | Speed in "x". If omitted you are asked; with `--yes` it uses 8x |
| `--drive` | Index of the burner to use (see `--info`) |
| `--dry-run`, `-n` | 🧪 **Rehearsal**: shows the track list, checks disc and capacity, **never touches the disc** |
| `--info`, `-i` | System, burners and inserted disc, then exits |
| `--yes`, `-y` | No questions: all tracks, default speed, no confirmation |
| `--no-eject` | Do not eject the disc when burning finishes |
| `--lang`, `-l` | Interface language for this run (`it`/`en`), or `ask` to choose again and save |

Examples — these are **alternatives**, run one at a time. The harmless two first:

```bash
python BurnDex.py --info                                        # reconnaissance
python BurnDex.py -d "download_audio/Molchat Doma - Etazhi" -n  # rehearsal
```

Then the ones that **actually write to the disc** (do not paste them together with the above):

```bash
python BurnDex.py -d "download_audio/Molchat Doma - Etazhi"     # burn
python BurnDex.py -d "..." --speed 24 --yes --no-eject          # unattended
```

> 🧪 **Use `--dry-run` the first time.** It runs every check — track list, ordering, disc type, capacity, available speeds — without writing anything. A wasted CD-R is unrecoverable; a rehearsal costs two seconds.

### Track order on the disc

On a CD-R the running order is decided **once and for all**: there is no way to reorder, add or remove songs afterwards. BurnDex uses three criteria, in order of precedence:

1. **`ordine.txt`** in the folder — one filename per line, blank lines and `#` ignored. Absolute manual control
2. **Numeric prefix in the name** (`01 - Song.m4a`) — exactly how AudioDex saves playlists, so this is usually what applies and the album order is already correct. It counts **only if every file has one**: with even a single unnumbered file the ordering would become arbitrary precisely where it matters
3. **Creation date** — a fallback for folders assembled by hand. Careful: if you **copied** the files, the creation date is the date of the copy

The criterion actually used is **always printed** below the track list, before the confirmation.

```txt
# ordine.txt — one filename per line, the order is what you read
03 - Фильмы.m4a
01 - На Дне.m4a
09 - Клетка.m4a
```

### Recognised disc types

BurnDex classifies the disc inserted and explains **what to do** in each case, rather than merely answering "blank yes/no":

| Disc | Outcome | Reason and remedy |
|---|---|---|
| 💿 **Blank CD-R** | ✅ burns | The ideal case for the car |
| 💿 **Blank CD-RW** | ✅ burns, with a warning | Lower reflectivity: many car stereos and older hi-fis will not read it |
| 🔒 **Written CD-R** | ❌ | Writing is permanent: you need a new disc |
| ♻️ **Written CD-RW** | ❌ | But it is erasable: File Explorer → right-click the drive → *Erase this disc* |
| 📀 **CD-ROM** | ❌ | Factory-pressed, read-only |
| 📀 **DVD±R / DVD±RW / DVD-RAM / BD-R / BD-RE** | ❌ | **Red Book does not exist on DVD or Blu-ray.** However capacious, there is no audio format a car player could interpret |
| ❓ **Unrecognised** | ❌ | Scratched disc, badly inserted, or a type the drive does not handle |

> 🐛 The **DVD** case was the nastiest gap: a blank DVD reports as "blank and writable", so the previous version would have started and then crashed on an inscrutable IMAPI error midway through.

### System detection

`--info` opens with a survey of the machine, read from **WMI**:

```
┌───────────────────────── Il tuo sistema ─────────────────────────┐
│  Computer        PC portatile  Aspire A315-23                    │
│  Unita' D:       MATSHITA DVD+-RW UJ8E2 USB Device               │
│                  collegata in USB (esterna)                      │
└──────────────────────────────────────────────────────────────────┘
L'unita' e' esterna e si alimenta dalla porta USB.
In scrittura il laser assorbe molto piu' che in lettura, e una porta al limite
fa riavviare l'unita' a meta' masterizzazione. Se una scrittura fallisce:
  1. collega entrambi gli spinotti, se il cavo ne ha due
  2. usa una porta diretta sul PC, mai un hub non alimentato
```

What it detects, and how:

- 💻 **Laptop or desktop** — from `Win32_SystemEnclosure.ChassisTypes` (8-12, 14, 18, 21, 30-32 = portable; 3-7, 13, 15-17, 23, 24 = stationary) and the model in `Win32_ComputerSystem`
- 🔌 **Internal or external drive** — from the branch of the PnP tree in `Win32_CDROMDrive.PNPDeviceID`: USB devices sit under `USBSTOR\`, internal ones under `SCSI\` or `IDE\`
- 🚫 **No drive at all** — normal on a recent laptop: BurnDex says so explicitly and explains that an external USB burner is needed

The power warning appears **only for external drives** and **before** burning, not as a post-mortem. On an internal drive it would be noise at every startup.

> ⚠️ **A WMI failure is not fatal**: you lose the advice, not the burn.

### How writing works (IMAPI2)

Five stages, all through the native Windows COM API:

1. **Enumeration** — `IMAPI2.MsftDiscMaster2` returns a unique ID for each drive
2. **Initialisation** — `MsftDiscRecorder2.InitializeDiscRecorder(id)`, which yields the drive letter, make and model
3. **Querying the medium** — type, state, capacity and supported speeds
4. **Decoding** — FFmpeg produces raw PCM at 44.1 kHz / 16 bit / stereo
5. **Track-At-Once writing** — `PrepareMedia()` → one `AddAudioTrack()` per track → `ReleaseMedia()`, which closes and finalises the disc

Three non-obvious details, all discovered the hard way:

- 🔍 **The medium is queried with a different object.** `FreeSectorsOnMedia` and `NumberOfExistingTracks` on the Track-At-Once writer only answer **after `PrepareMedia()`**, which has already opened the write session: far too late to decide whether the disc is suitable. BurnDex uses `MsftDiscFormat2Data` as a **read-only probe** — it answers as soon as you assign the recorder — and keeps Track-At-Once for the actual write
- 📏 **IMAPI2 is fussy about PCM.** It wants the audio **bare, with no WAV header**, aligned to exact multiples of **2352 bytes** (the size of a Red Book audio sector) and at least **4 seconds** long. Off by one byte and `AddAudioTrack` fails. BurnDex pads with just enough silence to satisfy both constraints
- ⚡ **Speeds are not a continuous scale.** Each drive exposes a few discrete steps (`SupportedWriteSpeeds`, in sectors per second: e.g. 599 and 1800, i.e. 8x and 24x). Asking for 4x does not slow things down, it makes `SetWriteSpeed` **fail**. BurnDex picks the nearest available step without exceeding the request, and passes the **raw** value — 599, not 600 — because that is the only one the drive accepts without argument

### Audio CD limits

| Limit | Value | Why |
|---|---|---|
| ⏱️ **Duration** | ~80 min (BurnDex uses **79**) | The outer edge is the area worn players get wrong most often |
| 🎚️ **Sampling** | 44.1 kHz / 16 bit / stereo, fixed | Red Book mandates it: any source is brought to this |
| 🏷️ **Metadata** | None | CD-DA has no fields for title or artist |
| 🔇 **Gaps** | 2 s before every track | Inserted by the burner, **counted** in the minutes total |
| 🚫 **Erasing** | Impossible on CD-R | The laser physically burns a dye layer: it is a change of state of matter |
| 💾 **Temporary space** | ~10 MB per minute (~850 MB for a full CD) | Raw PCM takes far more room than the compressed source files |

> ℹ️ **A CD's 700 MB have nothing to do with the size of your files.** Only duration counts: 3 GB of MP4 lasting 75 minutes will fit, because burning converts it back to PCM.

### Error diagnosis

IMAPI errors arrive as inscrutable COM codes. BurnDex recognises the recurring ones and translates them into a diagnosis with the remedy:

| Error | Diagnosis |
|---|---|
| `0xC0AA020D` *(command timeout)* | The drive did not answer the write command. On USB burners this is almost always **insufficient power**: when the laser switches to write power the current draw jumps and the drive resets. Remedies in order: both plugs of the cable, a port directly on the PC, a powered hub |

The final summary reports **how many tracks were actually written**, not how many were queued:

```
╔═══════════════════ ✗  Masterizzazione fallita ═══════════════════╗
║   Tracce scritte    0 su 9                                       ║
║   Esito             ✗ interrotto                                 ║
║   Disco             nessun dato audio scritto: e' ancora buono   ║
╚══════════════════════════════════════════════════════════════════╝
```

The distinction matters: at `0 su 9` the disc is **still blank and reusable**, at `4 su 9` it is half-written and fit for the bin.

Other safety nets:

- 🔓 **`ReleaseMedia()` is attempted even on error**, otherwise the drive stays locked in exclusive access. It is itself guarded: if the drive is what vanished, the failure to close must not mask the real error
- 📝 A full log in `logs/burndex.log`, including the COM exception's stack trace
- 🛑 **Ctrl+C** during writing does not stop the laser — the disc is lost either way — but the drive is released properly

---

## 🧩 Project architecture

```
AudioDex/
├── AudioDex.py               # Main CLI: search, selection, download, Rich UI
├── BurnDex.py                # 💿 Audio CD burner (Windows, IMAPI2)
├── Shared/
│   ├── __init__.py
│   ├── logger_setup.py       # File logger + shared Rich theme/symbols
│   └── http_client.py        # Shared HTTP helpers (User-Agent, headers, retry backoff)
├── Database_Globale/
│   ├── scraper_db.py         # Global SQLite download database
│   └── scraper_metadata.db   # The database (created automatically, git-ignored)
├── download_audio/           # Output folder (created automatically, git-ignored)
│   └── <Artist> - <Album>/   # One folder per playlist, with numbered tracks
│       └── ordine.txt        # (optional) manual running order for BurnDex
├── logs/
│   ├── audiodex.log          # Detailed log of every session (git-ignored)
│   └── burndex.log           # Burning log (git-ignored)
├── requirements.txt          # Python dependencies
├── README.md                 # Italian version
└── README.en.md              # This file
```

The `Shared/` and `Database_Globale/` modules are designed to be **shared across several scrapers** (audio, manga, anime): same visual theme, same logging, same database with type-specific columns.

`BurnDex.py` is **independent**: it shares only `Shared/logger_setup.py` with AudioDex (Rich theme and logger), imports nothing from `AudioDex.py`, and works on audio folders assembled by hand. It does not write to the global database — burning is not a download, and recording it there would distort the download log.

---

## 📊 Global database

Every successful download is recorded in `Database_Globale/scraper_metadata.db`, an SQLite database **shared across scrapers** with a single `downloads` table:

- **Common fields**: scraper type, media type (`audio`/`video`), source ID, title, URL, file path (relative, so it survives folder moves), size, ISO 8601 date
- **Audio fields**: artist, duration, format, track number, album

Technical details:

- 🧵 **One connection per thread** (`threading.local`): sqlite3 forbids sharing a connection across threads, and writes come from the download threads
- ⚡ **WAL mode**: concurrent reads and writes without blocking each other
- ♻️ **`INSERT OR REPLACE`** on the `UNIQUE(scraper_type, source_id, media_kind)` constraint: re-downloading the same track **in the same format** updates the existing row instead of duplicating it, while the **audio** and **video** versions of the same YouTube video coexist as two rows — they are two distinct files on disk
- 🔄 **Automatic migration**: databases created before video downloading arrived have the old `UNIQUE(scraper_type, source_id)` key, which SQLite cannot change with an `ALTER TABLE`. On first start the table is **rebuilt** and the data copied across, inside a single transaction and after a **safety copy** of the file (`scraper_metadata.db.backup-pre-media-kind`). Historical rows are labelled as `audio`. If anything goes wrong the migration rolls back and the data is left intact
- 🛡️ **Errors are never fatal**: the database is an auxiliary log — a problem with it is logged as a warning and never interrupts downloads

---

## 🧯 Error handling and failed tracks

- Every failed track (after all retries) appears in the **final summary**, with the reason in the log
- Titles and URLs of failed tracks are saved to **`failed_tracks.txt`** in the output folder, ready to retry with `python AudioDex.py --url <URL>` without redoing the search
- The full log of every session lives in `logs/audiodex.log` — the logger writes **to file only**: log lines on screen would ruin the live progress bars
- 🛑 **Ctrl+C**: the first starts a clean shutdown (downloads in flight finish, queued ones are cancelled), the second forces an immediate exit

---

## 📚 Libraries used, and why

| Library | What it does | Why this one |
|---|---|---|
| `yt-dlp` | YouTube search and audio stream extraction/download | The de facto standard: it handles streams, playlists, resuming and metadata |
| `requests` | Downloading cover art and calling LRCLIB | Simple and ubiquitous; two GETs are all that is needed here |
| `rich` | Terminal interface: tables, panels, live bars | Turns the CLI into a polished experience (`Table`, `Progress`, `Live`) |
| `mutagen` | *(optional)* Metadata and cover art in `.m4a` files | Pure Python, reads/writes MP4 (iTunes) atoms with no external dependencies |
| `pywin32` | *(BurnDex only)* Bridge to COM: IMAPI2 for burning, WMI for system detection | The only way to talk to native Windows APIs from Python. It avoids depending on third-party burning software |

### External tool (not pip)

| Tool | What it does | Notes |
|---|---|---|
| **[FFmpeg](https://ffmpeg.org)** | Audio extraction and conversion; PCM decoding for BurnDex | **Required**, installed once. With `m4a` it does not re-encode: it only remuxes |
| **ffprobe** | Reading durations without decoding | Bundled with FFmpeg. BurnDex uses it to compute capacity before committing the disc |

### System APIs (nothing to install)

| API | What it does | Notes |
|---|---|---|
| **IMAPI2** | Audio CD burning | *Image Mastering API v2*, present in Windows since Vista. The same one File Explorer and Windows Media Player use |
| **WMI** | Computer type and optical drives | `Win32_SystemEnclosure`, `Win32_ComputerSystem`, `Win32_CDROMDrive` |

### External service (no key)

| Service | What it does | Notes |
|---|---|---|
| **[LRCLIB](https://lrclib.net)** | Synced lyrics (LRC) | A public, free API, **no registration and no key**. If it does not answer, the download carries on regardless |

### Standard library (nothing to install)

`os`, `re`, `json`, `shutil`, `signal`, `time`, `random`, `threading`, `sqlite3`, `tempfile`, `subprocess`, `concurrent.futures`: paths and files, regexes, disk space, Ctrl+C handling, retry backoff, thread pools, the database, temporary PCM files and invoking FFmpeg.

---

## 📝 Changelog

### 2026-07-26

**New**

- 🌍 **Interface in Italian or English.** On first launch both tools ask for the language, **in English**, because it is the one language anyone who does not speak Italian can certainly read. Pick English and everything follows: prompts, tables, panels, bars, summaries, error diagnostics and the `--help` texts. The choice is remembered in `settings.json` and not asked again; `--lang it|en` overrides it for a single run without touching the preference, `--lang ask` asks again. See [Interface language](#-interface-language)
- 🗣 **Answers accepted in both languages** whichever one is selected: `s`/`si`/`y`/`yes` to confirm, `q`/`esci`/`exit` to quit, `all`/`tutti`/`tutte` to select everything. Someone running the English interface who types `s` out of habit no longer gets the operation cancelled

**Changes**

- 🧱 **Text separated from code**: the phrases shown to the user live in `Shared/strings_audiodex.py` and `Shared/strings_burndex.py`, the machinery that picks between them in `Shared/i18n.py`. Comments, docstrings and file logs stay in Italian: they address whoever maintains the program, not whoever uses it
- 📅 **Upload date in ISO form in English** (`2013-04-19`) instead of day/month/year: it is the only form that is unambiguous between the American convention, which puts the month first, and the British one, which puts the day first. In Italian it stays `19/04/2013`
- 🔢 **Large-number abbreviations translated**: `1.2 Mrd` / `4.3 Mln` in Italian become `1.2 B` / `4.3 M` in English

### 2026-07-25

**New tool**

- 💿 **BurnDex — audio CD burner.** `BurnDex.py` turns a downloaded collection into a real **audio CD** (Red Book CD-DA), the only format car stereos and older hi-fis are guaranteed to read. It uses **IMAPI2**, the native Windows COM API: no third-party burning software. A four-step wizard with a Rich UI consistent with AudioDex — collection picker, track list with capacity bar, speed choice, confirmation card — plus `--dry-run` to rehearse everything without consuming a disc
- 🔢 **Three-criteria track ordering**: `ordine.txt` for manual control, numeric filename prefix (the one AudioDex already writes), creation date as a fallback. The criterion in use is **always stated** before the confirmation, because on a CD-R the running order is decided once and for all
- 💾 **Recognition of the disc inserted**: it distinguishes CD-R, CD-RW, CD-ROM, DVD±R/RW, DVD-RAM, BD-R/RE and unidentified media, saying for each **why** it will not do and how to fix it. The critical case is a **blank DVD**, which reports as "blank and writable" but cannot hold an audio CD: Red Book is not defined on DVD
- 💻 **System detection** via WMI: laptop or desktop, presence of an optical drive, and above all whether the drive is **internal or external USB**. On external drives the power warning now appears **before** burning
- ⚡ **Write speed taken from the drive's real values**: `SupportedWriteSpeeds` exposes a few discrete steps, and asking for a value outside the list makes `SetWriteSpeed` fail rather than slowing down. BurnDex picks the nearest step without exceeding the request, with 8x recommended for in-car listening

**Fixes**

- 🐛 **YouTube Mixes broke single-video downloads** *(AudioDex)*: when you copy a link from the player, YouTube appends `&list=RD<videoId>&start_radio=1` — the radio built around that song. `_is_playlist_url` saw the `&list=` and treated it as a playlist, but the canonical `playlist?list=RD…` URL makes YouTube answer *"This playlist type is unviewable"*, and the download stopped with "no tracks found in the playlist". Mixes are now recognised (`RD` + video id, the `RDMM`/`RDEM`/`RDAMVM`/`RDGMEM`/`RDAO` prefixes, or `start_radio=1`) and the video is downloaded, while YouTube Music's `RDCLAK5uy_…` playlists, which are browsable, are still treated as playlists. On top of that, if **any** playlist turns out to be inaccessible but the URL contains a `v=`, the program falls back to the single video instead of giving up
- 🐛 **Source format chosen according to the output format** *(AudioDex)*: the selector was pinned to `bestaudio[ext=m4a]` regardless of the format requested, so `--format opus` downloaded **AAC** and then recompressed it to Opus — two lossy compressions in a row. The `AUDIO_SOURCE_FORMATS` table now asks YouTube for the codec it serves natively: `opus` takes itag 251 and **copies** it without re-encoding, `mp3` starts from the best available stream. The behaviour of `m4a`, the default, is unchanged
- 🐛 **Querying the disc before committing the drive** *(BurnDex)*: `FreeSectorsOnMedia` on the Track-At-Once writer only answers **after `PrepareMedia()`**, which has already opened the write session. The first version died there with a `com_error`. The medium is now read with `MsftDiscFormat2Data`, which answers immediately, leaving Track-At-Once for writing alone
- 🐛 **Truthful count of tracks written** *(BurnDex)*: the summary showed the tracks **prepared** rather than the ones actually burned, and after a failure at zero tracks it claimed "9 written". It now counts successful `AddAudioTrack` calls and distinguishes the two cases that matter: `0 of 9` (disc still blank and reusable) from `4 of 9` (half-written, fit for the bin)
- 🐛 **Paths and filenames inside Rich markup** *(BurnDex)*: a string such as `D:\` ended up inside a markup tag, and since backslash is Rich's escape character it swallowed the closing tag, printing `D:[/dim]`. This applied to any name containing `\` or `[`. Every string coming from disk now goes through `rich.markup.escape()`
- 🐛 **Consistent totals between the picker and the track list** *(BurnDex)*: the collection list summed raw durations while the track list added the 2-second gaps, showing two different numbers for the same album. Both now use `_settori_totali()`
- 🐛 **`ReleaseMedia()` guarded** *(BurnDex)*: when the drive itself disappears from the bus, closing the session fails too, and the secondary exception masked the real error

**Changes**

- 🎨 **Unified presentation layer** *(BurnDex)*: tables, panels and rules share one width; progress bars gained a percentage and a fixed-width description column, so the bar no longer jitters at every track change; a colour-coded capacity bar sits under every track list
- 🩺 **IMAPI errors translated**: code `0xC0AA020D` (*command timeout*) is recognised and presented as a USB power problem with remedies in order of effectiveness, instead of the raw COM message
- 📦 **`pywin32>=306`** added to `requirements.txt`, marked as needed only by BurnDex

### 2026-07-19

**New features**

- 🔢 **Playlist order preserved on disk**: playlist files are saved with the track number at the front of the name (`01 - Song.m4a`), zero-padded to the playlist size. The number is the one from the **source playlist**: a partial selection (tracks 5-8) keeps `05`-`08`, and a removed video does not shift the following tracks
- ♻️ **Numbering of already-downloaded files**: songs already present **without a number** (downloaded with an earlier version) are **renamed** rather than re-downloaded — re-running a download on an old folder aligns the numbering at no cost
- 📊 **Per-phase progress bars**: four bars (Download, Conversion, Lyrics, Tags) show how many tracks have cleared each stage. Previously there was only the byte bar, which sat at 100% while the track was still converting, looking up lyrics or writing tags — it looked stuck
- 🎬 **Full video download**, alongside audio-only: in interactive mode you are **asked** before starting, on the command line there is `--media video` (or `--format mp4`/`mkv` directly). Videos are **tagged like audio** (title, artist, album, track number, cover art, chapters): in `mp4` with mutagen, in `mkv` with FFmpeg. Duplicate detection now separates audio formats from video ones, so the same song can exist in both versions
- 🎬 **Video card before downloading**: pasting a single video URL brings up a panel with channel, views, likes, subscribers, category, language, date and chapters, followed by a confirmation prompt. Previously a single-video URL started the download **showing nothing**
- 💿 **Enriched playlist card**: the summary gains the channel, aggregate views, last-updated date, visibility and the number of **unavailable** videos. These were data yt-dlp already returned in the same call and that were being discarded: **no extra network requests**
- 🗄️ **Database: audio and video coexist**. The unique key includes the **media type**, so downloading the same video first as audio and then as video no longer overwrites the previous row. Existing databases are **migrated automatically** on first start, with a safety copy

**Fixes**

- 🐛 **"Failed" tracks that were actually already present**: the "already downloaded" branch read `progress.tasks[task_id]`, but Rich's `Progress.tasks` is a **positional list**, not indexed by `TaskID`. Since the bars of completed files are removed as they go, indices shifted and an `IndexError` was raised, which `download_batch` caught and marked as a **failure** — despite a perfectly good file on disk. On a fully-downloaded playlist the summary showed half the tracks as "Failed"
- 🐛 **Same-titled tracks fighting over one file**: with two songs sharing a title in the same playlist (e.g. single and album versions), renumbering matched "same title, any number" and the two tracks renamed each other's file, letting only one be downloaded. A file that is **already numbered is now never renamed**
- 🐛 **Result order in the summary**: the final reordering compared **titles**, so two same-titled tracks (or a title changed by yt-dlp) ended up out of place or at the bottom. Results are now reassembled by the **track's position**

### 2026-06-11

**Fixes**

- **YouTube search repaired**: yt-dlp's `default_search` option always returned 0 results with recent versions — search now uses the explicit `ytsearchN:` prefix. yt-dlp was also updated to 2026.6.9 and pinned as a minimum version in `requirements.txt`
- **IDE-friendly import**: `scraper_db` is imported as `from Database_Globale import scraper_db` instead of via `sys.path` manipulation, so Pylance/VS Code resolve it without false errors
- **Artist/channel fallback**: `uploader`/`channel` fields with a `None` value no longer print "None" in the tables
- **Phone-compatible filenames**: `_sanitize_filename` now converts the full-width Unicode look-alikes yt-dlp uses in place of forbidden characters (`/ : | ? * " < >` → `⧸ ： ｜ …`) into `_`, and strips emoji; the file is renamed accordingly after download. Those characters made copying tracks to a phone over USB fail

**Changes**

- **Audio only**: the video download path was removed entirely. The default moved from `mp4` (full video) to `m4a` (audio track only): files of a few MB instead of hundreds, at identical sound quality. Available formats: `m4a`, `mp3`, `opus`
- **Code documentation in Italian**: every function, class and module has a docstring explaining what it does and why it exists; targeted comments on the non-obvious parts (yt-dlp options, threading, database)

**New features**

- **Karaoke-style synced lyrics**: after each download the timestamped lyrics are looked up on LRCLIB and embedded in the audio file's tags (LRC format) — a single file that also carries its lyrics. Summary with a `♫ Testi karaoke` count; disable with `--no-lyrics`
- **Private playlists and videos**: a new `--cookies-from-browser <browser>` option that authenticates yt-dlp with browser cookies; the simpler alternative ("Unlisted" playlists) is documented too
- **Playlist track table** shown before the download confirmation, plus a **Views** column (compact format: `2.1 Mrd`, `45 Mln`, `350 K`) wherever YouTube supplies the figure — playlists do not expose it, so the column is hidden there. Likes are not shown: fetching them would cost ~5 s per track
- **Separate Title and Artist columns**: the artist is derived from the title (`Artist - Song`) or from the channel name, and the title is cleaned of decorations (`(Official Video)`, `(Lyrics)`, …)
- **`requirements.txt`** with minimum versions and notes on FFmpeg and yt-dlp's frequent updates
- **GitHub repository** with a `.gitignore` that excludes downloaded content, the local database and logs

---

## 📜 Legal notes

AudioDex downloads content from YouTube. Its use may be subject to the [YouTube Terms of Service](https://www.youtube.com/t/terms) and to the **copyright** rules of your jurisdiction. It is intended for **personal and educational** use (e.g. listening offline to music you have the rights to): use it responsibly and only for content you are entitled to access.

The same applies to **BurnDex**: burning to CD is an act of copying, and in many jurisdictions private copying is permitted only from content you are legitimately entitled to access, for personal use and without commercial purpose. Check what your country's law provides for.

The libraries used (yt-dlp, Rich, mutagen, requests, pywin32) are distributed under their respective open source licences.

---

## 📄 Licence

Released under the **[PolyForm Noncommercial License 1.0.0](LICENSE)**.

In short — **this is not a legal summary; the licence text governs**:

- ✅ **You may** use, study, modify and redistribute AudioDex for **non-commercial purposes**: personal use, research, hobby projects, and use by **charitable or educational** organisations (schools, universities).
- ❌ **You may not** use it for commercial purposes: selling it, offering it as a paid service, or using it in a company's business.
- 📎 If you redistribute it, you must **include the licence** (or its URL) and keep the `Required Notice:` line.

> Need commercial use? Get in touch: a separate licence is negotiable.
