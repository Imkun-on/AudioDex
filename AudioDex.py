# AudioDex.py
# Downloader audio da YouTube (singoli brani e playlist) con UI Rich:
# scarica il solo flusso audio, tagga i metadati e la copertina via mutagen,
# incorpora il testo sincronizzato (karaoke) da LRCLIB e registra ogni
# download sul database SQLite globale condiviso con gli altri scraper.
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
    # Stringhe grezze (r'...'): il disegno è fitto di backslash e con le
    # sequenze di escape normali diventerebbe illeggibile da correggere.
    banner_lines = [
        r'    ___             ___       ____           ',
        r'   /   | __  ______/ (_)___  / __ \___  _  __',
        r'  / /| |/ / / / __  / / __ \/ / / / _ \| |/_/',
        r' / ___ / /_/ / /_/ / / /_/ / /_/ /  __/>  <  ',
        r'/_/  |_\__,_/\__,_/_/\____/_____/\___/_/|_|  ',
    ]
    colors = ['bright_magenta', 'magenta', 'bright_blue', 'blue', 'bright_cyan', 'cyan']
    text = Text()
    for i, line in enumerate(banner_lines):
        # A capo solo *tra* le righe: sull'ultima lascerebbe una riga
        # vuota in fondo al pannello.
        suffisso = '\n' if i < len(banner_lines) - 1 else ''
        text.append(line + suffisso, style=Style(color=colors[i % len(colors)], bold=True))
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

# Estensioni per tipo di media. Servono al controllo anti-duplicati: un
# brano gia' scaricato in .m4a non deve far saltare il download dello
# stesso titolo in video (e viceversa), mentre tra formati dello stesso
# tipo il file esistente vale comunque come "gia' fatto".
AUDIO_EXTS = frozenset({'m4a', 'mp3', 'opus'})
VIDEO_EXTS = frozenset({'mp4', 'mkv'})


log = setup_logger('audiodex', 'audiodex.log')


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


# yt-dlp sostituisce i caratteri vietati da Windows (/ : | ? * " < >) con dei
# "sosia" Unicode a tutta larghezza (es. / -> ⧸, : -> ：, | -> ｜). Alcuni
# telefoni rifiutano questi nomi durante la copia via cavo USB, quindi li
# riconvertiamo in '_': lo stesso simbolo usato per i caratteri vietati, così
# il nome resta coerente con il controllo dei file "gia' scaricati".
_LOOKALIKE_MAP = str.maketrans({
    '⧸': '_', '⧹': '_',  # ⧸ ⧹  (al posto di / \)
    '／': '_', '＼': '_',  # ／ ＼  (al posto di / \)
    '：': '_',                 # ：     (al posto di :)
    '｜': '_',                 # ｜     (al posto di |)
    '？': '_', '＊': '_',  # ？ ＊  (al posto di ? *)
    '＂': '_',                 # ＂     (al posto di ")
    '＜': '_', '＞': '_',  # ＜ ＞  (al posto di < >)
})

# Blocchi Unicode di emoji e simboli pittografici: anche questi mandano in
# errore la copia verso il telefono, quindi li togliamo del tutto.
_EMOJI_RE = re.compile(
    '[\U0001F000-\U0001FAFF'  # emoji, emoticon e simboli pittografici
    '\U00002600-\U000027BF'   # simboli vari e dingbat
    '\U00002300-\U000023FF'   # simboli tecnici (orologi, ecc.)
    '\U00002B00-\U00002BFF'   # stelle e frecce decorative
    '︀-️'           # selettori di variazione (emoji a colori)
    '‍]+'                # giunzione a larghezza zero (emoji composte)
)


