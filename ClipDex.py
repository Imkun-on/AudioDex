"""ClipDex — taglia, unisce e converte i video scaricati con AudioDex.

A cosa serve
    Le operazioni di montaggio che servono davvero dopo un download, senza
    aprire un programma di editing: ritagliare uno spezzone, unire piu' file
    in uno solo, ricavarne una GIF o un provino, e riportare un video in un
    formato che le apparecchiature datate sappiano leggere.

Le sei operazioni
    taglia   — estrae uno spezzone, in copia o preciso al fotogramma
    unisci   — mette in fila piu' file, con un capitolo per ciascuno
    gif      — ricava una GIF con la palette calcolata su misura
    webp     — come la GIF ma in WebP animato, che pesa una frazione
    provino  — una griglia di fotogrammi per capire al volo cosa c'e' dentro
    compat   — riporta il video a un H.264 che leggono anche gli apparecchi vecchi

Copia o ricodifica
    E' la scelta che governa tutto il file. Copiare significa spostare i
    pacchetti gia' compressi da un contenitore all'altro: costa secondi e non
    perde un bit, ma vincola i tagli ai fotogrammi chiave e pretende che i
    file da unire siano gia' omogenei. Ricodificare toglie entrambi i vincoli
    e costa minuti, piu' una generazione di qualita'. ClipDex sceglie da solo
    la copia quando puo', e dice sempre quale delle due sta usando.

Come e' organizzato il file
    1. banner e presentazione Rich condivisa con gli altri strumenti;
    2. lettura dei file e utilita' di tempo;
    3. le sei operazioni, una funzione ciascuna;
    4. ``main()`` con i sottocomandi e la procedura guidata.

Nota sulla portabilita'
    Serve solo FFmpeg, quindi gira ovunque, come PixDex e a differenza di
    BurnDex.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import sys as _sys
# Tool standalone: eseguibile anche da fuori la cartella del progetto.
_HERE = os.path.dirname(os.path.abspath(__file__))
_sys.path.insert(0, _HERE)

from rich.align import Align
from rich.box import DOUBLE, HEAVY_HEAD, ROUNDED
from rich.markup import escape
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn,
    TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn,
)
from rich.rule import Rule
from rich.style import Style
from rich.table import Column, Table
from rich.text import Text

from Shared.logger_setup import setup_logger, console, SYM_OK
from Shared import i18n
from Shared.strings_clipdex import TESTI

i18n.register(TESTI)
t = i18n.t

log = setup_logger('clipdex', 'clipdex.log')

# Larghezza condivisa con gli altri tre strumenti.
LARGHEZZA = 68

VIDEO_EXTS = frozenset({'.mp4', '.mkv', '.webm', '.avi', '.mov', '.m4v',
                        '.flv', '.wmv', '.mpg', '.mpeg', '.ts', '.m2ts'})

# ── Valori di riferimento per GIF e WebP ─────────────────────────────────────
#
# La palette di una GIF ha 256 colori e basta: usare quella generica di FFmpeg
# su un video con sfumature produce una poltiglia di puntini. Calcolarla sul
# filmato costa un passaggio in piu' ed e' l'unico modo di ottenere qualcosa di
# guardabile.
#
# Misurato su tre secondi di un video reale, a 480 px e 15 fps, contro gli
# stessi fotogrammi non ridotti a palette:
#
#     un passaggio, palette generica      24.85 dB    1414 KB
#     due passaggi, palette su misura     26.57 dB    2479 KB
#     due passaggi, dither sierra2_4a     26.56 dB    3133 KB
#     WebP animato                             —       283 KB
#
# Da qui i default: due passaggi (+1.72 dB, si vede), dither ordinato di Bayer
# (il sierra2_4a costa un quarto di peso in piu' senza dare nulla in cambio) e
# la spinta verso il WebP, che a parita' di contenuto pesa quasi nove volte
# meno perche' non e' vincolato ai 256 colori.
GIF_FPS = 15                 # sopra i 15 il peso raddoppia senza guadagno visibile
GIF_LARGHEZZA = 480          # la larghezza e' il fattore che pesa di piu'
GIF_DITHER = 'bayer:bayer_scale=5'
WEBP_QUALITA = 70

# Griglia del provino: 4x4 fotogrammi presi a intervalli regolari bastano a
# capire di cosa parla un file senza aprirlo.
PROVINO_RIGHE = 4
PROVINO_COLONNE = 4
PROVINO_LARGHEZZA = 320

# Qualita' di ricodifica. 20 e' un gradino sotto il 18 di PixDex: qui non si
# sta rimasterizzando, si sta rimontando, e il sorgente e' gia' compresso.
CRF_DEFAULT = 20


def _print_banner() -> None:
    """Stampa il banner ASCII colorato 'ClipDex' all'avvio."""
    banner_lines = [
        r'   _________       ____           ',
        r'  / ____/ (_)___  / __ \___  _  __',
        r' / /   / / / __ \/ / / / _ \| |/_/',
        r'/ /___/ / / /_/ / /_/ /  __/>  <  ',
        r'\____/_/_/ .___/_____/\___/_/|_|  ',
        r'        /_/                       ',
    ]
    colors = ['bright_magenta', 'magenta', 'bright_blue', 'blue', 'bright_cyan', 'cyan']
    text = Text()
    for i, line in enumerate(banner_lines):
        text.append(line + '\n', style=Style(color=colors[i % len(colors)], bold=True))
    text.append('\n' + t('banner.subtitle'), style=Style(color='white', bold=True))
    text.append('  ·  ', style='dim')
    text.append(t('banner.tagline'), style='dim')

    console.print()
    console.print(Panel(Align.center(text), border_style='bright_blue',
                        box=DOUBLE, padding=(1, 2), width=LARGHEZZA))


