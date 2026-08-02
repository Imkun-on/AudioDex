"""AudioDex GUI — interfaccia grafica Flet per AudioDex e BurnDex.

Interfaccia unica per le due componenti (download audio da YouTube e
masterizzazione CD audio) senza toccare la logica dei CLI esistenti.
La GUI si limita a raccogliere gli input, chiamare le funzioni di
``AudioDex.py`` e ``BurnDex.py`` in thread separati, e mostrare log,
progressi e risultati con un'estetica synthwave (blu notte + viola neon).

Autore: Imkun-on (https://github.com/Imkun-on/AudioDex)
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import threading
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr

import flet as ft

# ── Percorso progetto e import moduli condivisi ───────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from Shared import i18n
from Shared.strings_audiodex import TESTI as TESTI_AUDIO
from Shared.strings_burndex import TESTI as TESTI_BURN

# Registra entrambi i cataloghi nel motore i18n condiviso.
i18n.register(TESTI_AUDIO)
i18n.register(TESTI_BURN)

# Import "pigri" dei CLI: alcuni moduli (pywin32) esistono solo su Windows,
# quindi carichiamo AudioDex/BurnDex al primo uso di ciascuna sezione.
_audiodex_mod = None
_burndex_mod = None
_pixdex_mod = None


def _load_audiodex():
    global _audiodex_mod
    if _audiodex_mod is None:
        import AudioDex as _ad  # noqa: WPS433
        _audiodex_mod = _ad
    return _audiodex_mod


def _load_burndex():
    global _burndex_mod
    if _burndex_mod is None:
        import BurnDex as _bd  # noqa: WPS433
        _burndex_mod = _bd
    return _burndex_mod


def _load_pixdex():
    global _pixdex_mod
    if _pixdex_mod is None:
        import PixDex as _px  # noqa: WPS433
        _pixdex_mod = _px
    return _pixdex_mod


# ── Testi propri della GUI ───────────────────────────────────────────────────
GUI_TESTI: dict[str, dict[str, str]] = {
    'gui.app_title':      {'it': 'AudioDex Suite', 'en': 'AudioDex Suite'},
    'gui.subtitle':       {'it': 'Download · Masterizzazione · Video', 'en': 'Download · Burning · Video'},
    'gui.menu.audio':     {'it': 'Audio', 'en': 'Audio'},
    'gui.menu.burn':      {'it': 'Masterizzazione', 'en': 'Burning'},
    'gui.menu.pix':       {'it': 'Rimasterizza video', 'en': 'Remaster video'},
    'gui.menu.settings':  {'it': 'Impostazioni', 'en': 'Settings'},
    'gui.language':       {'it': 'Lingua', 'en': 'Language'},
    'gui.theme':          {'it': 'Tema', 'en': 'Theme'},
    'gui.theme.dark':     {'it': 'Synthwave', 'en': 'Synthwave'},
    'gui.theme.light':    {'it': 'Chiaro', 'en': 'Light'},
    'gui.author':         {'it': 'di Imkun-on', 'en': 'by Imkun-on'},
    # Progress
    'gui.progress.download': {'it': 'Download in corso', 'en': 'Downloading'},
    'gui.progress.burn':  {'it': 'Masterizzazione in corso', 'en': 'Burning'},
    'gui.progress.done':  {'it': 'Operazione completata', 'en': 'Operation completed'},
    'gui.progress.err':   {'it': 'Operazione fallita', 'en': 'Operation failed'},
    # Track reorder
    'gui.tracks.up':      {'it': 'Sposta su', 'en': 'Move up'},
    'gui.tracks.down':    {'it': 'Sposta giù', 'en': 'Move down'},
    'gui.tracks.hint':    {'it': "Usa le frecce per riordinare (l'ordine sul CD segue questa lista).",
                           'en': 'Use arrows to reorder (CD order follows this list).'},
    # Audio view
    'gui.audio.title':    {'it': 'Downloader Audio', 'en': 'Audio Downloader'},
    'gui.audio.desc':     {'it': 'Scarica brani, album e playlist da YouTube con metadati, copertina e testi sincronizzati.',
                           'en': 'Download tracks, albums and playlists from YouTube with metadata, cover art and synced lyrics.'},
    'gui.audio.mode':     {'it': 'Modalità', 'en': 'Mode'},
    'gui.audio.mode.url': {'it': 'URL diretto', 'en': 'Direct URL'},
    'gui.audio.mode.search': {'it': 'Ricerca', 'en': 'Search'},
    'gui.audio.url.hint': {'it': 'Incolla qui link video, playlist o album di YouTube', 'en': 'Paste YouTube video, playlist or album URL here'},
    'gui.audio.search.hint': {'it': 'Titolo brano, artista, album…', 'en': 'Song title, artist, album…'},
    'gui.audio.output':   {'it': 'Cartella di output', 'en': 'Output folder'},
    'gui.audio.output.hint': {'it': 'Lascia vuoto per usare download_audio/', 'en': 'Leave empty to use download_audio/'},
    'gui.audio.format':   {'it': 'Formato', 'en': 'Format'},
    'gui.audio.media':    {'it': 'Media', 'en': 'Media'},
    'gui.audio.media.audio': {'it': 'Solo audio', 'en': 'Audio only'},
    'gui.audio.media.video': {'it': 'Video intero', 'en': 'Full video'},
    'gui.audio.workers':  {'it': 'Worker paralleli', 'en': 'Parallel workers'},
    'gui.audio.lyrics':   {'it': 'Scarica testi sincronizzati (LRCLIB)', 'en': 'Download synced lyrics (LRCLIB)'},
    'gui.audio.action.search': {'it': 'Cerca su YouTube', 'en': 'Search on YouTube'},
    'gui.audio.action.fetch':  {'it': 'Analizza URL', 'en': 'Analyze URL'},
    'gui.audio.action.download': {'it': 'Avvia download', 'en': 'Start download'},
    'gui.audio.action.stop': {'it': 'Ferma', 'en': 'Stop'},
    'gui.audio.results':  {'it': 'Risultati', 'en': 'Results'},
    'gui.audio.no_results': {'it': 'Nessun risultato ancora. Inserisci una URL o cerca un brano.',
                             'en': 'No results yet. Enter a URL or search for a track.'},
    # Burn view
    'gui.burn.title':     {'it': 'Masterizzazione CD audio', 'en': 'Audio CD burning'},
    'gui.burn.desc':      {'it': 'Trasforma una cartella di brani in un CD audio Red Book compatibile con qualsiasi lettore.',
                           'en': 'Turn a folder of tracks into a Red Book audio CD compatible with any player.'},
    'gui.burn.folder':    {'it': 'Cartella brani', 'en': 'Tracks folder'},
    'gui.burn.folder.hint': {'it': 'Percorso alla cartella con i file audio', 'en': 'Path to the folder with audio files'},
    'gui.burn.pick':      {'it': 'Sfoglia', 'en': 'Browse'},
    'gui.burn.speed':     {'it': 'Velocità (x)', 'en': 'Speed (x)'},
    'gui.burn.speed.auto':{'it': 'Automatica', 'en': 'Automatic'},
    'gui.burn.drive':     {'it': 'Unità', 'en': 'Drive'},
    'gui.burn.drive.auto':{'it': 'Rileva automaticamente', 'en': 'Auto-detect'},
    'gui.burn.dryrun':    {'it': 'Simulazione (non scrive sul disco)', 'en': 'Dry run (no writing to disc)'},
    'gui.burn.noeject':   {'it': 'Non espellere al termine', 'en': 'Do not eject when finished'},
    'gui.burn.action.info': {'it': 'Info sistema & unità', 'en': 'System & drive info'},
    'gui.burn.action.burn': {'it': 'Masterizza', 'en': 'Burn'},
    'gui.burn.action.stop': {'it': 'Interrompi', 'en': 'Stop'},
    'gui.burn.scanning':  {'it': 'Scansione disco in corso…', 'en': 'Scanning disc…'},
    'gui.burn.writing':   {'it': 'Scrittura tracce sul CD…', 'en': 'Writing tracks to CD…'},
    'gui.burn.ready':     {'it': 'Pronto per masterizzare', 'en': 'Ready to burn'},
    'gui.burn.tracks':    {'it': 'Tracce trovate', 'en': 'Tracks found'},
    'gui.burn.tracks.empty': {'it': 'Nessuna cartella selezionata. Le tracce compariranno qui.',
                              'en': 'No folder selected. Tracks will appear here.'},
    'gui.burn.tracks.none': {'it': 'Nessun file audio compatibile trovato in questa cartella.',
                             'en': 'No compatible audio file found in this folder.'},
    'gui.burn.tracks.total': {'it': '{n} tracce · durata totale {dur}',
                              'en': '{n} tracks · total duration {dur}'},
    'gui.burn.tracks.limit': {'it': 'Il CD audio standard ha ~74–80 minuti di capienza.',
                              'en': 'A standard audio CD holds ~74–80 minutes.'},
    # Log
    'gui.log.title':      {'it': 'Log operazione', 'en': 'Operation log'},
    'gui.log.clear':      {'it': 'Svuota', 'en': 'Clear'},
    'gui.log.empty':      {'it': 'Il log delle operazioni comparirà qui.', 'en': 'Operation log will appear here.'},
    # Status
    'gui.status.idle':    {'it': 'In attesa', 'en': 'Idle'},
    'gui.status.working': {'it': 'In esecuzione…', 'en': 'Working…'},
    'gui.status.done':    {'it': 'Completato', 'en': 'Completed'},
    'gui.status.error':   {'it': 'Errore', 'en': 'Error'},
    # Errori
    'gui.err.no_url':     {'it': 'Inserisci una URL o un termine di ricerca.', 'en': 'Enter a URL or search term.'},
    'gui.err.no_folder':  {'it': 'Seleziona una cartella con i brani da masterizzare.', 'en': 'Select a folder with tracks to burn.'},
    'gui.err.win_only':   {'it': 'La masterizzazione è disponibile solo su Windows (IMAPI2/pywin32).',
                           'en': 'Burning is available on Windows only (IMAPI2/pywin32).'},
    # ── Sezione Rimasterizza video (PixDex) ──────────────────────────────────
    'gui.pix.title':      {'it': 'Rimasterizza un video', 'en': 'Remaster a video'},
    'gui.pix.desc':       {'it': 'Toglie i difetti della compressione, appiana le bande e ingrandisce. '
                                 'Non inventa dettaglio: lavora in sottrazione.',
                           'en': 'Removes compression artifacts, smooths banding and upscales. '
                                 'It invents no detail: it works by subtraction.'},
    'gui.pix.file':       {'it': 'Video da rimasterizzare', 'en': 'Video to remaster'},
    'gui.pix.file.hint':  {'it': 'Percorso del file, oppure usa Sfoglia', 'en': 'File path, or use Browse'},
    'gui.pix.pick':       {'it': 'Sfoglia', 'en': 'Browse'},
    'gui.pix.preset':     {'it': 'Preset', 'en': 'Preset'},
    'gui.pix.preset.auto': {'it': 'Automatico (dalla diagnosi)', 'en': 'Automatic (from diagnosis)'},
    'gui.pix.height':     {'it': 'Risoluzione finale', 'en': 'Final resolution'},
    'gui.pix.height.auto': {'it': 'Automatica', 'en': 'Automatic'},
    'gui.pix.gpu':        {'it': 'Codifica sulla GPU AMD — circa 2,4× più veloce, file un po\' più pesante',
                           'en': 'Encode on the AMD GPU — about 2.4× faster, slightly heavier file'},
    'gui.pix.compare':    {'it': 'Salva immagine di confronto prima/dopo',
                           'en': 'Save a before/after comparison image'},
    'gui.pix.action.analyze': {'it': 'Analizza', 'en': 'Analyse'},
    'gui.pix.action.start': {'it': 'Rimasterizza', 'en': 'Remaster'},
    'gui.pix.diag.title': {'it': 'Diagnosi', 'en': 'Diagnosis'},
    'gui.pix.diag.empty': {'it': 'Scegli un video e premi Analizza: qui compare cosa c\'è da sistemare.',
                           'en': 'Pick a video and press Analyse: what needs fixing shows up here.'},
    'gui.pix.diag.suggested': {'it': 'Preset consigliato', 'en': 'Suggested preset'},
    'gui.pix.preview':    {'it': 'Confronto prima / dopo', 'en': 'Before / after comparison'},
    'gui.pix.preview.empty': {'it': 'A lavoro finito, qui vedi lo stesso fotogramma prima e dopo.',
                              'en': 'When it is done, the same frame before and after shows up here.'},
    'gui.pix.progress':   {'it': 'Rimasterizzazione in corso', 'en': 'Remastering'},
    'gui.pix.err.no_file': {'it': 'Scegli il video da rimasterizzare.', 'en': 'Pick the video to remaster.'},
    'gui.pix.err.probe':  {'it': 'Nessun flusso video leggibile in questo file.',
                           'en': 'No readable video stream in this file.'},
    'gui.pix.err.ffmpeg': {'it': 'FFmpeg non è nel PATH: installalo con  winget install Gyan.FFmpeg',
                           'en': 'FFmpeg is not in PATH: install it with  winget install Gyan.FFmpeg'},
    'gui.pix.done':       {'it': 'Fatto: {file}', 'en': 'Done: {file}'},
}
i18n.register(GUI_TESTI)


# ── Palette cyberpunk (allineata al video di sfondo) ────────────────────────
class Colors:
    # Palette derivata dal fermo-immagine di ``assets/cyberpunk-citadel.mp4``.
    BG_DEEP     = '#0d0620'   # viola quasi nero sotto al video
    BG_PANEL    = '#1a0b2ecc' # pannello viola scuro con leggera trasparenza
    BG_PANEL_2  = '#2c1f3bcc' # pannello elevato (indigo scuro)
    STROKE      = '#3a2a5a'   # bordi tenui
    NEON_PURPLE = '#c46bff'   # viola neon (accento primario)
    NEON_MAGENTA= '#ff2df1'   # magenta elettrico
    NEON_BLUE   = '#4cc9ff'   # azzurro
    NEON_CYAN   = '#00ffff'   # ciano neon vivido
    NEON_YELLOW = '#ffd800'   # giallo neon del citadel
    TEXT        = '#ffffff'
    TEXT_DIM    = '#cbc4e8'
    OK          = '#5cffb2'
    ERR         = '#ff5b78'
    SIDEBAR_BG  = '#0a0518e6'   # sidebar quasi opaca sopra al video
    SIDEBAR_SEL = '#2a1550'


# ── Preset store (persistenza scelte utente) ─────────────────────────────────
import json as _json
import pathlib as _pathlib

_PRESET_PATH = _pathlib.Path.home() / '.audiodex_gui.json'


class PresetStore:
    """Persistenza JSON di preferenze UI (tema, formato preferito, workers,
    ultima cartella di output/masterizzazione, ultimo formato lyrics on/off)."""

    _DEFAULTS = {
        'audio_format': 'm4a',
        'audio_media': 'audio',
        'audio_workers': '4',
        'audio_lyrics': True,
        'audio_output': '',
        'burn_folder': '',
        'burn_speed': 'auto',
        'burn_drive': 'auto',
        'burn_dry_run': False,
        'burn_no_eject': False,
    }

    def __init__(self, path: _pathlib.Path = _PRESET_PATH):
        self.path = path
        self.data = dict(self._DEFAULTS)
        self._load()

    def _load(self):
        try:
            if self.path.exists():
                loaded = _json.loads(self.path.read_text('utf-8'))
                if isinstance(loaded, dict):
                    self.data.update({k: v for k, v in loaded.items()
                                       if k in self._DEFAULTS})
        except Exception:
            pass

    def save(self):
        try:
            self.path.write_text(_json.dumps(self.data, indent=2), encoding='utf-8')
        except Exception:
            pass

    def get(self, key: str):
        return self.data.get(key, self._DEFAULTS.get(key))

    def set(self, key: str, value):
        if key in self._DEFAULTS:
            self.data[key] = value
            self.save()


# ── Progress panel (barra download / masterizzazione in tempo reale) ─────────
class ProgressPanel:
    """Piccolo pannello con testo di stato + barra di progresso.
    - ``begin(total, kind)``: mostra la barra a 0 (o indeterminata se total=None).
    - ``step(name)``: incrementa di 1 il conteggio corrente e aggiorna il testo.
    - ``end(ok, message)``: nasconde la barra e mostra il riepilogo.
    """

    def __init__(self):
        self.total = 0
        self.done = 0
        self.progress = ft.ProgressBar(
            value=0.0, expand=True, height=8, bar_height=8,
            color=Colors.NEON_MAGENTA, bgcolor=Colors.SIDEBAR_SEL,
            border_radius=4,
        )
        self.title = ft.Text('', color=Colors.TEXT, size=12,
                             weight=ft.FontWeight.W_700)
        self.detail = ft.Text('', color=Colors.TEXT_DIM, size=11)
        self.percent = ft.Text('', color=Colors.NEON_CYAN, size=12,
                               weight=ft.FontWeight.W_800,
                               font_family='JetBrains Mono')
        self.container = ft.Container(
            visible=False,
            padding=ft.Padding.symmetric(vertical=10, horizontal=14),
            border_radius=12, bgcolor=Colors.BG_PANEL,
            border=ft.Border.all(1, Colors.NEON_PURPLE),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(controls=[
                        self.title, ft.Container(expand=True), self.percent,
                    ]),
                    self.progress,
                    self.detail,
                ],
            ),
        )
        self.page: ft.Page | None = None

    def bind(self, page: ft.Page):
        self.page = page

    def _update(self):
        try:
            if self.page is not None:
                self.page.update()
        except Exception:
            pass

    def begin(self, total: int | None, title: str):
        self.total = total or 0
        self.done = 0
        self.title.value = title
        self.detail.value = ''
        self.percent.value = '0%' if total else '···'
        self.progress.value = 0.0 if total else None  # None = indeterminata
        self.container.visible = True
        self._update()

    def step(self, name: str, ok: bool = True):
        self.done += 1
        if self.total > 0:
            frac = min(1.0, self.done / self.total)
            self.progress.value = frac
            self.percent.value = f'{int(frac * 100)}%'
        prefix = '✓' if ok else '✗'
        color = Colors.OK if ok else Colors.ERR
        self.detail.value = f'{prefix}  [{self.done}/{self.total or "?"}]  {name}'
        self.detail.color = color
        self._update()

    def seek(self, done: int, total: int | None, detail: str = ''):
        """Porta la barra a un valore assoluto, invece di avanzare di uno.

        ``step()`` va bene quando le unità sono poche e ognuna ha un nome — i
        brani di una playlist. Per una codifica video le unità sono decine di
        migliaia di fotogrammi: chiamare ``step()`` per ognuno significherebbe
        altrettanti ridisegni della finestra, che da soli rallenterebbero la
        codifica. Qui si scrive direttamente dove è arrivata, e chi chiama
        decide ogni quanto farlo.
        """
        self.total = total or 0
        self.done = done
        if self.total > 0:
            frac = min(1.0, done / self.total)
            self.progress.value = frac
            self.percent.value = f'{int(frac * 100)}%'
        else:
            self.progress.value = None
            self.percent.value = '···'
        self.detail.value = detail
        self.detail.color = Colors.TEXT_DIM
        self._update()

    def end(self, ok: bool, message: str):
        # Lascia visibile per un attimo il completamento.
        if self.total > 0:
            self.progress.value = 1.0 if ok else self.progress.value or 0
            self.percent.value = '100%' if ok else self.percent.value
        else:
            self.progress.value = 1.0 if ok else 0.0
            self.percent.value = 'ok' if ok else 'err'
        self.title.value = message
        self.title.color = Colors.OK if ok else Colors.ERR
        self.detail.value = ''
        self._update()

    def hide(self):
        self.container.visible = False
        self._update()


# ── Video di sfondo: scaricato al primo avvio ────────────────────────────────
# Il file pesa ~74 MB: tenerlo dentro al repository renderebbe lento ogni
# ``git clone``, quindi vive come allegato di una GitHub Release e viene
# scaricato una volta sola nella cartella ``assets/``. Finché non è pronto la
# GUI usa il gradiente di fallback, che è già previsto qui sotto.
BG_VIDEO_NAME = 'cyberpunk-citadel.mp4'
BG_VIDEO_URL = ('https://github.com/Imkun-on/AudioDex/releases/download/'
                'assets-v1/cyberpunk-citadel.mp4')
BG_VIDEO_MIN_BYTES = 1_000_000   # sotto questa soglia il file è un download monco


def background_video_path() -> str:
    """Percorso del video di sfondo dentro la cartella ``assets/``."""
    return os.path.join(_HERE, 'assets', BG_VIDEO_NAME)


def background_video_ready() -> bool:
    """True se il video è già stato scaricato ed è di dimensione plausibile."""
    path = background_video_path()
    try:
        return os.path.getsize(path) >= BG_VIDEO_MIN_BYTES
    except OSError:
        return False


def download_background_video() -> bool:
    """Scarica il video di sfondo dalla Release, se manca. Restituisce True se
    alla fine il file è disponibile.

    Scrive prima su un file ``.part`` e rinomina solo a download completato: se
    la rete cade a metà non resta un video troncato che poi non parte. Ogni
    errore è silenzioso a parte una riga di avviso — lo sfondo è decorativo, la
    GUI funziona identica col gradiente.
    """
    if background_video_ready():
        return True

    path = background_video_path()
    tmp = path + '.part'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        import requests
        print('[sfondo] Scarico una volta sola il video di sfondo (~74 MB)…')
        with requests.get(BG_VIDEO_URL, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with open(tmp, 'wb') as fh:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    if chunk:
                        fh.write(chunk)
        os.replace(tmp, path)
        print('[sfondo] Video pronto: si vedrà al prossimo avvio.')
        return True
    except Exception as exc:
        print(f'[sfondo] Download non riuscito ({exc}); uso lo sfondo a gradiente.')
        try:
            os.remove(tmp)
        except OSError:
            pass
        return False


def ensure_background_video_async() -> None:
    """Avvia il download del video in un thread daemon, senza bloccare l'avvio
    della finestra. Il video comparirà al lancio successivo."""
    if background_video_ready():
        return
    threading.Thread(target=download_background_video,
                     name='bg-video-download', daemon=True).start()


# ── Sfondo video cyberpunk (loop) ────────────────────────────────────────────
def cyberpunk_background(page: ft.Page) -> ft.Control:
    """Restituisce lo Stack di sfondo: un video cyberpunk in loop + una
    velatura scura per garantire leggibilità dei pannelli. Se il video non è
    ancora stato scaricato, o se ``flet_video`` non riesce a inizializzare
    (piattaforma senza codec), degrada su un gradient statico che replica i toni
    del video (viola scuro con accenti magenta).
    """
    fallback_gradient = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=['#0d0620', '#1a0b2a', '#2c1f3b', '#3a1550', '#0d0620'],
            stops=[0.0, 0.3, 0.55, 0.8, 1.0],
        ),
    )

    video_ctrl: ft.Control | None = None
    try:
        if not background_video_ready():
            raise FileNotFoundError(BG_VIDEO_NAME)
        from flet_video import Video, VideoMedia  # type: ignore
        video_ctrl = Video(
            expand=True,
            autoplay=True,
            muted=True,
            show_controls=False,
            wakelock=False,
            fit=ft.BoxFit.COVER,
            fill_color='#0d0620',
            playlist_mode='loop',
            playlist=[
                VideoMedia(resource='cyberpunk-citadel.mp4'),
            ],
        )
    except Exception:
        video_ctrl = None

    # Velatura scura sopra al video per migliorare la leggibilità dei pannelli
    # (bordi tenui e testo brillano di più su un fondo più scuro).
    veil = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=['#0d0620cc', '#0d062088', '#0d0620dd'],
            stops=[0.0, 0.5, 1.0],
        ),
    )

    controls: list[ft.Control] = [fallback_gradient]
    if video_ctrl is not None:
        controls.append(video_ctrl)
    controls.append(veil)

    return ft.Stack(expand=True, controls=controls)


# ── Widget: pannello sidebar synthwave ───────────────────────────────────────
def build_sidebar(state: 'AppState') -> ft.Container:
    """Costruisce la sidebar con logo, menu, selettore lingua."""

    def menu_item(icon, key: str, section: str) -> ft.Control:
        selected = state.section == section
        indicator = ft.Container(
            width=3,
            height=26,
            bgcolor=Colors.NEON_MAGENTA if selected else 'transparent',
            border_radius=2,
            shadow=(ft.BoxShadow(blur_radius=14, color=Colors.NEON_MAGENTA, spread_radius=1)
                    if selected else None),
        )
        inner_row = ft.Row(
            spacing=12,
            controls=[
                indicator,
                ft.Icon(icon, color=Colors.NEON_PURPLE if selected else Colors.TEXT_DIM, size=20),
                ft.Text(
                    i18n.t(key),
                    color=Colors.TEXT if selected else Colors.TEXT_DIM,
                    weight=ft.FontWeight.W_600 if selected else ft.FontWeight.W_500,
                    size=14,
                ),
            ],
        )
        # Uso TextButton per un click affidabile in Flet 0.86.
        return ft.TextButton(
            content=ft.Container(
                content=inner_row,
                padding=ft.Padding.symmetric(vertical=10, horizontal=8),
                width=228,
                bgcolor=Colors.SIDEBAR_SEL if selected else 'transparent',
                border=ft.Border.all(1, Colors.STROKE) if selected else None,
                border_radius=10,
            ),
            on_click=lambda e, s=section: state.set_section(s),
            style=ft.ButtonStyle(
                padding=ft.Padding.all(0),
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=Colors.NEON_PURPLE + '22',
            ),
            data=f'menu-item-{section}',
        )

    lang_dropdown = ft.Dropdown(
        value=i18n.get_language(),
        options=[
            ft.dropdown.Option(key='it', text='Italiano'),
            ft.dropdown.Option(key='en', text='English'),
        ],
        border_color=Colors.STROKE,
        focused_border_color=Colors.NEON_PURPLE,
        color=Colors.TEXT,
        bgcolor=Colors.BG_PANEL_2,
        text_size=13,
        on_select=lambda e: state.set_language(e.control.value if hasattr(e.control, 'value') else e.data),
        dense=True,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        data=None,
    )

    logo = ft.Row(
        spacing=12,
        controls=[
            ft.Container(
                width=44, height=44, border_radius=12,
                bgcolor=Colors.BG_PANEL_2,
                border=ft.Border.all(1, Colors.NEON_PURPLE),
                shadow=ft.BoxShadow(blur_radius=18, color=Colors.NEON_PURPLE, spread_radius=-2),
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(ft.Icons.GRAPHIC_EQ, color=Colors.NEON_MAGENTA, size=22),
            ),
            ft.Column(
                spacing=0,
                controls=[
                    ft.Text('AUDIODEX', color=Colors.TEXT, size=15,
                            weight=ft.FontWeight.W_800, font_family='Orbitron'),
                    ft.Text(i18n.t('gui.subtitle'), color=Colors.NEON_PURPLE, size=10,
                            weight=ft.FontWeight.W_500),
                ],
            ),
        ],
    )

    return ft.Container(
        width=260,
        bgcolor=Colors.SIDEBAR_BG,
        border=ft.Border.only(right=ft.BorderSide(1, Colors.STROKE)),
        padding=ft.Padding.symmetric(vertical=22, horizontal=16),
        content=ft.Column(
            expand=True,
            controls=[
                logo,
                ft.Container(height=28),
                ft.Text(
                    i18n.t('gui.menu.audio').upper() + ' / ' + i18n.t('gui.menu.burn').upper()
                    + ' / ' + i18n.t('gui.menu.pix').upper(),
                    color=Colors.TEXT_DIM, size=10, weight=ft.FontWeight.W_700,
                ),
                ft.Container(height=8),
                menu_item(ft.Icons.MUSIC_NOTE, 'gui.menu.audio', 'audio'),
                ft.Container(height=6),
                menu_item(ft.Icons.ALBUM, 'gui.menu.burn', 'burn'),
                ft.Container(height=6),
                menu_item(ft.Icons.AUTO_FIX_HIGH, 'gui.menu.pix', 'pix'),
                ft.Container(expand=True),
                ft.Divider(color=Colors.STROKE, height=1),
                ft.Container(height=10),
                ft.Text(i18n.t('gui.language'), color=Colors.TEXT_DIM, size=11,
                        weight=ft.FontWeight.W_600),
                ft.Container(height=6),
                lang_dropdown,
                ft.Container(height=10),
                ft.Text(i18n.t('gui.author'), color=Colors.TEXT_DIM, size=10),
            ],
        ),
    )


# ── Widget: scanner CD animato ───────────────────────────────────────────────
class CDScanner(ft.Stack):
    """Rappresentazione grafica di un CD con anello rotante quando "scansiona"."""

    def __init__(self, size: int = 200):
        super().__init__()
        self.size = size
        self._angle = 0.0
        self._running = False

        self.disc = ft.Container(
            width=size, height=size,
            border_radius=size,
            gradient=ft.RadialGradient(
                colors=['#e6e4ff', '#8f8bb8', '#4cc9ff', '#b46bff', '#12102b'],
                stops=[0.15, 0.35, 0.55, 0.78, 1.0],
            ),
            border=ft.Border.all(2, Colors.NEON_PURPLE),
            shadow=ft.BoxShadow(blur_radius=40, color=Colors.NEON_PURPLE, spread_radius=-6),
        )
        # Foro centrale
        self.hole = ft.Container(
            width=size * 0.22, height=size * 0.22,
            border_radius=size, bgcolor=Colors.BG_DEEP,
            border=ft.Border.all(1, Colors.STROKE),
        )

        # Anello scanner (rotante)
        self.scan_ring = ft.Container(
            width=size * 0.85, height=size * 0.85,
            border_radius=size,
            border=ft.Border.all(2, Colors.NEON_CYAN),
            gradient=ft.SweepGradient(
                center=ft.Alignment(0, 0),
                colors=['#7df9ff00', '#7df9ff', '#7df9ff00'],
                stops=[0.0, 0.15, 0.35],
            ),
            rotate=ft.Rotate(angle=0),
            animate_rotation=ft.Animation(1200, ft.AnimationCurve.LINEAR),
            shadow=ft.BoxShadow(blur_radius=20, color=Colors.NEON_CYAN, spread_radius=-4),
        )

        self.status_text = ft.Text(
            i18n.t('gui.burn.ready'),
            color=Colors.NEON_CYAN, size=12,
            weight=ft.FontWeight.W_600,
        )

        self.width = size + 40
        self.height = size + 60
        self.controls = [
            ft.Container(width=size, height=size, left=20, top=10, content=self.disc),
            ft.Container(
                width=size * 0.85, height=size * 0.85,
                left=20 + size * 0.075, top=10 + size * 0.075,
                content=self.scan_ring,
            ),
            ft.Container(
                width=size * 0.22, height=size * 0.22,
                left=20 + size * 0.39, top=10 + size * 0.39,
                content=self.hole,
            ),
            ft.Container(
                width=size + 40, top=size + 16, left=0,
                alignment=ft.Alignment.CENTER,
                content=self.status_text,
            ),
        ]

    def start(self, message: str | None = None):
        """Avvia l'animazione di scansione con un timer periodico."""
        if message:
            self.status_text.value = message
            self.status_text.color = Colors.NEON_CYAN
        self._running = True
        self._tick()

    def _tick(self):
        if not self._running:
            return
        self._angle += 0.9
        self.scan_ring.rotate = ft.Rotate(self._angle)
        try:
            self.update()
        except Exception:
            self._running = False
            return
        t = threading.Timer(0.8, self._tick)
        t.daemon = True
        t.start()

    def stop(self, message: str | None = None, ok: bool = True):
        self._running = False
        if message:
            self.status_text.value = message
            self.status_text.color = Colors.OK if ok else Colors.ERR
            try:
                self.update()
            except Exception:
                pass


