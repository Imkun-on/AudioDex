# Scraper_Audio.py
# Downloader audio da YouTube (singoli brani e playlist) con UI Rich,
# tagging dei metadati .m4a via mutagen e registrazione su database globale.
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import re
import shutil
import signal
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import yt_dlp

import sys as _sys
# Tool standalone: eseguibile anche da fuori la cartella del progetto.
_HERE = os.path.dirname(os.path.abspath(__file__))
_sys.path.insert(0, _HERE)

from Database_Globale import scraper_db

from rich.align import Align
from rich.box import DOUBLE, ROUNDED
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn, MofNCompleteColumn,
    TimeElapsedColumn, TimeRemainingColumn, TaskProgressColumn,
    DownloadColumn, TransferSpeedColumn,
)
from rich.style import Style
from rich.table import Table
from rich.text import Text

from Shared.logger_setup import setup_logger, console, SYM_OK, SYM_FAIL, SYM_ARROW, SYM_DOT
from Shared.http_client import retry_delay

try:
    from mutagen.mp4 import MP4, MP4Cover
    _HAS_MUTAGEN = True
except ImportError:
    _HAS_MUTAGEN = False

SYM_NOTE = '[accent]♫[/accent]'

# API pubblica e gratuita di testi sincronizzati (formato LRC), senza chiave.
LRCLIB_API = 'https://lrclib.net/api'


def _print_banner() -> None:
    """Stampa il banner ASCII colorato 'AudioDex' all'avvio del programma."""
    banner_lines = [
        '    ___             ___           _____                                ',
        '   /   | __  ______/ (_)___      / ___/______________ _____  ___  _____',
        '  / /| |/ / / / __  / / __ \\     \\__ \\/ ___/ ___/ __ `/ __ \\/ _ \\/ ___/',
        ' / ___ / /_/ / /_/ / / /_/ /    ___/ / /__/ /  / /_/ / /_/ /  __/ /    ',
        '/_/  |_\\__,_/\\__,_/_/\\____/____/____/\\___/_/   \\__,_/ .___/\\___/_/     ',
        '                         /_____/                   /_/                 ',
    ]
    colors = ['bright_magenta', 'magenta', 'bright_blue', 'blue', 'bright_cyan', 'cyan']
    text = Text()
    for i, line in enumerate(banner_lines):
        text.append(line + '\n', style=Style(color=colors[i % len(colors)], bold=True))
    console.print()
    console.print(Panel(
        Align.center(text),
        border_style='bright_blue',
        box=DOUBLE,
        padding=(1, 2),
        expand=False,
    ))


# Parametri di funzionamento
MAX_DOWNLOAD_WORKERS = 3   # Download simultanei (thread)
MAX_RETRIES = 4            # Tentativi per traccia prima di dichiararla fallita
RETRY_BASE_DELAY = 3       # Secondi di base del backoff esponenziale tra i retry
REQUEST_TIMEOUT = 30       # Timeout (secondi) delle richieste HTTP
MIN_DISK_SPACE_MB = 200    # Sotto questa soglia di spazio libero si chiede conferma
MAX_SEARCH_RESULTS = 15    # Numero massimo di risultati mostrati per una ricerca


log = setup_logger('scraper_audio', 'scraper_audio.log')


# Evento condiviso tra i thread: quando viene impostato (primo Ctrl+C) i
# download non ancora partiti vengono annullati e il programma si chiude
# in modo pulito appena terminano quelli in corso.
_shutdown_event = threading.Event()

# Impostato da --cookies-from-browser: yt-dlp legge i cookie del browser
# indicato e si presenta a YouTube autenticato. Serve per playlist e video
# privati, che altrimenti risultano "inesistenti".
_cookies_browser: str | None = None


def _apply_cookies(ydl_opts: dict) -> dict:
    """Aggiunge le opzioni cookie a un dict di opzioni yt-dlp, se richieste."""
    if _cookies_browser:
        ydl_opts['cookiesfrombrowser'] = (_cookies_browser,)
    return ydl_opts


def _signal_handler(signum, frame):
    """Gestisce Ctrl+C: il primo chiede l'arresto pulito, il secondo forza l'uscita."""
    if _shutdown_event.is_set():
        log.warning('Secondo Ctrl+C - terminazione forzata')
        os._exit(1)
    log.warning('Ctrl+C ricevuto - completamento download in corso, poi arresto...')
    _shutdown_event.set()


def _retry_delay(attempt: int) -> float:
    """Calcola l'attesa tra un tentativo fallito e il successivo.

    Backoff esponenziale (cresce a ogni tentativo) con jitter casuale, per
    non riprovare a raffica e non sincronizzare i retry dei vari thread.
    """
    return retry_delay(attempt, base=RETRY_BASE_DELAY, jitter=(1.0, 3.0))


