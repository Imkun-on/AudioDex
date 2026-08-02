"""PixDex — rimasterizzatore video per i download di AudioDex.

A cosa serve
    Ripulire un video di qualita' scarsa: togliere i difetti lasciati dalla
    compressione, appianare le sfumature a scalini, e portarlo a una
    risoluzione piu' alta con un ingrandimento fatto bene.

Cosa NON fa (ed e' importante saperlo)

    Non inventa dettaglio che nel file non c'e'. Un ingrandimento, per quanto
    curato, non puo' ricostruire quello che la compressione ha buttato via:
    quello lo fanno i modelli AI, che ricostruiscono un dettaglio *plausibile*
    ma inventato. Qui si lavora in sottrazione — si toglie il disturbo, non si
    aggiunge finta incisione — ed e' il motivo per cui il risultato regge
    anche a schermo intero, dove l'AI spesso tradisce.

Perche' funziona lo stesso
    Su materiale YouTube i difetti che l'occhio nota davvero sono tre, e sono
    tutti rimovibili: i quadretti (blocking) nelle scene scure e nei
    movimenti rapidi, le bande a scalini nei cieli e nelle dissolvenze, e
    l'alone sporco intorno ai contorni. Tolti quelli, la stessa identica
    quantita' di dettaglio si legge molto meglio.

L'ordine dei filtri non e' negoziabile
    1. deinterlacciamento, se serve: lavorare su semiquadri falsa tutto il resto;
    2. sblocco e riduzione del disturbo, *prima* di ogni nitidezza — altrimenti
       si incide il disturbo e lo si rende permanente;
    3. sbandatura, svolta a 10 bit: a 8 bit il rimedio genera bande nuove;
    4. ingrandimento, su un fotogramma ormai pulito;
    5. nitidezza adattiva, per ultima: applicarla prima di ingrandire
       significa buttare via meta' del lavoro nella riscalatura.

Come e' organizzato il file
    1. banner e presentazione Rich condivisa con AudioDex e BurnDex;
    2. lettura delle caratteristiche del file con ffprobe;
    3. diagnosi dei difetti e scelta del preset consigliato;
    4. costruzione della catena di filtri;
    5. esecuzione con barra di avanzamento e confronto prima/dopo;
    6. ``main()`` con la procedura guidata.

Nota sulla portabilita'
    Serve solo FFmpeg, quindi gira ovunque: a differenza di BurnDex non e'
    legato a Windows. Se e' presente una GPU AMD, ``--gpu`` usa il suo
    codificatore hardware.
"""
from __future__ import annotations

import argparse
import json
import os
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
from Shared.strings_pixdex import TESTI

# Stessa convenzione degli altri due strumenti: le frasi mostrate all'utente
# stanno tutte nel catalogo, commenti e log su file restano in italiano.
i18n.register(TESTI)
t = i18n.t

log = setup_logger('pixdex', 'pixdex.log')


# Larghezza condivisa con AudioDex e BurnDex: i tre strumenti stampano
# riquadri della stessa misura, cosi' l'output sembra un programma solo.
LARGHEZZA = 68


def _print_banner() -> None:
    """Stampa il banner ASCII colorato 'PixDex' all'avvio del programma.

    Stesse tinte e stesso riquadro doppio di AudioDex e BurnDex: chi apre il
    terminale capisce a colpo d'occhio che e' lo stesso progetto.
    """
    banner_lines = [
        r'    ____  _      ____           ',
        r'   / __ \(_)  __/ __ \___  _  __',
        r'  / /_/ / / |/_/ / / / _ \| |/_/',
        r' / ____/ />  </ /_/ /  __/>  <  ',
        r'/_/   /_/_/|_/_____/\___/_/|_|  ',
    ]
    colors = ['bright_magenta', 'magenta', 'bright_blue', 'blue', 'bright_cyan', 'cyan']
    text = Text()
    for i, line in enumerate(banner_lines):
        text.append(line + '\n', style=Style(color=colors[i % len(colors)], bold=True))
    text.append('\n' + t('banner.subtitle'), style=Style(color='white', bold=True))
    text.append('  ·  ', style='dim')
    text.append(t('banner.tagline'), style='dim')

    console.print()
    console.print(Panel(
        Align.center(text),
        border_style='bright_blue',
        box=DOUBLE,
        padding=(1, 2),
        width=LARGHEZZA,
    ))


def _passo(numero: int, totale: int, titolo: str) -> None:
    """Riga di separazione che annuncia il passo corrente della procedura."""
    console.print()
    console.print(Rule(
        Text.assemble(
            (t('step.label', n=numero, tot=totale),
             Style(color='black', bgcolor='bright_blue', bold=True)),
            ('  ', ''),
            (titolo.upper(), Style(color='bright_blue', bold=True)),
            ('  ', ''),
        ),
        style='bright_blue',
        align='left',
    ), width=LARGHEZZA)


def _progress() -> Progress:
    """Barra di avanzamento della rimasterizzazione.

    Tiene il tempo rimanente oltre a quello trascorso: una codifica lunga
    senza stima e' indistinguibile da una bloccata, e la differenza conta
    quando si tratta di ore.
    """
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
    """Legge una risposta dal terminale trattando Ctrl-C come rinuncia."""
    try:
        return console.input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return ''


# ── Estensioni video riconosciute ────────────────────────────────────────────
# Solo contenitori che possono trasportare un flusso video: i file di solo
# audio prodotti da AudioDex non hanno niente da rimasterizzare.
VIDEO_EXTS = frozenset({'.mp4', '.mkv', '.webm', '.avi', '.mov', '.m4v',
                        '.flv', '.wmv', '.mpg', '.mpeg', '.ts', '.m2ts'})