def _passo(numero: int, totale: int, titolo: str) -> None:
    """Riga di separazione che annuncia il passo corrente."""
    console.print()
    console.print(Rule(
        Text.assemble(
            (t('step.label', n=numero, tot=totale),
             Style(color='black', bgcolor='bright_blue', bold=True)),
            ('  ', ''), (titolo.upper(), Style(color='bright_blue', bold=True)), ('  ', ''),
        ),
        style='bright_blue', align='left',
    ), width=LARGHEZZA)


def _progress() -> Progress:
    """Barra di avanzamento comune a tutte le operazioni che ricodificano."""
    return Progress(
        SpinnerColumn(style='bright_blue'),
        TextColumn('{task.description}', table_column=Column(
            width=26, no_wrap=True, overflow='ellipsis')),
        BarColumn(bar_width=None, style='grey37',
                  complete_style='bright_blue', finished_style='bright_green'),
        TaskProgressColumn(),
        TextColumn('{task.fields[extra]}', style='dim'),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def _chiedi(prompt: str) -> str:
    """Legge una risposta trattando Ctrl-C come rinuncia."""
    try:
        return console.input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return ''


def _check_ffmpeg() -> bool:
    """Verifica che ffmpeg e ffprobe siano nel PATH."""
    mancanti = [n for n in ('ffmpeg', 'ffprobe') if not shutil.which(n)]
    if mancanti:
        console.print(t('tools.no_ffmpeg', tools=', '.join(mancanti)))
        console.print(t('tools.install_ffmpeg'))
        return False
    return True


# ── Tempi ────────────────────────────────────────────────────────────────────

def leggi_tempo(valore: str | None) -> float | None:
    """Converte un istante scritto a mano in secondi.

    Accetta le forme che vengono spontanee a chi guarda un lettore video:
    ``90``, ``1:30``, ``01:02:03.5``. Restituisce None se non si capisce,
    invece di indovinare: un taglio nel punto sbagliato si scopre solo
    riguardando il risultato.
    """
    if valore is None:
        return None
    testo = valore.strip()
    if not testo:
        return None
    try:
        parti = [float(p) for p in testo.split(':')]
    except ValueError:
        return None
    if not 1 <= len(parti) <= 3 or any(p < 0 for p in parti):
        return None
    secondi = 0.0
    for p in parti:
        secondi = secondi * 60 + p
    return secondi


def _fmt_tempo(secondi: float) -> str:
    """Formatta una durata in h:mm:ss oppure m:ss."""
    s = int(secondi)
    ore, resto = divmod(s, 3600)
    minuti, sec = divmod(resto, 60)
    return f'{ore}:{minuti:02d}:{sec:02d}' if ore else f'{minuti}:{sec:02d}'


def _fmt_peso(byte: int) -> str:
    """Formatta una dimensione in MB o GB."""
    mb = byte / (1024 * 1024)
    return f'{mb / 1024:.2f} GB' if mb >= 1024 else f'{mb:.1f} MB'


def _fps(valore: str | None) -> float:
    """Converte una frequenza fotogrammi 'num/den' in un numero."""
    if not valore:
        return 0.0
    try:
        if '/' in valore:
            num, den = valore.split('/', 1)
            return float(num) / float(den) if float(den) else 0.0
        return float(valore)
    except (ValueError, ZeroDivisionError):
        return 0.0


def probe(path: str) -> dict | None:
    """Legge le caratteristiche di un file. None se non contiene video."""
    try:
        dati = json.loads(subprocess.run(
            ['ffprobe', '-v', 'error', '-print_format', 'json',
             '-show_format', '-show_streams', path],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', check=True, timeout=60).stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        log.warning('ffprobe fallito su %s: %s', path, exc)
        return None

    video = next((s for s in dati.get('streams', [])
                  if s.get('codec_type') == 'video'), None)
    audio = next((s for s in dati.get('streams', [])
                  if s.get('codec_type') == 'audio'), None)
    if not video:
        return None

    formato = dati.get('format', {})
    return {
        'path': path,
        'width': int(video.get('width') or 0),
        'height': int(video.get('height') or 0),
        'fps': _fps(video.get('avg_frame_rate')) or _fps(video.get('r_frame_rate')),
        'codec': video.get('codec_name') or '?',
        'pix_fmt': video.get('pix_fmt') or '?',
        'audio_codec': (audio or {}).get('codec_name') or '',
        'audio_rate': int((audio or {}).get('sample_rate') or 0),
        'audio_ch': int((audio or {}).get('channels') or 0),
        'duration': float(formato.get('duration') or 0.0),
        'size': int(formato.get('size') or 0),
        'has_audio': audio is not None,
    }


def _esegui(cmd: list[str], descrizione: str, fotogrammi: int = 0) -> bool:
    """Lancia FFmpeg mostrando l'avanzamento. True se ha funzionato.

    Lo standard error finisce su file: lasciato in una pipe non letta,
    riempirebbe il buffer del sistema operativo e bloccherebbe FFmpeg a meta'
    lavoro senza dire niente.
    """
    log.info('Comando: %s', ' '.join(cmd))
    completo = [*cmd[:-1], '-progress', 'pipe:1', '-nostats', cmd[-1]]

    with tempfile.TemporaryFile(mode='w+', encoding='utf-8', errors='replace') as err:
        proc = subprocess.Popen(completo, stdout=subprocess.PIPE, stderr=err,
                                text=True, encoding='utf-8', errors='replace',
                                bufsize=1)
        with _progress() as prog:
            task = prog.add_task(descrizione, total=fotogrammi or None, extra='')
            try:
                for riga in proc.stdout:
                    riga = riga.strip()
                    if riga.startswith('frame='):
                        try:
                            n = int(riga.split('=', 1)[1])
                        except ValueError:
                            continue
                        prog.update(task, completed=min(n, fotogrammi) if fotogrammi else n)
                    elif riga.startswith('speed='):
                        prog.update(task, extra=riga.split('=', 1)[1].strip())
            except KeyboardInterrupt:
                proc.terminate()
                console.print(t('run.interrupted'))
                return False
            finally:
                proc.stdout.close()

        if proc.wait() != 0:
            err.seek(0)
            righe = err.read().strip().splitlines()
            ultima = righe[-1] if righe else 'exit != 0'
            log.error('FFmpeg fallito: %s', ultima)
            console.print(t('run.failed', reason=escape(ultima[:120])))
            return False
    return True


def _pannello_esito(dst: str, sorgente: dict | None = None,
                    nota: str | None = None) -> None:
    """Riepilogo finale con il file prodotto e quanto pesa."""
    tab = Table(box=ROUNDED, show_header=False, border_style='grey37',
                width=LARGHEZZA, padding=(0, 1))
    tab.add_column(style='dim_label', no_wrap=True, width=18)
    tab.add_column(style='white', overflow='fold')

    nuovo = probe(dst) if os.path.splitext(dst)[1].lower() in VIDEO_EXTS else None
    tab.add_row(t('result.file'), escape(dst))
    peso = os.path.getsize(dst) if os.path.exists(dst) else 0
    if sorgente:
        tab.add_row(t('result.size'),
                    f"{_fmt_peso(sorgente['size'])} [dim]→[/dim] "
                    f'[bold]{_fmt_peso(peso)}[/bold]')
    else:
        tab.add_row(t('result.size'), f'[bold]{_fmt_peso(peso)}[/bold]')
    if nuovo:
        tab.add_row(t('result.video'),
                    f"{nuovo['width']}×{nuovo['height']}  ·  {nuovo['fps']:.0f} fps"
                    f"  ·  {_fmt_tempo(nuovo['duration'])}")
    if nota:
        tab.add_row('', f'[dim]{nota}[/dim]')

    console.print()
    console.print(Panel(tab, title=f"{SYM_OK} {t('result.title')}", title_align='left',
                        border_style='bright_green', box=ROUNDED,
                        width=LARGHEZZA, padding=(0, 0)))


# ── 1. Taglio ────────────────────────────────────────────────────────────────

def taglia(src: str, dst: str, inizio: float, fine: float | None,
           preciso: bool = False, crf: int = CRF_DEFAULT) -> bool:
    """Estrae lo spezzone fra ``inizio`` e ``fine``.

    In copia il taglio si aggancia al fotogramma chiave precedente, perche' i
    pacchetti compressi insieme non si spezzano a meta': l'inizio puo'
    scostarsi di qualche secondo, ma costa un istante e non perde nulla. Con
    ``preciso`` si ricodifica e il taglio cade dove e' stato chiesto.

    Sull'audio la differenza non esiste: i fotogrammi durano millisecondi.
    """
    info = probe(src)
    if not info:
        console.print(t('error.unreadable', path=escape(os.path.basename(src))))
        return False

    durata = (fine - inizio) if fine else max(info['duration'] - inizio, 0)
    if durata <= 0:
        console.print(t('error.empty_range'))
        return False

    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y',
           '-ss', f'{inizio:.3f}', '-t', f'{durata:.3f}', '-i', src]
    if preciso:
        cmd += ['-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k']
    else:
        cmd += ['-c', 'copy']
    cmd += ['-avoid_negative_ts', 'make_zero', '-movflags', '+faststart', dst]

    if not _esegui(cmd, t('run.cutting'), int(durata * info['fps'])):
        return False

    nota = t('cut.note_precise') if preciso else t('cut.note_copy')

    # In copia lo scostamento non e' un difetto ma una conseguenza, e va detto
    # con un numero: chiedere quattro secondi e riceverne sette sorprende, e
    # senza una spiegazione sembra un errore del programma. Su un file con i
    # fotogrammi chiave molto distanziati puo' arrivare a dieci secondi.
    if not preciso:
        prodotto = probe(dst)
        if prodotto:
            scostamento = abs(prodotto['duration'] - durata)
            if scostamento > 0.5:
                nota = t('cut.note_drift',
                         chiesta=f'{durata:.1f}', reale=f"{prodotto['duration']:.1f}",
                         scarto=f'{scostamento:.1f}')

    _pannello_esito(dst, info, nota)
    return True


# ── 2. Unione ────────────────────────────────────────────────────────────────

def _omogenei(infos: list[dict]) -> bool:
    """True se i file si possono incollare senza ricodificare.

    Il concat demuxer accosta i pacchetti cosi' come sono: pretende quindi
    che codec, risoluzione, formato dei pixel e frequenza coincidano. Basta
    che un file sia stato scaricato in un'altra qualita' perche' il risultato
    sia un video che si blocca a meta'. Meglio accorgersene prima.
    """
    if len(infos) < 2:
        return True
    primo = infos[0]
    chiavi = ('codec', 'width', 'height', 'pix_fmt', 'audio_codec',
              'audio_rate', 'audio_ch')
    return all(
        all(i[k] == primo[k] for k in chiavi)
        and abs(i['fps'] - primo['fps']) < 0.01
        for i in infos[1:]
    )


def _scrivi_capitoli(infos: list[dict], percorso: str) -> None:
    """Scrive un file ffmetadata con un capitolo per ogni file di partenza.

    Cosi' il video unito resta navigabile: si salta da un pezzo all'altro
    come in un DVD, invece di andare a cercare il minuto a mano.
    """
    righe = [';FFMETADATA1']
    inizio_ms = 0
    for info in infos:
        fine_ms = inizio_ms + int(info['duration'] * 1000)
        titolo = os.path.splitext(os.path.basename(info['path']))[0]
        righe += ['[CHAPTER]', 'TIMEBASE=1/1000',
                  f'START={inizio_ms}', f'END={fine_ms}',
                  f'title={titolo}']
        inizio_ms = fine_ms
    with open(percorso, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(righe) + '\n')


def unisci(sorgenti: list[str], dst: str, *, capitoli: bool = True,
           crf: int = CRF_DEFAULT) -> bool:
    """Mette in fila i file in un unico video.

    Se sono omogenei li incolla in copia — secondi, nessuna perdita. Se non lo
    sono li porta tutti alla risoluzione del primo e ricodifica, perche' non
    c'e' altro modo: i pacchetti di due codifiche diverse non si possono
    accostare.
    """
    infos = []
    for s in sorgenti:
        info = probe(s)
        if not info:
            console.print(t('error.unreadable', path=escape(os.path.basename(s))))
            return False
        infos.append(info)

    copia = _omogenei(infos)
    console.print(t('merge.mode_copy') if copia else t('merge.mode_encode'))

    with tempfile.TemporaryDirectory(prefix='clipdex_') as tmp:
        meta = os.path.join(tmp, 'capitoli.txt')
        if capitoli:
            _scrivi_capitoli(infos, meta)

        if copia:
            lista = os.path.join(tmp, 'lista.txt')
            with open(lista, 'w', encoding='utf-8', newline='\n') as fh:
                for s in sorgenti:
                    # L'apice singolo nel nome va raddoppiato con la sequenza
                    # di uscita del formato concat, altrimenti chiude la
                    # stringa e il file successivo diventa illeggibile.
                    fh.write("file '%s'\n" % os.path.abspath(s).replace("'", r"'\''"))
            cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y',
                   '-f', 'concat', '-safe', '0', '-i', lista]
            if capitoli:
                cmd += ['-i', meta, '-map_metadata', '1', '-map_chapters', '1']
            cmd += ['-c', 'copy', '-movflags', '+faststart', dst]
        else:
            larghezza, altezza = infos[0]['width'], infos[0]['height']
            fps = infos[0]['fps'] or 25
            cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y']
            for s in sorgenti:
                cmd += ['-i', s]
            if capitoli:
                cmd += ['-i', meta]

            catena, etichette = [], []
            for i, info in enumerate(infos):
                # force_original_aspect_ratio + pad: un file di proporzioni
                # diverse viene incorniciato invece che stirato.
                catena.append(
                    f'[{i}:v]scale={larghezza}:{altezza}:'
                    'force_original_aspect_ratio=decrease,'
                    f'pad={larghezza}:{altezza}:-1:-1,setsar=1,fps={fps:.4f}[v{i}]')
                if info['has_audio']:
                    catena.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]')
                else:
                    # Un file muto in mezzo sfaserebbe il montaggio audio:
                    # gli si mette sotto il silenzio della stessa durata.
                    catena.append(
                        f"anullsrc=r=48000:cl=stereo,atrim=0:{info['duration']:.3f},"
                        f'asetpts=PTS-STARTPTS[a{i}]')
                etichette.append(f'[v{i}][a{i}]')
            catena.append(''.join(etichette) + f'concat=n={len(infos)}:v=1:a=1[v][a]')

            cmd += ['-filter_complex', ';'.join(catena), '-map', '[v]', '-map', '[a]']
            if capitoli:
                cmd += ['-map_metadata', str(len(sorgenti)),
                        '-map_chapters', str(len(sorgenti))]
            cmd += ['-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', dst]

        totale = int(sum(i['duration'] * (i['fps'] or 25) for i in infos))
        if not _esegui(cmd, t('run.merging'), totale):
            return False

    _pannello_esito(dst, None,
                    t('merge.note_chapters', n=len(sorgenti)) if capitoli else None)
    return True


