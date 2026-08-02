"""Testi di ClipDex in italiano e in inglese.

Stessa forma degli altri cataloghi: una voce per frase mostrata all'utente,
``'chiave': {'it': ..., 'en': ...}``, segnaposto di ``str.format``.

Il tema ricorrente qui e' la distinzione fra copia e ricodifica: e' la scelta
che governa tempi, qualita' e vincoli di ogni operazione, e va detta a chi usa
il programma ogni volta che il programma la compie al posto suo.
"""
from __future__ import annotations

TESTI: dict[str, dict[str, str]] = {

    # ── Banner e struttura ───────────────────────────────────────────────────
    'banner.subtitle': {
        'it': 'Montaggio e conversione',
        'en': 'Editing and conversion',
    },
    'banner.tagline': {
        'it': 'taglia, unisci, GIF, provini',
        'en': 'cut, join, GIFs, contact sheets',
    },
    'step.label': {'it': ' Passo {n}/{tot} ', 'en': ' Step {n}/{tot} '},
    'step.inputs': {'it': 'File di partenza', 'en': 'Source files'},
    'step.working': {'it': 'Lavorazione', 'en': 'Processing'},

    # ── Menu delle operazioni ────────────────────────────────────────────────
    'menu.col_action': {'it': 'Operazione', 'en': 'Operation'},
    'menu.col_desc': {'it': 'Cosa fa', 'en': 'What it does'},
    'menu.taglia': {
        'it': 'Estrae uno spezzone. In copia e\' istantaneo',
        'en': 'Extracts a segment. In copy mode it is instant',
    },
    'menu.unisci': {
        'it': 'Mette in fila piu\' file, con un capitolo per ciascuno',
        'en': 'Puts several files in a row, one chapter each',
    },
    'menu.gif': {
        'it': 'Ricava una GIF con la palette calcolata sul filmato',
        'en': 'Makes a GIF with the palette computed on the footage',
    },
    'menu.webp': {
        'it': 'Come la GIF ma in WebP: pesa quasi nove volte meno',
        'en': 'Like the GIF but in WebP: almost nine times lighter',
    },
    'menu.provino': {
        'it': 'Una griglia di fotogrammi per capire cosa c\'e\' dentro',
        'en': 'A grid of frames to see what is inside at a glance',
    },
    'menu.compat': {
        'it': 'H.264 leggibile da autoradio e TV datate',
        'en': 'H.264 that old car stereos and TVs can read',
    },
    'menu.prompt': {
        'it': '\n[accent]Quale operazione[/accent] [dim](numero o nome, invio per uscire)[/dim]: ',
        'en': '\n[accent]Which operation[/accent] [dim](number or name, enter to quit)[/dim]: ',
    },

    # ── Scelta del file ──────────────────────────────────────────────────────
    'choose.none': {
        'it': '[warning]Nessun video in[/warning] {path}',
        'en': '[warning]No video found in[/warning] {path}',
    },
    'choose.ask_path': {
        'it': '\n[accent]Percorso del video[/accent] [dim](invio per uscire)[/dim]: ',
        'en': '\n[accent]Path to the video[/accent] [dim](enter to quit)[/dim]: ',
    },
    'choose.col_file': {'it': 'File', 'en': 'File'},
    'choose.col_dur': {'it': 'Durata', 'en': 'Length'},
    'choose.col_size': {'it': 'Peso', 'en': 'Size'},
    'choose.prompt': {
        'it': '\n[accent]Quale video[/accent] [dim](numero o percorso, invio per uscire)[/dim]: ',
        'en': '\n[accent]Which video[/accent] [dim](number or path, enter to quit)[/dim]: ',
    },

    # ── Taglio ───────────────────────────────────────────────────────────────
    'cut.ask_from': {
        'it': '[accent]Da che punto[/accent] [dim](es. 1:20)[/dim]: ',
        'en': '[accent]From where[/accent] [dim](e.g. 1:20)[/dim]: ',
    },
    'cut.ask_to': {
        'it': '[accent]Fino a[/accent] [dim](invio = fino alla fine)[/dim]: ',
        'en': '[accent]Up to[/accent] [dim](enter = to the end)[/dim]: ',
    },
    'cut.note_copy': {
        'it': 'tagliato in copia: nessuna perdita, ma l\'inizio si aggancia al '
              'fotogramma chiave piu\' vicino',
        'en': 'cut in copy mode: no loss, but the start snaps to the nearest '
              'keyframe',
    },
    'cut.note_drift': {
        'it': 'chiesti {chiesta} s, ottenuti {reale}: {scarto} s in piu\'. In copia '
              'l\'inizio si aggancia al fotogramma chiave precedente, e in questo '
              'file sono distanziati. Con --preciso il taglio cade dove hai detto, '
              'al prezzo di una ricodifica',
        'en': '{chiesta} s asked, {reale} obtained: {scarto} s more. In copy mode '
              'the start snaps back to the previous keyframe, and in this file they '
              'are far apart. With --preciso the cut lands where you said, at the '
              'cost of a re-encode',
    },
    'cut.note_precise': {
        'it': 'tagliato al fotogramma esatto, quindi ricodificato',
        'en': 'cut at the exact frame, therefore re-encoded',
    },

    # ── Unione ───────────────────────────────────────────────────────────────
    'merge.item': {
        'it': '  [dim]{n:>2}.[/dim] {file}  [dim]{durata}[/dim]',
        'en': '  [dim]{n:>2}.[/dim] {file}  [dim]{durata}[/dim]',
    },
    'merge.mode_copy': {
        'it': '\n[bright_green]I file sono omogenei:[/bright_green] li unisco in '
              'copia, senza ricodificare.',
        'en': '\n[bright_green]The files match:[/bright_green] joining them in '
              'copy mode, without re-encoding.',
    },
    'merge.mode_encode': {
        'it': '\n[warning]I file hanno formati diversi:[/warning] li porto tutti '
              'alla misura del primo e ricodifico. Ci vorra\' di piu\'.',
        'en': '\n[warning]The files differ:[/warning] bringing them all to the '
              'size of the first one and re-encoding. This will take longer.',
    },
    'merge.need_inputs': {
        'it': '[error]Serve indicare i file da unire[/error] [dim](--input a.mp4 '
              'b.mp4, oppure --dir cartella)[/dim]',
        'en': '[error]You must say which files to join[/error] [dim](--input a.mp4 '
              'b.mp4, or --dir folder)[/dim]',
    },
    'merge.need_two': {
        'it': '[error]Per unire servono almeno due file.[/error]',
        'en': '[error]Joining needs at least two files.[/error]',
    },
    'merge.note_chapters': {
        'it': 'un capitolo per ciascuno dei {n} file: il risultato resta navigabile',
        'en': 'one chapter per each of the {n} files: the result stays navigable',
    },

    # ── GIF, WebP, provino, compatibilita' ───────────────────────────────────
    'gif.note': {
        'it': 'da {inizio}, {durata} s, {fps} fotogrammi al secondo, largo {w} px',
        'en': 'from {inizio}, {durata} s, {fps} frames per second, {w} px wide',
    },
    'sheet.note': {
        'it': '{n} fotogrammi, uno ogni {ogni} circa, distribuiti su tutta la durata',
        'en': '{n} frames, roughly one every {ogni}, spread across the whole length',
    },
    'compat.note': {
        'it': 'H.264 baseline, colore yuv420p, indice in testa al file: le tre '
              'cose che gli apparecchi datati pretendono',
        'en': 'H.264 baseline, yuv420p colour, index at the head of the file: the '
              'three things old devices insist on',
    },

    # ── Lavorazione ──────────────────────────────────────────────────────────
    'run.cutting': {'it': 'Taglio', 'en': 'Cutting'},
    'run.merging': {'it': 'Unione', 'en': 'Joining'},
    'run.gif': {'it': 'Creo la GIF', 'en': 'Building the GIF'},
    'run.webp': {'it': 'Creo il WebP', 'en': 'Building the WebP'},
    'run.sheet': {'it': 'Compongo il provino', 'en': 'Composing the sheet'},
    'run.compat': {'it': 'Riconverto', 'en': 'Converting'},
    'run.failed': {
        'it': '\n[error]FFmpeg si e\' fermato.[/error]\n[dim]{reason}[/dim]',
        'en': '\n[error]FFmpeg stopped.[/error]\n[dim]{reason}[/dim]',
    },
    'run.interrupted': {
        'it': '\n[warning]Interrotto.[/warning] [dim]Il file parziale resta sul disco.[/dim]',
        'en': '\n[warning]Interrupted.[/warning] [dim]The partial file stays on disk.[/dim]',
    },

    # ── Risultato ────────────────────────────────────────────────────────────
    'result.title': {'it': ' Fatto ', 'en': ' Done '},
    'result.file': {'it': 'File', 'en': 'File'},
    'result.size': {'it': 'Peso', 'en': 'Size'},
    'result.video': {'it': 'Video', 'en': 'Video'},

    # ── Errori ───────────────────────────────────────────────────────────────
    'error.unreadable': {
        'it': '[error]Nessun flusso video leggibile in[/error] {path}',
        'en': '[error]No readable video stream in[/error] {path}',
    },
    'error.missing': {
        'it': '[error]Il file non esiste:[/error] {path}',
        'en': '[error]File does not exist:[/error] {path}',
    },
    'error.empty_range': {
        'it': '[error]L\'intervallo e\' vuoto:[/error] [dim]la fine deve venire '
              'dopo l\'inizio.[/dim]',
        'en': '[error]The range is empty:[/error] [dim]the end must come after '
              'the start.[/dim]',
    },
    'error.bad_time': {
        'it': '[error]Tempo non riconosciuto.[/error] [dim]Usa 90, 1:30 oppure '
              '01:02:03.5[/dim]',
        'en': '[error]Time not recognised.[/error] [dim]Use 90, 1:30 or '
              '01:02:03.5[/dim]',
    },
    'error.bad_grid': {
        'it': '[error]Griglia non valida:[/error] {valore} [dim](usa la forma 4x4)[/dim]',
        'en': '[error]Invalid grid:[/error] {valore} [dim](use the form 4x4)[/dim]',
    },
    'common.goodbye': {
        'it': '[dim]Niente da fare, alla prossima.[/dim]\n',
        'en': '[dim]Nothing to do, see you next time.[/dim]\n',
    },

    # ── Strumenti esterni ────────────────────────────────────────────────────
    'tools.no_ffmpeg': {
        'it': '[error]Manca all\'appello:[/error] {tools}',
        'en': '[error]Missing from PATH:[/error] {tools}',
    },
    'tools.install_ffmpeg': {
        'it': '[dim]FFmpeg non e\' installabile con pip. Su Windows:[/dim]\n'
              '  [accent]winget install Gyan.FFmpeg[/accent]\n'
              '[dim]poi riapri il terminale, cosi\' il PATH viene riletto.[/dim]',
        'en': '[dim]FFmpeg cannot be installed with pip. On Windows:[/dim]\n'
              '  [accent]winget install Gyan.FFmpeg[/accent]\n'
              '[dim]then reopen the terminal so PATH is read again.[/dim]',
    },

    # ── Riga di comando ──────────────────────────────────────────────────────
    'cli.desc': {
        'it': 'ClipDex — taglia, unisce e converte i video: spezzoni, montaggi, '
              'GIF, provini e ricodifiche per apparecchi datati.',
        'en': 'ClipDex — cuts, joins and converts videos: segments, edits, GIFs, '
              'contact sheets and conversions for old devices.',
    },
    'cli.epilog': {
        'it': 'Senza sottocomando parte la procedura guidata.\n'
              'Esempi:\n'
              '  python ClipDex.py taglia -i v.mp4 --da 1:20 --a 3:45\n'
              '  python ClipDex.py unisci -d "download_audio/Album"\n'
              '  python ClipDex.py gif -i v.mp4 --da 0:30 --durata 4\n'
              '  python ClipDex.py provino -i v.mp4 --griglia 5x3\n'
              '  python ClipDex.py compat -i v.mp4',
        'en': 'Without a subcommand the guided procedure starts.\n'
              'Examples:\n'
              '  python ClipDex.py taglia -i v.mp4 --da 1:20 --a 3:45\n'
              '  python ClipDex.py unisci -d "download_audio/Album"\n'
              '  python ClipDex.py gif -i v.mp4 --da 0:30 --durata 4\n'
              '  python ClipDex.py provino -i v.mp4 --griglia 5x3\n'
              '  python ClipDex.py compat -i v.mp4',
    },
    'cli.base': {
        'it': 'Cartella in cui cercare i video (default: download_audio)',
        'en': 'Folder to look for videos in (default: download_audio)',
    },
    'cli.crf': {
        'it': 'Qualita\' quando si ricodifica: piu\' basso = migliore e piu\' '
              'pesante (default {default})',
        'en': 'Quality when re-encoding: lower = better and heavier (default {default})',
    },
    'cli.input': {
        'it': 'File di partenza (senza, li elenca e li fa scegliere)',
        'en': 'Source file (without it, they are listed to choose from)',
    },
    'cli.input_multi': {
        'it': 'File da unire, nell\'ordine in cui vanno messi',
        'en': 'Files to join, in the order they should appear',
    },
    'cli.dir': {
        'it': 'Unisci tutti i video di questa cartella, in ordine di nome',
        'en': 'Join every video in this folder, in filename order',
    },
    'cli.output': {
        'it': 'File di destinazione (default: accanto all\'originale)',
        'en': 'Destination file (default: next to the original)',
    },
    'cli.da': {
        'it': 'Da che punto partire (90, 1:30 oppure 01:02:03.5)',
        'en': 'Where to start from (90, 1:30 or 01:02:03.5)',
    },
    'cli.a': {
        'it': 'Fino a che punto (senza, fino alla fine)',
        'en': 'Where to stop (without it, to the end)',
    },
    'cli.durata': {
        'it': 'Quanto deve durare (senza, 5 secondi)',
        'en': 'How long it should last (without it, 5 seconds)',
    },
    'cli.preciso': {
        'it': 'Taglia al fotogramma esatto invece che al fotogramma chiave: '
              'ricodifica, quindi molto piu\' lento',
        'en': 'Cut at the exact frame instead of the keyframe: re-encodes, so '
              'much slower',
    },
    'cli.no_chapters': {
        'it': 'Non inserire un capitolo per ogni file unito',
        'en': 'Do not insert a chapter for each joined file',
    },
    'cli.fps': {
        'it': 'Fotogrammi al secondo (default {default}: sopra, il peso raddoppia '
              'senza guadagno visibile)',
        'en': 'Frames per second (default {default}: above that, the size doubles '
              'for no visible gain)',
    },
    'cli.larghezza': {
        'it': 'Larghezza in pixel (default {default}): e\' il fattore che pesa di piu\'',
        'en': 'Width in pixels (default {default}): it is the factor that weighs most',
    },
    'cli.griglia': {
        'it': 'Griglia del provino, nella forma colonne x righe (es. 5x3)',
        'en': 'Contact sheet grid, as columns x rows (e.g. 5x3)',
    },
}