# ── Scala delle risoluzioni ──────────────────────────────────────────────────
# L'ingrandimento non va oltre il doppio: sopra quella soglia l'interpolazione
# non ha piu' pixel veri da cui partire e restituisce un'immagine molle, che
# poi la nitidezza puo' solo peggiorare. Meglio un 720p onesto di un 4K finto.
SCALA_ALTEZZE = (480, 720, 1080, 1440, 2160)
MAX_FATTORE_UPSCALE = 2.0

# Modalita' di ingrandimento offerte per nome, sia a schermo che con --height.
# ``None`` significa "decidi tu": e' l'automatico, che si ferma al doppio.
# Le altre sono richieste esplicite, e vengono rispettate anche quando la
# sorgente non le giustifica — ma non in silenzio: la tabella di scelta dice
# apertamente quando un 4K sarebbe solo un 360p gonfiato.
MODI_QUALITA: dict[str, int | None] = {
    'auto': None,
    'none': 0,      # nessun ingrandimento: solo pulizia, alla risoluzione nativa
    'hd': 1080,
    '2k': 1440,
    '4k': 2160,
}

# Soglie del giudizio sul fattore di ingrandimento. Fino al doppio
# l'interpolazione ha abbastanza pixel veri da cui partire; fino al triplo il
# risultato regge ma si ammorbidisce; oltre, si sta solo scrivendo un numero
# piu' grande nei metadati del file.
FATTORE_BUONO = 2.0
FATTORE_MOLLE = 3.0

# Sotto questa densita' di bit per pixel il file e' compresso al punto che i
# quadretti si vedono: 0.05 bpp e' la soglia empirica sotto cui YouTube inizia
# a lasciare artefatti visibili anche a un occhio non allenato.
BPP_COMPRESSO = 0.05
BPP_MOLTO_COMPRESSO = 0.025

# Qualita' di default per libx264: 18 e' il punto in cui la differenza dal
# sorgente smette di essere visibile a occhio, senza gonfiare il file come
# farebbe un valore piu' basso.
CRF_DEFAULT = 18


def _check_ffmpeg() -> bool:
    """Verifica che ffmpeg e ffprobe siano raggiungibili nel PATH."""
    mancanti = [nome for nome in ('ffmpeg', 'ffprobe') if not shutil.which(nome)]
    if mancanti:
        console.print(t('tools.no_ffmpeg', tools=', '.join(mancanti)))
        console.print(t('tools.install_ffmpeg'))
        return False
    return True


def _fps(valore: str | None) -> float:
    """Converte una frequenza fotogrammi in forma 'num/den' in un numero.

    ffprobe restituisce i frame rate come frazione esatta ('30000/1001' per i
    29.97 fps del NTSC): valutarla come divisione invece di leggere il numero
    approssimato evita che il conteggio dei fotogrammi si scosti su un video
    lungo.
    """
    if not valore:
        return 0.0
    try:
        if '/' in valore:
            num, den = valore.split('/', 1)
            den_f = float(den)
            return float(num) / den_f if den_f else 0.0
        return float(valore)
    except (ValueError, ZeroDivisionError):
        return 0.0


def probe(path: str) -> dict | None:
    """Legge le caratteristiche del video con ffprobe.

    Restituisce un dizionario con risoluzione, fotogrammi al secondo, codec,
    bitrate, durata e formato dei pixel, oppure None se il file non contiene
    un flusso video leggibile.
    """
    try:
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-print_format', 'json',
             '-show_format', '-show_streams', path],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', check=True,
        ).stdout
        dati = json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError) as exc:
        log.warning('ffprobe fallito su %s: %s', path, exc)
        return None

    video = next((s for s in dati.get('streams', [])
                  if s.get('codec_type') == 'video'), None)
    if not video:
        return None

    formato = dati.get('format', {})
    durata = float(formato.get('duration') or video.get('duration') or 0.0)
    fps = _fps(video.get('avg_frame_rate')) or _fps(video.get('r_frame_rate'))

    # Il bitrate del solo flusso video spesso manca nei file WebM: in quel
    # caso si ricava dalla dimensione totale, che lo sovrastima di quanto pesa
    # l'audio. E' un'approssimazione accettabile perche' serve solo a decidere
    # quanto e' compresso il video, non a rifare i conti dell'encoder.
    bitrate = int(video.get('bit_rate') or 0)
    dimensione = int(formato.get('size') or 0)
    if not bitrate and durata > 0 and dimensione:
        bitrate = int(dimensione * 8 / durata)

    larghezza = int(video.get('width') or 0)
    altezza = int(video.get('height') or 0)

    # Fotogrammi totali: il campo dichiarato non c'e' quasi mai nei file
    # scaricati, quindi si stima da durata e frequenza. Serve solo alla barra
    # di avanzamento, dove un errore dell'uno per cento non si nota.
    frames = int(video.get('nb_frames') or 0)
    if not frames and durata and fps:
        frames = int(durata * fps)

    return {
        'path': path,
        'width': larghezza,
        'height': altezza,
        'fps': fps,
        'codec': video.get('codec_name') or '?',
        'pix_fmt': video.get('pix_fmt') or '?',
        'bitrate': bitrate,
        'duration': durata,
        'size': dimensione,
        'frames': frames,
        # field_order diverso da 'progressive' significa semiquadri: materiale
        # televisivo o riversato da nastro, che va deinterlacciato prima di
        # qualunque altra cosa.
        'interlaced': (video.get('field_order') or 'progressive') not in
                      ('progressive', 'unknown'),
        'bpp': (bitrate / (larghezza * altezza * fps)
                if larghezza and altezza and fps and bitrate else 0.0),
    }