# ── 3. GIF e WebP ────────────────────────────────────────────────────────────

def _finestra(info: dict, inizio: float | None, durata: float | None,
              durata_default: float) -> tuple[float, float]:
    """Sceglie da dove e per quanto prendere lo spezzone.

    Senza indicazioni parte da un terzo del video: l'inizio e' quasi sempre
    una sigla o una schermata nera, e una GIF di nulla non serve a niente.
    """
    if inizio is None:
        inizio = info['duration'] / 3 if info['duration'] else 0.0
    if durata is None:
        durata = min(durata_default, max(info['duration'] - inizio, 1.0))
    return max(inizio, 0.0), max(durata, 0.1)


def gif(src: str, dst: str, inizio: float | None = None,
        durata: float | None = None, fps: int = GIF_FPS,
        larghezza: int = GIF_LARGHEZZA) -> bool:
    """Ricava una GIF calcolando la palette sul filmato stesso.

    La GIF ha 256 colori e basta. La palette generica di FFmpeg su un video
    con sfumature produce una poltiglia di puntini; calcolarla sui fotogrammi
    veri costa un passaggio in piu' e su contenuto reale vale 1.7 dB di
    fedelta' in piu'. ``split`` serve proprio a questo: manda lo stesso flusso
    sia al generatore di palette sia all'applicatore, senza file temporanei.
    """
    info = probe(src)
    if not info:
        console.print(t('error.unreadable', path=escape(os.path.basename(src))))
        return False
    inizio, durata = _finestra(info, inizio, durata, 5.0)

    catena = (f'fps={fps},scale={larghezza}:-1:flags=lanczos,split[a][b];'
              '[a]palettegen=stats_mode=diff[p];'
              f'[b][p]paletteuse=dither={GIF_DITHER}:diff_mode=rectangle')
    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y',
           '-ss', f'{inizio:.3f}', '-t', f'{durata:.3f}', '-i', src,
           '-lavfi', catena, '-loop', '0', dst]

    if not _esegui(cmd, t('run.gif'), int(durata * fps)):
        return False
    _pannello_esito(dst, None, t('gif.note', inizio=_fmt_tempo(inizio),
                                 durata=f'{durata:.1f}', fps=fps, w=larghezza))
    return True