# ── Console redirect verso ListView ──────────────────────────────────────────
class LogSink(io.TextIOBase):
    """File-like che aggiunge righe a un ListView Flet in modo thread-safe."""

    def __init__(self, list_view: ft.ListView, page: ft.Page):
        self.list_view = list_view
        self.page = page
        self._buffer = ''
        self._lock = threading.Lock()

    def write(self, s: str) -> int:  # type: ignore[override]
        if not s:
            return 0
        with self._lock:
            self._buffer += s
            while '\n' in self._buffer:
                line, self._buffer = self._buffer.split('\n', 1)
                self._append(line)
        return len(s)

    def flush(self):
        with self._lock:
            if self._buffer:
                self._append(self._buffer)
                self._buffer = ''

    def _append(self, raw_line: str):
        # Rimuove le sequenze ANSI di Rich lasciando solo il testo.
        import re
        text = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', raw_line).rstrip()
        if not text:
            return
        color = Colors.TEXT
        low = text.lower()
        if any(x in low for x in ('error', 'errore', 'fail')):
            color = Colors.ERR
        elif any(x in low for x in ('ok', 'success', 'completato', 'completed', '✓')):
            color = Colors.OK
        elif any(x in low for x in ('warning', 'attenzione')):
            color = '#ffd36e'
        try:
            self.list_view.controls.append(
                ft.Text(text, color=color, size=12, selectable=True,
                        font_family='JetBrains Mono')
            )
            if len(self.list_view.controls) > 500:
                self.list_view.controls = self.list_view.controls[-500:]
            self.page.update()
        except Exception:
            pass


