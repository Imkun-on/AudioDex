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
  <img src="https://img.shields.io/badge/IMAPI2-native_COM-0078D4?logo=windows&logoColor=white" alt="IMAPI2">
  <img src="https://img.shields.io/badge/pywin32-COM_bridge-3776AB?logo=python&logoColor=white" alt="pywin32">
  <img src="https://img.shields.io/badge/Red_Book-CD--DA_44.1kHz_16bit-C0392B?logo=audiomack&logoColor=white" alt="Red Book">
  <img src="https://img.shields.io/badge/Windows-burning_only-0078D4?logo=windows11&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/PixDex-video_remaster-F97316?logo=vlcmediaplayer&logoColor=white" alt="PixDex">
  <img src="https://img.shields.io/badge/10--bit-debanding-0EA5E9?logo=adobelightroom&logoColor=white" alt="10 bit">
  <img src="https://img.shields.io/badge/Lanczos-upscaling-6366F1?logo=imagedotsc&logoColor=white" alt="Lanczos">
  <img src="https://img.shields.io/badge/libx264_·_h264__amf-encoding-C0392B?logo=amd&logoColor=white" alt="Encoder">
  <img src="https://img.shields.io/badge/pywebview-6.2-2C5BB4?logo=python&logoColor=white" alt="pywebview">
  <img src="https://img.shields.io/badge/WebView2-already_in_Windows-0078D4?logo=microsoftedge&logoColor=white" alt="WebView2">
  <img src="https://img.shields.io/badge/HTML_·_CSS_·_JS-interface-E34F26?logo=html5&logoColor=white" alt="HTML CSS JS">
  <img src="https://img.shields.io/badge/Theme-dark_cyberpunk-EC4899?logo=neovim&logoColor=white" alt="Dark theme">
  <img src="https://img.shields.io/badge/m4a_·_mp3_·_opus-audio_only-EC1C24?logo=itunes&logoColor=white" alt="Formats">
  <img src="https://img.shields.io/badge/License-PolyForm_Noncommercial-orange" alt="PolyForm Noncommercial License">
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
python AudioDexApp.py                                 # everything, graphical interface
python PixDex.py                                      # remaster a downloaded video
python ClipDex.py                                     # cut, join, GIFs, contact sheets
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