def webp(src: str, dst: str, inizio: float | None = None,
         durata: float | None = None, fps: int = GIF_FPS,
         larghezza: int = GIF_LARGHEZZA) -> bool:
    """Come la GIF, ma in WebP animato.

    Non essendo vincolato a 256 colori non ha bisogno di palette, e sullo
    stesso spezzone pesa quasi nove volte meno di una GIF fatta bene. Lo
    leggono tutti i browser dell'ultimo decennio; se la destinazione e' un
    forum di vent'anni fa, allora serve la GIF.
    """
    info = probe(src)
    if not info:
        console.print(t('error.unreadable', path=escape(os.path.basename(src))))
        return False
    inizio, durata = _finestra(info, inizio, durata, 5.0)

    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y',
           '-ss', f'{inizio:.3f}', '-t', f'{durata:.3f}', '-i', src,
           '-vf', f'fps={fps},scale={larghezza}:-1:flags=lanczos',
           '-c:v', 'libwebp', '-lossless', '0', '-q:v', str(WEBP_QUALITA),
           '-loop', '0', '-an', dst]

    if not _esegui(cmd, t('run.webp'), int(durata * fps)):
        return False
    _pannello_esito(dst, None, t('gif.note', inizio=_fmt_tempo(inizio),
                                 durata=f'{durata:.1f}', fps=fps, w=larghezza))
    return True