def _sanitize_filename(name: str) -> str:
    """Rende il nome del file compatibile con Windows e con i telefoni.

    Oltre a sostituire con '_' i caratteri vietati da Windows, riconverte i
    "sosia" Unicode che yt-dlp usa al loro posto (⧸ ： ｜ ...) e rimuove le
    emoji: in entrambi i casi alcuni telefoni rifiuterebbero il file durante
    la copia via cavo USB.
    """
    name = name.translate(_LOOKALIKE_MAP)
    name = _EMOJI_RE.sub('', name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s{2,}', ' ', name).strip()
    return name.rstrip(' .')


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


def _split_artist_title(title: str, uploader: str | None = None) -> tuple[str, str]:
    """Separa artista e brano dal titolo di un video YouTube.

    I titoli musicali sono quasi sempre nel formato 'Artista - Brano
    (decorazioni)': dopo la pulizia delle decorazioni, la parte prima del
    trattino è l'artista. Se il formato manca, come artista si usa il nome
    del canale (senza il suffisso ' - Topic' dei canali auto-generati).
    Restituisce (artista, brano); artista può essere stringa vuota.
    """
    cleaned = _clean_track_title(title)
    if ' - ' in cleaned:
        artist, track = cleaned.split(' - ', 1)
        return artist.strip(), track.strip()
    artist = (uploader or '').removesuffix(' - Topic').strip()
    return artist, cleaned


def _fetch_lyrics(title: str, artist: str, duration: int | float | None) -> tuple[str | None, str | None]:
    """Cerca su LRCLIB il testo sincronizzato (karaoke) di una traccia.

    Restituisce (testo_sincronizzato_lrc, testo_semplice); entrambi None se
    non trovato. Prima tenta la corrispondenza esatta artista+titolo+durata,
    poi una ricerca libera scartando i risultati con durata troppo diversa
    (>10s: probabilmente versione live o remix). Qualsiasi errore di rete
    viene solo loggato: i testi sono un extra, mai un motivo di fallimento.
    """
    artist, track = _split_artist_title(title, artist)

    headers = {'User-Agent': 'AudioDex/1.0 (https://github.com/Imkun-on/AudioDex)'}
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

    Usa la ricerca interna di yt-dlp con 'extract_flat': ottiene solo i
    metadati (titolo, canale, durata, views, URL) senza scaricare nulla.
    La lista serve a mostrare i risultati all'utente e fargli scegliere
    cosa scaricare.
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


def get_playlist_entries(url: str) -> tuple[str, list[dict], dict]:
    """Recupera titolo, tracce e dati d'insieme di una playlist/album.

    Come per la ricerca, 'extract_flat' scarica solo i metadati — ma per
    le voci di una playlist YouTube fornisce SOLO titolo e durata (niente
    canale né views): l'artista mostrato in tabella viene quindi ricavato
    dal titolo. A livello di **playlist**, invece, la stessa chiamata
    riporta canale, visualizzazioni complessive, data di modifica e
    visibilità: li restituiamo nel terzo valore, così il pannello di
    riepilogo non costa una richiesta in più.

    Con 'ignoreerrors' i video privati o rimossi vengono saltati invece
    di far fallire l'intera playlist; le playlist private richiedono
    --cookies-from-browser. Restituisce (titolo, tracce, dati playlist).
    """
    log.info('Recupero playlist: %s', url)
    entries = []
    playlist_title = 'Playlist'
    meta: dict = {}

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
                return playlist_title, [], meta
            playlist_title = info.get('title', 'Playlist')
            meta = {
                'channel': info.get('channel') or info.get('uploader'),
                'views': info.get('view_count'),
                'modified': info.get('modified_date'),
                'availability': info.get('availability'),
                'count': info.get('playlist_count'),
            }
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
                        'index': 1,
                    })
                return playlist_title, entries, meta
            # 'index' è la posizione nella playlist di origine, non nella lista
            # che restituiamo: le voci saltate (video privati o rimossi) non
            # fanno scalare le successive, e una selezione parziale conserva
            # comunque la numerazione originale.
            for pos, entry in enumerate(raw_entries, 1):
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
                    'index': entry.get('playlist_index') or pos,
                })

            # Dimensione della playlist intera: fissa la larghezza dello
            # zero-padding anche quando se ne scarica solo un pezzo, così i
            # numeri restano allineati con quelli già presenti in cartella.
            playlist_size = max((e['index'] for e in entries), default=0)
            for e in entries:
                e['playlist_size'] = playlist_size
    except Exception as e:
        log.error('Errore recupero playlist: %s', e)

    return playlist_title, entries, meta


def get_video_details(url: str) -> dict | None:
    """Recupera i metadati completi di un singolo video, senza scaricarlo.

    A differenza di get_playlist_entries qui NON si usa 'extract_flat':
    serve l'estrazione piena, l'unica che riporta visualizzazioni, mi
    piace, iscritti al canale, categoria e lingua. Costa un paio di
    secondi, accettabili per un video solo (su una playlist intera
    sarebbero secondi per traccia, ed è il motivo per cui lì restiamo
    sull'estrazione veloce). Restituisce None se il video non esiste o
    non è accessibile.
    """
    ydl_opts = _apply_cookies({
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    })
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and info.get('entries'):
                # URL di playlist passato per errore: si prende il primo
                info = info['entries'][0]
            return info or None
    except Exception as e:
        log.error('Errore info video: %s', e)
        return None


# Codici lingua più frequenti su YouTube, in forma leggibile. Gli altri
# vengono mostrati com'è (il codice ISO resta comunque comprensibile).
_LINGUE = {
    'it': 'Italiano', 'en': 'Inglese', 'es': 'Spagnolo', 'fr': 'Francese',
    'de': 'Tedesco', 'pt': 'Portoghese', 'ru': 'Russo', 'ja': 'Giapponese',
    'ko': 'Coreano', 'zh': 'Cinese', 'ar': 'Arabo', 'nl': 'Olandese',
    'pl': 'Polacco', 'tr': 'Turco', 'hi': 'Hindi', 'sv': 'Svedese',
    'ro': 'Rumeno', 'el': 'Greco', 'uk': 'Ucraino', 'cs': 'Ceco',
}


def _format_language(code: str | None) -> str | None:
    """Converte un codice lingua ('en', 'it-IT') nel nome esteso."""
    if not code:
        return None
    return _LINGUE.get(code.split('-')[0].lower(), code)