# ── Stato applicazione ───────────────────────────────────────────────────────
class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.presets = PresetStore()
        self.section = os.environ.get('AUDIODEX_DEFAULT_SECTION', 'audio')
        self.working = False
        self.worker_thread: threading.Thread | None = None
        self.on_render = lambda: None
        self.progress = ProgressPanel()
        self.progress.bind(page)

    def set_section(self, s: str):
        self.section = s
        self.on_render()

    def set_language(self, code: str):
        i18n.set_language(code)
        i18n.save(code)
        self.on_render()


# ── Sezione Audio ────────────────────────────────────────────────────────────
def build_audio_view(state: AppState, log_view: ft.ListView, status_ctrl: ft.Text) -> ft.Control:
    mode = ft.Ref[ft.Dropdown]()
    input_field = ft.Ref[ft.TextField]()
    output_field = ft.Ref[ft.TextField]()
    fmt_field = ft.Ref[ft.Dropdown]()
    media_field = ft.Ref[ft.Dropdown]()
    workers_field = ft.Ref[ft.TextField]()
    lyrics_switch = ft.Ref[ft.Switch]()
    results_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    presets = state.presets

    def _persist(_e=None):
        # Salva le impostazioni correnti nel preset store.
        presets.set('audio_format', fmt_field.current.value if fmt_field.current else 'm4a')
        presets.set('audio_media', media_field.current.value if media_field.current else 'audio')
        presets.set('audio_workers', workers_field.current.value if workers_field.current else '4')
        presets.set('audio_lyrics', lyrics_switch.current.value if lyrics_switch.current else True)
        presets.set('audio_output', output_field.current.value if output_field.current else '')

    def log(msg: str, color: str = Colors.TEXT):
        log_view.controls.append(ft.Text(msg, color=color, size=12, selectable=True,
                                          font_family='JetBrains Mono'))
        state.page.update()

    def set_status(text: str, color: str = Colors.NEON_CYAN):
        status_ctrl.value = text
        status_ctrl.color = color
        state.page.update()

    def run_bg(fn):
        if state.working:
            return
        state.working = True
        set_status(i18n.t('gui.status.working'), Colors.NEON_CYAN)

        def wrap():
            sink = LogSink(log_view, state.page)
            try:
                with redirect_stdout(sink), redirect_stderr(sink):
                    fn()
                set_status(i18n.t('gui.status.done'), Colors.OK)
            except Exception as exc:  # noqa: BLE001
                log(f'{exc}', Colors.ERR)
                log(traceback.format_exc(), Colors.ERR)
                set_status(i18n.t('gui.status.error'), Colors.ERR)
            finally:
                sink.flush()
                state.working = False

        state.worker_thread = threading.Thread(target=wrap, daemon=True)
        state.worker_thread.start()

    def on_search_or_fetch(e):
        val = (input_field.current.value or '').strip()
        if not val:
            log(i18n.t('gui.err.no_url'), Colors.ERR)
            return
        m = mode.current.value
        ad = _load_audiodex()

        def action():
            results_col.controls.clear()
            state.page.update()
            if m == 'search':
                res = ad.search_youtube(val)
                if not res:
                    log('— nessun risultato —', Colors.TEXT_DIM)
                    return
                for i, r in enumerate(res, 1):
                    results_col.controls.append(_result_card(r, i))
            else:
                # URL: prova come playlist, poi come video singolo
                if ad._is_playlist_url(val):
                    title, entries, meta = ad.get_playlist_entries(val)
                    log(f'Playlist: {title} — {len(entries)} elementi', Colors.NEON_CYAN)
                    for i, r in enumerate(entries, 1):
                        results_col.controls.append(_result_card(r, i))
                else:
                    info = ad.get_video_details(val)
                    if info:
                        results_col.controls.append(_result_card(info, 1))
            state.page.update()

        run_bg(action)

    def _result_card(r: dict, idx: int) -> ft.Control:
        title = r.get('title') or r.get('fulltitle') or '—'
        uploader = r.get('uploader') or r.get('channel') or ''
        dur = r.get('duration')
        try:
            dur_s = f'{int(dur)//60}:{int(dur)%60:02d}' if dur else '—'
        except Exception:
            dur_s = '—'
        return ft.Container(
            padding=12,
            border_radius=10,
            bgcolor=Colors.BG_PANEL_2,
            border=ft.Border.all(1, Colors.STROKE),
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=32, height=32, border_radius=8,
                        bgcolor=Colors.SIDEBAR_SEL,
                        border=ft.Border.all(1, Colors.NEON_PURPLE),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(str(idx), color=Colors.NEON_MAGENTA,
                                        weight=ft.FontWeight.W_800, size=13),
                    ),
                    ft.Column(
                        expand=True, spacing=2,
                        controls=[
                            ft.Text(title, color=Colors.TEXT, size=13,
                                    weight=ft.FontWeight.W_600, max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f'{uploader} · {dur_s}',
                                    color=Colors.TEXT_DIM, size=11),
                        ],
                    ),
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE,
                            color=Colors.NEON_CYAN, size=18),
                ],
            ),
        )

    def on_download(e):
        val = (input_field.current.value or '').strip()
        if not val:
            log(i18n.t('gui.err.no_url'), Colors.ERR)
            return
        _persist()
        ad = _load_audiodex()
        out = (output_field.current.value or '').strip() or os.path.join(_HERE, 'download_audio')
        fmt = fmt_field.current.value or 'm4a'
        media = 'video' if media_field.current.value == 'video' else 'audio'
        try:
            workers = max(1, int(workers_field.current.value or '4'))
        except ValueError:
            workers = 4
        get_lyrics = lyrics_switch.current.value

        def action():
            os.makedirs(out, exist_ok=True)
            if ad._is_playlist_url(val):
                _title, entries, _meta = ad.get_playlist_entries(val)
            else:
                info = ad.get_video_details(val)
                entries = [ad._entry_from_info(info, val)] if info else []
            if not entries:
                log('Nessun elemento da scaricare.', Colors.ERR)
                return
            log(f'Download di {len(entries)} elementi in {out}', Colors.NEON_CYAN)
            # Loop personalizzato per avere una progress bar in GUI: iteriamo
            # con ThreadPoolExecutor(max_workers=workers) e completiamo uno per
            # uno aggiornando la barra alla conclusione di ciascun download.
            from concurrent.futures import ThreadPoolExecutor, as_completed
            state.progress.begin(len(entries), i18n.t('gui.progress.download'))
            futures = {}
            with ThreadPoolExecutor(max_workers=workers) as ex:
                for entry in entries:
                    fut = ex.submit(
                        ad.download_single, entry, out,
                        audio_format=fmt,
                        fetch_lyrics=get_lyrics,
                        media=media,
                    )
                    futures[fut] = entry
                for fut in as_completed(futures):
                    entry = futures[fut]
                    name = entry.get('title') or entry.get('id') or '—'
                    try:
                        fut.result()
                        state.progress.step(name, ok=True)
                    except Exception as exc:  # noqa: BLE001
                        log(f'{name}: {exc}', Colors.ERR)
                        state.progress.step(f'{name} — {exc}', ok=False)
            state.progress.end(ok=True, message=i18n.t('gui.progress.done'))

        run_bg(action)

    header = ft.Column(
        spacing=6,
        controls=[
            ft.Text(i18n.t('gui.audio.title'), color=Colors.TEXT, size=22,
                    weight=ft.FontWeight.W_800, font_family='Orbitron'),
            ft.Text(i18n.t('gui.audio.desc'), color=Colors.TEXT_DIM, size=12),
        ],
    )

    input_row = ft.Row(
        spacing=10,
        controls=[
            ft.Dropdown(
                ref=mode, width=160, value='url',
                options=[
                    ft.dropdown.Option('url', i18n.t('gui.audio.mode.url')),
                    ft.dropdown.Option('search', i18n.t('gui.audio.mode.search')),
                ],
                border_color=Colors.STROKE,
                focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label=i18n.t('gui.audio.mode'),
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
            ),
            ft.TextField(
                ref=input_field, expand=True,
                hint_text=i18n.t('gui.audio.url.hint'),
                border_color=Colors.STROKE,
                focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                data='audio-input',
            ),
            ft.ElevatedButton(
                content=i18n.t('gui.audio.action.fetch'),
                icon=ft.Icons.SEARCH,
                on_click=on_search_or_fetch,
                bgcolor=Colors.NEON_PURPLE, color=Colors.BG_DEEP,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=18, vertical=16),
                ),
                data='audio-fetch',
            ),
        ],
    )

    opts_row = ft.ResponsiveRow(
        columns=12, run_spacing=10, spacing=10,
        controls=[
            ft.TextField(
                ref=output_field, col={'xs': 12, 'md': 6},
                label=i18n.t('gui.audio.output'),
                hint_text=i18n.t('gui.audio.output.hint'),
                value=presets.get('audio_output'),
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_blur=_persist,
            ),
            ft.Dropdown(
                ref=fmt_field, value=presets.get('audio_format'), col={'xs': 6, 'md': 2},
                label=i18n.t('gui.audio.format'),
                options=[
                    ft.dropdown.Option('m4a', 'M4A'),
                    ft.dropdown.Option('mp3', 'MP3'),
                    ft.dropdown.Option('opus', 'OPUS'),
                    ft.dropdown.Option('webm', 'WEBM'),
                ],
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2, text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_select=_persist,
            ),
            ft.Dropdown(
                ref=media_field, value=presets.get('audio_media'), col={'xs': 6, 'md': 2},
                label=i18n.t('gui.audio.media'),
                options=[
                    ft.dropdown.Option('audio', i18n.t('gui.audio.media.audio')),
                    ft.dropdown.Option('video', i18n.t('gui.audio.media.video')),
                ],
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2, text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_select=_persist,
            ),
            ft.TextField(
                ref=workers_field, value=presets.get('audio_workers'), col={'xs': 12, 'md': 2},
                label=i18n.t('gui.audio.workers'),
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2, text_size=13, dense=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_blur=_persist,
            ),
        ],
    )

    lyrics_row = ft.Row(
        spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Switch(ref=lyrics_switch, value=presets.get('audio_lyrics'),
                      active_color=Colors.NEON_PURPLE,
                      inactive_thumb_color=Colors.TEXT_DIM,
                      on_change=_persist),
            ft.Text(i18n.t('gui.audio.lyrics'), color=Colors.TEXT_DIM, size=12),
            ft.Container(expand=True),
            ft.ElevatedButton(
                content=i18n.t('gui.audio.action.download'),
                icon=ft.Icons.DOWNLOAD,
                on_click=on_download,
                bgcolor=Colors.NEON_MAGENTA, color=Colors.BG_DEEP,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=22, vertical=18),
                ),
                data='audio-download',
            ),
        ],
    )

    results_panel = ft.Container(
        border_radius=12, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE),
        padding=14, expand=True,
        content=ft.Column(
            expand=True, spacing=10,
            controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.LIBRARY_MUSIC, color=Colors.NEON_CYAN, size=16),
                    ft.Text(i18n.t('gui.audio.results'), color=Colors.TEXT, size=13,
                            weight=ft.FontWeight.W_700),
                ]),
                ft.Container(
                    expand=True,
                    content=results_col,
                ),
            ],
        ),
    )

    # Placeholder quando nessun risultato
    results_col.controls.append(
        ft.Container(
            padding=20, alignment=ft.Alignment.CENTER,
            content=ft.Text(i18n.t('gui.audio.no_results'),
                            color=Colors.TEXT_DIM, size=12),
        )
    )

    return ft.Column(
        expand=True, spacing=16,
        controls=[
            header,
            ft.Container(
                padding=16, border_radius=14, bgcolor=Colors.BG_PANEL,
                border=ft.Border.all(1, Colors.STROKE),
                content=ft.Column(spacing=12, controls=[input_row, opts_row, lyrics_row]),
            ),
            results_panel,
        ],
    )