# ── 4. Provino a griglia ─────────────────────────────────────────────────────

def provino(src: str, dst: str, righe: int = PROVINO_RIGHE,
            colonne: int = PROVINO_COLONNE,
            larghezza: int = PROVINO_LARGHEZZA) -> bool:
    """Compone una griglia di fotogrammi presi a intervalli regolari.

    Per capire cosa contiene un file e' piu' utile di un'anteprima animata:
    sedici istanti sparsi su tutta la durata dicono in un colpo d'occhio se
    e' il video giusto, dove cambiano le scene e se ci sono parti nere.
    """
    info = probe(src)
    if not info or not info['duration']:
        console.print(t('error.unreadable', path=escape(os.path.basename(src))))
        return False

    caselle = righe * colonne
    # Un fotogramma ogni N secondi, con N scelto perche' la griglia copra
    # esattamente tutta la durata: campionare a intervallo fisso lascerebbe
    # fuori la seconda meta' dei video lunghi.
    intervallo = max(info['duration'] / (caselle + 1), 0.1)

    # La casella ha misura fissa, ricavata dalle proporzioni del video. Senza,
    # basta che il filmato cambi formato a meta' — succede spesso nei montaggi
    # con spezzoni d'archivio — perche' la griglia esca a scalini. Le
    # proporzioni originali si conservano comunque: cio' che avanza viene
    # riempito di nero invece che stirato.
    altezza = max(2, round(larghezza * (info['height'] or 9)
                           / (info['width'] or 16) / 2) * 2)

    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', src,
           '-vf', (f'fps=1/{intervallo:.4f},'
                   f'scale={larghezza}:{altezza}:force_original_aspect_ratio=decrease'
                   ':flags=lanczos,'
                   f'pad={larghezza}:{altezza}:-1:-1:color=black,setsar=1,'
                   f'tile={colonne}x{righe}:padding=4:margin=4'),
           '-frames:v', '1', dst]

    if not _esegui(cmd, t('run.sheet'), 0):
        return False
    _pannello_esito(dst, None, t('sheet.note', n=caselle,
                                 ogni=_fmt_tempo(intervallo)))
    return True