def _fmt_durata(secondi: float) -> str:
    """Formatta una durata in h:mm:ss oppure m:ss se sta sotto l'ora."""
    secondi = int(secondi)
    ore, resto = divmod(secondi, 3600)
    minuti, sec = divmod(resto, 60)
    return f'{ore}:{minuti:02d}:{sec:02d}' if ore else f'{minuti}:{sec:02d}'


def _fmt_dimensione(byte: int) -> str:
    """Formatta una dimensione in MB o GB, con una cifra decimale."""
    mb = byte / (1024 * 1024)
    return f'{mb / 1024:.2f} GB' if mb >= 1024 else f'{mb:.1f} MB'


def _pannello_sorgente(info: dict) -> None:
    """Mostra la carta d'identita' del file di partenza.

    Serve a rendere evidente il tetto invalicabile del lavoro: se la sorgente
    e' 360p, nessun preset produrra' un vero 1080p, e vederlo scritto prima di
    partire evita l'aspettativa sbagliata.
    """
    tab = Table(box=ROUNDED, show_header=False, border_style='grey37',
                width=LARGHEZZA, padding=(0, 1))
    tab.add_column(style='dim_label', no_wrap=True, width=22)
    tab.add_column(style='white')

    tab.add_row(t('info.file'), escape(os.path.basename(info['path'])))
    tab.add_row(t('info.resolution'), f"{info['width']} × {info['height']}")
    tab.add_row(t('info.fps'), f"{info['fps']:.2f}")
    tab.add_row(t('info.codec'), f"{info['codec']}  ({info['pix_fmt']})")
    tab.add_row(t('info.bitrate'), f"{info['bitrate'] / 1000:.0f} kbit/s")
    tab.add_row(t('info.duration'), _fmt_durata(info['duration']))
    tab.add_row(t('info.size'), _fmt_dimensione(info['size']))
    if info['interlaced']:
        tab.add_row(t('info.scan'), t('info.interlaced'))

    console.print()
    console.print(Panel(tab, title=t('info.title'), title_align='left',
                        border_style='bright_blue', box=ROUNDED,
                        width=LARGHEZZA, padding=(0, 0)))


def diagnosi(info: dict) -> tuple[list[str], str]:
    """Elenca i difetti rilevati e restituisce il preset consigliato.

    La diagnosi guarda tre grandezze: la risoluzione (dice se ha senso
    ingrandire), i bit per pixel (dicono quanto la compressione ha
    infierito) e l'ordine dei campi (dice se il materiale e' televisivo).
    Nessuna di queste richiede di decodificare il video, quindi il consiglio
    e' istantaneo anche su file da un'ora.
    """
    problemi: list[str] = []
    preset = 'standard'

    if info['interlaced']:
        problemi.append(t('diag.interlaced'))
        preset = 'vecchio'

    if info['height'] and info['height'] <= 480:
        problemi.append(t('diag.lowres', h=info['height']))

    bpp = info['bpp']
    if bpp and bpp < BPP_MOLTO_COMPRESSO:
        problemi.append(t('diag.very_compressed', bpp=f'{bpp:.3f}'))
        if preset != 'vecchio':
            preset = 'forte'
    elif bpp and bpp < BPP_COMPRESSO:
        problemi.append(t('diag.compressed', bpp=f'{bpp:.3f}'))

    # Un formato pixel a 8 bit e' la norma, ma e' anche la causa delle bande
    # nelle sfumature: vale la pena dirlo perche' e' esattamente il difetto
    # che la lavorazione a 10 bit va a sanare.
    if info['pix_fmt'].startswith('yuv420p') and '10' not in info['pix_fmt']:
        problemi.append(t('diag.banding_risk'))

    if not problemi:
        problemi.append(t('diag.clean'))
        preset = 'pulito'

    return problemi, preset


def _pannello_diagnosi(problemi: list[str], consigliato: str) -> None:
    """Mostra i difetti rilevati e il preset che li affronta."""
    corpo = Text()
    for p in problemi:
        corpo.append('  • ', style='bright_blue')
        corpo.append(p + '\n', style='white')
    corpo.append('\n')
    corpo.append('  ' + t('diag.suggested') + ' ', style='dim')
    corpo.append(PRESETS[consigliato]['nome'](), style='bold bright_green')

    console.print()
    console.print(Panel(corpo, title=t('diag.title'), title_align='left',
                        border_style='bright_blue', box=ROUNDED,
                        width=LARGHEZZA, padding=(0, 1)))


# ── Preset di rimasterizzazione ──────────────────────────────────────────────
#
# Ogni preset e' una funzione che, viste le caratteristiche del file,
# restituisce la lista dei filtri FFmpeg da applicare *prima* della
# riscalatura. La riscalatura e la nitidezza finale le aggiunge
# ``catena_filtri``, perche' il loro posto nell'ordine e' sempre lo stesso.
#
# Sui parametri di hqdn3d: i quattro numeri sono luma spaziale, croma
# spaziale, luma temporale, croma temporale. Il temporale e' il piu'
# efficace sul disturbo da compressione, che cambia a ogni fotogramma,
# ed e' anche il piu' pericoloso: alzato troppo lascia scie dietro
# agli oggetti in movimento. Per questo resta sempre moderato.


# ── Come e' tarata la sbandatura ─────────────────────────────────────────────
#
# ``deband`` non appiattisce i gradini: li dissolve in rumore, come fa il
# dithering. E' il modo giusto di togliere una banda vera, perche' un contorno
# visibile viene barattato con una granulosita' che l'occhio non nota. Ma il
# filtro lavora su tutto il fotogramma, comprese le zone piatte dove banda non
# ce n'e': li' non c'e' niente da barattare e resta solo il rumore.
#
# Misurato su un video molto compresso (AV1 a 305 kbit/s, 720p -> 1440p), nella
# stessa parete scura uniforme:
#
#     taratura                    granulosita'   quadretti
#     solo ingrandimento              0.805        1.618
#     1thr 0.035 range 24 cas 0.55    2.686        1.204
#     1thr 0.010 range 16 cas 0.35    1.581        1.166
#
# La taratura prudente vince su *entrambi* i fronti: meno rumore e anche meno
# quadretti. Quella aggressiva non comprava niente — sporcava e basta, e il
# file finiva per pesare il triplo perche' l'encoder spendeva bit per
# descrivere quel puntinato. Da qui le soglie basse che si vedono sotto.