def _sanitize_filename(name: str) -> str:
    """Sostituisce con '_' i caratteri vietati da Windows nei nomi file."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def _check_disk_space(path: str) -> bool:
    """Controlla lo spazio libero sul disco di destinazione.

    Sotto la soglia MIN_DISK_SPACE_MB avvisa e chiede conferma; restituisce
    False solo se l'utente rinuncia. Un errore di lettura non blocca: meglio
    tentare il download che fermarsi per un controllo accessorio.
    """
    try:
        os.makedirs(path, exist_ok=True)
        free_mb = shutil.disk_usage(path).free / 1048576
        if free_mb < MIN_DISK_SPACE_MB:
            log.warning('Spazio disco basso: %.0f MB liberi', free_mb)
            console.print(f'\n[warning]ATTENZIONE: solo {free_mb:.0f} MB liberi.[/warning]')
            answer = console.input('[bold]Continuare? (s/n): [/bold]').strip().lower()
            if answer != 's':
                return False
        else:
            log.info('Spazio disco: %.0f MB liberi', free_mb)
        return True
    except OSError:
        return True


def _format_duration(seconds: int | float | None) -> str:
    """Converte una durata in secondi nel formato leggibile M:SS o H:MM:SS."""
    if not seconds:
        return '??:??'
    seconds = int(seconds)
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    if h > 0:
        return f'{h}:{m:02d}:{s:02d}'
    return f'{m}:{s:02d}'


def _format_size(bytes_val: int | float | None) -> str:
    """Converte una dimensione in byte in una stringa leggibile (MB o GB)."""
    if not bytes_val:
        return '?? MB'
    mb = bytes_val / 1048576
    if mb >= 1024:
        return f'{mb / 1024:.1f} GB'
    return f'{mb:.1f} MB'


def _format_views(views: int | float | None) -> str:
    """Converte un conteggio di visualizzazioni in forma compatta (es. 2.1 Mrd)."""
    if not views:
        return '—'
    views = int(views)
    if views >= 1_000_000_000:
        return f'{views / 1_000_000_000:.1f} Mrd'
    if views >= 1_000_000:
        return f'{views / 1_000_000:.1f} Mln'
    if views >= 1_000:
        return f'{views / 1_000:.0f} K'
    return str(views)


def _clean_track_title(title: str) -> str:
    """Ripulisce il titolo YouTube dalle decorazioni non musicali.

    Rimuove le parentesi tipo '(Official Video)', '[HD]', '(Lyrics)' ecc.,
    che farebbero fallire la ricerca del testo nei database di lyrics.
    """
    cleaned = re.sub(
        r'[\(\[][^)\]]*(official|video|lyric|audio|visualizer|hd|4k|remaster|m/?v)[^)\]]*[\)\]]',
        '', title, flags=re.IGNORECASE,
    )
    cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip(' -_|')
    return cleaned or title


def _fetch_lyrics(title: str, artist: str, duration: int | float | None) -> tuple[str | None, str | None]:
    """Cerca su LRCLIB il testo sincronizzato (karaoke) di una traccia.

    Restituisce (testo_sincronizzato_lrc, testo_semplice); entrambi None se
    non trovato. Prima tenta la corrispondenza esatta artista+titolo+durata,
    poi una ricerca libera scartando i risultati con durata troppo diversa
    (>10s: probabilmente versione live o remix). Qualsiasi errore di rete
    viene solo loggato: i testi sono un extra, mai un motivo di fallimento.
    """
    cleaned = _clean_track_title(title)
    artist = (artist or '').removesuffix(' - Topic').strip()
    track = cleaned
    # Titoli nel formato 'Artista - Brano': più affidabili del nome canale
    if ' - ' in cleaned:
        maybe_artist, maybe_track = cleaned.split(' - ', 1)
        artist, track = maybe_artist.strip(), maybe_track.strip()

    headers = {'User-Agent': 'AudioDex/1.0 (https://github.com/Imkun-on/Scraper_Audio)'}
    try:
        if artist and duration:
            resp = requests.get(
                f'{LRCLIB_API}/get',
                params={'artist_name': artist, 'track_name': track, 'duration': int(duration)},
                headers=headers, timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                if not data.get('instrumental'):
                    return data.get('syncedLyrics'), data.get('plainLyrics')

        params = {'track_name': track, 'artist_name': artist} if artist else {'q': track}
        resp = requests.get(f'{LRCLIB_API}/search', params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            for item in resp.json():
                if item.get('instrumental'):
                    continue
                if duration and item.get('duration') and abs(item['duration'] - duration) > 10:
                    continue
                if item.get('syncedLyrics') or item.get('plainLyrics'):
                    return item.get('syncedLyrics'), item.get('plainLyrics')
    except Exception as e:
        log.debug("LRCLIB errore per '%s': %s", title, e)
    return None, None


def search_youtube(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list[dict]:
    """Cerca brani su YouTube e restituisce i metadati dei risultati.

    Usa la ricerca interna di yt-dlp con 'extract_flat': ottiene solo titolo,
    canale, durata e URL senza scaricare nulla. La lista serve a mostrare i
    risultati all'utente e fargli scegliere cosa scaricare.
    """
    log.info("Ricerca YouTube: '%s'", query)
    results = []

    ydl_opts = _apply_cookies({
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 'default_search' restituisce 0 risultati con yt-dlp recenti:
            # serve il prefisso esplicito ytsearchN:
            info = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
            if not info:
                return []
            entries = info.get('entries', [])
            if not entries:
                # Risultato singolo (URL diretto)
                if info.get('id'):
                    results.append({
                        'id': info['id'],
                        'title': info.get('title', 'Sconosciuto'),
                        'uploader': info.get('uploader') or info.get('channel') or '??',
                        'duration': info.get('duration'),
                        'views': info.get('view_count'),
                        'url': info.get('webpage_url', f"https://www.youtube.com/watch?v={info['id']}"),
                    })
                return results
            for entry in entries:
                if not entry:
                    continue
                vid_id = entry.get('id', '')
                results.append({
                    'id': vid_id,
                    'title': entry.get('title', 'Sconosciuto'),
                    'uploader': entry.get('uploader') or entry.get('channel') or '??',
                    'duration': entry.get('duration'),
                    'views': entry.get('view_count'),
                    'url': entry.get('url', entry.get('webpage_url', f'https://www.youtube.com/watch?v={vid_id}')),
                })
    except Exception as e:
        log.error('Errore ricerca: %s', e)

    return results


def _normalize_playlist_url(url: str) -> str:
    """Converte un URL 'watch?v=...&list=...' nell'URL canonico della playlist.

    Se si passa a yt-dlp l'URL di un video appartenente a una playlist, viene
    estratto solo quel video: per avere l'elenco completo serve l'URL
    'playlist?list=<ID>'.
    """
    match = re.search(r'[?&]list=([\w-]+)', url)
    if match and 'playlist?list=' not in url:
        return f'https://www.youtube.com/playlist?list={match.group(1)}'
    return url


def get_playlist_entries(url: str) -> tuple[str, list[dict]]:
    """Recupera titolo e tracce di una playlist/album, o di un singolo video.

    Come per la ricerca, 'extract_flat' scarica solo i metadati. Con
    'ignoreerrors' i video privati o rimossi vengono saltati invece di far
    fallire l'intera playlist. Restituisce (titolo, lista di tracce).
    """
    log.info('Recupero playlist: %s', url)
    entries = []
    playlist_title = 'Playlist'

    if _is_playlist_url(url):
        url = _normalize_playlist_url(url)
        log.debug('URL normalizzato: %s', url)

    ydl_opts = _apply_cookies({
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
        'noplaylist': False,
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return playlist_title, []
            playlist_title = info.get('title', 'Playlist')
            raw_entries = info.get('entries', [])
            if not raw_entries:
                # Forse è un video singolo invece di una playlist
                if info.get('id'):
                    entries.append({
                        'id': info['id'],
                        'title': info.get('title', 'Sconosciuto'),
                        'uploader': info.get('uploader') or info.get('channel') or '??',
                        'duration': info.get('duration'),
                        'views': info.get('view_count'),
                        'url': info.get('webpage_url', url),
                    })
                return playlist_title, entries
            for entry in raw_entries:
                if not entry:
                    continue
                vid_id = entry.get('id', '')
                entries.append({
                    'id': vid_id,
                    'title': entry.get('title', 'Sconosciuto'),
                    'uploader': entry.get('uploader') or entry.get('channel') or '??',
                    'duration': entry.get('duration'),
                    'views': entry.get('view_count'),
                    'url': entry.get('url', entry.get('webpage_url', f'https://www.youtube.com/watch?v={vid_id}')),
                })
    except Exception as e:
        log.error('Errore recupero playlist: %s', e)

    return playlist_title, entries


def _display_search_results(results: list[dict], table_title: str = 'Risultati ricerca') -> None:
    """Mostra un elenco di tracce in una tabella numerata (per la selezione).

    Usata sia per i risultati di ricerca sia per le tracce di una playlist.
    """
    table = Table(
        title=table_title,
        box=ROUNDED,
        border_style='bright_blue',
        header_style='bold bright_cyan',
        row_styles=['', 'dim'],
        expand=False,
    )
    table.add_column('#', style='bold yellow', justify='right', width=4)
    table.add_column('Titolo', style='white', max_width=50, no_wrap=True)
    table.add_column('Artista/Canale', style='bright_magenta', max_width=25, no_wrap=True)
    table.add_column('Durata', style='cyan', justify='right', width=8)
    table.add_column('Views', style='green', justify='right', width=9)

    for i, r in enumerate(results, 1):
        table.add_row(
            str(i),
            r['title'][:50],
            (r.get('uploader') or '??')[:25],
            _format_duration(r.get('duration')),
            _format_views(r.get('views')),
        )

    console.print()
    console.print(table)


def _display_playlist_info(title: str, entries: list[dict]) -> None:
    """Mostra un pannello riassuntivo della playlist: titolo, tracce, durata totale."""
    total_duration = sum(e.get('duration', 0) or 0 for e in entries)
    console.print()
    console.print(Panel(
        f'[title]{title}[/title]\n'
        f'[dim_label]Tracce:[/dim_label] [ep]{len(entries)}[/ep]   '
        f'[dim_label]Durata totale:[/dim_label] [ep]{_format_duration(total_duration)}[/ep]',
        border_style='bright_blue',
        box=ROUNDED,
        expand=False,
    ))


def _display_download_summary(results: list[dict]) -> None:
    """Mostra il riepilogo finale: quante tracce scaricate, già presenti, fallite."""
    ok = sum(1 for r in results if r['status'] == 'ok')
    fail = sum(1 for r in results if r['status'] == 'fail')
    skip = sum(1 for r in results if r['status'] == 'skip')

    summary_table = Table(show_header=False, box=None, padding=(0, 2), expand=False)
    summary_table.add_column('Label', style='dim_label')
    summary_table.add_column('Value')

    summary_table.add_row('Tracce totali', f'[bold]{len(results)}[/bold]')
    summary_table.add_row(f'{SYM_OK} Scaricate', f'[success]{ok}[/success]')
    lyrics_found = sum(1 for r in results if r.get('lyrics'))
    if lyrics_found > 0:
        summary_table.add_row(f'{SYM_NOTE} Testi karaoke', f'[info]{lyrics_found}[/info]')
    if skip > 0:
        summary_table.add_row(f"{SYM_DOT} Gia' presenti", f'[info]{skip}[/info]')
    if fail > 0:
        summary_table.add_row(f'{SYM_FAIL} Fallite', f'[error]{fail}[/error]')
        failed_titles = [r['title'] for r in results if r['status'] == 'fail']
        summary_table.add_row('  Tracce', f"[error]{', '.join(t[:30] for t in failed_titles)}[/error]")

    border = 'red' if fail else 'bright_green'
    title_icon = '❌' if fail else '✅'

    console.print()
    console.print(Panel(
        summary_table,
        title=f'{title_icon} Riepilogo',
        border_style=border,
        box=DOUBLE,
        expand=False,
        padding=(1, 3),
    ))


def _tag_m4a(filepath: str, title: str | None = None, artist: str | None = None,
             album: str | None = None, track_num: int | None = None,
             thumbnail_url: str | None = None, lyrics: str | None = None) -> None:
    """Scrive i metadati (titolo, artista, album, n. traccia, copertina, testo) nel file.

    I file .m4a usano il container MP4, quindi i tag seguono lo standard
    iTunes (©nam, ©ART, ...). La copertina viene scaricata dalla thumbnail
    di YouTube e incorporata nel file. Se mutagen non è installato non fa
    nulla: il download resta comunque valido, solo senza tag.
    """
    if not _HAS_MUTAGEN:
        log.debug('mutagen non installato - skip tagging')
        return

    try:
        audio = MP4(filepath)
        tags = audio.tags
        if tags is None:
            audio.add_tags()
            tags = audio.tags

        if title:
            tags['©nam'] = [title]
        if artist:
            tags['©ART'] = [artist]
        if album:
            tags['©alb'] = [album]
        if track_num:
            tags['trkn'] = [(track_num, 0)]
        if lyrics:
            tags['©lyr'] = [lyrics]

        if thumbnail_url:
            try:
                resp = requests.get(thumbnail_url, timeout=15)
                resp.raise_for_status()
                content_type = resp.headers.get('Content-Type', '')
                if 'png' in content_type:
                    img_format = MP4Cover.FORMAT_PNG
                else:
                    img_format = MP4Cover.FORMAT_JPEG
                tags['covr'] = [MP4Cover(resp.content, imageformat=img_format)]
                log.debug('Copertina aggiunta: %s', title)
            except Exception as e:
                log.debug('Impossibile scaricare copertina: %s', e)

        audio.save()
        log.debug('Tag salvati: %s', filepath)
    except Exception as e:
        log.warning('Errore tagging %s: %s', os.path.basename(filepath), e)


def _is_already_downloaded(title: str, output_dir: str) -> str | None:
    """Controlla se la traccia è già stata scaricata nella cartella di destinazione.

    Confronta il titolo sanificato con i nomi dei file esistenti, ignorando
    l'estensione. I file sotto i 10 KB vengono considerati download
    incompleti e quindi da rifare. Restituisce il percorso del file trovato
    oppure None: evita di riscaricare le stesse tracce nei run successivi.
    """
    safe_title = _sanitize_filename(title).lower()
    if not os.path.isdir(output_dir):
        return None
    for f in os.listdir(output_dir):
        name_no_ext = os.path.splitext(f)[0].lower()
        if name_no_ext == safe_title:
            full = os.path.join(output_dir, f)
            if os.path.getsize(full) > 10240:
                return full
    return None


class _YtDlpProgressHook:
    """Ponte tra yt-dlp e la barra di avanzamento Rich del singolo file.

    yt-dlp invoca quest'oggetto a ogni blocco scaricato; noi aggiorniamo la
    barra con i byte ricevuti. La dimensione totale non è nota subito (a
    volte è solo una stima che arriva dopo le prime chiamate), perciò viene
    impostata al primo valore disponibile.
    """

    def __init__(self, progress: Progress, task_id, title: str):
        self.progress = progress
        self.task_id = task_id
        self.title = title
        self._started = False
        self._total = 0

    def __call__(self, d: dict) -> None:
        """Callback invocata da yt-dlp con lo stato corrente del download."""
        try:
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    self._total = total
                    if not self._started:
                        self.progress.update(self.task_id, total=total)
                        self._started = True
                    self.progress.update(self.task_id, completed=downloaded)
            elif d['status'] == 'finished':
                if self._started and self._total > 0:
                    self.progress.update(self.task_id, completed=self._total)
        except Exception:
            pass


def download_single(entry: dict, output_dir: str, audio_format: str = 'm4a',
                    track_num: int | None = None, album: str | None = None,
                    progress: Progress | None = None, task_id=None,
                    fetch_lyrics: bool = True) -> dict:
    """Scarica una singola traccia come file audio e ne registra i metadati.

    Flusso completo:
      1. salta subito se il file esiste già su disco (status 'skip');
      2. scarica il solo flusso audio (mai il video) e lo converte nel
         formato richiesto tramite ffmpeg;
      3. cerca il testo sincronizzato su LRCLIB e, se trovato, lo incorpora
         nei tag del file audio (un file unico, nessun .lrc separato);
      4. scrive anche titolo, artista, album e copertina nei tag;
      5. registra il download nel database globale.
    In caso di errore riprova fino a MAX_RETRIES volte con attesa crescente.

    Restituisce {'title', 'status' ('ok'/'skip'/'fail'), 'file', 'error',
    'lyrics' (True se è stato trovato e incorporato il testo)}.
    """
    title = entry.get('title', 'Sconosciuto')
    url = entry.get('url', '')
    uploader = entry.get('uploader', '')

    result = {'title': title, 'status': 'fail', 'file': '', 'error': '', 'lyrics': False}

    if _shutdown_event.is_set():
        result['error'] = 'shutdown'
        return result

    existing = _is_already_downloaded(title, output_dir)
    if existing:
        log.info("Gia' scaricato: %s", title)
        result['status'] = 'skip'
        result['file'] = os.path.basename(existing)
        if progress and task_id is not None:
            progress.update(task_id, completed=progress.tasks[task_id].total or 1, total=1)
        return result

    os.makedirs(output_dir, exist_ok=True)

    outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')

    # Solo audio: niente traccia video, il file occupa una frazione dello spazio.
    # 'FFmpegExtractAudio' converte (o rimuxa senza ricodifica, quando il
    # formato sorgente coincide) nel formato scelto dall'utente.
    ydl_opts = _apply_cookies({
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'retries': MAX_RETRIES,
        'fragment_retries': MAX_RETRIES,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '0',
        }],
        'writethumbnail': False,
        'noplaylist': True,
    })

    if progress and task_id is not None:
        hook = _YtDlpProgressHook(progress, task_id, title)
        ydl_opts['progress_hooks'] = [hook]

    for attempt in range(1, MAX_RETRIES + 1):
        if _shutdown_event.is_set():
            result['error'] = 'shutdown'
            return result
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise Exception('Nessuna info estratta')

                final_ext = audio_format
                expected_file = ydl.prepare_filename(info)
                base, _ = os.path.splitext(expected_file)
                final_file = f'{base}.{final_ext}'

                if not os.path.isfile(final_file):
                    # Fallback: cerca il file per nome ed estensione
                    safe = _sanitize_filename(info.get('title', title)).lower()
                    for f in os.listdir(output_dir):
                        if not f.lower().endswith(f'.{final_ext}'):
                            continue
                        name_no_ext = os.path.splitext(f)[0].lower()
                        if name_no_ext != safe:
                            continue
                        final_file = os.path.join(output_dir, f)
                        break

                if os.path.isfile(final_file):
                    # Testo: incorporato direttamente nei tag del file audio
                    # (formato LRC con i timestamp), così il brano resta un
                    # file unico che porta con sé anche il testo.
                    synced, plain = (None, None)
                    if fetch_lyrics:
                        synced, plain = _fetch_lyrics(
                            info.get('title', title),
                            info.get('artist') or info.get('uploader') or uploader,
                            info.get('duration') or entry.get('duration'),
                        )
                        if synced or plain:
                            result['lyrics'] = True
                            log.info('Testo trovato: %s', title)

                    thumbnail = info.get('thumbnail')
                    _tag_m4a(
                        final_file,
                        title=info.get('title', title),
                        artist=info.get('artist') or info.get('uploader') or uploader,
                        album=album or info.get('album'),
                        track_num=track_num,
                        thumbnail_url=thumbnail,
                        lyrics=synced or plain,
                    )

                    result['status'] = 'ok'
                    result['file'] = os.path.basename(final_file)
                    log.info('%s Scaricato: %s', SYM_OK, title)

                    scraper_db.record_audio_download(
                        source_id=entry.get('id', ''),
                        title=info.get('title', title),
                        source_url=url,
                        file_path=final_file,
                        file_size_bytes=os.path.getsize(final_file),
                        collection_name=album or info.get('album', ''),
                        artist=info.get('artist') or info.get('uploader') or uploader,
                        duration_secs=info.get('duration') or entry.get('duration') or 0,
                        audio_format=audio_format,
                        track_number=track_num or 0,
                    )

                    return result

                raise FileNotFoundError(f'File non trovato dopo download: {final_file}')
        except Exception as e:
            log.warning("Tentativo %d/%d fallito per '%s': %s", attempt, MAX_RETRIES, title, e)
            result['error'] = str(e)[:100]
            if attempt < MAX_RETRIES:
                delay = _retry_delay(attempt)
                log.debug('Retry tra %.1fs...', delay)
                time.sleep(delay)

    log.error('%s Fallito: %s - %s', SYM_FAIL, title, result['error'])
    return result


def download_batch(entries: list[dict], output_dir: str, audio_format: str = 'm4a',
                   album: str | None = None, max_workers: int = MAX_DOWNLOAD_WORKERS,
                   fetch_lyrics: bool = True) -> list[dict]:
    """Scarica più tracce in parallelo mostrando le barre di avanzamento.

    Usa un pool di thread (max_workers download simultanei) e due barre
    Rich aggiornate live: una complessiva sulle tracce e una per ciascun
    file in corso. Un Ctrl+C ferma l'accodamento di nuove tracce lasciando
    finire quelle già partite. I risultati vengono riordinati secondo
    l'ordine originale delle entry (i thread terminano in ordine sparso).
    """
    os.makedirs(output_dir, exist_ok=True)
    total = len(entries)
    results = []
    stopped_early = False

    console.print()
    console.rule('[phase]⬇ Download audio[/phase]', style='bright_green')
    console.print(f'  [dim_label]Thread:[/dim_label] [info]{max_workers}[/info]  [dim_label]Tracce:[/dim_label] [bold]{total}[/bold]\n')

    overall_progress = Progress(
        SpinnerColumn('dots', style='bright_green'),
        TextColumn('[bold bright_green]{task.description}'),
        BarColumn(bar_width=50, style='bar.back', complete_style='bright_green', finished_style='bold green'),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TextColumn('[dim]│[/dim]'),
        TimeElapsedColumn(),
        TextColumn('[dim]→[/dim]'),
        TimeRemainingColumn(),
        console=console,
        expand=False,
    )

    file_progress = Progress(
        SpinnerColumn('dots', style='cyan'),
        TextColumn('{task.description}', markup=True),
        BarColumn(bar_width=30, style='bar.back', complete_style='cyan', finished_style='bold cyan'),
        TaskProgressColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TextColumn('[dim]→[/dim]'),
        TimeRemainingColumn(),
        console=console,
        expand=False,
    )

    overall_task = overall_progress.add_task('Tracce', total=total)

    with Live(Group(overall_progress, file_progress), console=console, refresh_per_second=10):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            task_ids = {}

            for i, entry in enumerate(entries):
                if _shutdown_event.is_set():
                    stopped_early = True
                    break
                tid = file_progress.add_task(
                    f"[bold]#{i + 1}[/bold] {entry['title'][:40]}",
                    total=None,
                    visible=True,
                )
                task_ids[i] = tid
                future = executor.submit(
                    download_single, entry, output_dir, audio_format,
                    track_num=i + 1, album=album,
                    progress=file_progress, task_id=tid,
                    fetch_lyrics=fetch_lyrics,
                )
                futures[future] = i

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    result = {
                        'title': entries[idx]['title'],
                        'status': 'fail',
                        'error': str(e)[:100],
                        'file': '',
                    }
                    log.error('Eccezione download: %s', e)

                results.append(result)
                overall_progress.advance(overall_task)

                tid = task_ids.get(idx)
                if tid is not None:
                    file_progress.remove_task(tid)

                if _shutdown_event.is_set():
                    stopped_early = True
                    for f in futures:
                        f.cancel()
                    break

    results.sort(key=lambda r: next((i for i, e in enumerate(entries) if e['title'] == r['title']), 999))

    return results


def _export_failed(output_dir: str, results: list[dict], entries: list[dict]) -> None:
    """Salva titoli e URL delle tracce fallite in failed_tracks.txt.

    Così l'utente può ritentarle in un secondo momento con --url senza
    dover rifare la ricerca o ricaricare l'intera playlist.
    """
    failed = [r for r in results if r['status'] == 'fail']
    if not failed:
        return

    filepath = os.path.join(output_dir, 'failed_tracks.txt')
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('# Tracce fallite\n')
            f.write('# Per ritentare, copia gli URL e usa: python Scraper_Audio.py --url <URL>\n#\n')
            for r in failed:
                matching = [e for e in entries if e['title'] == r['title']]
                url = matching[0]['url'] if matching else '??'
                f.write(f"{r['title']} | {url}\n")
        console.print(f'\n  Tracce fallite salvate in: [info]{filepath}[/info]')
    except OSError as e:
        log.error('Impossibile salvare tracce fallite: %s', e)


def _select_from_results(results: list[dict]) -> list[dict]:
    """Chiede all'utente quali tracce scaricare tra quelle elencate.

    Accetta un numero singolo (3), un intervallo (1-5), un elenco (1,3,7),
    'all'/'tutti' per tutte oppure 'q' per annullare. Ripete la domanda
    finché l'input non è valido. Restituisce le entry scelte, senza
    duplicati e nell'ordine di selezione.
    """
    console.print(
        '\n[dim_label]Seleziona:[/dim_label] numero singolo ([accent]3[/accent]), '
        'intervallo ([accent]1-5[/accent]), multipli ([accent]1,3,7[/accent]), '
        '[accent]all[/accent] per tutti, [accent]q[/accent] per uscire'
    )

    while True:
        choice = console.input('\n[bold]Scegli > [/bold]').strip().lower()
        if choice in ('q', 'quit', 'esci'):
            return []
        if choice in ('all', 'a', 'tutti'):
            return results

        selected = []
        try:
            parts = choice.replace(' ', ',').split(',')
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if '-' in part:
                    start, end = part.split('-', 1)
                    for n in range(int(start), int(end) + 1):
                        if 1 <= n <= len(results):
                            selected.append(results[n - 1])
                else:
                    n = int(part)
                    if 1 <= n <= len(results):
                        selected.append(results[n - 1])

            if selected:
                # Rimuovi duplicati mantenendo l'ordine
                seen = set()
                unique = []
                for s in selected:
                    if s['id'] not in seen:
                        seen.add(s['id'])
                        unique.append(s)
                return unique
        except ValueError:
            pass

        console.print('[error]Selezione non valida. Riprova.[/error]')


def _is_playlist_url(url: str) -> bool:
    """Riconosce dall'URL se si tratta di una playlist o di un album.

    Copre i pattern di YouTube ('playlist?list=', '&list='), Spotify
    ('/playlist/', '/album/') e SoundCloud ('/sets/'). Serve a decidere se
    creare una sottocartella con il nome dell'album e proporre la
    selezione delle tracce.
    """
    return any(x in url for x in ('playlist?list=', '/playlist/', '/album/', '/sets/', '&list='))


def main() -> None:
    """Punto di ingresso: legge gli argomenti da riga di comando e avvia il flusso.

    Tre modalità d'uso:
      - nessun argomento  -> modalità interattiva (loop: cerca o incolla URL);
      - --search "testo"  -> ricerca una tantum con selezione dei risultati;
      - --url <link>      -> download diretto di un video o di una playlist.
    Le playlist vengono scaricate in una sottocartella col nome dell'album.
    """
    parser = argparse.ArgumentParser(
        description='AudioDex - Downloader audio da YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--search', '-s', type=str, help='Cerca per nome canzone/artista')
    group.add_argument('--url', '-u', type=str, help='URL diretto (video, playlist, album)')

    parser.add_argument('--output', '-o', type=str,
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download_audio'),
                        help='Cartella output (default: Scraper_Audio/download_audio)')
    parser.add_argument('--format', '-f', type=str, default='m4a',
                        choices=['m4a', 'mp3', 'opus'],
                        help='Formato audio, solo audio senza video (default: m4a)')
    parser.add_argument('--workers', '-w', type=int, default=MAX_DOWNLOAD_WORKERS,
                        help=f'Worker paralleli (default: {MAX_DOWNLOAD_WORKERS})')
    parser.add_argument('--max-results', type=int, default=MAX_SEARCH_RESULTS,
                        help=f'Risultati ricerca max (default: {MAX_SEARCH_RESULTS})')
    parser.add_argument('--no-lyrics', action='store_true',
                        help='Non cercare i testi sincronizzati su LRCLIB')
    parser.add_argument('--cookies-from-browser', type=str, default=None,
                        choices=['firefox', 'chrome', 'edge', 'brave', 'opera', 'vivaldi'],
                        help='Usa i cookie del browser indicato per accedere a playlist/video privati')

    args = parser.parse_args()
    fetch_lyrics = not args.no_lyrics

    global _cookies_browser
    _cookies_browser = args.cookies_from_browser

    signal.signal(signal.SIGINT, _signal_handler)

    scraper_db.init_db()

    _print_banner()

    if not _HAS_MUTAGEN:
        console.print('[warning]mutagen non installato - tagging disabilitato[/warning]')
        console.print('[dim]Installa con: pip install mutagen[/dim]\n')

    output_dir = os.path.abspath(args.output)

    if not _check_disk_space(output_dir):
        console.print('[error]Operazione annullata.[/error]')
        return

    if not args.search and not args.url:
        # Modalita' interattiva
        console.print(
            f"\n[dim_label]Modalita' interattiva[/dim_label]\n  "
            f"{SYM_DOT} Digita un [accent]nome canzone/artista[/accent] per cercare\n  "
            f"{SYM_DOT} Incolla un [accent]URL[/accent] (video/playlist) per download diretto\n  "
            f"{SYM_DOT} Digita [accent]q[/accent] per uscire\n"
        )

        while not _shutdown_event.is_set():
            try:
                query = console.input(f'\n{SYM_NOTE} [bold]Cerca o incolla URL > [/bold]').strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not query or query.lower() in ('q', 'quit', 'esci'):
                break

            if query.startswith(('http://', 'https://', 'www.')):
                if _is_playlist_url(query):
                    title, entries = get_playlist_entries(query)
                    if not entries:
                        console.print('[error]Nessuna traccia trovata nella playlist.[/error]')
                        continue
                    _display_playlist_info(title, entries)
                    _display_search_results(entries, table_title='Tracce della playlist')
                    console.print(f'\n[dim_label]Scaricare tutte le {len(entries)} tracce? (s/n)[/dim_label]')
                    answer = console.input('[bold]> [/bold]').strip().lower()
                    if answer != 's':
                        selected = _select_from_results(entries)
                        if not selected:
                            continue
                        entries = selected
                    album_name = _sanitize_filename(title)
                    sub_dir = os.path.join(output_dir, album_name)
                    results = download_batch(entries, sub_dir, args.format, album=title, max_workers=args.workers, fetch_lyrics=fetch_lyrics)
                else:
                    title, entries = get_playlist_entries(query)
                    if not entries:
                        console.print('[error]Impossibile estrarre info dal URL.[/error]')
                        continue
                    results = download_batch(entries, output_dir, args.format, max_workers=args.workers, fetch_lyrics=fetch_lyrics)

                _display_download_summary(results)
                _export_failed(output_dir, results, entries)
            else:
                results = search_youtube(query, args.max_results)
                if not results:
                    console.print('[error]Nessun risultato trovato.[/error]')
                    continue
                _display_search_results(results)
                selected = _select_from_results(results)
                if not selected:
                    continue
                dl_results = download_batch(selected, output_dir, args.format, max_workers=args.workers, fetch_lyrics=fetch_lyrics)
                _display_download_summary(dl_results)
                _export_failed(output_dir, dl_results, selected)

        console.print('\n[dim]Arrivederci![/dim]\n')
        return

    if args.search:
        results = search_youtube(args.search, args.max_results)
        if not results:
            console.print('[error]Nessun risultato trovato.[/error]')
            return
        _display_search_results(results)
        selected = _select_from_results(results)
        if not selected:
            return
        dl_results = download_batch(selected, output_dir, args.format, max_workers=args.workers, fetch_lyrics=fetch_lyrics)
        _display_download_summary(dl_results)
        _export_failed(output_dir, dl_results, selected)
        return

    if args.url:
        if _is_playlist_url(args.url):
            title, entries = get_playlist_entries(args.url)
            if not entries:
                console.print('[error]Nessuna traccia trovata.[/error]')
                return
            _display_playlist_info(title, entries)
            _display_search_results(entries, table_title='Tracce della playlist')
            album_name = _sanitize_filename(title)
            sub_dir = os.path.join(output_dir, album_name)
            results = download_batch(entries, sub_dir, args.format, album=title, max_workers=args.workers, fetch_lyrics=fetch_lyrics)
        else:
            title, entries = get_playlist_entries(args.url)
            if not entries:
                console.print('[error]Impossibile estrarre info.[/error]')
                return
            results = download_batch(entries, output_dir, args.format, max_workers=args.workers, fetch_lyrics=fetch_lyrics)

        _display_download_summary(results)
        _export_failed(output_dir, results, entries)
        return


if __name__ == '__main__':
    main()