# ── 5. Compatibilita' ────────────────────────────────────────────────────────

def compat(src: str, dst: str, crf: int = CRF_DEFAULT) -> bool:
    """Riporta il video a un H.264 che leggono anche gli apparecchi datati.

    Tre vincoli, tutti necessari e tutti spesso violati dai file scaricati:
    il profilo *baseline* (niente fotogrammi B, che i decodificatori piu'
    semplici non sanno gestire), il formato pixel ``yuv420p`` (molti file
    YouTube sono yuv444 o a 10 bit, che una TV del 2012 non decodifica) e le
    dimensioni pari, richieste dalla codifica stessa.

    ``+faststart`` sposta l'indice all'inizio del file: senza, un lettore da
    chiavetta USB deve leggere fino in fondo prima di poter partire.
    """
    info = probe(src)
    if not info:
        console.print(t('error.unreadable', path=escape(os.path.basename(src))))
        return False

    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', src,
           '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
           '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
           '-pix_fmt', 'yuv420p', '-crf', str(crf), '-preset', 'medium',
           '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-ar', '44100',
           '-movflags', '+faststart', dst]

    if not _esegui(cmd, t('run.compat'), int(info['duration'] * (info['fps'] or 25))):
        return False
    _pannello_esito(dst, info, t('compat.note'))
    return True


# ── Scelta interattiva ───────────────────────────────────────────────────────

def _trova_video(base: str) -> list[str]:
    """Elenca i video presenti, i piu' recenti per primi."""
    trovati = []
    for radice, _dirs, files in os.walk(base):
        for nome in files:
            if os.path.splitext(nome)[1].lower() in VIDEO_EXTS:
                trovati.append(os.path.join(radice, nome))
    trovati.sort(key=os.path.getmtime, reverse=True)
    return trovati