def _f_pulito(_info: dict) -> list[str]:
    """Sorgente gia' discreta: si toglie solo la sporcizia della compressione."""
    return [
        'deblock=filter=weak:block=4',
        'deband=1thr=0.008:2thr=0.008:3thr=0.008:4thr=0.008:range=16:blur=1',
    ]


def _f_standard(_info: dict) -> list[str]:
    """Il caso normale di un video YouTube: quadretti, aloni, bande."""
    return [
        'deblock=filter=weak:block=4',
        'hqdn3d=1.5:1.2:4:3',
        'deband=1thr=0.010:2thr=0.010:3thr=0.010:4thr=0.010:range=16:blur=1',
    ]


def _f_forte(_info: dict) -> list[str]:
    """Sorgente molto rovinata: si accetta di perdere un po' di micro-dettaglio.

    ``atadenoise`` media i fotogrammi vicini solo dove non c'e' movimento:
    e' il filtro giusto contro il disturbo da compressione, che salta da un
    fotogramma all'altro mentre l'immagine vera resta ferma.
    """
    return [
        'deblock=filter=strong:block=4',
        'atadenoise=0a=0.02:1a=0.02:2a=0.02:s=9',
        'hqdn3d=3:2.5:6:4.5',
        'deband=1thr=0.010:2thr=0.010:3thr=0.010:4thr=0.010:range=16:blur=1',
    ]


def _f_animazione(_info: dict) -> list[str]:
    """Cartoni e anime: linee nette e campiture piatte, regole opposte.

    Qui il disturbo va tolto con la mano leggerissima — la riduzione del
    rumore mangia le linee sottili, che nell'animazione *sono* il disegno —
    mentre la sbandatura va spinta, perche' le grandi campiture di colore
    uniforme sono proprio dove le bande si vedono di piu'.
    """
    return [
        'deblock=filter=weak:block=4',
        'hqdn3d=1:0.8:2:2',
        'deband=1thr=0.020:2thr=0.020:3thr=0.020:4thr=0.020:range=24:blur=1',
    ]


def _f_vecchio(_info: dict) -> list[str]:
    """Materiale televisivo o da nastro: prima si separano i semiquadri.

    ``bwdif`` in modalita' send_frame produce un fotogramma progressivo per
    ogni coppia di semiquadri, mantenendo la frequenza originale: raddoppiarla
    con send_field darebbe un movimento piu' fluido ma un file doppio, che su
    materiale d'archivio non ripaga.
    """
    return [
        'bwdif=mode=send_frame:parity=auto:deint=all',
        'deblock=filter=strong:block=4',
        'hqdn3d=4:3:6:4.5',
        'deband=1thr=0.012:2thr=0.012:3thr=0.012:4thr=0.012:range=16:blur=1',
    ]


PRESETS: dict[str, dict] = {
    'pulito': {
        'nome': lambda: t('preset.pulito.name'),
        'desc': lambda: t('preset.pulito.desc'),
        'filtri': _f_pulito,
        'sharpen': 0.20,
        'upscale': False,
    },
    'standard': {
        'nome': lambda: t('preset.standard.name'),
        'desc': lambda: t('preset.standard.desc'),
        'filtri': _f_standard,
        'sharpen': 0.30,
        'upscale': True,
    },
    'forte': {
        'nome': lambda: t('preset.forte.name'),
        'desc': lambda: t('preset.forte.desc'),
        'filtri': _f_forte,
        'sharpen': 0.35,
        'upscale': True,
    },
    'animazione': {
        'nome': lambda: t('preset.animazione.name'),
        'desc': lambda: t('preset.animazione.desc'),
        'filtri': _f_animazione,
        'sharpen': 0.45,
        'upscale': True,
    },
    'vecchio': {
        'nome': lambda: t('preset.vecchio.name'),
        'desc': lambda: t('preset.vecchio.desc'),
        'filtri': _f_vecchio,
        'sharpen': 0.30,
        'upscale': True,
    },
}


def altezza_obiettivo(info: dict, richiesta: int | None, preset: str) -> int:
    """Decide a che altezza portare il video.

    Senza indicazione esplicita sale al gradino successivo della scala
    standard, ma mai oltre il doppio dell'originale: il limite e' quello che
    separa un ingrandimento credibile da un'immagine gonfia e molle.
    """
    h = info['height']
    if not h:
        return 0
    if richiesta is not None:
        # Zero e' la richiesta esplicita di non ingrandire ("solo pulizia"):
        # va distinta da "nessuna richiesta", che invece lascia decidere qui.
        # Trattarle allo stesso modo — come farebbe un banale ``if richiesta``
        # — riporterebbe l'automatico proprio a chi ha chiesto di non toccare
        # la risoluzione.
        return richiesta if richiesta > 0 else h
    if not PRESETS[preset]['upscale']:
        return h

    tetto = int(h * MAX_FATTORE_UPSCALE)
    candidati = [a for a in SCALA_ALTEZZE if h < a <= tetto]
    return candidati[-1] if candidati else h