# ── Sezione Masterizzazione ──────────────────────────────────────────────────
AUDIO_EXTS_LOCAL = frozenset({'.m4a', '.mp3', '.opus', '.mp4', '.wav',
                              '.flac', '.aac', '.ogg', '.wma'})


def _read_duration(path: str) -> float | None:
    """Legge la durata in secondi con mutagen (già dipendenza del progetto)."""
    try:
        from mutagen import File as _MFile  # type: ignore
        mf = _MFile(path)
        if mf is not None and getattr(mf, 'info', None) is not None:
            return float(mf.info.length)
    except Exception:
        return None
    return None


def _format_duration(sec: float | int) -> str:
    if not sec or sec < 0:
        return '--:--'
    sec = int(round(sec))
    m, s = divmod(sec, 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f'{h}:{m:02d}:{s:02d}'
    return f'{m}:{s:02d}'


def _scan_audio_folder(folder: str) -> list[dict]:
    """Elenca i file audio della cartella, ordinati come da CLI (nome file)."""
    if not folder or not os.path.isdir(folder):
        return []
    entries = []
    for name in sorted(os.listdir(folder), key=lambda x: x.lower()):
        full = os.path.join(folder, name)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext not in AUDIO_EXTS_LOCAL:
            continue
        try:
            size = os.path.getsize(full)
        except OSError:
            size = 0
        entries.append({
            'name': name,
            'path': full,
            'ext': ext,
            'size': size,
            'duration': _read_duration(full),
        })
    return entries


def build_burn_view(state: AppState, log_view: ft.ListView,
                    status_ctrl: ft.Text) -> ft.Control:
    folder_field = ft.Ref[ft.TextField]()
    speed_field = ft.Ref[ft.Dropdown]()
    drive_field = ft.Ref[ft.Dropdown]()
    dryrun_switch = ft.Ref[ft.Switch]()
    noeject_switch = ft.Ref[ft.Switch]()
    presets = state.presets
    _default_folder = os.environ.get('AUDIODEX_DEFAULT_FOLDER',
                                     presets.get('burn_folder') or '')

    # Ordine tracce corrente (lista di dict). Aggiornato dallo scan e dalle
    # frecce su/giù nel pannello Tracce trovate.
    tracks_state: list[dict] = []

    def _persist(_e=None):
        presets.set('burn_folder', folder_field.current.value if folder_field.current else '')
        presets.set('burn_speed', speed_field.current.value if speed_field.current else 'auto')
        presets.set('burn_drive', drive_field.current.value if drive_field.current else 'auto')
        presets.set('burn_dry_run', dryrun_switch.current.value if dryrun_switch.current else False)
        presets.set('burn_no_eject', noeject_switch.current.value if noeject_switch.current else False)

    scanner = CDScanner(size=180)
    tracks_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO,
                            expand=True)
    tracks_summary = ft.Text('', color=Colors.TEXT_DIM, size=11)

    def _render_empty_tracks(message_key: str = 'gui.burn.tracks.empty'):
        tracks_list.controls.clear()
        tracks_list.controls.append(
            ft.Container(
                padding=16, alignment=ft.Alignment.CENTER,
                content=ft.Text(i18n.t(message_key),
                                color=Colors.TEXT_DIM, size=12,
                                italic=True, text_align=ft.TextAlign.CENTER),
            )
        )
        tracks_summary.value = ''

    def _render_tracks_list():
        """Ridisegna la lista in base a ``tracks_state`` (permutata dall'utente)."""
        tracks_list.controls.clear()
        if not tracks_state:
            _render_empty_tracks('gui.burn.tracks.none')
            return
        total_dur = 0.0
        n = len(tracks_state)
        for i, tr in enumerate(tracks_state, 1):
            dur = tr.get('duration')
            if dur:
                total_dur += dur
            over_limit = total_dur > 80 * 60
            row = ft.Container(
                padding=ft.Padding.symmetric(vertical=6, horizontal=10),
                border_radius=8,
                bgcolor=Colors.BG_PANEL_2,
                border=ft.Border.all(1,
                    Colors.ERR if over_limit else Colors.STROKE),
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=26, height=26, border_radius=6,
                            bgcolor=Colors.SIDEBAR_SEL,
                            border=ft.Border.all(1, Colors.NEON_PURPLE),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(f'{i:02d}',
                                            color=Colors.NEON_MAGENTA,
                                            size=11,
                                            weight=ft.FontWeight.W_800,
                                            font_family='JetBrains Mono'),
                        ),
                        ft.Column(
                            expand=True, spacing=1,
                            controls=[
                                ft.Text(tr['name'], color=Colors.TEXT,
                                        size=12, weight=ft.FontWeight.W_600,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(f"{tr['ext'].upper().lstrip('.')} · "
                                        f"{tr['size'] // 1024} KB",
                                        color=Colors.TEXT_DIM, size=10),
                            ],
                        ),
                        ft.Text(_format_duration(dur or 0),
                                color=Colors.NEON_CYAN, size=12,
                                weight=ft.FontWeight.W_700,
                                font_family='JetBrains Mono'),
                        # Frecce su/giù per riordinare
                        ft.IconButton(
                            icon=ft.Icons.ARROW_UPWARD, icon_size=16,
                            icon_color=Colors.NEON_PURPLE if i > 1 else Colors.TEXT_DIM,
                            tooltip=i18n.t('gui.tracks.up'),
                            disabled=(i == 1),
                            on_click=lambda _e, idx=i - 1: _move_track(idx, idx - 1),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_DOWNWARD, icon_size=16,
                            icon_color=Colors.NEON_PURPLE if i < n else Colors.TEXT_DIM,
                            tooltip=i18n.t('gui.tracks.down'),
                            disabled=(i == n),
                            on_click=lambda _e, idx=i - 1: _move_track(idx, idx + 1),
                        ),
                    ],
                ),
            )
            tracks_list.controls.append(row)
        over = total_dur > 80 * 60
        tracks_summary.value = i18n.t('gui.burn.tracks.total').format(
            n=n, dur=_format_duration(total_dur))
        tracks_summary.color = Colors.ERR if over else Colors.TEXT_DIM

    def _move_track(i: int, j: int):
        if 0 <= i < len(tracks_state) and 0 <= j < len(tracks_state):
            tracks_state[i], tracks_state[j] = tracks_state[j], tracks_state[i]
            _render_tracks_list()
            state.page.update()

    def _refresh_tracks():
        folder = (folder_field.current.value or '').strip() if folder_field.current else ''
        _persist()
        if not folder:
            tracks_state.clear()
            _render_empty_tracks('gui.burn.tracks.empty')
            state.page.update()
            return
        entries = _scan_audio_folder(folder)
        tracks_state.clear()
        tracks_state.extend(entries)
        _render_tracks_list()
        state.page.update()

    file_picker = ft.FilePicker()
    state.page.services.append(file_picker) if hasattr(state.page, 'services') else state.page.overlay.append(file_picker)

    def pick_folder(_e):
        # In Flet 0.86 get_directory_path restituisce direttamente il path.
        try:
            path = file_picker.get_directory_path()
        except Exception as exc:  # noqa: BLE001
            log(f'{exc}', Colors.ERR)
            return
        if path:
            folder_field.current.value = path
            state.page.update()
            _refresh_tracks()

    def log(msg: str, color: str = Colors.TEXT):
        log_view.controls.append(ft.Text(msg, color=color, size=12, selectable=True,
                                          font_family='JetBrains Mono'))
        state.page.update()

    def set_status(text: str, color: str = Colors.NEON_CYAN):
        status_ctrl.value = text
        status_ctrl.color = color
        state.page.update()

    def run_bg(fn, scan_msg: str | None = None):
        if state.working:
            return
        state.working = True
        set_status(i18n.t('gui.status.working'), Colors.NEON_CYAN)
        scanner.start(scan_msg)

        def wrap():
            sink = LogSink(log_view, state.page)
            try:
                with redirect_stdout(sink), redirect_stderr(sink):
                    fn()
                scanner.stop(i18n.t('gui.status.done'), ok=True)
                set_status(i18n.t('gui.status.done'), Colors.OK)
            except Exception as exc:  # noqa: BLE001
                log(f'{exc}', Colors.ERR)
                log(traceback.format_exc(), Colors.ERR)
                scanner.stop(i18n.t('gui.status.error'), ok=False)
                set_status(i18n.t('gui.status.error'), Colors.ERR)
            finally:
                sink.flush()
                state.working = False

        threading.Thread(target=wrap, daemon=True).start()

    def on_info(e):
        try:
            bd = _load_burndex()
        except Exception as exc:  # noqa: BLE001
            log(i18n.t('gui.err.win_only') + f' [{exc}]', Colors.ERR)
            return

        def action():
            bd._modalita_info()

        run_bg(action, i18n.t('gui.burn.scanning'))

    def on_burn(e):
        folder = (folder_field.current.value or '').strip()
        if not folder:
            log(i18n.t('gui.err.no_folder'), Colors.ERR)
            return
        _persist()
        try:
            bd = _load_burndex()
        except Exception as exc:  # noqa: BLE001
            log(i18n.t('gui.err.win_only') + f' [{exc}]', Colors.ERR)
            return

        speed_val = speed_field.current.value
        speed_x = None if not speed_val or speed_val == 'auto' else int(speed_val)
        drive_val = drive_field.current.value
        drive_idx = None if not drive_val or drive_val == 'auto' else int(drive_val)

        # Se l'utente ha riordinato, prepariamo una cartella temporanea di
        # hardlink numerati (01_, 02_, …) che verrà passata al CLI. Il CLI
        # ordina per nome, quindi i prefissi impongono l'ordine desiderato.
        ordered_paths = [tr['path'] for tr in tracks_state] if tracks_state else []
        original_order = [os.path.basename(tr['path'])
                          for tr in _scan_audio_folder(folder)] if ordered_paths else []
        current_order = [os.path.basename(p) for p in ordered_paths]
        needs_reorder = (ordered_paths and current_order != original_order)

        import tempfile as _tempfile
        import shutil as _shutil
        burn_folder = folder
        temp_dir_holder: dict[str, str | None] = {'path': None}

        if needs_reorder:
            tmp = _tempfile.mkdtemp(prefix='audiodex_burn_')
            temp_dir_holder['path'] = tmp
            pad = max(2, len(str(len(ordered_paths))))
            for i, src in enumerate(ordered_paths, 1):
                base = os.path.basename(src)
                dst = os.path.join(tmp, f'{i:0{pad}d} - {base}')
                try:
                    os.link(src, dst)  # hardlink (Windows/Linux stesso volume)
                except OSError:
                    try:
                        os.symlink(src, dst)
                    except OSError:
                        _shutil.copy2(src, dst)
            burn_folder = tmp
            log(f'Riordino attivo → cartella temporanea: {tmp}', Colors.NEON_CYAN)

        def action():
            state.progress.begin(None, i18n.t('gui.progress.burn'))
            try:
                bd.masterizza_cartella(
                    burn_folder,
                    speed_x=speed_x,
                    dry_run=dryrun_switch.current.value,
                    drive_index=drive_idx,
                    skip_confirm=True,
                    eject=not noeject_switch.current.value,
                )
                state.progress.end(ok=True, message=i18n.t('gui.progress.done'))
            except Exception:
                state.progress.end(ok=False, message=i18n.t('gui.progress.err'))
                raise
            finally:
                # Pulizia cartella temporanea di riordino, se creata.
                tmp = temp_dir_holder.get('path')
                if tmp and os.path.isdir(tmp):
                    try:
                        _shutil.rmtree(tmp, ignore_errors=True)
                    except Exception:
                        pass

        run_bg(action, i18n.t('gui.burn.writing'))

    header = ft.Column(
        spacing=6,
        controls=[
            ft.Text(i18n.t('gui.burn.title'), color=Colors.TEXT, size=22,
                    weight=ft.FontWeight.W_800, font_family='Orbitron'),
            ft.Text(i18n.t('gui.burn.desc'), color=Colors.TEXT_DIM, size=12),
        ],
    )

    folder_row = ft.Row(
        spacing=10,
        controls=[
            ft.TextField(
                ref=folder_field, expand=True,
                label=i18n.t('gui.burn.folder'),
                hint_text=i18n.t('gui.burn.folder.hint'),
                value=_default_folder,
                border_color=Colors.STROKE,
                focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                data='burn-folder',
                on_blur=lambda _e: _refresh_tracks(),
                on_submit=lambda _e: _refresh_tracks(),
            ),
            ft.OutlinedButton(
                content=i18n.t('gui.burn.pick'), icon=ft.Icons.FOLDER_OPEN,
                on_click=pick_folder,
                style=ft.ButtonStyle(
                    color=Colors.NEON_CYAN,
                    side=ft.BorderSide(1, Colors.STROKE),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=18),
                ),
                data='burn-pick',
            ),
        ],
    )

    opts_row = ft.ResponsiveRow(
        columns=12, spacing=10, run_spacing=10,
        controls=[
            ft.Dropdown(
                ref=speed_field, value=presets.get('burn_speed'), col={'xs': 6, 'md': 4},
                label=i18n.t('gui.burn.speed'),
                options=[
                    ft.dropdown.Option('auto', i18n.t('gui.burn.speed.auto')),
                    ft.dropdown.Option('4', '4x'),
                    ft.dropdown.Option('8', '8x'),
                    ft.dropdown.Option('16', '16x'),
                    ft.dropdown.Option('24', '24x'),
                    ft.dropdown.Option('32', '32x'),
                    ft.dropdown.Option('40', '40x'),
                    ft.dropdown.Option('48', '48x'),
                ],
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_select=_persist,
            ),
            ft.Dropdown(
                ref=drive_field, value=presets.get('burn_drive'), col={'xs': 6, 'md': 4},
                label=i18n.t('gui.burn.drive'),
                options=[
                    ft.dropdown.Option('auto', i18n.t('gui.burn.drive.auto')),
                    ft.dropdown.Option('0', '#0'),
                    ft.dropdown.Option('1', '#1'),
                    ft.dropdown.Option('2', '#2'),
                ],
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_select=_persist,
            ),
        ],
    )

    toggles = ft.Column(
        spacing=8,
        controls=[
            ft.Row(spacing=10, controls=[
                ft.Switch(ref=dryrun_switch, value=presets.get('burn_dry_run'),
                          active_color=Colors.NEON_PURPLE, on_change=_persist),
                ft.Text(i18n.t('gui.burn.dryrun'), color=Colors.TEXT_DIM, size=12),
            ]),
            ft.Row(spacing=10, controls=[
                ft.Switch(ref=noeject_switch, value=presets.get('burn_no_eject'),
                          active_color=Colors.NEON_PURPLE, on_change=_persist),
                ft.Text(i18n.t('gui.burn.noeject'), color=Colors.TEXT_DIM, size=12),
            ]),
        ],
    )

    actions = ft.Row(
        spacing=10,
        controls=[
            ft.OutlinedButton(
                content=i18n.t('gui.burn.action.info'), icon=ft.Icons.INFO_OUTLINE,
                on_click=on_info,
                style=ft.ButtonStyle(
                    color=Colors.NEON_CYAN,
                    side=ft.BorderSide(1, Colors.NEON_CYAN),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=18, vertical=18),
                ),
                data='burn-info',
            ),
            ft.Container(expand=True),
            ft.ElevatedButton(
                content=i18n.t('gui.burn.action.burn'), icon=ft.Icons.ALBUM,
                on_click=on_burn,
                bgcolor=Colors.NEON_MAGENTA, color=Colors.BG_DEEP,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=24, vertical=18),
                ),
                data='burn-start',
            ),
        ],
    )

    scanner_panel = ft.Container(
        padding=20, border_radius=14, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE),
        alignment=ft.Alignment.CENTER,
        content=scanner,
    )

    form_panel = ft.Container(
        padding=16, border_radius=14, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE),
        expand=True,
        content=ft.Column(spacing=14, controls=[folder_row, opts_row, toggles, actions]),
    )

    # Pannello tracce (anteprima cartella)
    _render_empty_tracks('gui.burn.tracks.empty')
    if _default_folder:
        # popola in modo asincrono al primo render
        import threading as _th
        _th.Timer(0.5, _refresh_tracks).start()
    tracks_panel = ft.Container(
        border_radius=14, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE),
        padding=14, height=260,
        content=ft.Column(
            expand=True, spacing=8,
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.QUEUE_MUSIC,
                                    color=Colors.NEON_CYAN, size=16),
                            ft.Text(i18n.t('gui.burn.tracks'),
                                    color=Colors.TEXT, size=13,
                                    weight=ft.FontWeight.W_700),
                        ]),
                        ft.Container(expand=True),
                        tracks_summary,
                    ],
                ),
                ft.Container(
                    expand=True,
                    content=tracks_list,
                ),
                ft.Text(i18n.t('gui.tracks.hint') + '  ·  ' + i18n.t('gui.burn.tracks.limit'),
                        color=Colors.TEXT_DIM, size=10, italic=True),
            ],
        ),
    )

    return ft.Column(
        expand=True, spacing=16,
        controls=[
            header,
            ft.ResponsiveRow(
                columns=12, spacing=16, run_spacing=16,
                controls=[
                    ft.Container(col={'xs': 12, 'md': 8}, content=form_panel),
                    ft.Container(col={'xs': 12, 'md': 4}, content=scanner_panel),
                ],
            ),
            tracks_panel,
        ],
    )


