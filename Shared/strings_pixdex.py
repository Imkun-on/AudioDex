"""Testi di PixDex in italiano e in inglese.

Stessa forma dei cataloghi di AudioDex e BurnDex: una voce per frase mostrata
all'utente, ``'chiave': {'it': ..., 'en': ...}``, segnaposto di ``str.format``.

Qui ricorre un tema che negli altri due non c'e': dire con chiarezza cosa il
programma *non* fa. Chi arriva alla rimasterizzazione dopo aver visto un video
di ingrandimento con l'intelligenza artificiale si aspetta un dettaglio che
non puo' arrivare, e una frase onesta al momento giusto vale piu' di dieci
opzioni in piu'.
"""
from __future__ import annotations

TESTI: dict[str, dict[str, str]] = {

    # ── Banner e struttura ───────────────────────────────────────────────────
    'banner.subtitle': {
        'it': 'Rimasterizzatore video',
        'en': 'Video remasterer',
    },
    'banner.tagline': {
        'it': 'pulizia, sbandatura, ingrandimento',
        'en': 'cleanup, debanding, upscaling',
    },
    'step.label': {
        'it': ' Passo {n}/{tot} ',
        'en': ' Step {n}/{tot} ',
    },
    'step.source': {'it': 'Sorgente', 'en': 'Source'},
    'step.diagnosis': {'it': 'Diagnosi', 'en': 'Diagnosis'},
    'step.quality': {'it': 'Risoluzione d\'arrivo', 'en': 'Target resolution'},
    'step.plan': {'it': 'Piano di lavoro', 'en': 'Work plan'},
    'step.remaster': {'it': 'Rimasterizzazione', 'en': 'Remastering'},

    # ── Scelta della risoluzione ─────────────────────────────────────────────
    # Le note accanto a ogni voce sono il punto di tutta la schermata: la
    # stessa tabella che offre il 4K dice, sulla stessa riga, quando quel 4K
    # non porterebbe un solo dettaglio in piu'.
    'quality.col_mode': {'it': 'Come', 'en': 'How'},
    'quality.col_result': {'it': 'Risultato', 'en': 'Result'},
    'quality.col_note': {'it': 'Quanto vale', 'en': 'What it is worth'},
    'quality.auto': {'it': 'Automatica', 'en': 'Automatic'},
    'quality.none': {'it': 'Solo pulizia', 'en': 'Cleanup only'},
    'quality.hd': {'it': 'HD  1080p', 'en': 'HD  1080p'},
    'quality.2k': {'it': '2K  1440p', 'en': '2K  1440p'},
    'quality.4k': {'it': '4K  2160p', 'en': '4K  2160p'},
    'quality.custom': {
        'it': 'Altra altezza…',
        'en': 'Another height…',
    },
    # I commenti stanno in una colonna da 18 caratteri: devono restare corti
    # o il riquadro spezza le parole a meta'. La spiegazione lunga sta nella
    # riga di aiuto sotto la tabella, dove c'e' spazio.
    'quality.note_native': {'it': 'originale', 'en': 'original'},
    'quality.note_ok': {'it': 'credibile', 'en': 'believable'},
    'quality.note_soft': {'it': 'si ammorbidisce', 'en': 'goes soft'},
    'quality.note_fake': {'it': 'solo piu\' pesante', 'en': 'just heavier'},
    'quality.hint': {
        'it': '[dim]★ la consigliata: si ferma al doppio, il limite oltre cui\n'
              '  l\'ingrandimento non aggiunge dettaglio ma solo peso.[/dim]',
        'en': '[dim]★ the suggested one: it stops at double, the limit past which\n'
              '  upscaling adds no detail, only size.[/dim]',
    },
    'quality.prompt': {
        'it': '\n[accent]Quale risoluzione[/accent] [dim](numero, invio per la consigliata)[/dim]: ',
        'en': '\n[accent]Which resolution[/accent] [dim](number, enter for the suggested one)[/dim]: ',
    },
    'quality.custom_prompt': {
        'it': '[accent]Altezza in pixel[/accent] [dim](es. 900)[/dim]: ',
        'en': '[accent]Height in pixels[/accent] [dim](e.g. 900)[/dim]: ',
    },
    'quality.invalid': {
        'it': '[warning]Scelta non valida:[/warning] [dim]uso quella consigliata.[/dim]',
        'en': '[warning]Invalid choice:[/warning] [dim]using the suggested one.[/dim]',
    },

    # ── Voci comuni ──────────────────────────────────────────────────────────
    'common.cancelled': {
        'it': '[dim]Annullato.[/dim]\n',
        'en': '[dim]Cancelled.[/dim]\n',
    },
    'common.goodbye': {
        'it': '[dim]Niente da fare, alla prossima.[/dim]\n',
        'en': '[dim]Nothing to do, see you next time.[/dim]\n',
    },
    'common.file_missing': {
        'it': '[error]Il file non esiste:[/error] {path}',
        'en': '[error]File does not exist:[/error] {path}',
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
    'probe.error': {
        'it': '[error]Nessun flusso video leggibile in[/error] {path}\n'
              '[dim]Un file di solo audio non ha niente da rimasterizzare.[/dim]',
        'en': '[error]No readable video stream in[/error] {path}\n'
              '[dim]An audio-only file has nothing to remaster.[/dim]',
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
    'choose.col_res': {'it': 'Risoluzione', 'en': 'Resolution'},
    'choose.col_size': {'it': 'Peso', 'en': 'Size'},
    'choose.hint': {
        'it': '[dim]I piu\' recenti per primi. Si puo\' anche incollare un percorso qualsiasi.[/dim]',
        'en': '[dim]Most recent first. You can also paste any path.[/dim]',
    },
    'choose.prompt': {
        'it': '\n[accent]Quale video[/accent] [dim](numero o percorso, invio per uscire)[/dim]: ',
        'en': '\n[accent]Which video[/accent] [dim](number or path, enter to quit)[/dim]: ',
    },

    # ── Carta d'identita' del file ───────────────────────────────────────────
    'info.title': {'it': ' Il file di partenza ', 'en': ' Source file '},
    'info.file': {'it': 'Nome', 'en': 'Name'},
    'info.resolution': {'it': 'Risoluzione', 'en': 'Resolution'},
    'info.fps': {'it': 'Fotogrammi al secondo', 'en': 'Frames per second'},
    'info.codec': {'it': 'Codifica', 'en': 'Codec'},
    'info.bitrate': {'it': 'Bitrate', 'en': 'Bitrate'},
    'info.duration': {'it': 'Durata', 'en': 'Duration'},
    'info.size': {'it': 'Peso', 'en': 'Size'},
    'info.scan': {'it': 'Scansione', 'en': 'Scan'},
    'info.interlaced': {
        'it': 'interlacciata [dim](materiale televisivo)[/dim]',
        'en': 'interlaced [dim](broadcast material)[/dim]',
    },

    # ── Diagnosi ─────────────────────────────────────────────────────────────
    'diag.title': {'it': ' Cosa c\'e\' da sistemare ', 'en': ' What needs fixing '},
    'diag.lowres': {
        'it': 'Risoluzione bassa ({h}p): l\'ingrandimento aiuta la resa a schermo '
              'intero, ma il dettaglio resta quello di partenza.',
        'en': 'Low resolution ({h}p): upscaling helps on a full screen, but the '
              'detail stays what it was.',
    },
    'diag.compressed': {
        'it': 'Compressione marcata ({bpp} bit per pixel): quadretti nelle scene '
              'scure e aloni intorno ai contorni.',
        'en': 'Heavy compression ({bpp} bits per pixel): blocking in dark scenes '
              'and halos around edges.',
    },
    'diag.very_compressed': {
        'it': 'Compressione estrema ({bpp} bit per pixel): il file e\' stato '
              'strizzato al punto che i difetti si vedono anche in movimento.',
        'en': 'Extreme compression ({bpp} bits per pixel): the file was squeezed '
              'so hard the artifacts show even in motion.',
    },
    'diag.interlaced': {
        'it': 'Immagine interlacciata: va separata in fotogrammi interi prima di '
              'qualunque altra lavorazione.',
        'en': 'Interlaced picture: it must be woven into whole frames before any '
              'other processing.',
    },
    'diag.banding_risk': {
        'it': 'Colore a 8 bit: cieli e dissolvenze tendono a mostrare bande a '
              'scalini, che la lavorazione a 10 bit appiana.',
        'en': '8-bit colour: skies and fades tend to show stepped bands, which '
              'the 10-bit pipeline smooths out.',
    },
    'diag.clean': {
        'it': 'Niente di grave: il file e\' gia\' in buono stato, basta una '
              'passata leggera.',
        'en': 'Nothing serious: the file is already in good shape, a light pass '
              'is enough.',
    },
    'diag.suggested': {'it': 'Preset consigliato:', 'en': 'Suggested preset:'},

    # ── Preset ───────────────────────────────────────────────────────────────
    'preset.pulito.name': {'it': 'Pulito', 'en': 'Clean'},
    'preset.pulito.desc': {
        'it': 'Toglie quadretti e bande, non ingrandisce. Il piu\' veloce.',
        'en': 'Removes blocking and banding, no upscaling. The fastest.',
    },
    'preset.standard.name': {'it': 'Standard', 'en': 'Standard'},
    'preset.standard.desc': {
        'it': 'Il caso normale di un video YouTube: pulizia misurata e '
              'ingrandimento.',
        'en': 'The normal YouTube case: measured cleanup plus upscaling.',
    },
    'preset.forte.name': {'it': 'Forte', 'en': 'Strong'},
    'preset.forte.desc': {
        'it': 'Sorgente molto rovinata. Accetta di perdere micro-dettaglio pur '
              'di togliere il disturbo.',
        'en': 'Badly degraded source. Trades micro-detail away to get rid of the '
              'noise.',
    },
    'preset.animazione.name': {'it': 'Animazione', 'en': 'Animation'},
    'preset.animazione.desc': {
        'it': 'Cartoni e anime: mano leggera sul disturbo per non mangiare le '
              'linee, mano pesante sulle bande.',
        'en': 'Cartoons and anime: light on noise so the linework survives, heavy '
              'on banding.',
    },
    'preset.vecchio.name': {'it': 'Vecchio', 'en': 'Vintage'},
    'preset.vecchio.desc': {
        'it': 'Materiale televisivo o da nastro: prima separa i semiquadri, poi '
              'pulisce a fondo.',
        'en': 'Broadcast or tape material: weaves the fields first, then cleans '
              'thoroughly.',
    },

    # ── Piano di lavoro ──────────────────────────────────────────────────────
    'plan.title': {'it': ' Cosa sto per fare ', 'en': ' What I am about to do '},
    'plan.preset': {'it': 'Preset', 'en': 'Preset'},
    'plan.resolution': {'it': 'Risoluzione', 'en': 'Resolution'},
    'plan.no_upscale': {'it': 'nessun ingrandimento', 'en': 'no upscaling'},
    'plan.encoder': {'it': 'Codificatore', 'en': 'Encoder'},
    'plan.audio': {'it': 'Audio', 'en': 'Audio'},
    'plan.audio_copy': {
        'it': 'copiato identico [dim](nessuna ricodifica, nessuna perdita)[/dim]',
        'en': 'copied as is [dim](no re-encode, no loss)[/dim]',
    },
    'plan.output': {'it': 'File in uscita', 'en': 'Output file'},
    'plan.filters': {'it': 'Catena di filtri', 'en': 'Filter chain'},
    'confirm.proceed': {
        'it': '\n[accent]Procedo?[/accent] [dim](invio per si\', n per annullare)[/dim]: ',
        'en': '\n[accent]Go ahead?[/accent] [dim](enter for yes, n to cancel)[/dim]: ',
    },

    # ── Lavorazione ──────────────────────────────────────────────────────────
    'run.working': {'it': 'Rimasterizzo', 'en': 'Remastering'},
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
    'result.resolution': {'it': 'Risoluzione', 'en': 'Resolution'},
    'result.size': {'it': 'Peso', 'en': 'Size'},
    'result.file': {'it': 'File', 'en': 'File'},
    'result.compare': {'it': 'Confronto', 'en': 'Comparison'},
    'result.compare_hint': {
        'it': 'a sinistra il file di partenza, a destra il rimasterizzato, alla '
              'stessa altezza per non barare',
        'en': 'source on the left, remaster on the right, at the same height so '
              'the comparison stays honest',
    },

    # ── Riga di comando ──────────────────────────────────────────────────────
    'cli.desc': {
        'it': 'PixDex — rimasterizza un video: toglie i difetti della '
              'compressione, appiana le bande e ingrandisce.',
        'en': 'PixDex — remaster a video: removes compression artifacts, smooths '
              'banding and upscales.',
    },
    'cli.epilog': {
        'it': 'Nota: nessun filtro puo\' ricostruire dettaglio che nel file non '
              'c\'e\'. PixDex lavora in sottrazione, togliendo il disturbo che '
              'nasconde il dettaglio rimasto.\n'
              'Esempi:\n'
              '  python PixDex.py                        procedura guidata\n'
              '  python PixDex.py -i video.mp4 --info    solo analisi, non scrive\n'
              '  python PixDex.py -i video.mp4 -p forte  preset esplicito\n'
              '  python PixDex.py -i video.mp4 --gpu -y  veloce, senza domande',
        'en': 'Note: no filter can rebuild detail that is not in the file. PixDex '
              'works by subtraction, removing the noise that hides the detail '
              'still there.\n'
              'Examples:\n'
              '  python PixDex.py                        guided procedure\n'
              '  python PixDex.py -i video.mp4 --info    analysis only, writes nothing\n'
              '  python PixDex.py -i video.mp4 -p forte  explicit preset\n'
              '  python PixDex.py -i video.mp4 --gpu -y  fast, no questions',
    },
    'cli.input': {
        'it': 'Video da rimasterizzare (senza, li elenca e li fa scegliere)',
        'en': 'Video to remaster (without it, they are listed to choose from)',
    },
    'cli.output': {
        'it': 'File di destinazione (default: accanto all\'originale, col suffisso PixDex)',
        'en': 'Destination file (default: next to the original, with a PixDex suffix)',
    },
    'cli.base': {
        'it': 'Cartella in cui cercare i video (default: download_audio)',
        'en': 'Folder to look for videos in (default: download_audio)',
    },
    'cli.preset': {
        'it': 'Preset da usare; senza, lo sceglie la diagnosi',
        'en': 'Preset to use; without it, the diagnosis picks one',
    },
    'cli.height': {
        'it': 'Risoluzione d\'arrivo: auto (fino al doppio), none (solo pulizia), '
              'hd, 2k, 4k, oppure un\'altezza in pixel. Senza, la si sceglie a schermo',
        'en': 'Target resolution: auto (up to double), none (cleanup only), '
              'hd, 2k, 4k, or a height in pixels. Without it, you pick it on screen',
    },
    'cli.crf': {
        'it': 'Qualita\' di libx264: piu\' basso = migliore e piu\' pesante (default {default})',
        'en': 'libx264 quality: lower = better and heavier (default {default})',
    },
    'cli.gpu': {
        'it': 'Usa il codificatore hardware AMD: molto piu\' veloce, un filo meno pulito',
        'en': 'Use the AMD hardware encoder: much faster, slightly less clean',
    },
    'cli.no_compare': {
        'it': 'Non salvare l\'immagine di confronto prima/dopo',
        'en': 'Do not save the before/after comparison image',
    },
    'cli.info': {
        'it': 'Analizza il file e mostra la diagnosi, senza rimasterizzare',
        'en': 'Analyse the file and show the diagnosis, without remastering',
    },
    'cli.yes': {
        'it': 'Nessuna domanda: usa il preset consigliato e parte',
        'en': 'No questions: use the suggested preset and start',
    },
}