def risolvi_altezza(valore: str | None) -> int | None:
    """Traduce il valore di ``--height`` in un'altezza in pixel.

    Accetta sia i nomi (``auto``, ``hd``, ``2k``, ``4k``, ``none``) sia un
    numero. I nomi esistono perche' nessuno ragiona in "millequaranta pixel di
    altezza": si ragiona in "HD" e "4K", ed e' giusto che il programma parli
    la stessa lingua di chi lo usa. ``None`` significa automatico.
    """
    if valore is None:
        return None
    chiave = valore.strip().lower()
    if chiave in MODI_QUALITA:
        return MODI_QUALITA[chiave]
    try:
        altezza = int(chiave.rstrip('p'))
    except ValueError:
        return None
    return altezza if altezza > 0 else None


def _fattore(info: dict, altezza: int) -> float:
    """Di quante volte l'immagine viene ingrandita in altezza."""
    h = info['height']
    return (altezza / h) if h and altezza else 1.0


def _giudizio_fattore(fattore: float) -> tuple[str, str]:
    """Restituisce (colore, chiave del commento) per un fattore di ingrandimento.

    E' il cuore dell'onesta' di questa schermata: la stessa tabella che offre
    il 4K dice anche, sulla stessa riga, che da un 360p il 4K non aggiunge
    un solo dettaglio vero.
    """
    if fattore <= 1.0:
        return 'bright_green', 'quality.note_native'
    if fattore <= FATTORE_BUONO:
        return 'bright_green', 'quality.note_ok'
    if fattore <= FATTORE_MOLLE:
        return 'yellow', 'quality.note_soft'
    return 'red', 'quality.note_fake'


def _scegli_qualita(info: dict, preset: str) -> int | None:
    """Fa scegliere a che risoluzione portare il video.

    Mostra per ogni modalita' il risultato concreto su *questo* file — non
    l'etichetta commerciale — con il fattore di ingrandimento e un giudizio.
    Vedere scritto "360p → 2160p, 6.00×, nessun dettaglio in piu'" accanto
    alla voce 4K vale piu' di qualsiasi avvertenza in un manuale.

    Restituisce l'altezza scelta, oppure None se si rinuncia.
    """
    automatica = altezza_obiettivo(info, None, preset)

    voci: list[tuple[str, int]] = [
        ('quality.auto', automatica),
        ('quality.none', info['height']),
        ('quality.hd', 1080),
        ('quality.2k', 1440),
        ('quality.4k', 2160),
    ]

    # Le larghezze sono fissate a mano perche' la somma deve stare nei 68
    # caratteri comuni a tutto il progetto: lasciate libere, la colonna del
    # commento si stringe fino a spezzare le parole a meta'.
    tab = Table(box=HEAVY_HEAD, border_style='grey37', width=LARGHEZZA,
                header_style='bold bright_blue', padding=(0, 1))
    tab.add_column('#', justify='right', width=2, style='dim')
    tab.add_column(t('quality.col_mode'), width=14, no_wrap=True)
    tab.add_column(t('quality.col_result'), width=21, justify='right')
    tab.add_column(t('quality.col_note'), width=18, no_wrap=True)

    for i, (chiave, altezza) in enumerate(voci, 1):
        fattore = _fattore(info, altezza)
        colore, nota = _giudizio_fattore(fattore)
        etichetta = t(chiave)
        if chiave == 'quality.auto':
            etichetta = '★ ' + etichetta
        risultato = (f"{info['height']}p → [bold]{altezza}p[/bold]  "
                     f'[{colore}]{fattore:.2f}×[/{colore}]'
                     if altezza != info['height']
                     else f"[bold]{altezza}p[/bold]  [{colore}]{fattore:.2f}×[/{colore}]")
        tab.add_row(str(i), f'[{colore}]{etichetta}[/{colore}]', risultato,
                    f'[{colore}]{t(nota)}[/{colore}]')

    tab.add_row(str(len(voci) + 1), t('quality.custom'), '', '')

    console.print()
    console.print(tab)
    console.print(t('quality.hint'))

    risposta = _chiedi(t('quality.prompt'))
    if not risposta:
        return automatica
    if not risposta.isdigit():
        console.print(t('quality.invalid'))
        return automatica

    scelta = int(risposta)
    if 1 <= scelta <= len(voci):
        return voci[scelta - 1][1]
    if scelta == len(voci) + 1:
        libera = _chiedi(t('quality.custom_prompt'))
        altezza = risolvi_altezza(libera)
        if altezza:
            return altezza
        console.print(t('quality.invalid'))
        return automatica

    console.print(t('quality.invalid'))
    return automatica


def catena_filtri(preset: str, info: dict, altezza: int) -> str:
    """Compone la catena di filtri completa, nell'ordine corretto.

    Il passaggio a 10 bit in testa e il ritorno a 8 bit in coda non sono un
    vezzo: la sbandatura funziona sostituendo i gradini con una rampa, e una
    rampa ha bisogno di valori intermedi che a 8 bit semplicemente non
    esistono. Lavorare a 10 bit e scendere solo alla fine e' quello che
    distingue una sfumatura pulita da una che ha solo bande diverse.
    """
    catena: list[str] = ['format=yuv420p10le']
    catena += PRESETS[preset]['filtri'](info)

    if altezza and altezza != info['height']:
        catena.append(f'scale=-2:{altezza}:flags=lanczos')

    # La nitidezza adattiva viene per ultima e va dosata: ``cas`` alza il
    # contrasto locale solo dove trova gia' un contorno, quindi non rimarca
    # il disturbo nelle zone piatte come farebbe una maschera di contrasto
    # tradizionale.
    forza = PRESETS[preset]['sharpen']
    if forza > 0:
        catena.append(f'cas={forza}')

    catena.append('format=yuv420p')
    return ','.join(catena)