def _format_upload_date(raw: str | None) -> str:
    """Converte la data di pubblicazione da 'AAAAMMGG' a 'GG/MM/AAAA'."""
    if not raw or len(raw) != 8 or not raw.isdigit():
        return '—'
    return f'{raw[6:8]}/{raw[4:6]}/{raw[0:4]}'


def _display_video_card(info: dict) -> None:
    """Mostra la scheda di un video: canale, numeri, categoria, durata.

    È il riepilogo che si vede dopo aver incollato un URL, prima di
    confermare il download: serve a capire a colpo d'occhio se il video
    è quello giusto. I campi assenti (YouTube non sempre li espone)
    vengono semplicemente omessi invece di mostrare un vuoto.
    """
    table = Table(show_header=False, box=None, padding=(0, 2), expand=False)
    table.add_column('Campo', style='dim_label', no_wrap=True)
    table.add_column('Valore', style='white')

    righe = [
        ('📺', 'Canale', info.get('uploader') or info.get('channel')),
        ('👁', 'Visualizzazioni', _format_views(info.get('view_count'))),
        ('👍', 'Mi piace', _format_views(info.get('like_count'))),
        ('👥', 'Iscritti', _format_views(info.get('channel_follower_count'))),
        ('🏷', 'Categoria', (info.get('categories') or [None])[0]),
        ('🗣', 'Lingua', _format_language(info.get('language'))),
        ('📅', 'Pubblicato', _format_upload_date(info.get('upload_date'))),
        ('⏱', 'Durata', _format_duration(info.get('duration'))),
    ]
    # I segnaposto dei formattatori ('—', '??:??') indicano un dato che
    # YouTube non ha esposto: meglio togliere la riga che mostrare un vuoto.
    for icona, etichetta, valore in righe:
        if valore and str(valore) not in ('—', '??:??'):
            table.add_row(f'{icona}  {etichetta}', str(valore))

    capitoli = info.get('chapters') or []
    if capitoli:
        table.add_row('📑  Capitoli', f'{len(capitoli)} sezioni')

    console.print()
    console.print(Panel(
        table,
        title=f"[title]🎬 {info.get('title', 'Sconosciuto')[:60]}[/title]",
        border_style='bright_blue',
        box=ROUNDED,
        expand=False,
        padding=(1, 2),
    ))


def _confirm_video(info: dict) -> bool:
    """Mostra la scheda del video e chiede conferma prima di scaricare."""
    _display_video_card(info)
    answer = console.input(
        '\n[bold]Procedo con il download di questo video? (s/n): [/bold]'
    ).strip().lower()
    return answer in ('s', 'si', 'sì', 'y', 'yes')


def _entry_from_info(info: dict, url: str) -> dict:
    """Costruisce la entry di download dai metadati completi di un video."""
    return {
        'id': info.get('id', ''),
        'title': info.get('title', 'Sconosciuto'),
        'uploader': info.get('uploader') or info.get('channel') or '??',
        'duration': info.get('duration'),
        'views': info.get('view_count'),
        'url': info.get('webpage_url', url),
    }


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
    # Nelle playlist YouTube non fornisce le views: la colonna compare
    # solo quando almeno una riga ha il dato (es. risultati di ricerca).
    show_views = any(r.get('views') for r in results)

    table.add_column('#', style='bold yellow', justify='right', width=4)
    table.add_column('Titolo', style='white', max_width=45, no_wrap=True)
    table.add_column('Artista', style='bright_magenta', max_width=25, no_wrap=True)
    table.add_column('Durata', style='cyan', justify='right', width=8)
    if show_views:
        table.add_column('Views', style='green', justify='right', width=9)

    for i, r in enumerate(results, 1):
        artist, track = _split_artist_title(r['title'], r.get('uploader'))
        row = [
            str(i),
            track[:45],
            (artist or '??')[:25],
            _format_duration(r.get('duration')),
        ]
        if show_views:
            row.append(_format_views(r.get('views')))
        table.add_row(*row)

    console.print()
    console.print(table)


_VISIBILITA = {
    'public': 'Pubblica',
    'unlisted': 'Non in elenco',
    'private': 'Privata',
}