# ── Sezione Rimasterizza video (PixDex) ──────────────────────────────────────
def build_pix_view(state: AppState, log_view: ft.ListView,
                   status_ctrl: ft.Text) -> ft.Control:
    """Sezione della GUI che pilota PixDex.

    Rispetto alle altre due sezioni ha una particolarità: mostra la diagnosi
    *prima* di lavorare. Una rimasterizzazione dura minuti od ore, e vedere
    scritto cosa non va nel file — e quale preset lo affronta — evita di
    scoprire a lavoro finito di aver scelto il trattamento sbagliato.
    """
    file_field = ft.Ref[ft.TextField]()
    preset_field = ft.Ref[ft.Dropdown]()
    height_field = ft.Ref[ft.Dropdown]()
    gpu_switch = ft.Ref[ft.Switch]()
    compare_switch = ft.Ref[ft.Switch]()
    presets = state.presets

    # Ultima diagnosi calcolata: evita di rileggere il file al momento di
    # partire e ricorda quale preset applicare quando la scelta è "automatico".
    diagnosi_corrente: dict = {}

    diag_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    # ``src`` è obbligatorio in Flet 0.86: nasce vuota e invisibile, e prende
    # il percorso del PNG solo quando il confronto è stato prodotto davvero.
    preview_image = ft.Image(src='', fit=ft.BoxFit.CONTAIN, visible=False,
                             border_radius=10, expand=True)
    preview_placeholder = ft.Text(i18n.t('gui.pix.preview.empty'),
                                  color=Colors.TEXT_DIM, size=12, italic=True,
                                  text_align=ft.TextAlign.CENTER)

    def _persist(_e=None):
        presets.set('pix_preset', preset_field.current.value if preset_field.current else 'auto')
        presets.set('pix_height', height_field.current.value if height_field.current else 'auto')
        presets.set('pix_gpu', gpu_switch.current.value if gpu_switch.current else False)
        presets.set('pix_compare', compare_switch.current.value if compare_switch.current else True)

    def log(msg: str, color: str = Colors.TEXT):
        log_view.controls.append(ft.Text(msg, color=color, size=12, selectable=True,
                                         font_family='JetBrains Mono'))
        state.page.update()

    def set_status(text: str, color: str = Colors.NEON_CYAN):
        status_ctrl.value = text
        status_ctrl.color = color
        state.page.update()

    def run_bg(fn):
        if state.working:
            return
        state.working = True
        set_status(i18n.t('gui.status.working'), Colors.NEON_CYAN)

        def wrap():
            sink = LogSink(log_view, state.page)
            try:
                with redirect_stdout(sink), redirect_stderr(sink):
                    fn()
                set_status(i18n.t('gui.status.done'), Colors.OK)
            except Exception as exc:  # noqa: BLE001
                log(f'{exc}', Colors.ERR)
                log(traceback.format_exc(), Colors.ERR)
                set_status(i18n.t('gui.status.error'), Colors.ERR)
            finally:
                sink.flush()
                state.working = False

        state.worker_thread = threading.Thread(target=wrap, daemon=True)
        state.worker_thread.start()

    file_picker = ft.FilePicker()
    (state.page.services.append(file_picker) if hasattr(state.page, 'services')
     else state.page.overlay.append(file_picker))

    def pick_file(_e):
        try:
            scelti = file_picker.pick_files(
                dialog_title=i18n.t('gui.pix.file'),
                allowed_extensions=[e.lstrip('.') for e in sorted(_load_pixdex().VIDEO_EXTS)],
                allow_multiple=False,
            )
        except Exception as exc:  # noqa: BLE001
            log(f'{exc}', Colors.ERR)
            return
        if scelti:
            file_field.current.value = scelti[0].path
            state.page.update()
            on_analyze(None)

    def _riga_diagnosi(testo: str, icona=ft.Icons.ARROW_RIGHT, colore=None) -> ft.Control:
        return ft.Row(
            spacing=8, vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(icona, color=colore or Colors.NEON_CYAN, size=14),
                ft.Text(testo, color=Colors.TEXT, size=12, expand=True,
                        no_wrap=False),
            ],
        )

    def _mostra_diagnosi(info: dict, problemi: list[str], consigliato: str):
        px = _load_pixdex()
        diag_column.controls.clear()
        diag_column.controls.append(
            _riga_diagnosi(
                f"{os.path.basename(info['path'])}  ·  {info['width']}×{info['height']}"
                f"  ·  {info['fps']:.0f} fps  ·  {info['bitrate'] // 1000} kbit/s",
                ft.Icons.MOVIE, Colors.NEON_PURPLE,
            )
        )
        diag_column.controls.append(ft.Divider(color=Colors.STROKE, height=12))
        for p in problemi:
            diag_column.controls.append(_riga_diagnosi(p))
        diag_column.controls.append(ft.Container(height=6))
        diag_column.controls.append(
            ft.Row(spacing=8, controls=[
                ft.Text(i18n.t('gui.pix.diag.suggested') + ':',
                        color=Colors.TEXT_DIM, size=12),
                ft.Text(px.PRESETS[consigliato]['nome'](), color=Colors.OK,
                        size=12, weight=ft.FontWeight.W_800),
            ])
        )
        state.page.update()

    def _percorso() -> str:
        grezzo = (file_field.current.value or '') if file_field.current else ''
        return grezzo.strip().strip('"')

    def on_analyze(_e):
        path = _percorso()
        if not path:
            log(i18n.t('gui.pix.err.no_file'), Colors.ERR)
            return
        if not shutil.which('ffprobe'):
            log(i18n.t('gui.pix.err.ffmpeg'), Colors.ERR)
            return
        px = _load_pixdex()
        info = px.probe(path)
        if not info:
            log(i18n.t('gui.pix.err.probe'), Colors.ERR)
            return
        problemi, consigliato = px.diagnosi(info)
        diagnosi_corrente.clear()
        diagnosi_corrente.update({'info': info, 'preset': consigliato})
        _mostra_diagnosi(info, problemi, consigliato)

    def on_start(_e):
        path = _percorso()
        if not path:
            log(i18n.t('gui.pix.err.no_file'), Colors.ERR)
            return
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            log(i18n.t('gui.pix.err.ffmpeg'), Colors.ERR)
            return

        _persist()
        px = _load_pixdex()
        scelta_preset = preset_field.current.value if preset_field.current else 'auto'
        scelta_altezza = height_field.current.value if height_field.current else 'auto'
        usa_gpu = bool(gpu_switch.current.value) if gpu_switch.current else False
        vuole_confronto = bool(compare_switch.current.value) if compare_switch.current else True

        def action():
            info = diagnosi_corrente.get('info')
            consigliato = diagnosi_corrente.get('preset', 'standard')
            # La diagnosi in memoria vale solo se riguarda proprio questo file:
            # cambiare percorso senza premere Analizza non deve far applicare
            # il preset consigliato per il video precedente.
            if not info or info.get('path') != path:
                info = px.probe(path)
                if not info:
                    log(i18n.t('gui.pix.err.probe'), Colors.ERR)
                    return
                problemi, consigliato = px.diagnosi(info)
                _mostra_diagnosi(info, problemi, consigliato)

            preset = consigliato if scelta_preset == 'auto' else scelta_preset
            altezza = px.altezza_obiettivo(
                info, None if scelta_altezza == 'auto' else int(scelta_altezza), preset)
            catena = px.catena_filtri(preset, info, altezza)
            dst = px.nome_uscita(path, altezza or info['height'], None)

            totale = info['frames'] or 0
            state.progress.begin(totale or None, i18n.t('gui.pix.progress'))

            # La finestra si ridisegna al massimo tre volte al secondo: FFmpeg
            # riporta l'avanzamento molto più spesso, e inseguirlo fotogramma
            # per fotogramma ruberebbe alla codifica la CPU che le serve.
            ultimo = [0.0]

            def avanzamento(n: int, tot: int, velocita: str):
                adesso = time.monotonic()
                if adesso - ultimo[0] < 0.33 and (not tot or n < tot):
                    return
                ultimo[0] = adesso
                dettaglio = f'{n}/{tot}' if tot else str(n)
                if velocita:
                    dettaglio += f'  ·  {velocita}'
                state.progress.seek(n, tot or None, dettaglio)

            ok = px.rimasterizza(info, dst, catena, usa_gpu, px.CRF_DEFAULT,
                                 avanzamento=avanzamento)
            if not ok:
                state.progress.end(False, i18n.t('gui.progress.err'))
                return

            if vuole_confronto:
                # Il fotogramma si prende a un terzo del video: l'inizio è
                # quasi sempre una sigla o una schermata nera, dove nessun
                # filtro avrebbe niente da mostrare.
                istante = max(info['duration'] / 3, 0.0)
                png = px.confronto(path, dst,
                                   os.path.splitext(dst)[0] + ' [confronto].png',
                                   istante)
                if png:
                    preview_image.src = png
                    preview_image.visible = True
                    preview_placeholder.visible = False

            state.progress.end(True, i18n.t('gui.progress.done'))
            log(i18n.t('gui.pix.done', file=os.path.basename(dst)), Colors.OK)
            state.page.update()

        run_bg(action)

    header = ft.Column(
        spacing=6,
        controls=[
            ft.Text(i18n.t('gui.pix.title'), color=Colors.TEXT, size=22,
                    weight=ft.FontWeight.W_800, font_family='Orbitron'),
            ft.Text(i18n.t('gui.pix.desc'), color=Colors.TEXT_DIM, size=12),
        ],
    )

    file_row = ft.Row(
        spacing=10,
        controls=[
            ft.TextField(
                ref=file_field, expand=True,
                label=i18n.t('gui.pix.file'),
                hint_text=i18n.t('gui.pix.file.hint'),
                border_color=Colors.STROKE,
                focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                data='pix-file',
                on_submit=on_analyze,
            ),
            ft.OutlinedButton(
                content=i18n.t('gui.pix.pick'), icon=ft.Icons.VIDEO_FILE,
                on_click=pick_file,
                style=ft.ButtonStyle(
                    color=Colors.NEON_CYAN,
                    side=ft.BorderSide(1, Colors.STROKE),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=18),
                ),
                data='pix-pick',
            ),
        ],
    )

    _px = _load_pixdex()
    opts_row = ft.ResponsiveRow(
        columns=12, spacing=10, run_spacing=10,
        controls=[
            ft.Dropdown(
                ref=preset_field, value=presets.get('pix_preset') or 'auto',
                col={'xs': 12, 'md': 7}, label=i18n.t('gui.pix.preset'),
                options=[ft.dropdown.Option('auto', i18n.t('gui.pix.preset.auto'))] + [
                    ft.dropdown.Option(chiave, _px.PRESETS[chiave]['nome']())
                    for chiave in ('pulito', 'standard', 'forte', 'animazione', 'vecchio')
                ],
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_select=_persist,
            ),
            ft.Dropdown(
                ref=height_field, value=presets.get('pix_height') or 'auto',
                col={'xs': 12, 'md': 5}, label=i18n.t('gui.pix.height'),
                options=[
                    ft.dropdown.Option('auto', i18n.t('gui.pix.height.auto')),
                    ft.dropdown.Option('720', '720p'),
                    ft.dropdown.Option('1080', '1080p'),
                    ft.dropdown.Option('1440', '1440p'),
                    ft.dropdown.Option('2160', '2160p'),
                ],
                border_color=Colors.STROKE, focused_border_color=Colors.NEON_PURPLE,
                color=Colors.TEXT, bgcolor=Colors.BG_PANEL_2,
                text_size=13, dense=True,
                label_style=ft.TextStyle(color=Colors.TEXT_DIM, size=11),
                on_select=_persist,
            ),
        ],
    )

    # La codifica sulla GPU è accesa di default. Misurato su un portatile con
    # Ryzen 5 3500U e Vega 8, sulla catena di filtri vera: 30,9 s contro 73,6 s
    # per lo stesso spezzone: 2,4 volte più veloce. Il guadagno supera quello
    # della sola codifica perché su quattro core i filtri e l'encoder si
    # contendono la CPU, e spostando l'encoder i filtri se la prendono tutta.
    # Il prezzo è un file circa un quinto più pesante a parità di resa.
    _gpu_salvato = presets.get('pix_gpu')
    _confronto_salvato = presets.get('pix_compare')
    toggles = ft.Column(
        spacing=8,
        controls=[
            ft.Row(spacing=10, controls=[
                ft.Switch(ref=gpu_switch,
                          value=True if _gpu_salvato is None else bool(_gpu_salvato),
                          active_color=Colors.NEON_PURPLE, on_change=_persist),
                ft.Text(i18n.t('gui.pix.gpu'), color=Colors.TEXT_DIM, size=12,
                        expand=True, no_wrap=False),
            ]),
            ft.Row(spacing=10, controls=[
                ft.Switch(ref=compare_switch,
                          value=True if _confronto_salvato is None else bool(_confronto_salvato),
                          active_color=Colors.NEON_PURPLE, on_change=_persist),
                ft.Text(i18n.t('gui.pix.compare'), color=Colors.TEXT_DIM, size=12,
                        expand=True, no_wrap=False),
            ]),
        ],
    )

    actions = ft.Row(
        spacing=10,
        controls=[
            ft.OutlinedButton(
                content=i18n.t('gui.pix.action.analyze'), icon=ft.Icons.TROUBLESHOOT,
                on_click=on_analyze,
                style=ft.ButtonStyle(
                    color=Colors.NEON_CYAN,
                    side=ft.BorderSide(1, Colors.NEON_CYAN),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=18, vertical=18),
                ),
                data='pix-analyze',
            ),
            ft.Container(expand=True),
            ft.ElevatedButton(
                content=i18n.t('gui.pix.action.start'), icon=ft.Icons.AUTO_FIX_HIGH,
                on_click=on_start,
                bgcolor=Colors.NEON_MAGENTA, color=Colors.BG_DEEP,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=24, vertical=18),
                ),
                data='pix-start',
            ),
        ],
    )

    form_panel = ft.Container(
        padding=16, border_radius=14, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE),
        content=ft.Column(spacing=14, controls=[file_row, opts_row, toggles, actions]),
    )

    diag_column.controls.append(
        ft.Container(
            padding=16, alignment=ft.Alignment.CENTER,
            content=ft.Text(i18n.t('gui.pix.diag.empty'), color=Colors.TEXT_DIM,
                            size=12, italic=True,
                            text_align=ft.TextAlign.CENTER),
        )
    )
    diag_panel = ft.Container(
        padding=14, border_radius=14, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE), height=250,
        content=ft.Column(
            expand=True, spacing=8,
            controls=[
                ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.TROUBLESHOOT, color=Colors.NEON_CYAN, size=16),
                    ft.Text(i18n.t('gui.pix.diag.title'), color=Colors.TEXT,
                            size=13, weight=ft.FontWeight.W_700),
                ]),
                ft.Container(expand=True, content=diag_column),
            ],
        ),
    )

    preview_panel = ft.Container(
        padding=14, border_radius=14, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE), height=250,
        content=ft.Column(
            expand=True, spacing=8,
            controls=[
                ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.COMPARE, color=Colors.NEON_CYAN, size=16),
                    ft.Text(i18n.t('gui.pix.preview'), color=Colors.TEXT,
                            size=13, weight=ft.FontWeight.W_700),
                ]),
                ft.Container(
                    expand=True, alignment=ft.Alignment.CENTER,
                    content=ft.Stack(expand=True, controls=[
                        ft.Container(expand=True, alignment=ft.Alignment.CENTER,
                                     content=preview_placeholder),
                        preview_image,
                    ]),
                ),
            ],
        ),
    )

    return ft.Column(
        expand=True, spacing=16,
        controls=[
            header,
            form_panel,
            ft.ResponsiveRow(
                columns=12, spacing=16, run_spacing=16,
                controls=[
                    ft.Container(col={'xs': 12, 'md': 6}, content=diag_panel),
                    ft.Container(col={'xs': 12, 'md': 6}, content=preview_panel),
                ],
            ),
        ],
    )