def _comando_encoder(gpu: bool, crf: int) -> list[str]:
    """Restituisce gli argomenti del codificatore video.

    Il codificatore hardware AMD e' molto piu' veloce ma, a parita' di peso,
    restituisce un'immagine meno pulita: su una rimasterizzazione, dove il
    punto e' proprio la qualita', il software resta il default e l'hardware
    e' una scelta consapevole per i file lunghi.
    """
    if gpu:
        return ['-c:v', 'h264_amf', '-quality', 'quality',
                '-rc', 'cqp', '-qp_i', '20', '-qp_p', '22', '-qp_b', '24']
    return ['-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf)]


def _pannello_piano(info: dict, preset: str, altezza: int,
                    catena: str, gpu: bool, crf: int, dst: str) -> None:
    """Mostra cosa verra' fatto, prima di farlo.

    Una rimasterizzazione dura minuti od ore: vedere prima la catena di
    filtri e la risoluzione d'arrivo permette di correggere una scelta
    sbagliata subito, invece di scoprirla a lavoro finito.
    """
    tab = Table(box=ROUNDED, show_header=False, border_style='grey37',
                width=LARGHEZZA, padding=(0, 1))
    tab.add_column(style='dim_label', no_wrap=True, width=22)
    tab.add_column(style='white', overflow='fold')

    tab.add_row(t('plan.preset'), f"[bold bright_green]{PRESETS[preset]['nome']()}[/]")
    tab.add_row('', f"[dim]{PRESETS[preset]['desc']()}[/dim]")
    if altezza and altezza != info['height']:
        fattore = _fattore(info, altezza)
        colore, nota = _giudizio_fattore(fattore)
        tab.add_row(t('plan.resolution'),
                    f"{info['height']}p [dim]→[/dim] [bold]{altezza}p[/bold]"
                    f"  [{colore}]{fattore:.2f}×[/{colore}]")
        # L'avviso compare solo quando serve, e dice cosa aspettarsi invece di
        # limitarsi a sconsigliare: chi ha scelto il 4K sapendo cosa fa deve
        # poter tirare dritto senza sentirsi rimproverare a ogni lancio.
        if fattore > FATTORE_BUONO:
            tab.add_row('', f'[{colore}]{t(nota)}[/{colore}]')
    else:
        tab.add_row(t('plan.resolution'), f"{info['height']}p  [dim]({t('plan.no_upscale')})[/dim]")
    tab.add_row(t('plan.encoder'),
                'h264_amf  [dim](GPU AMD)[/dim]' if gpu
                else f'libx264  [dim](CRF {crf})[/dim]')
    tab.add_row(t('plan.audio'), t('plan.audio_copy'))
    tab.add_row(t('plan.output'), escape(os.path.basename(dst)))
    tab.add_row(t('plan.filters'), f'[dim]{escape(catena)}[/dim]')

    console.print()
    console.print(Panel(tab, title=t('plan.title'), title_align='left',
                        border_style='bright_blue', box=ROUNDED,
                        width=LARGHEZZA, padding=(0, 0)))


def _scorri_progresso(proc, su_fotogramma, su_velocita) -> bool:
    """Legge l'avanzamento di FFmpeg e lo inoltra a due callback.

    L'avanzamento arriva da ``-progress pipe:1``, che stampa coppie
    chiave=valore a intervalli regolari: e' l'unico modo affidabile di sapere
    a che fotogramma e' arrivato, perche' l'output normale di FFmpeg usa
    ritorni a capo che non si leggono riga per riga.

    Restituisce False se l'utente ha interrotto: separare la lettura dal modo
    in cui l'avanzamento viene mostrato e' quello che permette alla stessa
    funzione di alimentare tanto la barra Rich del terminale quanto quella
    della finestra grafica.
    """
    try:
        for riga in proc.stdout:
            riga = riga.strip()
            if riga.startswith('frame='):
                try:
                    su_fotogramma(int(riga.split('=', 1)[1]))
                except ValueError:
                    continue
            elif riga.startswith('speed='):
                su_velocita(riga.split('=', 1)[1].strip())
    except KeyboardInterrupt:
        proc.terminate()
        return False
    finally:
        proc.stdout.close()
    return True


def rimasterizza(info: dict, dst: str, catena: str, gpu: bool, crf: int,
                  avanzamento=None) -> bool:
    """Esegue FFmpeg mostrando l'avanzamento, restituisce True se ha funzionato.

    Con ``avanzamento`` valorizzato — e' il caso della GUI — le notifiche
    vanno a quella funzione, che riceve ``(fotogramma, totale, velocita)``, e
    a terminale non si stampa nulla. Senza, si disegna la solita barra Rich.
    """
    totale = info['frames'] or 0

    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y',
           '-i', info['path'],
           '-vf', catena,
           *_comando_encoder(gpu, crf),
           '-c:a', 'copy',
           '-movflags', '+faststart',
           '-progress', 'pipe:1', '-nostats',
           dst]
    log.info('Comando FFmpeg: %s', ' '.join(cmd))

    # Lo standard error finisce su file: se restasse in una pipe non letta,
    # una diagnostica lunga riempirebbe il buffer del sistema operativo e
    # bloccherebbe FFmpeg a meta' lavoro, senza alcun messaggio.
    with tempfile.TemporaryFile(mode='w+', encoding='utf-8',
                                errors='replace') as err:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err,
                                text=True, encoding='utf-8', errors='replace',
                                bufsize=1)

        if avanzamento is not None:
            velocita = ['']

            def _frame(n: int) -> None:
                avanzamento(n, totale, velocita[0])

            def _speed(v: str) -> None:
                velocita[0] = v

            completato = _scorri_progresso(proc, _frame, _speed)
        else:
            with _progress() as prog:
                task = prog.add_task(t('run.working'),
                                     total=totale or None, extra='')
                completato = _scorri_progresso(
                    proc,
                    lambda n: prog.update(
                        task, completed=min(n, totale) if totale else n),
                    lambda v: prog.update(task, extra=v),
                )

        if not completato:
            console.print(t('run.interrupted'))
            return False

        codice = proc.wait()
        if codice != 0:
            err.seek(0)
            dettaglio = err.read().strip().splitlines()
            ultima = dettaglio[-1] if dettaglio else f'exit {codice}'
            log.error('FFmpeg fallito (%s): %s', codice, ultima)
            console.print(t('run.failed', reason=escape(ultima)))
            return False

    return True