def _scegli_video(base: str) -> str | None:
    """Fa scegliere un video fra quelli scaricati, o accetta un percorso."""
    video = _trova_video(base) if os.path.isdir(base) else []
    if not video:
        console.print(t('choose.none', path=escape(base)))
        risposta = _chiedi(t('choose.ask_path'))
        return os.path.abspath(risposta.strip('"')) if risposta else None

    tab = Table(box=HEAVY_HEAD, border_style='grey37', width=LARGHEZZA,
                header_style='bold bright_blue')
    tab.add_column('#', justify='right', width=3, style='dim')
    tab.add_column(t('choose.col_file'), overflow='ellipsis', no_wrap=True)
    tab.add_column(t('choose.col_dur'), justify='right', width=9)
    tab.add_column(t('choose.col_size'), justify='right', width=10)

    mostrati = video[:15]
    for i, path in enumerate(mostrati, 1):
        info = probe(path)
        tab.add_row(str(i), escape(os.path.basename(path)),
                    _fmt_tempo(info['duration']) if info else '?',
                    _fmt_peso(os.path.getsize(path)))
    console.print()
    console.print(tab)

    risposta = _chiedi(t('choose.prompt'))
    if not risposta:
        return None
    if risposta.isdigit() and 1 <= int(risposta) <= len(mostrati):
        return mostrati[int(risposta) - 1]
    return os.path.abspath(risposta.strip('"'))


AZIONI = ('taglia', 'unisci', 'gif', 'webp', 'provino', 'compat')


def _scegli_azione() -> str | None:
    """Menu delle sei operazioni, per chi lancia il programma senza argomenti."""
    tab = Table(box=HEAVY_HEAD, border_style='grey37', width=LARGHEZZA,
                header_style='bold bright_blue')
    tab.add_column('#', justify='right', width=3, style='dim')
    tab.add_column(t('menu.col_action'), width=12, no_wrap=True)
    tab.add_column(t('menu.col_desc'), overflow='fold')

    for i, azione in enumerate(AZIONI, 1):
        tab.add_row(str(i), f'[bold]{azione}[/bold]', t(f'menu.{azione}'))

    console.print()
    console.print(tab)
    risposta = _chiedi(t('menu.prompt'))
    if risposta.isdigit() and 1 <= int(risposta) <= len(AZIONI):
        return AZIONI[int(risposta) - 1]
    if risposta in AZIONI:
        return risposta
    return None


def _nome_uscita(src: str, suffisso: str, estensione: str | None = None) -> str:
    """Nome del file prodotto, accanto all'originale.

    L'originale non viene mai sovrascritto: un montaggio e' una scelta, e la
    si rifa' volentieri con parametri diversi.
    """
    radice, ext = os.path.splitext(src)
    return f'{radice} [{suffisso}]{estensione or ext}'