# ── Pannello log condiviso ───────────────────────────────────────────────────
def build_log_panel(state: AppState) -> tuple[ft.Container, ft.ListView, ft.Text]:
    log_view = ft.ListView(expand=True, spacing=1, auto_scroll=True)
    log_view.controls.append(
        ft.Text(i18n.t('gui.log.empty'), color=Colors.TEXT_DIM, size=12,
                italic=True, font_family='JetBrains Mono')
    )
    status_ctrl = ft.Text(i18n.t('gui.status.idle'),
                          color=Colors.NEON_CYAN, size=11,
                          weight=ft.FontWeight.W_700)

    def clear_log(e):
        log_view.controls.clear()
        log_view.controls.append(
            ft.Text(i18n.t('gui.log.empty'), color=Colors.TEXT_DIM, size=12,
                    italic=True, font_family='JetBrains Mono')
        )
        state.page.update()

    header = ft.Row(
        controls=[
            ft.Row(spacing=8, controls=[
                ft.Container(width=8, height=8, border_radius=8,
                             bgcolor=Colors.NEON_MAGENTA,
                             shadow=ft.BoxShadow(blur_radius=10,
                                                 color=Colors.NEON_MAGENTA)),
                ft.Text(i18n.t('gui.log.title'), color=Colors.TEXT, size=13,
                        weight=ft.FontWeight.W_700),
                ft.Container(width=1, height=14, bgcolor=Colors.STROKE),
                status_ctrl,
            ]),
            ft.Container(expand=True),
            ft.TextButton(
                content=i18n.t('gui.log.clear'), icon=ft.Icons.DELETE_SWEEP,
                on_click=clear_log,
                style=ft.ButtonStyle(color=Colors.TEXT_DIM),
                data='log-clear',
            ),
        ],
    )

    panel = ft.Container(
        padding=14, border_radius=14, bgcolor=Colors.BG_PANEL,
        border=ft.Border.all(1, Colors.STROKE),
        height=220,
        content=ft.Column(expand=True, spacing=8, controls=[header, log_view]),
    )
    return panel, log_view, status_ctrl