def confronto(src: str, dst: str, destinazione: str,
               istante: float) -> str | None:
    """Salva un PNG con lo stesso fotogramma prima e dopo, affiancati.

    E' l'unico modo onesto di giudicare il risultato: i numeri di bitrate non
    dicono nulla sull'aspetto, e il confronto a memoria fra due riproduzioni
    successive inganna sempre in favore della seconda. I due fotogrammi sono
    portati alla stessa altezza perche' altrimenti l'ingrandimento renderebbe
    il secondo automaticamente piu' grande, e quindi piu' convincente a
    prescindere dal merito.
    """
    filtro = ('[0:v]scale=-2:540:flags=lanczos,setsar=1[a];'
              '[1:v]scale=-2:540:flags=lanczos,setsar=1[b];'
              '[a][b]hstack=inputs=2')
    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y',
           '-ss', str(istante), '-i', src,
           '-ss', str(istante), '-i', dst,
           '-filter_complex', filtro, '-frames:v', '1', destinazione]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except (subprocess.CalledProcessError, OSError) as exc:
        log.warning('Confronto non riuscito: %s', exc)
        return None
    return destinazione if os.path.exists(destinazione) else None


def _pannello_risultato(info: dict, dst: str, confronto: str | None) -> None:
    """Riepilogo finale: cosa e' cambiato e dove trovare i file."""
    nuovo = probe(dst)
    tab = Table(box=ROUNDED, show_header=False, border_style='grey37',
                width=LARGHEZZA, padding=(0, 1))
    tab.add_column(style='dim_label', no_wrap=True, width=22)
    tab.add_column(style='white', overflow='fold')

    if nuovo:
        tab.add_row(t('result.resolution'),
                    f"{info['width']}×{info['height']}  [dim]→[/dim]  "
                    f"[bold]{nuovo['width']}×{nuovo['height']}[/bold]")
        delta = nuovo['size'] - info['size']
        segno = '+' if delta >= 0 else '−'
        tab.add_row(t('result.size'),
                    f"{_fmt_dimensione(info['size'])}  [dim]→[/dim]  "
                    f"[bold]{_fmt_dimensione(nuovo['size'])}[/bold]"
                    f"  [dim]({segno}{_fmt_dimensione(abs(delta))})[/dim]")
    tab.add_row(t('result.file'), escape(dst))
    if confronto:
        tab.add_row(t('result.compare'), escape(confronto))
        tab.add_row('', f"[dim]{t('result.compare_hint')}[/dim]")

    console.print()
    console.print(Panel(tab, title=f"{SYM_OK} {t('result.title')}",
                        title_align='left', border_style='bright_green',
                        box=ROUNDED, width=LARGHEZZA, padding=(0, 0)))


def _trova_video(base: str) -> list[str]:
    """Elenca i video presenti nella cartella dei download, piu' recenti prima."""
    trovati: list[str] = []
    for radice, _dirs, files in os.walk(base):
        for nome in files:
            if os.path.splitext(nome)[1].lower() in VIDEO_EXTS:
                trovati.append(os.path.join(radice, nome))
    trovati.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return trovati


def _scegli_video(base: str) -> str | None:
    """Fa scegliere un video fra quelli scaricati, o accetta un percorso.

    La cartella dei download e' il punto di partenza naturale — chi
    rimasterizza ha quasi sempre appena scaricato — ma incollare un percorso
    qualsiasi resta possibile, perche' il programma funziona su qualunque
    file video, non solo sui propri.
    """
    video = _trova_video(base) if os.path.isdir(base) else []

    if not video:
        console.print(t('choose.none', path=escape(base)))
        risposta = _chiedi(t('choose.ask_path'))
        return os.path.abspath(risposta.strip('"')) if risposta else None

    tab = Table(box=HEAVY_HEAD, border_style='grey37', width=LARGHEZZA,
                header_style='bold bright_blue')
    tab.add_column('#', justify='right', width=3, style='dim')
    tab.add_column(t('choose.col_file'), overflow='ellipsis', no_wrap=True)
    tab.add_column(t('choose.col_res'), justify='right', width=10)
    tab.add_column(t('choose.col_size'), justify='right', width=10)

    mostrati = video[:15]
    for i, path in enumerate(mostrati, 1):
        info = probe(path)
        risoluzione = f"{info['height']}p" if info and info['height'] else '?'
        tab.add_row(str(i), escape(os.path.basename(path)), risoluzione,
                    _fmt_dimensione(os.path.getsize(path)))

    console.print()
    console.print(tab)
    console.print(t('choose.hint'))

    risposta = _chiedi(t('choose.prompt'))
    if not risposta:
        return None
    if risposta.isdigit() and 1 <= int(risposta) <= len(mostrati):
        return mostrati[int(risposta) - 1]
    return os.path.abspath(risposta.strip('"'))