def _display_playlist_info(title: str, entries: list[dict], meta: dict | None = None) -> None:
    """Mostra la scheda della playlist: canale, tracce, durata, visualizzazioni.

    I dati d'insieme arrivano da get_playlist_entries, che li ricava dalla
    stessa chiamata usata per l'elenco: nessuna richiesta aggiuntiva. I
    campi che YouTube non espone vengono omessi.
    """
    meta = meta or {}
    total_duration = sum(e.get('duration', 0) or 0 for e in entries)

    table = Table(show_header=False, box=None, padding=(0, 2), expand=False)
    table.add_column('Campo', style='dim_label', no_wrap=True)
    table.add_column('Valore', style='white')

    righe = [
        ('📺', 'Canale', meta.get('channel')),
        ('🎵', 'Tracce', str(len(entries))),
        ('⏱', 'Durata totale', _format_duration(total_duration)),
        ('👁', 'Visualizzazioni', _format_views(meta.get('views'))),
        ('📅', 'Aggiornata', _format_upload_date(meta.get('modified'))),
        ('🔓', 'Visibilità', _VISIBILITA.get(meta.get('availability') or '')),
    ]
    for icona, etichetta, valore in righe:
        if valore and str(valore) not in ('—', '??:??'):
            table.add_row(f'{icona}  {etichetta}', str(valore))

    # Se YouTube dichiara più video di quelli estratti, la differenza sono
    # voci private o rimosse: meglio dirlo che lasciar contare all'utente.
    dichiarati = meta.get('count')
    if dichiarati and dichiarati > len(entries):
        table.add_row(
            '⚠  Non disponibili',
            f'[warning]{dichiarati - len(entries)} (privati o rimossi)[/warning]',
        )

    console.print()
    console.print(Panel(
        table,
        title=f'[title]💿 {title[:60]}[/title]',
        border_style='bright_blue',
        box=ROUNDED,
        expand=False,
        padding=(1, 2),
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


def _track_prefix(track_num: int | None, total: int | None) -> str:
    """Costruisce il prefisso numerico del nome file (es. '01 - ').

    Serve a far comparire i brani sul disco (e quindi sul telefono, che
    ordina per nome file) nello stesso ordine della playlist di origine.
    Le cifre sono zero-padded sul totale delle tracce, minimo due, così
    l'ordinamento alfabetico coincide con quello numerico.
    """
    if not track_num:
        return ''
    width = max(2, len(str(total or track_num)))
    return f'{track_num:0{width}d} - '


def _is_already_downloaded(title: str, output_dir: str, prefix: str = '',
                           exts: frozenset[str] = AUDIO_EXTS) -> str | None:
    """Controlla se la traccia è già stata scaricata nella cartella di destinazione.

    Confronta il titolo sanificato con i nomi dei file esistenti, tra quelli
    con un'estensione in `exts` (i formati equivalenti: audio con audio,
    video con video — così un brano gia' scaricato in .m4a non fa saltare
    lo stesso titolo richiesto in video). I file sotto i 10 KB vengono
    considerati download incompleti e quindi da rifare. Restituisce il
    percorso del file trovato oppure None: evita di riscaricare le stesse
    tracce nei run successivi.

    Con un prefisso di traccia riconosce anche i file scaricati da versioni
    precedenti — cioè *senza* numero — e li rinomina invece di riscaricarli.
    I file che hanno già un numero diverso NON vengono toccati: in una
    playlist con due tracce omonime (succede: stesso brano in versione
    singolo e in versione album) si contenderebbero lo stesso file,
    rinominandolo a vicenda e lasciandone scaricare una sola.
    """
    if not os.path.isdir(output_dir):
        return None

    safe_title = _sanitize_filename(title)
    wanted = (prefix + safe_title).lower()

    fallback = None
    for f in os.listdir(output_dir):
        name_no_ext, ext = os.path.splitext(f)
        if ext.lstrip('.').lower() not in exts:
            continue
        name_no_ext = name_no_ext.lower()
        full = os.path.join(output_dir, f)
        if name_no_ext == wanted:
            if os.path.getsize(full) > 10240:
                return full
            continue
        if prefix and name_no_ext == safe_title.lower():
            if os.path.getsize(full) > 10240:
                fallback = full

    if fallback:
        # Stesso brano senza numerazione: basta rinominarlo.
        target = os.path.join(output_dir, _wanted_name(prefix, title, fallback))
        if not os.path.exists(target):
            try:
                os.replace(fallback, target)
                log.info('Rinumerato: %s', os.path.basename(target))
                return target
            except OSError as exc:
                log.warning('Rinumerazione non riuscita: %s', exc)
        return fallback
    return None


def _wanted_name(prefix: str, title: str, existing_path: str) -> str:
    """Nome file atteso per una traccia: prefisso + titolo + estensione attuale."""
    ext = os.path.splitext(existing_path)[1]
    return _sanitize_filename(prefix + _sanitize_filename(title)) + ext


class _PhaseTracker:
    """Tiene le barre di avanzamento delle quattro fasi di ogni traccia.

    Scaricare un brano non è un solo passaggio: dopo il trasferimento dei
    byte c'è la conversione FFmpeg, la ricerca del testo su LRCLIB e il
    tagging con la copertina. Con una sola barra il file sembrava fermo al
    100% mentre in realtà stava ancora lavorando; qui ogni fase ha la sua
    barra, che conta quante tracce l'hanno superata.

    I metodi sono chiamati dai thread di download, quindi lo stato è
    protetto da un lock. Ogni fase viene contata **una volta sola** per
    traccia: un retry che rifà il download non la conteggia due volte.
    """

    PHASES = (
        ('download', 'Download   '),
        ('convert', 'Conversione'),
        ('lyrics', 'Testi      '),
        ('tag', 'Tag        '),
    )

    def __init__(self, progress: Progress, total: int, skip: frozenset[str] = frozenset()):
        self._progress = progress
        self._lock = threading.Lock()
        self._seen: dict[int, set[str]] = {}
        self._tasks = {
            name: progress.add_task(label, total=total)
            for name, label in self.PHASES if name not in skip
        }

    def done(self, key: int, phase: str) -> None:
        """Segna che la traccia `key` ha superato la fase indicata.

        Le fasi senza barra (perché non pertinenti al tipo di download)
        vengono ignorate: chi le segnala non deve sapere quali sono attive.
        """
        with self._lock:
            if phase not in self._tasks:
                return
            reached = self._seen.setdefault(key, set())
            if phase in reached:
                return
            reached.add(phase)
            self._progress.advance(self._tasks[phase])

    def finish(self, key: int) -> None:
        """Chiude tutte le fasi rimaste aperte per una traccia.

        Serve a fine lavorazione: una traccia saltata non attraversa alcuna
        fase, e una fallita si ferma a metà. Senza questo, le barre non
        arriverebbero mai in fondo pur essendo il lavoro concluso.
        """
        for name, _ in self.PHASES:
            self.done(key, name)


class _YtDlpProgressHook:
    """Ponte tra yt-dlp e la barra di avanzamento Rich del singolo file.

    yt-dlp invoca quest'oggetto a ogni blocco scaricato; noi aggiorniamo la
    barra con i byte ricevuti. La dimensione totale non è nota subito (a
    volte è solo una stima che arriva dopo le prime chiamate), perciò viene
    impostata al primo valore disponibile.
    """

    def __init__(self, progress: Progress, task_id, title: str, on_downloaded=None):
        self.progress = progress
        self.task_id = task_id
        self.title = title
        self.on_downloaded = on_downloaded
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
                # I byte sono arrivati: da qui in poi lavora FFmpeg.
                if self.on_downloaded:
                    self.on_downloaded()
        except Exception:
            pass


def download_single(entry: dict, output_dir: str, audio_format: str = 'm4a',
                    track_num: int | None = None, album: str | None = None,
                    progress: Progress | None = None, task_id=None,
                    fetch_lyrics: bool = True, total_tracks: int | None = None,
                    numbered: bool = False, on_phase=None,
                    media: str = 'audio') -> dict:
    """Scarica una singola traccia e ne registra i metadati.

    Con media='audio' (default) scarica il solo flusso audio; con
    media='video' scarica anche la traccia video e unisce i due flussi.

    Flusso completo:
      1. salta subito se il file esiste già su disco (status 'skip');
      2. scarica il flusso richiesto e lo converte/unisce nel formato
         scelto tramite ffmpeg;
      3. *(solo audio)* cerca il testo sincronizzato su LRCLIB e, se
         trovato, lo incorpora nei tag (un file unico, nessun .lrc);
      4. scrive titolo, artista, album e copertina nei tag — nei video
         solo per l'mp4, che condivide il container MP4 con l'm4a;
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

    prefix = _track_prefix(track_num, total_tracks) if numbered else ''
    is_video = media == 'video'

    existing = _is_already_downloaded(
        title, output_dir, prefix,
        exts=VIDEO_EXTS if is_video else AUDIO_EXTS,
    )
    if existing:
        log.info("Gia' scaricato: %s", title)
        result['status'] = 'skip'
        result['file'] = os.path.basename(existing)
        if progress and task_id is not None:
            # Barra piena: la traccia c'è già, non serve leggere il totale
            # precedente (Progress.tasks è una lista posizionale, e con i
            # task rimossi a mano a mano l'indice non è più il TaskID).
            progress.update(task_id, total=1, completed=1)
        return result

    os.makedirs(output_dir, exist_ok=True)

    # Il prefisso numerico entra nel nome del file: sul disco (e sul telefono,
    # che ordina per nome) le tracce restano nell'ordine della playlist.
    outtmpl = os.path.join(output_dir, f'{prefix}%(title)s.%(ext)s')

    ydl_opts = _apply_cookies({
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'retries': MAX_RETRIES,
        'fragment_retries': MAX_RETRIES,
        'writethumbnail': False,
        'noplaylist': True,
    })

    if is_video:
        # Video completo: YouTube serve video e audio come flussi separati
        # (le risoluzioni alte non hanno audio incorporato), quindi si
        # scarica il meglio di entrambi e ffmpeg li unisce nel container
        # scelto. Il fallback 'best' copre i video a flusso unico.
        ydl_opts['format'] = (
            f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
            if audio_format == 'mp4' else 'bestvideo+bestaudio/best'
        )
        ydl_opts['merge_output_format'] = audio_format

        # Metadati scritti da ffmpeg durante il merge: titolo, autore, data
        # e i capitoli del video. Funziona su qualsiasi container, ed è
        # l'unica via per il Matroska, che mutagen non sa taggare.
        ydl_opts['postprocessors'] = [
            {'key': 'FFmpegMetadata', 'add_metadata': True, 'add_chapters': True},
        ]

        # Album e numero di traccia non stanno nell'info di yt-dlp: li
        # ricaviamo noi dalla playlist, quindi vanno passati a mano come
        # argomenti extra di ffmpeg. Senza, un video di playlist perderebbe
        # proprio i due campi che tengono insieme una raccolta.
        extra_meta = []
        if album:
            extra_meta += ['-metadata', f'album={album}']
        if track_num:
            extra_meta += ['-metadata', f'track={track_num}']
        if extra_meta:
            ydl_opts['postprocessor_args'] = {'metadata': extra_meta}
        if audio_format == 'mkv':
            # Nel Matroska la copertina è un allegato: la incorpora yt-dlp,
            # perché mutagen non scrive i metadati mkv. Nell'mp4 invece
            # ci pensa _tag_m4a più sotto, insieme a tutto il resto.
            ydl_opts['writethumbnail'] = True
            ydl_opts['postprocessors'].append(
                {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}
            )
    else:
        # Solo audio: niente traccia video, il file occupa una frazione
        # dello spazio. 'FFmpegExtractAudio' converte (o rimuxa senza
        # ricodifica, quando il formato sorgente coincide).
        ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '0',
        }]

    def phase(name: str) -> None:
        """Segnala il superamento di una fase, se c'è un tracker collegato."""
        if on_phase:
            on_phase(name)

    if progress and task_id is not None:
        hook = _YtDlpProgressHook(
            progress, task_id, title,
            on_downloaded=lambda: phase('download'),
        )
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
                    safe = _sanitize_filename(prefix + _sanitize_filename(info.get('title', title))).lower()
                    for f in os.listdir(output_dir):
                        if not f.lower().endswith(f'.{final_ext}'):
                            continue
                        name_no_ext = os.path.splitext(f)[0].lower()
                        if name_no_ext != safe:
                            continue
                        final_file = os.path.join(output_dir, f)
                        break

                if os.path.isfile(final_file):
                    # Ripulisce il nome dai "sosia" Unicode e dalle emoji che
                    # yt-dlp lascia nel nome del file: così il brano si copia
                    # senza intoppi sul telefono via cavo USB.
                    folder, current = os.path.split(final_file)
                    stem, ext = os.path.splitext(current)
                    clean = _sanitize_filename(stem)
                    if clean and clean != stem:
                        target = os.path.join(folder, clean + ext)
                        if not os.path.exists(target):
                            try:
                                os.replace(final_file, target)
                                final_file = target
                            except OSError as exc:
                                log.warning('Rinomina del file non riuscita: %s', exc)

                    # FFmpeg ha finito: il file nel formato richiesto esiste.
                    phase('convert')

                    # Testo: incorporato direttamente nei tag del file audio
                    # (formato LRC con i timestamp), così il brano resta un
                    # file unico che porta con sé anche il testo.
                    # Il testo si scrive nel tag ©lyr, che esiste solo nel
                    # container MP4: vale per m4a e mp4, non per il mkv.
                    synced, plain = (None, None)
                    if fetch_lyrics and final_ext != 'mkv':
                        synced, plain = _fetch_lyrics(
                            info.get('title', title),
                            info.get('artist') or info.get('uploader') or uploader,
                            info.get('duration') or entry.get('duration'),
                        )
                        if synced or plain:
                            result['lyrics'] = True
                            log.info('Testo trovato: %s', title)
                    phase('lyrics')

                    # I tag iTunes vivono nel container MP4: valgono per
                    # .m4a e .mp4, non per il Matroska (.mkv).
                    if final_ext != 'mkv':
                        _tag_m4a(
                            final_file,
                            title=info.get('title', title),
                            artist=info.get('artist') or info.get('uploader') or uploader,
                            album=album or info.get('album'),
                            track_num=track_num,
                            thumbnail_url=info.get('thumbnail'),
                            lyrics=synced or plain,
                        )
                    phase('tag')

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
                        media_kind=media,
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
                   fetch_lyrics: bool = True, numbered: bool = False,
                   media: str = 'audio') -> list[dict]:
    """Scarica più tracce in parallelo mostrando le barre di avanzamento.

    Usa un pool di thread (max_workers download simultanei) e due barre
    Rich aggiornate live: una complessiva sulle tracce e una per ciascun
    file in corso. Un Ctrl+C ferma l'accodamento di nuove tracce lasciando
    finire quelle già partite. I risultati vengono riordinati secondo
    l'ordine originale delle entry (i thread terminano in ordine sparso).

    Con numbered=True i file vengono salvati con il numero di traccia in
    testa al nome ('01 - Titolo.m4a'): i download finiscono in ordine
    sparso, ma sul disco le tracce restano nell'ordine della playlist.
    Il numero è quello della playlist di origine (campo 'index' della
    entry), non la posizione nella lista passata: scaricando solo le
    tracce 5-8 i file restano '05'-'08'.
    """
    os.makedirs(output_dir, exist_ok=True)
    total = len(entries)
    results_by_index: dict[int, dict] = {}
    stopped_early = False

    # Larghezza dello zero-padding: la dimensione della playlist di origine
    # se nota, altrimenti il numero di traccia più alto da scaricare.
    highest = max(
        (max(e.get('index') or 0, e.get('playlist_size') or 0) for e in entries),
        default=total,
    ) or total

    kind = 'video' if media == 'video' else 'audio'
    console.print()
    console.rule(f'[phase]⬇ Download {kind}[/phase]', style='bright_green')
    console.print(
        f'  [dim_label]Thread:[/dim_label] [info]{max_workers}[/info]  '
        f'[dim_label]Tracce:[/dim_label] [bold]{total}[/bold]  '
        f'[dim_label]Formato:[/dim_label] [info]{audio_format}[/info]\n'
    )

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

    # Una barra per fase: scaricare un brano non è un passaggio solo, e
    # senza queste il file sembrava fermo al 100% mentre convertiva,
    # cercava il testo o scriveva i tag.
    phase_progress = Progress(
        SpinnerColumn('dots', style='bright_blue'),
        TextColumn('[bright_blue]{task.description}'),
        BarColumn(bar_width=32, style='bar.back', complete_style='bright_blue', finished_style='bold blue'),
        MofNCompleteColumn(),
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
    # Nel Matroska il testo non è scrivibile, quindi non viene nemmeno
    # cercato: senza lavoro da fare, quella barra non ha senso.
    phases = _PhaseTracker(
        phase_progress, total,
        skip=frozenset({'lyrics'}) if audio_format == 'mkv' else frozenset(),
    )

    layout = Group(
        overall_progress,
        phase_progress,
        Text('  ' + '─' * 46, style='dim'),
        file_progress,
    )

    with Live(layout, console=console, refresh_per_second=10):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            task_ids = {}

            for i, entry in enumerate(entries):
                if _shutdown_event.is_set():
                    stopped_early = True
                    break
                track_num = entry.get('index') or (i + 1)
                tid = file_progress.add_task(
                    f"[bold]#{track_num}[/bold] {entry['title'][:40]}",
                    total=None,
                    visible=True,
                )
                task_ids[i] = tid
                future = executor.submit(
                    download_single, entry, output_dir, audio_format,
                    track_num=track_num, album=album,
                    progress=file_progress, task_id=tid,
                    fetch_lyrics=fetch_lyrics,
                    total_tracks=highest, numbered=numbered,
                    on_phase=lambda name, k=i: phases.done(k, name),
                    media=media,
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

                results_by_index[idx] = result
                overall_progress.advance(overall_task)
                # Traccia conclusa: chiude le fasi non attraversate (una
                # saltata non ne fa nessuna, una fallita si ferma a metà),
                # così le barre arrivano in fondo insieme al lavoro.
                phases.finish(idx)

                tid = task_ids.get(idx)
                if tid is not None:
                    file_progress.remove_task(tid)

                if _shutdown_event.is_set():
                    stopped_early = True
                    for f in futures:
                        f.cancel()
                    break

    # Ricostruisce l'ordine originale dalla posizione della entry, non dal
    # titolo: titoli duplicati o rinominati non spostano più le tracce.
    return [results_by_index[i] for i in sorted(results_by_index)]


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
            f.write('# Per ritentare, copia gli URL e usa: python AudioDex.py --url <URL>\n#\n')
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


def _ask_media_type() -> tuple[str, str] | None:
    """Chiede se scaricare il video intero o il solo audio.

    Restituisce (media, formato) con media in {'audio', 'video'}, oppure
    None se l'utente annulla. Il formato proposto è quello nativo di
    YouTube per il tipo scelto (m4a / mp4): in entrambi i casi non serve
    ricodificare, quindi non si perde qualità.
    """
    table = Table(show_header=False, box=ROUNDED, border_style='bright_blue',
                  padding=(0, 2), expand=False)
    table.add_column('N', style='bold yellow', justify='right', width=3)
    table.add_column('Scelta')
    table.add_row('1', f'{SYM_NOTE} [bold]Solo audio[/bold] [dim](m4a)[/dim]\n'
                       '  [dim]pochi MB, taggato, con il testo karaoke[/dim]')
    table.add_row('2', '🎬 [bold]Video intero[/bold] [dim](mp4)[/dim]\n'
                       '  [dim]immagine + audio, file molto più grande[/dim]')

    console.print()
    console.print(table)

    while True:
        choice = console.input(
            '\n[bold]Cosa scarico? (1 = audio · 2 = video · q = annulla): [/bold]'
        ).strip().lower()
        if choice in ('q', 'quit', 'esci'):
            return None
        if choice in ('1', 'a', 'audio', ''):
            return 'audio', 'm4a'
        if choice in ('2', 'v', 'video'):
            return 'video', 'mp4'
        console.print('[error]Scelta non valida. Riprova.[/error]')


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
    Opzioni trasversali: --format (m4a/mp3/opus), --workers (parallelismo),
    --no-lyrics (salta i testi karaoke), --cookies-from-browser (accesso
    a playlist e video privati con i cookie del browser).
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
                        help='Cartella output (default: AudioDex/download_audio)')
    parser.add_argument('--media', '-m', type=str, default=None,
                        choices=['audio', 'video'],
                        help='Scarica solo audio o il video intero. Se omesso, in '
                             'modalità interattiva viene chiesto; con --search/--url '
                             'il default è audio')
    parser.add_argument('--format', '-f', type=str, default=None,
                        choices=['m4a', 'mp3', 'opus', 'mp4', 'mkv'],
                        help='Formato del file (audio: m4a/mp3/opus · video: mp4/mkv). '
                             'Default: m4a per l\'audio, mp4 per il video')
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

    # Tipo di media e formato: coerenti tra loro. Un --format video implica
    # --media video (e viceversa), così non serve ricordarsi entrambi.
    media = args.media
    fmt = args.format
    if fmt in VIDEO_EXTS:
        if media == 'audio':
            parser.error(f"--format {fmt} è un formato video, incompatibile con --media audio")
        media = 'video'
    elif fmt in AUDIO_EXTS:
        if media == 'video':
            parser.error(f"--format {fmt} è un formato audio, incompatibile con --media video")
        media = 'audio'
    if media and not fmt:
        fmt = 'mp4' if media == 'video' else 'm4a'

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

        def resolve_media() -> tuple[str, str] | None:
            """Tipo di media da scaricare: da riga di comando o chiesto ora."""
            if media:
                return media, fmt
            return _ask_media_type()

        while not _shutdown_event.is_set():
            try:
                query = console.input(f'\n{SYM_NOTE} [bold]Cerca o incolla URL > [/bold]').strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not query or query.lower() in ('q', 'quit', 'esci'):
                break

            if query.startswith(('http://', 'https://', 'www.')):
                if _is_playlist_url(query):
                    title, entries, meta = get_playlist_entries(query)
                    if not entries:
                        console.print('[error]Nessuna traccia trovata nella playlist.[/error]')
                        continue
                    _display_playlist_info(title, entries, meta)
                    _display_search_results(entries, table_title='Tracce della playlist')
                    console.print(f'\n[dim_label]Scaricare tutte le {len(entries)} tracce? (s/n)[/dim_label]')
                    answer = console.input('[bold]> [/bold]').strip().lower()
                    if answer != 's':
                        selected = _select_from_results(entries)
                        if not selected:
                            continue
                        entries = selected
                    choice = resolve_media()
                    if not choice:
                        continue
                    mtype, mfmt = choice
                    album_name = _sanitize_filename(title)
                    sub_dir = os.path.join(output_dir, album_name)
                    results = download_batch(entries, sub_dir, mfmt, album=title, max_workers=args.workers, fetch_lyrics=fetch_lyrics, numbered=True, media=mtype)
                else:
                    console.print('\n[dim]Recupero le informazioni del video...[/dim]')
                    info = get_video_details(query)
                    if not info:
                        console.print('[error]Impossibile estrarre info dal URL.[/error]')
                        continue
                    if not _confirm_video(info):
                        console.print('[dim]Annullato.[/dim]')
                        continue
                    entries = [_entry_from_info(info, query)]
                    choice = resolve_media()
                    if not choice:
                        continue
                    mtype, mfmt = choice
                    results = download_batch(entries, output_dir, mfmt, max_workers=args.workers, fetch_lyrics=fetch_lyrics, media=mtype)

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
                choice = resolve_media()
                if not choice:
                    continue
                mtype, mfmt = choice
                dl_results = download_batch(selected, output_dir, mfmt, max_workers=args.workers, fetch_lyrics=fetch_lyrics, media=mtype)
                _display_download_summary(dl_results)
                _export_failed(output_dir, dl_results, selected)

        console.print('\n[dim]Arrivederci![/dim]\n')
        return

    # Fuori dalla modalità interattiva non si fanno domande: senza --media
    # esplicito si scarica l'audio, com'è sempre stato.
    media = media or 'audio'
    fmt = fmt or 'm4a'

    if args.search:
        results = search_youtube(args.search, args.max_results)
        if not results:
            console.print('[error]Nessun risultato trovato.[/error]')
            return
        _display_search_results(results)
        selected = _select_from_results(results)
        if not selected:
            return
        dl_results = download_batch(selected, output_dir, fmt, max_workers=args.workers, fetch_lyrics=fetch_lyrics, media=media)
        _display_download_summary(dl_results)
        _export_failed(output_dir, dl_results, selected)
        return

    if args.url:
        if _is_playlist_url(args.url):
            title, entries, meta = get_playlist_entries(args.url)
            if not entries:
                console.print('[error]Nessuna traccia trovata.[/error]')
                return
            _display_playlist_info(title, entries, meta)
            _display_search_results(entries, table_title='Tracce della playlist')
            album_name = _sanitize_filename(title)
            sub_dir = os.path.join(output_dir, album_name)
            results = download_batch(entries, sub_dir, fmt, album=title, max_workers=args.workers, fetch_lyrics=fetch_lyrics, numbered=True, media=media)
        else:
            info = get_video_details(args.url)
            if not info:
                console.print('[error]Impossibile estrarre info.[/error]')
                return
            # Scheda mostrata anche qui, ma senza chiedere conferma: con
            # --url si è già dichiarato cosa si vuole scaricare.
            _display_video_card(info)
            entries = [_entry_from_info(info, args.url)]
            results = download_batch(entries, output_dir, fmt, max_workers=args.workers, fetch_lyrics=fetch_lyrics, media=media)

        _display_download_summary(results)
        _export_failed(output_dir, results, entries)
        return


if __name__ == '__main__':
    main()