# ── Entry point Flet ─────────────────────────────────────────────────────────
def main(page: ft.Page):
    # Lingua salvata (o default IT come da CLI).
    saved = i18n.load_saved()
    if saved:
        i18n.set_language(saved)
    else:
        i18n.set_language('it')

    page.title = 'AudioDex Suite'
    page.bgcolor = Colors.BG_DEEP
    page.padding = 0
    page.window.min_width = 1100
    page.window.min_height = 720
    page.window.width = 1280
    page.window.height = 820
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {
        'Orbitron': 'https://fonts.gstatic.com/s/orbitron/v29/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nyGy6xpmIyXjU1pg.woff2',
        'JetBrains Mono': 'https://fonts.gstatic.com/s/jetbrainsmono/v20/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjPVmUsaaDhw.woff2',
    }
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=Colors.NEON_PURPLE,
            secondary=Colors.NEON_MAGENTA,
            surface=Colors.BG_PANEL,
        ),
        font_family='Inter',
    )

    state = AppState(page)

    def render():
        # Ricrea l'intero layout: cambia lingua e sezione senza mescolare stati.
        log_panel, log_view, status_ctrl = build_log_panel(state)
        if state.section == 'audio':
            content = build_audio_view(state, log_view, status_ctrl)
        elif state.section == 'pix':
            content = build_pix_view(state, log_view, status_ctrl)
        else:
            content = build_burn_view(state, log_view, status_ctrl)

        sidebar = build_sidebar(state)

        main_area = ft.Container(
            expand=True,
            padding=ft.Padding.only(left=26, right=26, top=22, bottom=22),
            content=ft.Column(
                expand=True, spacing=16,
                controls=[
                    ft.Container(expand=True, content=content),
                    state.progress.container,
                    log_panel,
                ],
            ),
        )

        foreground = ft.Row(
            expand=True, spacing=0,
            controls=[sidebar, main_area],
        )

        page.controls.clear()
        page.add(
            ft.Stack(
                expand=True,
                controls=[
                    cyberpunk_background(page),
                    foreground,
                ],
            )
        )
        page.update()

    state.on_render = render
    render()


if __name__ == '__main__':
    # In modalità desktop Flet apre una finestra nativa; in modalità WEB apre
    # un server HTTP e mostra la stessa GUI nel browser. La scelta viene dal
    # ambiente: FLET_VIEW=web_browser per l'anteprima nel container.
    view_mode = os.environ.get('FLET_VIEW', 'flet_app')
    _assets = os.path.join(_HERE, 'assets')
    os.makedirs(_assets, exist_ok=True)
    # Il video di sfondo non sta nel repository: se manca parte il download in
    # background, così la finestra si apre subito col gradiente di fallback.
    ensure_background_video_async()
    if view_mode == 'web_browser':
        ft.app(target=main, view=ft.AppView.WEB_BROWSER,
               port=int(os.environ.get('FLET_PORT', '8550')),
               host='0.0.0.0', assets_dir=_assets)
    else:
        ft.app(target=main, assets_dir=_assets)