def nome_uscita(src: str, altezza: int, cartella: str | None) -> str:
    """Costruisce il nome del file rimasterizzato accanto all'originale.

    Il suffisso porta la risoluzione perche' e' l'unica cosa che si vuole
    sapere guardando la cartella mesi dopo, e l'originale non viene mai
    sovrascritto: una rimasterizzazione e' un'interpretazione, non una
    correzione, e la si rifa' volentieri con parametri diversi.
    """
    radice, _ext = os.path.splitext(src)
    if cartella:
        radice = os.path.join(cartella, os.path.basename(radice))
    return f'{radice} [PixDex {altezza}p].mp4'


def main() -> None:
    """Punto di ingresso: legge gli argomenti e avvia la procedura.

    Tre modalita' d'uso:
      - nessun argomento     -> interattiva, sceglie fra i video scaricati;
      - --input <file>       -> rimasterizza quel file;
      - --info --input <f>   -> analizza e consiglia, senza scrivere nulla.

    La risoluzione d'arrivo si sceglie al terzo passo, con una tabella che per
    ogni modalita' mostra il risultato su *questo* file e quanto vale davvero:
    da riga di comando la stessa scelta si fissa con --height auto|hd|2k|4k.

    Come negli altri due strumenti la lingua va fissata prima di costruire il
    parser, perche' i testi di --help vengono composti mentre il parser si crea.
    """
    # Da riga di comando si parla solo italiano: nessuna domanda all'avvio,
    # nessuna opzione da ricordare. Il catalogo bilingue resta intatto perche'
    # la GUI continua a offrire la scelta della lingua.
    i18n.set_language('it')

    parser = argparse.ArgumentParser(
        description=t('cli.desc'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=t('cli.epilog'),
    )
    parser.add_argument('--input', '-i', type=str, default=None,
                        help=t('cli.input'))
    parser.add_argument('--output', '-o', type=str, default=None,
                        help=t('cli.output'))
    parser.add_argument('--base', '-b', type=str,
                        default=os.path.join(_HERE, 'download_audio'),
                        help=t('cli.base'))
    parser.add_argument('--preset', '-p', type=str, default=None,
                        choices=sorted(PRESETS), help=t('cli.preset'))
    parser.add_argument('--height', type=str, default=None,
                        metavar='auto|none|hd|2k|4k|PIXEL',
                        help=t('cli.height'))
    parser.add_argument('--crf', type=int, default=CRF_DEFAULT,
                        help=t('cli.crf', default=CRF_DEFAULT))
    parser.add_argument('--gpu', action='store_true', help=t('cli.gpu'))
    parser.add_argument('--no-compare', action='store_true',
                        help=t('cli.no_compare'))
    parser.add_argument('--info', action='store_true', help=t('cli.info'))
    parser.add_argument('--yes', '-y', action='store_true', help=t('cli.yes'))

    args = parser.parse_args()

    _print_banner()

    if not _check_ffmpeg():
        sys.exit(1)

    # ── Passo 1: sorgente ───────────────────────────────────────────────────
    _passo(1, 5, t('step.source'))
    src = (os.path.abspath(args.input) if args.input
           else _scegli_video(os.path.abspath(args.base)))
    if not src:
        console.print(t('common.goodbye'))
        return
    if not os.path.isfile(src):
        console.print(t('common.file_missing', path=escape(src)))
        sys.exit(1)

    info = probe(src)
    if not info:
        console.print(t('probe.error', path=escape(os.path.basename(src))))
        sys.exit(1)

    _pannello_sorgente(info)

    # ── Passo 2: diagnosi ───────────────────────────────────────────────────
    _passo(2, 5, t('step.diagnosis'))
    problemi, consigliato = diagnosi(info)
    _pannello_diagnosi(problemi, consigliato)

    if args.info:
        console.print()
        return

    preset = args.preset or consigliato

    # ── Passo 3: risoluzione d'arrivo ───────────────────────────────────────
    # La scelta si chiede solo quando ha senso chiederla: se --height e' stato
    # passato la decisione e' gia' presa, e con --yes non c'e' nessuno davanti
    # allo schermo. In entrambi i casi vale l'automatico, che si ferma al
    # doppio ed e' l'unico valore difendibile senza aver visto il file.
    _passo(3, 5, t('step.quality'))
    richiesta = risolvi_altezza(args.height)
    if args.height is None and not args.yes:
        richiesta = _scegli_qualita(info, preset)
    altezza = altezza_obiettivo(info, richiesta, preset)

    catena = catena_filtri(preset, info, altezza)
    dst = os.path.abspath(args.output) if args.output else nome_uscita(
        src, altezza or info['height'], None)

    # ── Passo 4: conferma ───────────────────────────────────────────────────
    _passo(4, 5, t('step.plan'))
    _pannello_piano(info, preset, altezza, catena, args.gpu, args.crf, dst)

    if not args.yes:
        # L'invio a vuoto vale "procedi": a questo punto il piano e' gia' sotto
        # gli occhi e chi arriva qui ha gia' deciso. Le altre risposte passano
        # dal riconoscitore condiviso, che accetta si'/no in entrambe le lingue.
        risposta = _chiedi(t('confirm.proceed'))
        if risposta and not i18n.is_yes(risposta):
            console.print(t('common.cancelled'))
            return

    # ── Passo 4: lavorazione ────────────────────────────────────────────────
    _passo(5, 5, t('step.remaster'))
    console.print()
    if not rimasterizza(info, dst, catena, args.gpu, args.crf):
        sys.exit(1)

    png_confronto = None
    if not args.no_compare:
        # Il fotogramma di confronto si prende a un terzo del video: l'inizio
        # e' quasi sempre una sigla o una schermata nera, che non mostrerebbe
        # nessuna differenza.
        istante = max(info['duration'] / 3, 0.0)
        png_confronto = confronto(
            src, dst, os.path.splitext(dst)[0] + ' [confronto].png', istante)

    _pannello_risultato(info, dst, png_confronto)
    console.print()


if __name__ == '__main__':
    main()