**Chapter 8 — [🖼️ Cover art and volume, automatically](#cover-art-and-volume-automatically)**

**Chapter 9 — [📀 Whole albums split into tracks](#-whole-albums-split-into-tracks)**

**Chapter 10 — [🔢 Track ordering](#-track-ordering)**
- 8.1 [The problem](#the-problem)
- 8.2 [How it is solved](#how-it-is-solved)
- 8.3 [Partial selections and playlists with gaps](#partial-selections-and-playlists-with-gaps)
- 8.4 [Numbering already-downloaded files](#numbering-already-downloaded-files)

**Chapter 11 — [🧾 Metadata tagging](#-metadata-tagging)**

**Chapter 12 — [🎵 Synced lyrics (karaoke)](#-synced-lyrics-karaoke)**

**Chapter 13 — [💾 Output formats](#-output-formats)**

**Chapter 14 — [💿 BurnDex — burning an audio CD](#-burndex--burning-an-audio-cd)**
- 12.1 [What it is for, and why an audio CD](#what-it-is-for-and-why-an-audio-cd)
- 12.2 [Additional requirements](#additional-requirements)
- 12.3 [The four-step flow](#the-four-step-flow)
- 12.4 [Command-line options](#command-line-options-burndex)
- 12.5 [What happens to the audio before burning](#what-happens-to-the-audio-before-burning)
- 12.6 [Track order on the disc](#track-order-on-the-disc)
- 12.6 [Recognised disc types](#recognised-disc-types)
- 12.8 [System detection](#system-detection)
- 12.9 [How writing works (IMAPI2)](#how-writing-works-imapi2)
- 12.9 [Audio CD limits](#audio-cd-limits)
- 12.10 [Error diagnosis](#error-diagnosis)

**Chapter 15 — [🎞 PixDex — remastering a video](#-pixdex--remastering-a-video)**
- 13.1 [What it does, and above all what it does not](#what-it-does-and-above-all-what-it-does-not)
- 13.2 [Why it works anyway](#why-it-works-anyway)
- 13.3 [The filter order is not negotiable](#the-filter-order-is-not-negotiable)
- 13.4 [The five presets](#the-five-presets)
- 13.5 [How debanding is tuned](#how-debanding-is-tuned)
- 13.6 [The diagnosis](#the-diagnosis)
- 13.7 [How far it upscales, and how to choose](#how-far-it-upscales-and-how-to-choose)
- 13.8 [The before/after comparison](#the-beforeafter-comparison)
- 13.9 [Encoding: software or GPU](#encoding-software-or-gpu)
- 13.10 [Command-line options](#command-line-options-pixdex)
- 13.11 [In the GUI](#in-the-gui)

**Chapter 16 — [✂ ClipDex — cutting, joining, converting](#-clipdex--cutting-joining-converting)**
- 15.1 [Copy or re-encode](#copy-or-re-encode-the-choice-that-governs-everything)
- 15.2 [`taglia`](#taglia--extracting-a-segment)
- 15.3 [`unisci`](#unisci--putting-several-files-in-a-row)
- 15.4 [`gif` and `webp`](#gif-and-webp--making-an-animation)
- 15.5 [`provino`](#provino--seeing-what-is-inside)
- 15.6 [`compat`](#compat--making-old-devices-read-it)

**Chapter 17 — [🧩 Project architecture](#-project-architecture)**

**Chapter 18 — [📊 Global database](#-global-database)**

**Chapter 19 — [🧯 Error handling and failed tracks](#-error-handling-and-failed-tracks)**

**Chapter 20 — [📚 Libraries used, and why](#-libraries-used-and-why)**

**Chapter 21 — [📝 Changelog](#-changelog)**

**Chapter 22 — [📜 Legal notes](#-legal-notes)**

**Chapter 23 — [📄 Licence](#-licence)**

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

**In the terminal, everything is in Italian.** The three command-line programs — `AudioDex.py`, `BurnDex.py`, `PixDex.py` — speak Italian only: no question on first launch, no `--lang` option to remember. Open the terminal, run, go.

**In the GUI the choice is there, one click away.** `AudioDexApp.py` has an **Italiano / English** dropdown in the sidebar: it switches instantly — menu entries, labels, buttons, diagnostics, messages — and remembers the choice in `settings.json` for later runs.

That is where the choice belongs. A dropdown is visible, you try it and see the effect right away; the same choice as a command-line argument was just one more thing to remember every time.

**What is not translated.** Log files in `logs/` and the comments in the code stay in Italian: they serve whoever maintains the program, not whoever uses it.

> 🗣 **Answers work in both languages.** `s` and `y` both count as confirmation, `q` and `esci` as quit: typing `y` out of habit never cancels the operation.

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
| `--split` | — | off | Split into tracks the videos whose chapters look like an album — see [Whole albums split into tracks](#-whole-albums-split-into-tracks) |
| `--no-split` | — | off | Never ask about splitting, not even in interactive mode |
| `--cookies-from-browser <browser>` | — | — | Use browser cookies (`firefox`, `chrome`, `edge`, …) to reach **private** playlists and videos |

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

### Cover art and volume, automatically

Two things happen by themselves on every download, with no options to remember.

**The cover comes out square.** YouTube thumbnails are 16:9, but players show cover art in a square: they either squash it or crop it wherever — often through a face, or cutting the title that sits at the edges. AudioDex places the **whole** image at the centre of a square filled with a blurred, enlarged copy of itself: nothing is lost, and there are none of the black bars that stand out in a grid of covers. It costs 0.4 seconds.

**The volume is measured and noted in the tags.** A YouTube playlist has 9-10 LU jumps between songs. AudioDex measures every file to the EBU R128 standard and writes down how much the player should raise or lower it: `replaygain_track_gain` and `replaygain_track_peak`, in the form VLC and foobar2000 look for.

**The audio is not touched.** They are two tags: no re-encoding, no loss, and it is undone by deleting them. The measurement costs 2.3 seconds on a four-minute song, against the 10-30 of the download itself: it disappears into the noise.

> 🎧 **Not every player reads them.** In `.m4a` files these tags are not standardised the way they are in FLAC or MP3. VLC, mpv and foobar2000 use them; Apple's Music app has its own different field (`iTunNORM`); some car stereos ignore them. Writing them costs nothing and breaks nothing, but do not expect it to work everywhere — if you mostly listen on CD, it is `BurnDex` that really levels, applying the gain to the burned audio.

---

## 📀 Whole albums split into tracks

A great many uploads are **"Full Album"**: a single three-quarter-hour video with chapters written by whoever uploaded it. AudioDex recognises them and, if you ask, cuts them into the individual tracks — **without re-encoding**, so in seconds and without losing a bit.

### The point is not cutting: it is knowing *whether* to cut

On YouTube chapters are used for everything. A tutorial has five, a review three, an interview uses them for the questions: splitting a ten-minute video into five two-minute pieces pleases nobody. For AudioDex to offer the split, **all** of these must hold:

| Criterion | Threshold | Why |
|---|---|---|
| Number of chapters | **≥ 3** | with two it is almost always "intro + the rest" |
| Video duration | **≥ 10 min** | below that, however long it looks, it is not a record |
| Chapter duration | **≥ 30 s** for at least 80% | below that they are markers, not songs |
| Coverage | chapters cover **≥ 80%** of the video | covering a third means indexing a part, not the whole |
| Order | increasing, non-overlapping times | if the data is inconsistent, cutting blindly produces overlapping tracks |

If even one fails, **nothing is asked**: pointless questions teach people to ignore prompts, including the ones that matter.

When everything holds:

```
This looks like an album: 8 chapters, averaging 2:10 each.
   1. Apertura  2:10
   2. Il secondo brano  2:10
   3. Interludio: pioggia  2:10
  … and 5 more

Split it into its tracks? (y/n — the whole file is kept anyway):
```

### What you get

A folder named after the video, holding the **numbered and tagged** tracks:

```
download_audio/
├── Gruppo di Prova - Disco Finto Completo (Full Album).m4a   ← the whole file, kept
└── Gruppo di Prova - Disco Finto Completo (Full Album)/
    ├── 01 - Apertura.m4a
    ├── 02 - Il secondo brano.m4a
    └── …
```

Every track carries **title** (from the chapter), **album** (from the video title), **track number** and cover art. The folder is already in the shape BurnDex expects: you can burn it straight away, and the order on the CD will be right.

The **whole file is kept** and sits *outside* the tracks folder — deliberately: BurnDex scans a whole folder, and finding the 45-minute album in there would mean seeing it in the running order as a track to burn.

### How to drive it

| | What it does |
|---|---|
| *(nothing, in interactive mode)* | asks, but **only** if the criteria hold |
| `--split` | always splits when the criteria hold, without asking |
| `--no-split` | never asks and never splits |
| `--url` / `--search` without `--split` | does not split: there is nobody there to answer, and silently reorganising folders inside a script is not done |

> ✂️ **On video the cut snaps to the keyframe.** In copy mode you cannot cut in the middle of a group of frames compressed together, so the start may drift by a few seconds. On audio the granularity is milliseconds and it does not show. Then again, hand-written YouTube chapters are not frame-accurate either.

> 🗃 **The carved-out tracks do not go into the global database**: the source file stays registered, which is what was actually downloaded.

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
| `--no-level` | Do not level the volume across tracks: leave every song at the volume it was uploaded with |
| `--trim` | Trim the silence at the start and end of each track |

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

### What happens to the audio before burning

An audio CD is 44.1 kHz, 16 bit, stereo, full stop: whatever you download — a 48 kHz opus, a 44.1 m4a, an old mono upload — has to get there. **How it gets there is not a detail.**

Dropping to 16 bit by **truncating** the values produces distortion that is *correlated with the signal*: on quiet passages, reverb tails and fades, the ear reads it as a dirty sound. **Dithering** replaces it with random noise, which the ear ignores instead. Measured on a −70 dBFS tone, the energy on the harmonics goes from **+46.9 dB to +31.1 dB** relative to the fundamental: almost 16 dB less grime. Dithering is now always on and cannot be turned off.

> 🔬 **The resampler, however, was left as the default.** `soxr` is considered better and the Gyan build has it, but I could not measure a real advantage on the 48 → 44.1 conversion — and asking for it on a build compiled without `libsoxr` would fail the burn halfway through. Not worth the risk for a gain I cannot demonstrate.

**`--level` — evens out the volume across tracks.** A YouTube playlist has 9-10 LU jumps between songs: the hand reaching for the volume knob at every track change. The option measures each track to the EBU R128 standard and brings it to −16 LUFS, never exceeding −1 dBTP of true peak — pushing past that would clip the waveform, and on a CD-R there is no going back.

Measured on three songs at −7, −14 and −21 dB:

| | Spread between loudest and quietest |
|---|---|
| Without `--level` | **14.0 dB** |
| With `--level` | **0.59 dB** |

The measurement uses `ebur128` rather than the first pass of `loudnorm`: they give the very same numbers — verified on one file, −35.8 LUFS and −31.6 dBFS against −35.78 and −31.56 — but the former takes **2.3 seconds against 11.6**. On a twenty-track CD that is eighty seconds instead of seven minutes, which is why levelling became the **normal behaviour**: turn it off with `--no-level`.

**`--trim` — trims the silence.** YouTube uploads often carry one or two seconds of nothing at the start and end, which **add** to the 2-second gap IMAPI2 inserts between tracks anyway: the result is four or five second pauses in the middle of an album. On the test collection it removed 3.4 seconds per track.

The tail is removed by reversing the stream, cutting the start and reversing it back: `silenceremove` only knows how to work at the beginning.

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

## 🎞 PixDex — remastering a video

### What it does, and above all what it does not

`PixDex.py` takes a poor-quality video and cleans it up: it removes the artifacts left by compression, smooths stepped gradients and brings it to a higher resolution with upscaling done properly.

This has to be said up front, because it is what creates the most wrong expectations: **PixDex invents no detail that is not in the file.** Upscaling, however careful, cannot rebuild what compression threw away. That is what AI models do — they reconstruct *plausible* detail, but invented, and on a full screen it often gives itself away.

PixDex works **by subtraction**: it removes noise, it does not add fake sharpness.

### Why it works anyway

On YouTube material there are three defects the eye actually notices, and all three are removable:

| Defect | Where you see it | How it is removed |
|---|---|---|
| 🧱 **Blocking** | dark scenes, fast motion | `deblock`, temporal noise reduction |
| 🪜 **Stepped banding** | skies, fades, gradients | `deband`, done at 10 bits |
| 👻 **Edge halos** | around text and sharp borders | noise reduction, then adaptive sharpening |

Remove those and **the very same amount of detail reads far better**. That is 70% of the perceived improvement, at a fraction of the cost of AI.

### The filter order is not negotiable

This is the part almost every guide gets wrong, and on its own it separates a good result from a mess:

1. **Deinterlacing**, if needed — working on fields falsifies everything downstream
2. **Deblocking and noise reduction**, *before* any sharpening — otherwise you engrave the noise and make it permanent
3. **Debanding, done at 10 bits** — at 8 bits the cure creates new bands: smoothing a step needs in-between values that do not exist at 8 bits
4. **Upscaling**, on a frame that is finally clean
5. **Adaptive sharpening**, last — applying it before upscaling throws half the work away in the rescale

### The five presets

| Preset | For what | What it does differently |
|---|---|---|
| 🧼 **Clean** | already decent source | removes blocking and banding, **no upscaling**. The fastest |
| ⚖️ **Standard** | the normal YouTube video | measured cleanup plus upscaling |
| 🔨 **Strong** | badly degraded source | trades micro-detail away to get rid of the noise |
| 🎨 **Animation** | cartoons and anime | very light on noise (it eats the linework, which in animation *is* the drawing), heavy on banding |
| 📼 **Vintage** | broadcast or tape material | weaves the fields first, then cleans thoroughly |

With no instructions, the **diagnosis** picks the preset.

### How debanding is tuned

`deband` **does not flatten the steps: it dissolves them into noise**, exactly like dithering does. That is the right way to remove a real band — a visible contour is traded for a graininess the eye does not notice. But the filter works on the whole frame, including flat areas where there is no banding at all: there is nothing to trade there, and only the noise is left.

Measured on a heavily compressed video (AV1 at 305 kbit/s, 720p to 1440p), on the same flat dark wall:

| Tuning | Graininess | Blocking |
|---|---|---|
| upscale only, no filters | 0.805 | 1.618 |
| threshold 0.035 · range 24 · sharpening 0.55 | 2.686 | 1.204 |
| **threshold 0.010 · range 16 · sharpening 0.35** | **1.581** | **1.166** |

The gentle tuning wins on **both** counts: less noise *and* less blocking too. The aggressive one bought nothing — it only dirtied the picture, and the file ended up three times heavier because the encoder was spending bits describing that speckle.

Hence the low thresholds in the presets. The one exception is **Animation**, which stays the boldest: the large flat colour fills of cartoons really do band, and there the trade pays off.

### The diagnosis

Before touching anything, PixDex reads the file with `ffprobe` and looks at three quantities:

- the **resolution**, which says whether upscaling makes sense;
- the **bits per pixel** — bitrate divided by pixels and frames per second — which say how hard compression hit. Below **0.05 bpp** blocking is visible; below **0.025** it is visible even in motion;
- the **field order**, which says whether the material is broadcast.

None of the three requires decoding the video, so the advice arrives **instantly** even on an hour-long file.

```bash
python PixDex.py -i video.mp4 --info      # analyse and advise, writes nothing
```

### How far it upscales, and how to choose

**At the third step PixDex lets you choose**, showing for each mode the result on *that* file — not the marketing label:

```
┌────┬────────────────┬───────────────────────┬────────────────────┐
│  # │ How            │                Result │ What it is worth   │
├────┼────────────────┼───────────────────────┼────────────────────┤
│  1 │ ★ Automatic    │    360p → 720p  2.00× │ believable         │
│  2 │ Cleanup only   │           360p  1.00× │ original           │
│  3 │ HD  1080p      │   360p → 1080p  3.00× │ goes soft          │
│  4 │ 2K  1440p      │   360p → 1440p  4.00× │ just heavier       │
│  5 │ 4K  2160p      │   360p → 2160p  6.00× │ just heavier       │
│  6 │ Another height…│                       │                    │
└────┴────────────────┴───────────────────────┴────────────────────┘
```

This is where the program is at its most honest: **the very table that offers you 4K tells you, on the same row, that from a 360p source that 4K adds not one real detail** — only a heavier file. The thresholds:

| Factor | Verdict | What actually happens |
|---|---|---|
| **up to 2×** | 🟢 believable | interpolation has enough real pixels to work from |
| **up to 3×** | 🟡 goes soft | it holds, but the picture loses bite |
| **beyond 3×** | 🔴 just heavier | you are only writing a bigger number in the metadata |

**You can pick 4K anyway.** PixDex warns you once, in the work plan, then does what you asked without nagging on every run.

The **automatic** mode (★) stops at double and climbs to the next step of the standard ladder: 360p reaches 720p, 540p reaches 1080p. It is the only defensible value without having seen the file, and it is what `--yes` uses.

From the command line the same choice is pinned with `--height`:

```bash
python PixDex.py -i video.mp4 --height auto   # up to double (default)
python PixDex.py -i video.mp4 --height none   # cleanup only, original resolution
python PixDex.py -i video.mp4 --height hd     # 1080p
python PixDex.py -i video.mp4 --height 2k     # 1440p
python PixDex.py -i video.mp4 --height 4k     # 2160p
python PixDex.py -i video.mp4 --height 900    # exact height in pixels
```

### The before/after comparison

When it finishes, PixDex saves a PNG with **the same frame before and after, side by side**. It is the only honest way to judge: bitrate numbers say nothing about appearance, and comparing two successive playbacks from memory always flatters the second one.

Both frames are brought to **the same height**: otherwise upscaling would make the second one automatically bigger, and therefore more convincing regardless of merit. The frame is taken **one third** of the way in, because the opening is almost always a title card or a black screen.

### Encoding: software or GPU

| | `libx264` (default) | `--gpu` (`h264_amf`) |
|---|---|---|
| Speed | slow | **2.4× faster** (measured on a Ryzen 5 3500U + Vega 8) |
| Quality at equal size | **better** | slightly less clean |
| When | the normal case | long files, when time matters more than the result |

**Audio is never re-encoded**: it is copied as is from the source file, so it loses nothing.

### Command-line options (PixDex)

| Option | Short | Default | What it does |
|---|---|---|---|
| `--input` | `-i` | *(list)* | Video to remaster. Without it, lists the downloaded ones to choose from |
| `--output` | `-o` | *next to the original* | Destination file. The original is **never** overwritten |
| `--base` | `-b` | `download_audio` | Folder to look for videos in |
| `--preset` | `-p` | *(from the diagnosis)* | `pulito`, `standard`, `forte`, `animazione`, `vecchio` |
| `--height` | | `auto` | `auto` (up to double), `none` (cleanup only), `hd`, `2k`, `4k`, or a height in pixels. Without it, you pick it on screen |
| `--crf` | | `18` | libx264 quality: lower = better and heavier |
| `--gpu` | | *off* | Encode on the AMD GPU |
| `--no-compare` | | *off* | Do not save the comparison image |
| `--info` | | *off* | Analyse and show the diagnosis, without remastering |
| `--yes` | `-y` | *off* | No questions: use the suggested preset and start |

### Examples

```bash
python PixDex.py                                  # guided procedure
python PixDex.py -i video.mp4 --info              # analysis only, writes nothing
python PixDex.py -i video.mp4 -p animazione       # explicit preset
python PixDex.py -i video.mp4 --height 1080 --gpu # 1080p, encoded on the GPU
python PixDex.py -i video.mp4 -y                  # no questions
```

### In the GUI

`AudioDexApp.py` has a **Remaster** section: pick the file, press **Analyse** and the diagnosis appears in a panel — what is wrong, and which preset addresses it — *before* committing minutes or hours of processing. When it finishes, the before/after comparison shows up right there in the window, next to the diagnosis.

> ⏱ **How long it takes.** It depends on the processor: remastering is the heaviest operation in the whole project. While it runs, the bar shows processed frames and live speed (`1.2x` means it is running faster than the video's duration, `0.5x` twice as long). `--gpu` is much faster.

---

## ✂ ClipDex — cutting, joining, converting

`ClipDex.py` is the editing bench: the operations you actually need after a download, without opening an editing suite. Six operations, one subcommand each.

```bash
python ClipDex.py                                        # guided procedure
python ClipDex.py taglia -i v.mp4 --da 1:20 --a 3:45
python ClipDex.py unisci -d "download_audio/Album"
python ClipDex.py gif -i v.mp4 --da 0:30 --durata 4
python ClipDex.py provino -i v.mp4 --griglia 5x3
python ClipDex.py compat -i v.mp4
```

### Copy or re-encode: the choice that governs everything

| | Copy | Re-encode |
|---|---|---|
| What it does | moves already-compressed packets from one container to another | decodes and recompresses them |
| Time | **seconds** | minutes |
| Quality | **identical, not a bit lost** | one generation down |
| Constraints | cuts snap to keyframes; files to join must match | none |

ClipDex picks copy by itself whenever it can, and **always says which of the two it is using**.

### `taglia` — extracting a segment

Times are written the way they come to mind: `90`, `1:30`, `01:02:03.5`.

In copy mode the cut is instant, but the start snaps back to the previous keyframe: frames compressed together cannot be split in half. On a video with sparse keyframes the drift shows, so ClipDex **measures it and tells you**:

```
4.0 s asked, 7.0 obtained: 3.0 s more. In copy mode the start snaps back to the
previous keyframe, and in this file they are far apart. With --preciso the cut
lands where you said, at the cost of a re-encode
```

With `--preciso` the cut lands on the exact frame — verified: 4.0 s asked, 4.0 s obtained.

### `unisci` — putting several files in a row

Before joining, ClipDex compares codec, resolution, pixel format, frame rate and audio characteristics of every file:

- **matching** → glues them in copy mode, instantly;
- **different** → brings them all to the size of the first and re-encodes, because there is no other way: packets from two different encodings cannot be placed side by side.

A file with different proportions is **framed, not stretched**, and a silent file in the middle gets silence of the same length placed under it — without that, every following audio edit would drift out of sync.

By default it adds **one chapter per joined file**, so the result stays navigable like a DVD. `--no-capitoli` turns it off.

### `gif` and `webp` — making an animation

A GIF has **256 colours and no more**. FFmpeg's generic palette on a video with gradients produces a mush of dots; computing it on the real frames costs one extra pass. Measured on three seconds of real video, against the same frames not reduced to a palette:

| | Fidelity | Size |
|---|---|---|
| One pass, generic palette | 24.85 dB | 1414 KB |
| **Two passes, tailored palette** | **26.57 dB** | 2479 KB |
| Two passes, `sierra2_4a` dither | 26.56 dB | 3133 KB |
| **Animated WebP** | — | **283 KB** |

Hence the defaults: two passes (**+1.72 dB**, it shows), ordered Bayer dither — `sierra2_4a` costs a quarter more size and gives nothing back — and the push towards **WebP**, which is not bound to 256 colours and weighs **almost nine times less**. Every browser of the last decade reads it; if the destination is a twenty-year-old forum, then you need the GIF.

The three levers that matter: `--fps` (past 15 the size doubles for no visible gain), `--larghezza` (the factor that weighs most) and the duration. With no instructions it starts **one third** of the way in, because the opening is almost always a title card or a black screen.

### `provino` — seeing what is inside

A grid of frames taken at regular intervals across the whole length. To understand what a file contains it beats an animated preview: sixteen moments tell you at a glance whether it is the right video, where the scenes change and whether there are black stretches.

The interval is computed so the grid covers **the whole** duration — sampling at a fixed interval would leave out the second half of long videos. The cell has a fixed size, so the grid stays regular even if the footage changes format halfway.

### `compat` — making old devices read it

Three constraints, all necessary and all often violated by downloaded files:

| Constraint | Why |
|---|---|
| **Baseline** profile | no B-frames, which simpler decoders cannot handle |
| **yuv420p** colour | many YouTube files are yuv444 or 10-bit, which a 2012 TV will not decode |
| **Index at the head** of the file | without it, a USB-stick player must read to the end before it can start |

Verified on the produced file: `Constrained Baseline`, `yuv420p`, `level 30`, index within the first 4 KB.

---

## 🧩 Project architecture

```
AudioDex/
├── AudioDex.py               # Main CLI: search, selection, download, Rich UI
├── BurnDex.py                # 💿 Audio CD burner (Windows, IMAPI2)
├── PixDex.py                 # 🎞 Video remasterer (FFmpeg, cross-platform)
├── ClipDex.py                # ✂ Editing: cut, join, GIFs, sheets, compatibility
├── AudioDexApp.py            # 🖥 Graphical interface: opens the window, exposes the engine
├── web/                      # The interface itself
│   ├── index.html            # Structure of the four sections
│   ├── style.css             # Theme and animated background
│   ├── app.js                # Core and Audio section
│   ├── sez-burn.js           # Burning section
│   ├── sez-pix.js            # Remaster section
│   └── sez-clip.js           # Editing section
├── Shared/
│   ├── __init__.py
│   ├── logger_setup.py       # File logger + shared Rich theme/symbols
│   ├── i18n.py               # Language engine (the choice lives in the GUI)
│   ├── strings_audiodex.py   # AudioDex texts, Italian and English
│   ├── strings_burndex.py    # BurnDex texts, Italian and English
│   ├── strings_pixdex.py     # PixDex texts, Italian and English
│   ├── strings_clipdex.py    # ClipDex texts, Italian and English
│   └── http_client.py        # Shared HTTP helpers (User-Agent, headers, retry backoff)
├── Database_Globale/
│   ├── scraper_db.py         # Global SQLite download database
│   └── scraper_metadata.db   # The database (created automatically, git-ignored)
├── assets/                   # GUI background (downloaded on first launch, git-ignored)
├── download_audio/           # Output folder (created automatically, git-ignored)
│   └── <Artist> - <Album>/   # One folder per playlist, with numbered tracks
│       └── ordine.txt        # (optional) manual running order for BurnDex
├── logs/
│   ├── audiodex.log          # Detailed log of every session (git-ignored)
│   ├── burndex.log           # Burning log (git-ignored)
│   ├── pixdex.log            # Remastering log (git-ignored)
│   └── clipdex.log           # Editing log (git-ignored)
├── settings.json             # Language chosen in the GUI (git-ignored: it is the user's)
├── requirements.txt          # Python dependencies
├── README.md                 # Italian version
└── README.en.md              # This file
```

The `Shared/` and `Database_Globale/` modules are designed to be **shared across several scrapers** (audio, manga, anime): same visual theme, same logging, same database with type-specific columns.

`BurnDex.py` and `PixDex.py` are **independent**: they share only `Shared/` with AudioDex (Rich theme, logger, texts), import nothing from `AudioDex.py`, and work on files assembled by hand. Neither writes to the global database — burning and remastering are not downloads, and recording them there would distort the download log.

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

### 2026-08-02

**New**

- 🖼️ **Square cover art and volume tags, automatically.** The 16:9 YouTube thumbnail went into the tag as it was, and players showing cover art in a square either squashed it or cropped it through a face: now the whole image sits at the centre of a square filled with a blurred copy of itself, and nothing is lost (0.4 s). Volume is measured to EBU R128 and noted in ReplayGain tags — the audio is not touched, they are two tags you can delete. The measurement uses `ebur128` instead of `loudnorm`: same numbers, **2.3 s instead of 11.6**. See [Cover art and volume](#cover-art-and-volume-automatically)
- ⚖️ **BurnDex levelling became the default**, now that it costs four seconds per track instead of twenty. Turn it off with `--no-level`
- ✂ **ClipDex — the editing bench.** Six command-line operations: `taglia` a segment (instant in copy mode, and if the keyframe drift shows it tells you with a number), `unisci` several files picking copy or re-encode by itself and adding one chapter each, `gif` and `webp` with the palette computed on the footage (+1.72 dB measured against the generic one; WebP weighs nine times less), `provino` grids and `compat` for old car stereos and TVs. See [ClipDex](#-clipdex--cutting-joining-converting)
- 📀 **Whole albums split into their tracks.** A great many uploads are "Full Album": a single three-quarter-hour video with chapters. AudioDex recognises them and cuts them **without re-encoding**, into a numbered, tagged folder already fit for BurnDex. The point is not cutting but knowing *whether* to cut: five criteria tell a record from an index, and if even one fails nothing is asked. From the command line, `--split` and `--no-split`. See [Whole albums split into tracks](#-whole-albums-split-into-tracks)
- 🔊 **16-bit dithering in BurnDex, always on.** The reduction to 16 bit was done by truncation, which produces distortion *correlated with the signal* — what you hear as a dirty sound on quiet passages. Measured on a −70 dBFS tone, the energy on the harmonics drops from +46.9 dB to +31.1 dB relative to the fundamental. See [What happens to the audio before burning](#what-happens-to-the-audio-before-burning)
- ⚖️ **`--level` in BurnDex**: evens out the volume across tracks to the EBU R128 standard, respecting true peak. On three songs at −7, −14 and −21 dB the spread goes from 14.0 dB to **0.59 dB**
- ✂️ **`--trim` in BurnDex**: trims the silence at the start and end of each track, which adds to the 2-second gap inserted by IMAPI2. On the test collection, 3.4 seconds per track
- 🛡 **Download integrity checks in AudioDex.** The check was "the file is over 10 KB", and a truncated download passed — only to be recognised as already downloaded on the next attempt, and never fetched again. Container, actual duration against the announced one, and audio stream decoding are now all checked. A damaged file is deleted and the track lands among the failed ones
- 🎞 **PixDex — video remasterer.** `PixDex.py` takes a poor-quality video and cleans it up: it removes compression blocking, smooths stepped banding in skies and fades, and upscales with Lanczos. **Five presets** (Clean, Standard, Strong, Animation, Vintage) picked automatically by a **diagnosis** that reads resolution, bits per pixel and field order without decoding the file. Debanding is done at **10 bits**, because at 8 bits the cure creates new bands. When it finishes it saves a PNG with the **before/after comparison**, both frames at the same height so the comparison stays honest. It invents no detail: it works by subtraction. See [PixDex](#-pixdex--remastering-a-video)
- 🔧 **Debanding retuned from measurements, not by eye.** The `deband` thresholds were too aggressive and produced speckle in flat areas: the filter does not flatten steps, it dissolves them into noise, and where there is no banding only the noise is left. Measured on an AV1 video at 305 kbit/s, the gentle tuning wins on **both** counts — graininess from 2.686 to 1.581 and blocking from 1.204 to 1.166 — and produces far lighter files, because the encoder no longer spends bits describing the speckle. See [How debanding is tuned](#how-debanding-is-tuned)
- ⚡ **GPU on by default in the GUI**: measured 2.4× faster on the real filter chain (30.9 s against 73.6 s for the same clip on a Ryzen 5 3500U + Vega 8)
- 🎚 **Target resolution chosen at the third step**, with a table that for each mode shows the result on *that* file, the upscaling factor and what it is actually worth: the very row that offers 4K says it adds not one detail from a 360p source. From the command line, `--height auto|none|hd|2k|4k|PIXELS`. See [How far it upscales](#how-far-it-upscales-and-how-to-choose)
- 🖥 **Remaster video section in the GUI**, with the diagnosis shown *before* committing hours of processing and the before/after comparison right there in the window

**Changes**

- 🇮🇹 **The three CLIs speak Italian only.** No more language question on first launch and no more `--lang`: whoever opens a terminal wants to see the banner and go. The Italian/English choice stays in the GUI, where it is one click and the effect is immediate
- 🔤 **UTF-8 console output across all tools.** Arrows, box drawing and emoji used to crash the programs with `UnicodeEncodeError` inside the classic `cmd.exe`, which uses the old cp1252 code page — halfway through a download or, worse, a burn. The streams are now reconfigured at startup

### 2026-07-26

**New**

- 🌍 **Interface in Italian or English.** The GUI has an **Italiano / English** dropdown in the sidebar: it switches instantly — menu entries, labels, buttons, diagnostics, messages — and remembers the choice in `settings.json`. The three command-line programs speak Italian only: no question on first launch and no option to remember. See [Interface language](#-interface-language)
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
