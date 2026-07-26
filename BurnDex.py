"""BurnDex — masterizzatore di CD audio per le raccolte di AudioDex.

A cosa serve
    Trasformare una cartella di brani in un CD audio vero, cioe' un disco
    conforme allo standard Red Book (CD-DA): tracce PCM a 44.1 kHz, 16 bit,
    stereo, senza file e senza metadati.

Perche' un CD audio e non un CD dati
    Copiare i file .m4a su un disco produce un CD dati, che solo i lettori
    recenti sanno decodificare. Il CD audio invece lo legge praticamente
    qualunque apparecchio, comprese le autoradio e gli stereo di venticinque
    anni fa. Il prezzo e' la rinuncia ai titoli sul display e il limite di
    circa 80 minuti.

Come scrive
    Attraverso IMAPI2, l'API COM nativa di Windows — la stessa che usano
    Esplora risorse e Windows Media Player. Non serve alcun programma di
    masterizzazione esterno: bastano pywin32 per il ponte verso COM e FFmpeg
    per decodificare l'audio in PCM.

Come e' organizzato il file
    1. costanti del formato Red Book e utilita' di conversione;
    2. presentazione Rich condivisa con AudioDex (passi, tabelle, barre);
    3. selezione della raccolta e ordinamento delle tracce;
    4. decodifica in PCM allineato al settore;
    5. ricognizione del sistema e del disco inserito (WMI + IMAPI2);
    6. scrittura Track-At-Once e diagnosi degli errori;
    7. ``main()`` con la procedura guidata in quattro passi.

Nota sulla portabilita'
    E' l'unico file del progetto vincolato a Windows. AudioDex resta
    multipiattaforma e non importa nulla da qui.
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
    Progress, SpinnerColumn, BarColumn, TextColumn, MofNCompleteColumn,
    TaskProgressColumn, TimeElapsedColumn,
)
from rich.rule import Rule
from rich.style import Style
from rich.table import Column, Table
from rich.text import Text

from Shared.logger_setup import setup_logger, console, SYM_OK, SYM_FAIL, SYM_ARROW
from Shared import i18n
from Shared.strings_burndex import TESTI

# Le frasi mostrate all'utente stanno tutte nel catalogo, in italiano e in
# inglese; qui si usa la scorciatoia t('chiave'). Commenti, docstring e log su
# file restano in italiano: si rivolgono a chi legge il codice, non a chi lo usa.
i18n.register(TESTI)
t = i18n.t

# pywin32 serve solo per masterizzare davvero: importarlo qui e non in cima
# permette a --help e alle modalita' di sola lettura di funzionare comunque,
# e di dare un messaggio comprensibile invece di un ImportError grezzo.
try:
    import pythoncom
    import win32com.client
    _HAS_PYWIN32 = True
except ImportError:
    _HAS_PYWIN32 = False

SYM_DISC = '[accent]💿[/accent]'


# Larghezza comune di pannelli e tabelle: allineandoli tutti sulla stessa
# misura l'output smette di sembrare un collage di riquadri scollegati.
LARGHEZZA = 68


def _print_banner() -> None:
    """Stampa il banner ASCII colorato 'BurnDex' all'avvio del programma.

    Ricalca quello di AudioDex — stesse tinte, stesso riquadro doppio — per
    dichiarare a colpo d'occhio che i due strumenti appartengono allo stesso
    progetto. Sotto il disegno, una riga dice a cosa serve il programma e in
    quale standard scrive: chi lo lancia dopo mesi ritrova subito il contesto.
    """
    banner_lines = [
        r'    ____                   ____           ',
        r'   / __ )__  ___________  / __ \___  _  __',
        r'  / __  / / / / ___/ __ \/ / / / _ \| |/_/',
        r' / /_/ / /_/ / /  / / / / /_/ /  __/>  <  ',
        r'/_____/\__,_/_/  /_/ /_/_____/\___/_/|_|',
    ]
    colors = ['bright_magenta', 'magenta', 'bright_blue', 'blue', 'bright_cyan', 'cyan']
    text = Text()
    for i, line in enumerate(banner_lines):
        text.append(line + '\n', style=Style(color=colors[i % len(colors)], bold=True))
    text.append('\n' + t('banner.subtitle'), style=Style(color='white', bold=True))
    text.append('  ·  ', style='dim')
    text.append(t('banner.standard'), style='dim')

    console.print()
    console.print(Panel(
        Align.center(text),
        border_style='bright_blue',
        box=DOUBLE,
        padding=(1, 2),
        width=LARGHEZZA,
    ))


def _passo(numero: int, totale: int, titolo: str) -> None:
    """Riga di separazione che annuncia il passo corrente della procedura.

    Dare un numero a ogni fase trasforma una sequenza di riquadri in una
    procedura guidata: si capisce a colpo d'occhio a che punto si e' e
    quanto manca prima del punto di non ritorno.
    """
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


def _barra_capienza(usati: int, capienza: int, larghezza: int = 40) -> Text:
    """Indicatore grafico di quanto disco si occupa.

    Un numero in minuti dice poco a chi non ha in mente che un CD ne regge 80:
    la barra rende immediato quanto margine resta, e cambia colore man mano
    che ci si avvicina al limite oltre il quale i lettori iniziano a sbagliare.
    """
    quota = min(usati / capienza, 1.0) if capienza else 0.0
    pieni = round(quota * larghezza)

    if usati >= SAFE_MINUTES * 60 * SECTORS_PER_SECOND:
        colore = 'red'
    elif quota >= 0.85:
        colore = 'yellow'
    else:
        colore = 'bright_green'

    barra = Text()
    barra.append('█' * pieni, style=colore)
    barra.append('░' * (larghezza - pieni), style='grey37')
    barra.append(f'  {_sectors_to_minutes(usati):.1f}', style='bold white')
    barra.append(f" / {_sectors_to_minutes(capienza):.0f} {t('common.min')}", style='dim')
    return barra


def _progress(descrizione_larghezza: int = 32) -> Progress:
    """Barra di avanzamento uniforme per decodifica e scrittura.

    La colonna della descrizione ha larghezza fissa: senza, ogni titolo di
    lunghezza diversa sposterebbe la barra a destra e a sinistra a ogni
    traccia, con un effetto di tremolio molto sgradevole.
    """
    return Progress(
        SpinnerColumn(style='bright_blue'),
        TextColumn('{task.description}', table_column=Column(
            width=descrizione_larghezza, no_wrap=True, overflow='ellipsis')),
        BarColumn(bar_width=None, style='grey37',
                  complete_style='bright_blue', finished_style='bright_green'),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    )


# ── Parametri del formato CD audio (standard Red Book) ───────────────────────
SECTOR_BYTES = 2352       # Dimensione di un settore audio: IMAPI2 pretende
                          # tracce esattamente multiple di questo valore
SECTORS_PER_SECOND = 75   # 75 settori/s = velocita' 1x
MIN_TRACK_SECTORS = 300   # 4 secondi: traccia piu' corta ammessa dallo standard
PREGAP_SECTORS = 150      # 2 secondi di stacco inseriti prima di ogni traccia
SAFE_MINUTES = 79         # Margine di sicurezza sugli 80 nominali: il bordo
                          # esterno e' la zona che i lettori usurati sbagliano
CD_NOMINALE = 80 * 60 * 75  # Settori di un CD-R da 80 minuti: serve come metro
                            # di paragone prima di sapere che disco e' inserito

DEFAULT_SPEED_X = 8       # Scrittura lenta = incisioni piu' nette = piu'
                          # compatibilita' con autoradio e lettori vecchi
MIN_FREE_MB = 1200        # Spazio temporaneo per il PCM: ~10 MB al minuto

AUDIO_EXTS = frozenset({'.m4a', '.mp3', '.opus', '.mp4', '.wav',
                        '.flac', '.aac', '.ogg', '.wma'})

# IMAPI_MEDIA_PHYSICAL_TYPE: solo i valori che possono capitare in un
# masterizzatore CD/DVD di consumo.
# Le sigle commerciali (CD-R, DVD+RW, BD-RE...) sono internazionali e restano
# identiche in ogni lingua. Solo le due voci generiche vanno tradotte, e per
# quelle qui c'e' la chiave di catalogo invece del testo.
MEDIA_TYPES = {
    0: 'media.unknown', 1: 'CD-ROM', 2: 'CD-R', 3: 'CD-RW',
    4: 'DVD-ROM', 5: 'DVD-RAM', 6: 'DVD+R', 7: 'DVD+RW',
    8: 'DVD+R DL', 9: 'DVD-R', 10: 'DVD-RW', 11: 'DVD-R DL',
    12: 'media.disc', 13: 'BD-ROM', 14: 'BD-R', 15: 'BD-RE',
}

# Solo su questi tre supporti esiste il formato Red Book: un "CD audio" su
# DVD o Blu-ray non e' definito da nessuno standard, e nessun lettore da auto
# saprebbe cosa farsene.
TIPI_CD = frozenset({1, 2, 3})
CD_ROM, CD_R, CD_RW = 1, 2, 3

# Win32_SystemEnclosure.ChassisTypes: i valori che indicano una macchina
# trasportabile. Sono quelle che di norma non hanno un lettore interno e che
# alimentano il masterizzatore esterno dalla sola porta dati.
CHASSIS_PORTATILE = frozenset({8, 9, 10, 11, 12, 14, 18, 21, 30, 31, 32})
CHASSIS_FISSO = frozenset({3, 4, 5, 6, 7, 13, 15, 16, 17, 23, 24})

# Codice IMAPI del comando andato in timeout (HRESULT 0xC0AA020D come intero
# con segno). E' l'errore che si vede quando l'unita' smette di rispondere a
# meta' scrittura, tipicamente perche' resta senza alimentazione.
HR_COMMAND_TIMEOUT = -1062600179

# Prefisso numerico dei file prodotti da AudioDex: "01 - Titolo.m4a".
_NUM_PREFIX = re.compile(r'^\s*(\d{1,3})\s*[-._)\s]')

log = setup_logger('burndex', 'burndex.log')


# ── Utilita' di formato ──────────────────────────────────────────────────────

def _format_duration(seconds: float | None) -> str:
    """Converte una durata in secondi nel formato leggibile M:SS.

    Qui, a differenza di AudioDex, non esiste il ramo con le ore: su un CD
    audio nessuna traccia puo' superare gli 80 minuti, quindi i minuti
    bastano sempre e il codice resta piu' corto di quello equivalente.
    """
    if not seconds:
        return '??:??'
    seconds = int(seconds)
    return f'{seconds // 60}:{seconds % 60:02d}'


def _sectors_to_minutes(sectors: int) -> float:
    """Converte un numero di settori nei minuti di audio corrispondenti.

    Il settore e' l'unita' di misura con cui ragionano sia lo standard Red
    Book sia IMAPI2: capienza del disco, spazio libero e lunghezza delle
    tracce arrivano tutti in settori. I minuti servono solo a mostrarli.

    La conversione e' esatta e non approssimata, perche' un secondo di audio
    occupa esattamente 75 settori per definizione dello standard.
    """
    return sectors / SECTORS_PER_SECOND / 60


def _settori_totali(durate: list[float | None]) -> int:
    """Settori occupati da un elenco di brani, stacchi inclusi.

    Una traccia va arrotondata al settore pieno e non puo' durare meno di
    4 secondi; a ciascuna si aggiungono i 2 secondi di stacco che il
    masterizzatore inserisce prima. Sommare le sole durate darebbe un totale
    ottimistico di qualche decimo di minuto, abbastanza per far sforare un
    disco che sembrava pieno al limite.
    """
    totale = 0
    for dur in durate:
        settori = max(int(dur * SECTORS_PER_SECOND) + 1, MIN_TRACK_SECTORS) if dur else 0
        totale += settori + PREGAP_SECTORS
    return totale


def _x(sectors_per_second: int) -> str:
    """Formatta una velocita' di scrittura in multipli di 1x, arrotondata.

    Le unita' dichiarano valori grezzi leggermente sfasati (599 invece di 600
    per gli 8x): si arrotonda per mostrarli, ma il valore grezzo va conservato
    perche' e' l'unico che SetWriteSpeed accetta senza discutere.
    """
    return f'{round(sectors_per_second / SECTORS_PER_SECOND)}x'


def _check_tools() -> bool:
    """Verifica che ffmpeg e ffprobe siano raggiungibili nel PATH.

    Il controllo e' fatto una volta sola all'avvio, prima di qualsiasi altra
    cosa. L'alternativa sarebbe scoprire l'assenza di FFmpeg a meta'
    decodifica, dopo che l'utente ha gia' scelto raccolta, tracce e velocita'.

    Servono entrambi gli eseguibili e per compiti distinti: ``ffprobe`` legge
    le durate senza decodificare, ``ffmpeg`` produce il PCM. Vengono elencati
    insieme quelli mancanti, cosi' chi ha installato male il pacchetto
    risolve tutto in un colpo invece di scoprire il secondo problema dopo
    aver corretto il primo.
    """
    mancanti = [exe for exe in ('ffmpeg', 'ffprobe') if shutil.which(exe) is None]
    if mancanti:
        console.print(t('tools.missing', tools=', '.join(mancanti)))
        console.print(t('tools.install_ffmpeg'))
        return False
    return True


def _chiedi(prompt: str) -> str:
    """Legge una risposta dal terminale, tollerando EOF e BOM iniziale.

    Il BOM compare quando l'input arriva da una pipe di PowerShell
    (`"" | python ...`), tipico delle prove da script: non essendo uno spazio
    non verrebbe tolto da strip(), e una riga vuota risulterebbe compilata.
    """
    try:
        return console.input(prompt).strip().lstrip('﻿').strip()
    except (EOFError, KeyboardInterrupt):
        return ''


def _check_temp_space() -> bool:
    """Controlla lo spazio per i file PCM temporanei (~850 MB per un CD pieno).

    Come in AudioDex: avvisa e chiede conferma, ma un errore di lettura non
    blocca nulla. Meglio tentare che fermarsi per un controllo accessorio.
    """
    try:
        free_mb = shutil.disk_usage(tempfile.gettempdir()).free / 1048576
        if free_mb < MIN_FREE_MB:
            log.warning('Spazio temporaneo basso: %.0f MB liberi', free_mb)
            console.print(t('temp.low', free=f'{free_mb:.0f}', need=MIN_FREE_MB))
            return i18n.is_yes(_chiedi(t('common.continue')))
        return True
    except OSError:
        return True


# ── Selezione e ordinamento delle tracce ─────────────────────────────────────

def _data_creazione(path: str) -> float:
    """Data di creazione del file, in secondi.

    Su Windows st_ctime e' storicamente la creazione, ma e' in via di
    deprecazione e passera' a indicare l'ultima modifica dei metadati:
    st_birthtime (Python 3.12+) e' il campo corretto, con ripiego per le
    versioni e i filesystem che non lo espongono.
    """
    info = os.stat(path)
    return getattr(info, 'st_birthtime', info.st_mtime)


def _ordina_tracce(cartella: str) -> tuple[list[str], str]:
    """Restituisce i file audio della cartella nell'ordine di masterizzazione.

    Tre criteri, in ordine di precedenza:
      1. ``ordine.txt`` nella cartella (un nome file per riga) - comando manuale;
      2. prefisso numerico nel nome ("01 - Titolo.m4a") - e' come AudioDex
         salva le playlist, quindi di norma scatta questo;
      3. data di creazione del file - ripiego per cartelle messe insieme a mano.

    Ritorna anche una descrizione del criterio usato, da mostrare all'utente:
    sul CD-R non si torna indietro, quindi deve essere chiaro *perche'*
    l'ordine e' quello.
    """
    lista = os.path.join(cartella, 'ordine.txt')
    if os.path.exists(lista):
        percorsi = []
        with open(lista, encoding='utf-8') as fh:
            for riga in fh:
                nome = riga.strip()
                if not nome or nome.startswith('#'):
                    continue
                p = os.path.join(cartella, nome)
                if not os.path.exists(p):
                    console.print(t('order.missing_file', name=nome))
                    return [], ''
                percorsi.append(p)
        return percorsi, t('order.file')

    file_audio = [os.path.join(cartella, n) for n in os.listdir(cartella)
                  if os.path.splitext(n)[1].lower() in AUDIO_EXTS]
    if not file_audio:
        return [], ''

    # Il prefisso numerico vale solo se ce l'hanno *tutti*: con un file senza
    # numero l'ordinamento diventerebbe arbitrario proprio dove conta.
    numeri = [_NUM_PREFIX.match(os.path.basename(p)) for p in file_audio]
    if all(numeri):
        coppie = sorted(zip(file_audio, numeri), key=lambda c: int(c[1].group(1)))
        return [p for p, _ in coppie], t('order.number')

    return sorted(file_audio, key=_data_creazione), t('order.created')


def _scegli_cartella(base: str) -> str | None:
    """Mostra le raccolte presenti in download_audio e ne fa scegliere una.

    E' il passo 1 della procedura guidata, quello che rende BurnDex usabile
    senza ricordare percorsi: elenca le sottocartelle create da AudioDex con
    numero di tracce e durata complessiva, quest'ultima in giallo quando
    supera la capienza di un disco.

    La cartella base compare anch'essa in elenco, come "brani singoli", se
    contiene direttamente dei file audio: e' li' che AudioDex lascia i brani
    scaricati fuori da una playlist, e ignorarli li renderebbe invisibili.

    Ritorna None se l'utente esce o sbaglia la scelta; il chiamante lo
    interpreta come rinuncia e chiude senza toccare nulla.
    """
    _passo(1, 4, t('step.collection'))
    if not os.path.isdir(base):
        console.print(t('common.folder_missing', path=base))
        return None

    cartelle = sorted(
        os.path.join(base, n) for n in os.listdir(base)
        if os.path.isdir(os.path.join(base, n))
    )
    # La cartella base stessa e' una candidata: AudioDex ci lascia dentro i
    # brani singoli, quelli scaricati fuori da una playlist.
    if any(os.path.splitext(n)[1].lower() in AUDIO_EXTS for n in os.listdir(base)):
        cartelle.insert(0, base)

    if not cartelle:
        console.print(t('collection.none_found', base=base))
        return None

    tabella = Table(box=HEAVY_HEAD, border_style='bright_blue', width=LARGHEZZA,
                    header_style='bold bright_blue', padding=(0, 1))
    tabella.add_column('#', style='dim_label', justify='right', width=2)
    tabella.add_column(t('collection.column'), style='bold white', overflow='ellipsis',
                       no_wrap=True, ratio=1)
    tabella.add_column(t('collection.tracks'), justify='right', style='info', width=6)
    tabella.add_column(t('collection.duration'), justify='right', style='info', width=9)

    # La durata complessiva e' il dato che decide se una raccolta ci sta su un
    # disco, ma costa un ffprobe per file: con molte raccolte l'attesa si
    # sente, quindi la si dichiara invece di lasciare il terminale muto.
    righe = []
    with console.status(t('collection.scanning'), spinner='dots'):
        for i, c in enumerate(cartelle, 1):
            tracce, _ = _ordina_tracce(c)
            nome = t('collection.singles') if c == base else escape(os.path.basename(c))
            # Stesso conteggio della scaletta (stacchi inclusi), altrimenti qui
            # si leggerebbe un totale e due schermate dopo un altro.
            minuti = _sectors_to_minutes(_settori_totali([_durata(p) for p in tracce]))
            durata = f"{minuti:.1f} {t('common.min')}"
            righe.append((str(i), nome, str(len(tracce)),
                          f'[warning]{durata}[/warning]' if minuti > SAFE_MINUTES
                          else durata))

    for riga in righe:
        tabella.add_row(*riga)

    console.print()
    console.print(tabella)

    scelta = _chiedi(t('collection.prompt', disc=SYM_DISC))
    if not scelta:
        return None
    try:
        idx = int(scelta)
        if not 1 <= idx <= len(cartelle):
            raise ValueError
    except ValueError:
        console.print(t('common.invalid_choice'))
        return None
    return cartelle[idx - 1]


# ── Lettura durate e decodifica ──────────────────────────────────────────────

def _durata(path: str) -> float | None:
    """Durata in secondi di un file audio, letta con ffprobe.

    Serve a calcolare la capienza prima di impegnare il masterizzatore:
    ffprobe legge l'intestazione del file senza decodificarlo, quindi risponde
    in millisecondi anche su un album intero. Decodificare per sapere quanto
    dura costerebbe minuti e centinaia di megabyte.

    Ritorna None invece di sollevare un'eccezione quando il file e' corrotto o
    non riconosciuto: il chiamante raccoglie tutti i file illeggibili e li
    elenca insieme, cosi' si sistemano in una volta sola.
    """
    try:
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'json', path],
            capture_output=True, text=True, check=True, encoding='utf-8',
        )
        return float(json.loads(out.stdout)['format']['duration'])
    except (subprocess.CalledProcessError, KeyError, ValueError, json.JSONDecodeError) as exc:
        log.error('ffprobe fallito su %s: %s', path, exc)
        return None


def _mostra_scaletta(tracce: list[str], durate: list[float | None],
                     criterio: str, titolo: str, capienza: int = CD_NOMINALE) -> int:
    """Stampa la scaletta numerata e ritorna i settori totali stimati.

    Con ``capienza`` (settori del disco inserito) aggiunge sotto la tabella
    la barra di riempimento: e' il colpo d'occhio che dice se ci sta.
    """
    totale = _settori_totali(durate)
    minuti = _sectors_to_minutes(totale)
    tabella = Table(
        box=HEAVY_HEAD, border_style='bright_blue', width=LARGHEZZA,
        title=f'[bold bright_magenta]{escape(titolo)}[/bold bright_magenta]',
        title_justify='center', header_style='bold bright_blue',
        show_footer=True, footer_style='bold', padding=(0, 1),
    )
    tabella.add_column('#', style='dim_label', justify='right', width=2, footer='')
    tabella.add_column(t('tracklist.column'), style='white', overflow='ellipsis',
                       no_wrap=True, ratio=1, footer=t('tracklist.count', n=len(tracce)))
    tabella.add_column(t('tracklist.duration'), justify='right', style='info', width=9,
                       footer=f"[bold white]{minuti:.1f} {t('common.min')}[/bold white]")

    for i, (path, dur) in enumerate(zip(tracce, durate), 1):
        tabella.add_row(str(i), escape(os.path.basename(path)), _format_duration(dur))

    console.print()
    console.print(tabella)

    if capienza:
        console.print(_barra_capienza(totale, capienza, LARGHEZZA - 24))

    console.print(t('tracklist.order_note', criterion=escape(criterio)))
    return totale


def _seleziona_tracce(tracce: list[str],
                      durate: list[float | None]) -> tuple[list[str], list[float | None]]:
    """Chiede quali tracce mettere sul disco tra quelle elencate.

    Stessa sintassi di selezione di AudioDex: numero singolo (3), intervallo
    (1-5), elenco (1,3,7), 'all' o invio per tutte, 'q' per annullare. Serve
    soprattutto quando una raccolta supera gli 80 minuti: invece di
    rinunciare si sceglie cosa portarsi dietro. L'ordine di masterizzazione
    resta quello della scaletta, non quello in cui si digitano i numeri: su
    un album la sequenza dei brani e' voluta.
    """
    console.print(t('select.hint'))

    while True:
        scelta = _chiedi(t('select.prompt')).lower()
        if i18n.is_quit(scelta):
            return [], []
        if not scelta or i18n.is_all(scelta):
            return tracce, durate

        indici: set[int] = set()
        try:
            for parte in scelta.replace(' ', ',').split(','):
                parte = parte.strip()
                if not parte:
                    continue
                if '-' in parte:
                    inizio, fine = parte.split('-', 1)
                    for n in range(int(inizio), int(fine) + 1):
                        if 1 <= n <= len(tracce):
                            indici.add(n - 1)
                else:
                    n = int(parte)
                    if 1 <= n <= len(tracce):
                        indici.add(n - 1)
        except ValueError:
            indici.clear()

        if indici:
            ordinati = sorted(indici)
            return [tracce[i] for i in ordinati], [durate[i] for i in ordinati]

        console.print(t('common.invalid_selection'))


def _pannello_unita(recorder, supporto: dict, sistema: dict | None = None) -> None:
    """Scheda dell'unita' e del disco inserito, pronta per la scrittura.

    Raccoglie in un unico riquadro quello che prima erano righe sparse:
    masterizzatore, tipo di disco, capienza e velocita' disponibili. E' la
    conferma visiva che il programma sta parlando con l'unita' giusta —
    dettaglio non ovvio quando ce n'e' piu' d'una collegata.

    Il parametro ``sistema`` e' opzionale perche' la ricognizione WMI puo'
    fallire o non essere stata fatta: quando c'e', accanto alla lettera
    compare l'etichetta (USB) che segnala un'unita' esterna, cioe' quella
    esposta al calo di tensione in scrittura.
    """
    tabella = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    tabella.add_column('Campo', style='dim_label', no_wrap=True, width=14)
    tabella.add_column('Valore', style='white', ratio=1, overflow='ellipsis')

    lettera = _lettera_unita(recorder)
    collegamento = ((sistema or {}).get('unita', {}).get(lettera) or {}).get('connessione')
    nota_usb = '  [warning](USB)[/warning]' if collegamento == 'USB' else ''

    tabella.add_row(t('drive.burner'),
                    f'[bold]{escape(_nome_unita(recorder))}[/bold]'
                    f'  [dim]{escape(lettera)}[/dim]{nota_usb}')
    tabella.add_row(t('drive.disc'),
                    f"[bold]{supporto['tipo']}[/bold] "
                    + t('drive.capacity',
                        min=f"{_sectors_to_minutes(supporto['settori']):.0f}"))
    if supporto['velocita']:
        tabella.add_row(t('drive.speed'), '[dim]' +
                        ', '.join(_x(v) for v in supporto['velocita']) + '[/dim]')

    console.print()
    console.print(Panel(
        tabella,
        title=t('drive.panel_title'),
        border_style='bright_blue',
        box=ROUNDED,
        width=LARGHEZZA,
        padding=(1, 1),
    ))


def _chiedi_velocita(supportate: list[int]) -> int | None:
    """Pannello di scelta della velocita', costruito sui valori reali dell'unita'.

    Non si propone una scala fissa: ogni masterizzatore espone i suoi gradini
    (qui 8x e 24x) e chiedere un valore fuori elenco farebbe fallire
    SetWriteSpeed. Invio sceglie la piu' adatta all'ascolto in auto.
    """
    if not supportate:
        return None

    consigliata = _scegli_velocita(supportate, DEFAULT_SPEED_X)

    tabella = Table(box=HEAVY_HEAD, border_style='bright_blue', width=LARGHEZZA,
                    header_style='bold bright_blue', padding=(0, 1))
    tabella.add_column('#', style='dim_label', justify='right', width=2)
    tabella.add_column(t('speed.column'), style='bold white', width=9)
    tabella.add_column(t('speed.result'), overflow='fold', ratio=1)

    for i, v in enumerate(supportate, 1):
        if v == consigliata:
            etichetta = f'{_x(v)} [success]★[/success]'
            nota = t('speed.recommended')
        elif v == max(supportate):
            etichetta = _x(v)
            nota = t('speed.fastest')
        else:
            etichetta = _x(v)
            nota = t('speed.middle')
        tabella.add_row(str(i), etichetta, nota)

    console.print()
    console.print(tabella)

    while True:
        scelta = _chiedi(t('speed.prompt', n=len(supportate),
                           default=_x(consigliata)))
        if not scelta:
            return consigliata
        try:
            n = int(scelta)
            if 1 <= n <= len(supportate):
                return supportate[n - 1]
        except ValueError:
            pass
        console.print(t('common.invalid_choice_retry'))


def _card_conferma(recorder, supporto: dict, velocita: int | None,
                   n_tracce: int, settori: int) -> bool:
    """Scheda riepilogativa e ultima conferma prima di scrivere.

    E' l'unico punto di non ritorno del programma: da qui in poi il CD-R
    e' consumato comunque, anche se qualcosa va storto a meta'.
    """
    tabella = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    tabella.add_column('Campo', style='dim_label', no_wrap=True, width=16)
    tabella.add_column('Valore', style='white', ratio=1, overflow='ellipsis')

    residuo = supporto['settori'] - settori
    tabella.add_row(t('confirm.drive'), escape(_nome_unita(recorder)))
    tabella.add_row(t('confirm.disc'),
                    f"[bold]{supporto['tipo']}[/bold] [dim]{t('common.empty')}[/dim]")
    tabella.add_row(t('confirm.speed'),
                    f"[bold]{_x(velocita) if velocita else t('common.automatic')}[/bold]")
    tabella.add_row(t('confirm.tracks'), f'[bold]{n_tracce}[/bold]')
    tabella.add_row(t('confirm.duration'),
                    f"[bold]{_sectors_to_minutes(settori):.1f} {t('common.min')}[/bold]  "
                    + t('confirm.free_after', min=f'{_sectors_to_minutes(residuo):.1f}'))

    contenuto = Table.grid(padding=(0, 0), expand=True)
    contenuto.add_column()
    contenuto.add_row(tabella)
    contenuto.add_row('')
    contenuto.add_row(Align.center(_barra_capienza(settori, supporto['settori'], 36)))

    console.print()
    console.print(Panel(
        contenuto,
        title=t('confirm.title'),
        subtitle=t('confirm.subtitle'),
        border_style='bright_magenta',
        box=DOUBLE,
        width=LARGHEZZA,
        padding=(1, 2),
    ))

    return i18n.is_yes(_chiedi(t('confirm.prompt')))


def _decodifica(src: str, dst: str) -> int:
    """Decodifica src in PCM grezzo 44.1 kHz / 16 bit / stereo dentro dst.

    IMAPI2 vuole l'audio nudo, senza header WAV, allineato al settore da
    2352 byte e lungo almeno 4 secondi: se sgarra di un byte la chiamata
    AddAudioTrack fallisce. Il riempimento con silenzio sistema entrambi i
    vincoli. Ritorna i settori occupati.
    """
    with open(dst, 'wb') as fh:
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-i', src, '-vn',
             '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', '-'],
            stdout=fh, stderr=subprocess.PIPE, check=True,
        )

    n = os.path.getsize(dst)
    padding = max(MIN_TRACK_SECTORS * SECTOR_BYTES - n, 0)
    padding += -(n + padding) % SECTOR_BYTES
    if padding:
        with open(dst, 'ab') as fh:
            fh.write(b'\x00' * padding)
    return (n + padding) // SECTOR_BYTES


# ── Interfaccia con IMAPI2 ───────────────────────────────────────────────────

def _elenca_unita() -> list:
    """Restituisce un MsftDiscRecorder2 inizializzato per ogni masterizzatore.

    E' il primo dei cinque passaggi IMAPI2. ``MsftDiscMaster2`` e' solo un
    elenco di identificativi opachi: da soli non dicono nulla, e per sapere
    marca, modello e lettera di unita' bisogna costruire un
    ``MsftDiscRecorder2`` e inizializzarlo su ciascuno. Qui si fa una volta
    sola e si restituiscono gli oggetti pronti.

    Una lista vuota significa che nessun masterizzatore e' raggiungibile: o
    non ce n'e', oppure quello esterno si e' scollegato — succede davvero,
    dopo un'interruzione di corrente durante la scrittura.
    """
    master = win32com.client.Dispatch('IMAPI2.MsftDiscMaster2')
    unita = []
    for i in range(master.Count):
        rec = win32com.client.Dispatch('IMAPI2.MsftDiscRecorder2')
        rec.InitializeDiscRecorder(master.Item(i))
        unita.append(rec)
    return unita


def _info_sistema() -> dict:
    """Riconosce il tipo di computer e le unita' ottiche presenti.

    Serve a rispondere prima ancora di provare: questo PC puo' masterizzare
    da solo o serve un lettore esterno? E se e' esterno, e' collegato in USB
    e quindi esposto al calo di tensione che fa fallire le scritture?

    Ritorna {'macchina', 'modello', 'unita': {lettera: {'nome', 'connessione'}}}.
    Un fallimento di WMI non e' bloccante: si perde solo il consiglio.
    """
    info = {'macchina': 'sconosciuta', 'modello': '', 'unita': {}}
    try:
        wmi = win32com.client.GetObject('winmgmts:')

        for enclosure in wmi.InstancesOf('Win32_SystemEnclosure'):
            for tipo in (enclosure.ChassisTypes or ()):
                if tipo in CHASSIS_PORTATILE:
                    info['macchina'] = 'portatile'
                elif tipo in CHASSIS_FISSO:
                    info['macchina'] = 'fisso'

        for sistema in wmi.InstancesOf('Win32_ComputerSystem'):
            info['modello'] = (sistema.Model or '').strip()

        for unita in wmi.InstancesOf('Win32_CDROMDrive'):
            lettera = (unita.Drive or '').rstrip('\\')
            # Le unita' esterne si riconoscono dal ramo USBSTOR dell'albero
            # PnP; quelle interne stanno sotto SCSI o IDE.
            pnp = (unita.PNPDeviceID or '').upper()
            info['unita'][lettera] = {
                'nome': (unita.Caption or '').strip(),
                'connessione': 'USB' if pnp.startswith('USBSTOR') else 'interna',
            }
    except Exception as exc:
        log.debug('Ricognizione WMI fallita: %s', exc)

    return info


def _pannello_sistema(info: dict) -> None:
    """Scheda con tipo di computer, unita' ottiche e cosa serve per masterizzare.

    Apre la modalita' ``--info`` e risponde alla domanda che viene prima di
    ogni altra: questo computer puo' masterizzare da solo, oppure serve un
    lettore esterno? Su un portatile recente la risposta e' quasi sempre la
    seconda, e conviene saperlo prima di cercare un'unita' che non c'e'.

    Mostra i dati grezzi; il giudizio su cosa farne e' delegato a
    ``_consiglio_sistema``, chiamata subito dopo.
    """
    tabella = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    tabella.add_column('Campo', style='dim_label', no_wrap=True, width=14)
    tabella.add_column('Valore', style='white', ratio=1, overflow='ellipsis')

    macchina = {'portatile': t('system.laptop'), 'fisso': t('system.desktop')}.get(
        info['macchina'], t('system.unknown_type'))
    modello = f"  [dim]{escape(info['modello'])}[/dim]" if info['modello'] else ''
    tabella.add_row(t('system.computer'), f'[bold]{macchina}[/bold]{modello}')

    if not info['unita']:
        tabella.add_row(t('system.cd_drive'), t('system.none_detected'))
    for lettera, unita in sorted(info['unita'].items()):
        esterna = unita['connessione'] == 'USB'
        tabella.add_row(
            t('system.drive_label', letter=escape(lettera)),
            f"[bold]{escape(unita['nome'])}[/bold]\n"
            + (t('system.usb_external') if esterna else t('system.internal')))

    console.print()
    console.print(Panel(
        tabella,
        title=t('system.panel_title'),
        border_style='bright_blue',
        box=ROUNDED,
        width=LARGHEZZA,
        padding=(1, 1),
    ))

    _consiglio_sistema(info)


def _consiglio_sistema(info: dict) -> None:
    """Stampa cosa serve per masterizzare, in base a quello che c'e'.

    Tre esiti, tre consigli diversi. Senza alcun lettore serve un
    masterizzatore esterno USB, e vale la pena dirlo esplicitamente perche'
    su un portatile senza unita' ottica il programma sembrerebbe rotto. Con
    un'unita' USB si avverte del problema di alimentazione **prima** della
    scrittura: e' la causa piu' frequente di masterizzazioni interrotte a
    meta', e i tre rimedi sono elencati in ordine di efficacia. Con un'unita'
    interna si conferma solo che non servono precauzioni.

    L'avviso resta legato alla connessione e non al tipo di computer: anche
    un PC fisso puo' avere un masterizzatore USB, e anche un portatile puo'
    averne uno interno.
    """
    if not info['unita']:
        console.print(t('system.advice_none'))
        return

    usb = [l for l, u in info['unita'].items() if u['connessione'] == 'USB']
    console.print(t('system.advice_usb') if usb else t('system.advice_internal'))


def _valuta_supporto(supporto: dict) -> tuple[bool, str, str]:
    """Decide se il disco inserito puo' diventare un CD audio.

    Ritorna (utilizzabile, descrizione, spiegazione). La distinzione serve
    perche' i motivi per cui un disco non va bene sono molto diversi tra
    loro, e ognuno ha un rimedio diverso: comprarne uno nuovo, cancellarlo,
    o rendersi conto di aver inserito un DVD.
    """
    codice = supporto['codice']
    tipo = supporto['tipo']

    if codice == 0:
        return False, t('disc.unknown_type'), t('disc.unknown_type_why')

    if codice not in TIPI_CD:
        return False, f'{tipo}', t('disc.not_a_cd_why')

    if codice == CD_ROM:
        return False, t('disc.pressed_cdrom'), t('disc.pressed_cdrom_why')

    if not supporto['vuoto']:
        if codice == CD_RW:
            return False, t('disc.cdrw_written'), t('disc.cdrw_written_why')
        return False, t('disc.cdr_written'), t('disc.cdr_written_why')

    if codice == CD_RW:
        return True, t('disc.cdrw_blank'), t('disc.cdrw_blank_why')

    return True, t('disc.cdr_blank'), ''


def _nome_unita(rec) -> str:
    """Marca e modello del masterizzatore.

    IMAPI2 espone i due campi separati e con spazi di riempimento in coda,
    perche' arrivano dalla stringa di identificazione SCSI, che ha campi a
    lunghezza fissa. Qui vengono ripuliti e uniti nell'etichetta usata in
    tutte le tabelle e le schede, cosi' la stessa unita' compare ovunque con
    lo stesso nome.
    """
    return f'{rec.VendorId.strip()} {rec.ProductId.strip()}'


def _lettera_unita(rec) -> str:
    """Lettera assegnata all'unita', senza la barra finale.

    La barra rovescia va tolta: nei markup di Rich e' il carattere di escape,
    e una stringa che finisce con '\\' si mangerebbe il tag successivo.
    """
    return (rec.VolumePathNames or ('',))[0].rstrip('\\') or '-'


def _scegli_unita(indice: int | None = None):
    """Sceglie il masterizzatore da usare.

    Con un'unica unita' collegata — il caso normale — la sceglie da sola
    senza chiedere nulla: una domanda con una sola risposta possibile e'
    solo un ostacolo. Con piu' unita' le elenca e lascia decidere.

    Parametri
    ---------
    indice : int | None
        Indice passato da ``--drive``, che salta la domanda anche quando le
        unita' sono piu' d'una: serve agli usi automatizzati, dove un prompt
        bloccherebbe lo script. Un indice fuori intervallo produce un errore
        esplicito invece di ricadere silenziosamente sulla prima unita'.

    Ritorna None quando non c'e' nulla da usare o la scelta non e' valida.
    """
    unita = _elenca_unita()
    if not unita:
        console.print(t('drive.none_detected'))
        return None

    if indice is not None:
        if not 0 <= indice < len(unita):
            console.print(t('drive.index_missing', index=indice, total=len(unita)))
            return None
        return unita[indice]

    if len(unita) == 1:
        # Senza scelta da fare non serve annunciarla: l'unita' viene comunque
        # mostrata subito dopo dalla scheda _pannello_unita().
        return unita[0]

    console.print(t('drive.available'))
    for i, rec in enumerate(unita):
        console.print(f'  [accent]{i}[/accent]  {escape(_nome_unita(rec))}'
                      f'  [dim]{escape(_lettera_unita(rec))}[/dim]')
    try:
        return unita[int(_chiedi(t('drive.which')))]
    except (ValueError, IndexError):
        console.print(t('common.invalid_choice'))
        return None


def _leggi_supporto(recorder) -> dict | None:
    """Legge tipo, stato e capacita' del disco inserito, senza impegnare l'unita'.

    Le stesse proprieta' sul writer Track-At-Once esistono, ma sono leggibili
    solo dopo PrepareMedia(), che pero' apre gia' la sessione di scrittura:
    troppo tardi per decidere se il disco va bene. Il formatter dati invece
    risponde appena gli si assegna il recorder, quindi lo si usa come sonda
    di sola lettura e si tiene il Track-At-Once per la scrittura vera.

    Ritorna None se non c'e' un disco leggibile nell'unita'.
    """
    sonda = win32com.client.Dispatch('IMAPI2.MsftDiscFormat2Data')
    sonda.ClientName = 'BurnDex'
    try:
        sonda.Recorder = recorder
        return {
            'codice': int(sonda.CurrentPhysicalMediaType),
            # Le sigle passano attraverso t() invariate — una chiave assente
            # dal catalogo viene restituita tale e quale — mentre le due voci
            # generiche vengono tradotte.
            'tipo': t(MEDIA_TYPES.get(sonda.CurrentPhysicalMediaType, '?')),
            'vuoto': bool(sonda.MediaPhysicallyBlank),
            'settori': int(sonda.FreeSectorsOnMedia),
            # Valori grezzi in settori/secondo, come li dichiara l'unita'.
            'velocita': sorted({int(v) for v in (sonda.SupportedWriteSpeeds or ())}),
        }
    except Exception as exc:
        log.debug('Lettura supporto fallita: %s', exc)
        return None


def _scegli_velocita(supportate: list[int], richiesta_x: int) -> int | None:
    """La velocita' supportata piu' vicina a quella richiesta, senza superarla.

    ``supportate`` e ``richiesta_x`` sono in unita' diverse: le prime in
    settori/secondo come le dichiara l'unita', la seconda in multipli di 1x
    come la scrive l'utente. Le unita' espongono pochi gradini discreti (qui
    solo 8x e 24x), quindi chiedere i 4x non rallenta: fa fallire la chiamata.
    Si scende al gradino disponibile piu' vicino, e se non ce n'e' nessuno
    sotto la soglia si prende il piu' lento in assoluto.

    Ritorna None se l'unita' non dichiara velocita': in quel caso si lascia
    fare a lei.
    """
    if not supportate:
        return None
    soglia = richiesta_x * SECTORS_PER_SECOND
    ammesse = [v for v in supportate if v <= soglia]
    return max(ammesse) if ammesse else min(supportate)


def _crea_writer(recorder, velocita: int | None):
    """Crea il writer Track-At-Once e vi imposta la velocita' di scrittura.

    ``velocita`` e' un valore grezzo in settori/secondo gia' scelto tra quelli
    che l'unita' dichiara, oppure None per lasciar decidere il masterizzatore.
    """
    audio = win32com.client.Dispatch('IMAPI2.MsftDiscFormat2TrackAtOnce')
    audio.ClientName = 'BurnDex'
    audio.Recorder = recorder

    if not audio.IsCurrentMediaSupported(recorder):
        console.print(t('disc.not_writable_audio'))
        return None

    if velocita is None:
        console.print(t('speed.writing_at', arrow=SYM_ARROW,
                        speed=t('common.automatic')))
        return audio

    try:
        audio.SetWriteSpeed(velocita, False)
        console.print(t('speed.writing_at', arrow=SYM_ARROW, speed=_x(velocita)))
    except Exception as exc:
        log.warning('SetWriteSpeed(%d settori/s) rifiutata: %s', velocita, exc)
        console.print(t('speed.refused'))

    return audio


def _hresult(exc: Exception) -> int | None:
    """Estrae il codice di errore COM da un'eccezione pywintypes.com_error.

    Le eccezioni COM di pywin32 hanno una struttura annidata e poco comoda:
    il codice specifico che identifica il guasto — quello che permette di
    distinguere "disco assente" da "unita' che non risponde" — sta nel sesto
    elemento della tupla contenuta nel terzo argomento.

    L'accesso e' protetto perche' questa funzione riceve anche eccezioni che
    con COM non c'entrano nulla: in quel caso ritorna None e il chiamante
    ripiega sul messaggio grezzo.
    """
    try:
        return exc.args[2][5]
    except (AttributeError, IndexError, TypeError):
        return None


def _spiega_errore(exc: Exception) -> None:
    """Traduce gli errori IMAPI ricorrenti in una diagnosi utile.

    Il messaggio grezzo di IMAPI dice cosa non ha funzionato ma non perche':
    un timeout sul primo comando di scrittura, in particolare, quasi mai
    dipende dal disco e quasi sempre dall'alimentazione dell'unita'.
    """
    codice = _hresult(exc)
    if codice == HR_COMMAND_TIMEOUT:
        console.print(t('burn.timeout'))
        console.print(t('burn.timeout_why'))
    else:
        console.print(t('burn.write_error', error=exc))


def _masterizza(audio, pcm_files: list[str], nomi: list[str]) -> tuple[bool, int]:
    """Scrive le tracce sul disco e lo finalizza.

    Ritorna (esito, tracce effettivamente scritte): il secondo valore non e'
    ridondante, perche' un guasto a meta' lascia il disco con solo una parte
    dei brani e il riepilogo deve dire il vero.
    """
    audio.PrepareMedia()
    scritte = 0
    esito = True
    try:
        with _progress() as progress:
            task = progress.add_task(t('burn.starting'), total=len(pcm_files))
            for pcm, nome in zip(pcm_files, nomi):
                progress.update(task, description=nome)
                # Lo stream va costruito in memoria: IMAPI2 vuole un IStream,
                # non un percorso. Un brano occupa ~50-100 MB, quindi si
                # carica una traccia alla volta e non tutto il disco.
                stream = pythoncom.CreateStreamOnHGlobal()
                with open(pcm, 'rb') as fh:
                    stream.Write(fh.read())
                stream.Seek(0, 0)
                audio.AddAudioTrack(stream)
                scritte += 1
                progress.advance(task)
            progress.update(task, description=t('burn.all_written'))
    except Exception as exc:
        log.exception('Masterizzazione fallita dopo %d tracce', scritte)
        _spiega_errore(exc)
        esito = False
    finally:
        # Chiude la sessione e finalizza: da qui il disco e' definitivo.
        # Va tentata anche in caso di errore, altrimenti l'unita' resta
        # bloccata in accesso esclusivo. Se pero' e' stata proprio l'unita'
        # a sparire, anche questa fallisce: non deve coprire l'errore vero.
        try:
            console.print(t('burn.closing'))
            audio.ReleaseMedia()
        except Exception as exc:
            log.warning('ReleaseMedia fallita: %s', exc)
            console.print(t('burn.close_failed'))

    return esito, scritte


def _mostra_riepilogo(scritte: int, totali: int, minuti: float, esito: bool) -> None:
    """Pannello finale con l'esito della masterizzazione.

    Riporta le tracce **effettivamente incise**, non quelle preparate: e' la
    differenza che dice se il disco e' ancora utilizzabile. A zero tracce il
    CD-R e' rimasto vergine e si puo' riprovare; a meta' e' compromesso in
    modo irreversibile e va sostituito. Sono due situazioni molto diverse, e
    confonderle costa un disco.

    La durata totale compare solo in caso di successo: dopo un fallimento
    indicherebbe quanto *sarebbe* durato il disco, un dato senza significato
    che si presterebbe a essere letto come quanto e' stato scritto.
    """
    tabella = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    tabella.add_column('Label', style='dim_label', no_wrap=True, width=16)
    tabella.add_column('Value', ratio=1)

    tabella.add_row(t('result.tracks_written'),
                    f'[bold]{scritte}[/bold] ' + t('result.out_of', total=totali))
    if esito:
        tabella.add_row(t('result.total_duration'),
                        f"[bold]{minuti:.1f} {t('common.min')}[/bold]")
        tabella.add_row(t('result.outcome'), f"{SYM_OK} {t('result.finalised')}")
        tabella.add_row('', t('result.ready_to_play'))
    else:
        tabella.add_row(t('result.outcome'), f"{SYM_FAIL} {t('result.aborted')}")
        tabella.add_row(t('result.disc'),
                        t('result.disc_still_good') if scritte == 0
                        else t('result.disc_ruined'))

    console.print()
    console.print(Panel(
        tabella,
        title=t('result.ok_title') if esito else t('result.fail_title'),
        border_style='bright_green' if esito else 'red',
        box=DOUBLE,
        width=LARGHEZZA,
        padding=(1, 2),
    ))


# ── Flusso principale ────────────────────────────────────────────────────────

def _modalita_info() -> None:
    """Mostra sistema, masterizzatori e disco inserito, senza scrivere nulla.

    E' la modalita' ``--info``, pensata come primo comando da lanciare: dice
    se il computer ha un lettore, se e' interno o esterno, che disco c'e'
    dentro e a quali velocita' l'unita' sa scrivere. Tutte informazioni che
    altrimenti si scoprirebbero a meta' procedura.

    E' anche lo strumento diagnostico da usare quando una masterizzazione
    fallisce: se qui l'unita' non compare piu', il problema e' il
    collegamento e non il programma.

    Non apre alcuna sessione di scrittura e non modifica nulla.
    """
    _pannello_sistema(_info_sistema())

    unita = _elenca_unita()
    if not unita:
        console.print(t('info.no_imapi_drive'))
        console.print(t('info.check_external'))
        return

    tabella = Table(box=HEAVY_HEAD, border_style='bright_blue', width=LARGHEZZA,
                    header_style='bold bright_blue', padding=(0, 1))
    tabella.add_column('#', style='dim_label', justify='right', width=2)
    tabella.add_column(t('info.drive_column'), style='bold white', overflow='ellipsis',
                       no_wrap=True, ratio=1)
    tabella.add_column(t('info.disc_column'), width=18)
    tabella.add_column(t('info.speed_column'), style='dim', width=8)

    for i, rec in enumerate(unita):
        info = _leggi_supporto(rec)
        if info is None:
            stato, velocita = t('info.no_disc'), '[dim]-[/dim]'
        else:
            capienza = f'{_sectors_to_minutes(info["settori"]):.0f} {t("common.min")}'
            stato = (t('info.blank', type=info['tipo'], capacity=capienza)
                     if info['vuoto']
                     else t('info.written', type=info['tipo']))
            velocita = ', '.join(_x(v) for v in info['velocita']) or '-'
        tabella.add_row(str(i),
                        f'{escape(_nome_unita(rec))} [dim]{escape(_lettera_unita(rec))}[/dim]',
                        stato, velocita)

    console.print()
    console.print(tabella)
    console.print()


def masterizza_cartella(cartella: str, *, speed_x: int | None, dry_run: bool,
                        auto_si: bool, espelli: bool, indice_unita: int | None) -> int:
    """Prepara e masterizza il contenuto di una cartella. Ritorna il codice di uscita.

    Con ``auto_si`` non viene posta alcuna domanda: tutte le tracce, velocita'
    da riga di comando o predefinita, nessuna conferma. Altrimenti il flusso
    e' a pannelli come in AudioDex - scaletta, selezione, velocita', scheda
    finale - e ogni passaggio si puo' annullare.
    """
    nome_raccolta = os.path.basename(cartella) or t('collection.default_name')
    tracce, criterio = _ordina_tracce(cartella)
    if not tracce:
        console.print(t('collection.no_audio', path=cartella))
        return 1

    if not auto_si:
        _passo(2, 4, t('step.tracklist'))
    # Percorso accorciato in testa invece che mandato a capo: la coda e' la
    # parte che identifica la raccolta, l'inizio si intuisce.
    percorso = (cartella if len(cartella) <= LARGHEZZA
                else '…' + cartella[-(LARGHEZZA - 1):])
    console.print(f'[dim]{escape(percorso)}[/dim]')

    durate = [_durata(p) for p in tracce]
    if any(d is None for d in durate):
        illeggibili = [os.path.basename(p) for p, d in zip(tracce, durate) if d is None]
        console.print(t('tracklist.unreadable', files=', '.join(illeggibili)))
        return 1

    stimati = _mostra_scaletta(tracce, durate, criterio, nome_raccolta)
    minuti = _sectors_to_minutes(stimati)

    if not auto_si:
        # La selezione arriva prima di ogni controllo di capienza: se la
        # raccolta sfora gli 80 minuti, la via d'uscita e' proprio scegliere
        # meno tracce, non vedersi respingere l'intera operazione.
        if minuti > SAFE_MINUTES:
            console.print(t('select.too_long_pick',
                            over=f'{minuti - SAFE_MINUTES:.1f}', limit=SAFE_MINUTES))

        scelte, durate_scelte = _seleziona_tracce(tracce, durate)
        if not scelte:
            console.print(t('common.cancelled'))
            return 1

        if len(scelte) != len(tracce):
            tracce, durate = scelte, durate_scelte
            stimati = _mostra_scaletta(
                tracce, durate, criterio,
                t('collection.selection_suffix', name=nome_raccolta))
            minuti = _sectors_to_minutes(stimati)

    if minuti > SAFE_MINUTES:
        console.print(t('disc.too_long', limit=SAFE_MINUTES,
                        over=f'{minuti - SAFE_MINUTES:.1f}'))
        console.print(t('disc.trim_hint'))
        return 1

    if not _HAS_PYWIN32:
        if dry_run:
            console.print(t('dry.tracklist_ok', ok=SYM_OK))
            console.print(t('tools.no_pywin32_skip'))
            return 0
        console.print(t('tools.no_pywin32_burn'))
        console.print(t('tools.install_pywin32'))
        return 1

    pythoncom.CoInitialize()

    if not auto_si:
        _passo(3, 4, t('step.disc_speed'))

    recorder = _scegli_unita(indice_unita)
    if recorder is None:
        return 1

    # Tutti i controlli sul disco vengono prima della decodifica: accorgersi
    # che manca il CD dopo due minuti di ffmpeg sarebbe solo tempo buttato.
    supporto = _leggi_supporto(recorder)
    if supporto is None:
        console.print(t('drive.no_readable_disc'))
        console.print(t('drive.insert_blank'))
        return 1

    liberi = supporto['settori']

    utilizzabile, descrizione, spiegazione = _valuta_supporto(supporto)
    if not utilizzabile:
        console.print(t('disc.unusable', reason=descrizione))
        console.print(f'[dim]{spiegazione}[/dim]\n')
        return 1

    sistema = _info_sistema()
    _pannello_unita(recorder, supporto, sistema)

    if spiegazione:
        console.print(f'[warning]{spiegazione}[/warning]')

    # Avviso sull'alimentazione solo dove serve davvero, cioe' su un'unita'
    # esterna: su una interna sarebbe rumore inutile a ogni masterizzazione.
    if (sistema['unita'].get(_lettera_unita(recorder)) or {}).get('connessione') == 'USB':
        console.print(t('drive.external_warning'))

    if stimati > liberi:
        console.print(t('disc.does_not_fit', need=f'{minuti:.1f}',
                        have=f'{_sectors_to_minutes(liberi):.1f}'))
        return 1

    # Velocita': esplicita da riga di comando, altrimenti la si chiede; con
    # --yes si prende la predefinita senza disturbare.
    if speed_x is not None or auto_si:
        velocita = _scegli_velocita(supporto['velocita'], speed_x or DEFAULT_SPEED_X)
    else:
        velocita = _chiedi_velocita(supporto['velocita'])

    if dry_run:
        console.print(t(
            'speed.would_use',
            arrow=SYM_ARROW,
            speed=_x(velocita) if velocita else t('common.automatic'),
            supported=', '.join(_x(v) for v in supporto['velocita']) or t('speed.none'),
        ))
        console.print(t('dry.passed', ok=SYM_OK))
        console.print(t('dry.nothing_touched'))
        return 0

    if not _check_temp_space():
        console.print(t('common.cancelled_op'))
        return 1

    if not auto_si:
        _passo(4, 4, t('step.burning'))

    audio = _crea_writer(recorder, velocita)
    if audio is None:
        return 1

    with tempfile.TemporaryDirectory(prefix='burndex_') as tmp:
        pcm_files, totale = [], 0
        with _progress() as progress:
            task = progress.add_task(t('burn.decoding'), total=len(tracce))
            for i, src in enumerate(tracce, 1):
                progress.update(task, description=os.path.basename(src))
                dst = os.path.join(tmp, f'{i:03d}.pcm')
                try:
                    totale += _decodifica(src, dst) + PREGAP_SECTORS
                except subprocess.CalledProcessError as exc:
                    log.error('ffmpeg fallito su %s: %s', src, exc.stderr)
                    console.print(t('burn.decode_failed', file=os.path.basename(src)))
                    return 1
                pcm_files.append(dst)
                progress.advance(task)
            progress.update(task, description=t('burn.decoded'))

        # Ricontrollo con i valori esatti: la stima da ffprobe puo' scostarsi
        # di qualche settore, e qui non c'e' piu' margine di errore.
        if totale > liberi:
            console.print(t('disc.does_not_fit_exact',
                            need=f'{_sectors_to_minutes(totale):.1f}',
                            have=f'{_sectors_to_minutes(liberi):.1f}'))
            return 1

        if not auto_si:
            if not _card_conferma(recorder, supporto, velocita, len(pcm_files), totale):
                console.print(t('confirm.disc_intact'))
                return 1

        nomi = [os.path.basename(p) for p in tracce]
        esito, scritte = _masterizza(audio, pcm_files, nomi)

    _mostra_riepilogo(scritte, len(pcm_files), _sectors_to_minutes(totale), esito)

    if esito and espelli:
        try:
            recorder.EjectMedia()
        except Exception as exc:
            log.warning('Espulsione fallita: %s', exc)

    log.info('Masterizzazione %s: %d/%d tracce scritte da %s',
             'riuscita' if esito else 'fallita', scritte, len(pcm_files), cartella)
    return 0 if esito else 1


def main() -> None:
    """Punto di ingresso: legge gli argomenti e avvia il flusso.

    Tre modalita' d'uso:
      - nessun argomento -> interattiva (sceglie la raccolta da download_audio);
      - --dir <cartella> -> masterizza quella cartella;
      - --info           -> elenca masterizzatori e disco inserito, senza scrivere.

    La lingua si risolve *prima* di costruire il parser: i testi di --help
    vengono composti mentre il parser si crea, e deciderla dopo significherebbe
    stampare sempre un aiuto nella lingua sbagliata.
    """
    _, lingua_da_chiedere = i18n.resolve()

    parser = argparse.ArgumentParser(
        description=t('cli.desc'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=t('cli.epilog'),
    )
    parser.add_argument('--dir', '-d', type=str, default=None,
                        help=t('cli.dir'))
    parser.add_argument('--base', '-b', type=str,
                        default=os.path.join(_HERE, 'download_audio'),
                        help=t('cli.base'))
    parser.add_argument('--speed', '-s', type=int, default=None,
                        help=t('cli.speed', default=DEFAULT_SPEED_X))
    parser.add_argument('--drive', type=int, default=None,
                        help=t('cli.drive'))
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help=t('cli.dry_run'))
    parser.add_argument('--info', '-i', action='store_true',
                        help=t('cli.info'))
    parser.add_argument('--yes', '-y', action='store_true',
                        help=t('cli.yes'))
    parser.add_argument('--no-eject', action='store_true',
                        help=t('cli.no_eject'))
    # Dichiarato anche se e' gia' stato letto a mano da i18n.resolve(): serve
    # perche' compaia in --help e perche' un valore fuori elenco venga
    # respinto da argparse invece di essere ignorato in silenzio.
    parser.add_argument('--lang', '-l', type=str, default=None,
                        choices=[*i18n.LANGUAGE_CODES, 'ask'],
                        help=t('cli.lang'))

    args = parser.parse_args()

    # La domanda sulla lingua precede il banner, che una riga di testo ce
    # l'ha: chiederla dopo farebbe vedere la prima schermata in una lingua e
    # tutto il resto nell'altra. Con --yes non si fanno domande di nessun
    # genere, nemmeno questa: e' la modalita' pensata per girare in uno script.
    i18n.confirm(lingua_da_chiedere and not args.yes)

    _print_banner()

    if not _check_tools():
        sys.exit(1)

    if args.info:
        if not _HAS_PYWIN32:
            console.print(t('tools.no_pywin32'))
            console.print(t('tools.install_pywin32'))
            sys.exit(1)
        pythoncom.CoInitialize()
        _modalita_info()
        return

    cartella = os.path.abspath(args.dir) if args.dir else _scegli_cartella(os.path.abspath(args.base))
    if not cartella:
        console.print(t('common.goodbye'))
        return
    if not os.path.isdir(cartella):
        console.print(t('common.folder_missing', path=cartella))
        sys.exit(1)

    try:
        codice = masterizza_cartella(
            cartella,
            speed_x=args.speed,
            dry_run=args.dry_run,
            auto_si=args.yes,
            espelli=not args.no_eject,
            indice_unita=args.drive,
        )
    except KeyboardInterrupt:
        # Durante la scrittura il Ctrl+C non ferma il laser: il disco e' perso
        # comunque, ma almeno l'unita' viene rilasciata da ReleaseMedia().
        console.print(t('common.interrupted'))
        codice = 1

    sys.exit(codice)


if __name__ == '__main__':
    main()