def main() -> None:
    """Punto di ingresso: sottocomandi, oppure procedura guidata senza argomenti."""
    i18n.set_language('it')

    parser = argparse.ArgumentParser(
        description=t('cli.desc'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=t('cli.epilog'),
    )
    parser.add_argument('--base', '-b', type=str,
                        default=os.path.join(_HERE, 'download_audio'),
                        help=t('cli.base'))
    parser.add_argument('--crf', type=int, default=CRF_DEFAULT,
                        help=t('cli.crf', default=CRF_DEFAULT))
    sub = parser.add_subparsers(dest='azione', metavar='|'.join(AZIONI))

    p = sub.add_parser('taglia', help=t('menu.taglia'))
    p.add_argument('--input', '-i', type=str, default=None, help=t('cli.input'))
    p.add_argument('--output', '-o', type=str, default=None, help=t('cli.output'))
    p.add_argument('--da', type=str, default=None, help=t('cli.da'))
    p.add_argument('--a', type=str, default=None, help=t('cli.a'))
    p.add_argument('--preciso', action='store_true', help=t('cli.preciso'))

    p = sub.add_parser('unisci', help=t('menu.unisci'))
    p.add_argument('--input', '-i', type=str, nargs='+', default=None,
                   help=t('cli.input_multi'))
    p.add_argument('--dir', '-d', type=str, default=None, help=t('cli.dir'))
    p.add_argument('--output', '-o', type=str, default=None, help=t('cli.output'))
    p.add_argument('--no-capitoli', action='store_true', help=t('cli.no_chapters'))

    for nome in ('gif', 'webp'):
        p = sub.add_parser(nome, help=t(f'menu.{nome}'))
        p.add_argument('--input', '-i', type=str, default=None, help=t('cli.input'))
        p.add_argument('--output', '-o', type=str, default=None, help=t('cli.output'))
        p.add_argument('--da', type=str, default=None, help=t('cli.da'))
        p.add_argument('--durata', type=str, default=None, help=t('cli.durata'))
        p.add_argument('--fps', type=int, default=GIF_FPS, help=t('cli.fps', default=GIF_FPS))
        p.add_argument('--larghezza', type=int, default=GIF_LARGHEZZA,
                       help=t('cli.larghezza', default=GIF_LARGHEZZA))

    p = sub.add_parser('provino', help=t('menu.provino'))
    p.add_argument('--input', '-i', type=str, default=None, help=t('cli.input'))
    p.add_argument('--output', '-o', type=str, default=None, help=t('cli.output'))
    p.add_argument('--griglia', type=str, default=f'{PROVINO_COLONNE}x{PROVINO_RIGHE}',
                   help=t('cli.griglia'))

    p = sub.add_parser('compat', help=t('menu.compat'))
    p.add_argument('--input', '-i', type=str, default=None, help=t('cli.input'))
    p.add_argument('--output', '-o', type=str, default=None, help=t('cli.output'))

    args = parser.parse_args()

    _print_banner()
    if not _check_ffmpeg():
        sys.exit(1)

    azione = args.azione or _scegli_azione()
    if not azione:
        console.print(t('common.goodbye'))
        return

    base = os.path.abspath(args.base)

    # ── unisci: piu' sorgenti, quindi un percorso a sé ──────────────────────
    if azione == 'unisci':
        sorgenti = getattr(args, 'input', None)
        cartella = getattr(args, 'dir', None)
        if cartella:
            sorgenti = _trova_video(os.path.abspath(cartella))
            sorgenti.sort()      # in una cartella conta l'ordine dei nomi
        if not sorgenti:
            console.print(t('merge.need_inputs'))
            return
        sorgenti = [os.path.abspath(s) for s in sorgenti]
        mancanti = [s for s in sorgenti if not os.path.isfile(s)]
        if mancanti:
            console.print(t('error.missing', path=escape(mancanti[0])))
            sys.exit(1)
        if len(sorgenti) < 2:
            console.print(t('merge.need_two'))
            return

        _passo(1, 2, t('step.inputs'))
        for i, s in enumerate(sorgenti, 1):
            info = probe(s)
            console.print(t('merge.item', n=i, file=escape(os.path.basename(s)),
                            durata=_fmt_tempo(info['duration']) if info else '?'))

        dst = (os.path.abspath(getattr(args, 'output', None))
               if getattr(args, 'output', None)
               else _nome_uscita(sorgenti[0], 'ClipDex unito', '.mp4'))
        _passo(2, 2, t('step.working'))
        ok = unisci(sorgenti, dst,
                    capitoli=not getattr(args, 'no_capitoli', False), crf=args.crf)
        sys.exit(0 if ok else 1)

    # ── tutte le altre: una sola sorgente ───────────────────────────────────
    src = getattr(args, 'input', None)
    src = os.path.abspath(src) if src else _scegli_video(base)
    if not src:
        console.print(t('common.goodbye'))
        return
    if not os.path.isfile(src):
        console.print(t('error.missing', path=escape(src)))
        sys.exit(1)

    esplicito = getattr(args, 'output', None)
    _passo(1, 1, t('step.working'))

    if azione == 'taglia':
        inizio = leggi_tempo(getattr(args, 'da', None))
        fine = leggi_tempo(getattr(args, 'a', None))
        if inizio is None:
            inizio = leggi_tempo(_chiedi(t('cut.ask_from')))
        if inizio is None:
            console.print(t('error.bad_time'))
            sys.exit(1)
        if fine is None and not getattr(args, 'a', None):
            fine = leggi_tempo(_chiedi(t('cut.ask_to')))
        if fine is not None and fine <= inizio:
            console.print(t('error.empty_range'))
            sys.exit(1)
        dst = os.path.abspath(esplicito) if esplicito else _nome_uscita(src, 'ClipDex taglio')
        ok = taglia(src, dst, inizio, fine,
                    preciso=getattr(args, 'preciso', False), crf=args.crf)

    elif azione in ('gif', 'webp'):
        estensione = '.gif' if azione == 'gif' else '.webp'
        dst = (os.path.abspath(esplicito) if esplicito
               else _nome_uscita(src, f'ClipDex {azione}', estensione))
        funzione = gif if azione == 'gif' else webp
        ok = funzione(src, dst,
                      leggi_tempo(getattr(args, 'da', None)),
                      leggi_tempo(getattr(args, 'durata', None)),
                      getattr(args, 'fps', GIF_FPS),
                      getattr(args, 'larghezza', GIF_LARGHEZZA))

    elif azione == 'provino':
        griglia = getattr(args, 'griglia', f'{PROVINO_COLONNE}x{PROVINO_RIGHE}')
        m = re.fullmatch(r'(\d+)\s*[x×]\s*(\d+)', griglia.strip())
        if not m:
            console.print(t('error.bad_grid', valore=escape(griglia)))
            sys.exit(1)
        colonne, righe = int(m.group(1)), int(m.group(2))
        dst = (os.path.abspath(esplicito) if esplicito
               else _nome_uscita(src, 'ClipDex provino', '.png'))
        ok = provino(src, dst, righe, colonne)

    else:   # compat
        dst = (os.path.abspath(esplicito) if esplicito
               else _nome_uscita(src, 'ClipDex compat', '.mp4'))
        ok = compat(src, dst, crf=args.crf)

    console.print()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
