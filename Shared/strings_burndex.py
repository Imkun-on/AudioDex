"""Testi di BurnDex in italiano e in inglese.

Stessa forma del catalogo di AudioDex: una voce per frase mostrata
all'utente, ``'chiave': {'it': ..., 'en': ...}``, segnaposto di
``str.format``.

Qui il peso delle frasi lunghe e' maggiore che in AudioDex, ed e' voluto: su
un CD-R non si torna indietro, quindi ogni diagnosi spiega anche *cosa fare*.
Le traduzioni conservano la stessa struttura a elenco numerato, perche' e'
quella che si segue davvero mentre si cerca di capire perche' una
masterizzazione e' fallita.
"""
from __future__ import annotations

TESTI: dict[str, dict[str, str]] = {

    # ── Banner e struttura ───────────────────────────────────────────────────
    'banner.subtitle': {
        'it': 'Masterizzatore di CD audio',
        'en': 'Audio CD burner',
    },
    'banner.standard': {
        'it': 'standard Red Book CD-DA',
        'en': 'Red Book CD-DA standard',
    },
    'step.label': {
        'it': ' Passo {n}/{tot} ',
        'en': ' Step {n}/{tot} ',
    },
    'step.collection': {'it': 'Raccolta', 'en': 'Collection'},
    'step.tracklist': {'it': 'Scaletta', 'en': 'Track list'},
    'step.disc_speed': {'it': 'Disco e velocita\'', 'en': 'Disc and speed'},
    'step.burning': {'it': 'Masterizzazione', 'en': 'Burning'},

    # ── Voci comuni ──────────────────────────────────────────────────────────
    'common.cancelled': {
        'it': '[dim]Annullato.[/dim]\n',
        'en': '[dim]Cancelled.[/dim]\n',
    },
    'common.cancelled_op': {
        'it': '[error]Operazione annullata.[/error]',
        'en': '[error]Operation cancelled.[/error]',
    },
    'common.goodbye': {
        'it': '\n[dim]Arrivederci![/dim]\n',
        'en': '\n[dim]Goodbye![/dim]\n',
    },
    'common.invalid_choice': {
        'it': '[error]Scelta non valida.[/error]',
        'en': '[error]Invalid choice.[/error]',
    },
    'common.invalid_choice_retry': {
        'it': '[error]Scelta non valida. Riprova.[/error]',
        'en': '[error]Invalid choice. Try again.[/error]',
    },
    'common.invalid_selection': {
        'it': '[error]Selezione non valida. Riprova.[/error]',
        'en': '[error]Invalid selection. Try again.[/error]',
    },
    'common.interrupted': {
        'it': '\n[warning]Interrotto dall\'utente.[/warning]\n',
        'en': '\n[warning]Interrupted by the user.[/warning]\n',
    },
    'common.continue': {
        'it': '[bold]Continuare? (s/n): [/bold]',
        'en': '[bold]Continue? (y/n): [/bold]',
    },
    'common.min': {'it': 'min', 'en': 'min'},
    'common.automatic': {'it': 'automatica', 'en': 'automatic'},
    'common.empty': {'it': 'vuoto', 'en': 'empty'},
    'common.folder_missing': {
        'it': '[error]Cartella inesistente: {path}[/error]',
        'en': '[error]Folder does not exist: {path}[/error]',
    },

    # ── Tipi di disco ────────────────────────────────────────────────────────
    'media.unknown': {'it': 'sconosciuto', 'en': 'unknown'},
    'media.disc': {'it': 'disco', 'en': 'disc'},

    # ── Strumenti esterni ────────────────────────────────────────────────────
    'tools.missing': {
        'it': '\n[error]{tools} non trovato nel PATH.[/error]',
        'en': '\n[error]{tools} not found in PATH.[/error]',
    },
    'tools.install_ffmpeg': {
        'it': '[dim]Installa con: winget install Gyan.FFmpeg[/dim]\n',
        'en': '[dim]Install with: winget install Gyan.FFmpeg[/dim]\n',
    },
    'tools.no_pywin32': {
        'it': '\n[error]pywin32 non installato.[/error]',
        'en': '\n[error]pywin32 not installed.[/error]',
    },
    'tools.no_pywin32_burn': {
        'it': '\n[error]pywin32 non installato: impossibile masterizzare.[/error]',
        'en': '\n[error]pywin32 not installed: cannot burn.[/error]',
    },
    'tools.no_pywin32_skip': {
        'it': '[dim]pywin32 non installato: controllo dell\'unita\' saltato.[/dim]\n',
        'en': '[dim]pywin32 not installed: drive check skipped.[/dim]\n',
    },
    'tools.install_pywin32': {
        'it': '[dim]Installa con: pip install pywin32[/dim]\n',
        'en': '[dim]Install with: pip install pywin32[/dim]\n',
    },

    # ── Spazio temporaneo ────────────────────────────────────────────────────
    'temp.low': {
        'it': '\n[warning]ATTENZIONE: solo {free} MB liberi per i file '
              'temporanei (ne servono ~{need}).[/warning]',
        'en': '\n[warning]WARNING: only {free} MB free for temporary files '
              '(~{need} are needed).[/warning]',
    },

    # ── Ordinamento delle tracce ─────────────────────────────────────────────
    'order.file': {'it': 'ordine.txt', 'en': 'ordine.txt'},
    'order.number': {
        'it': 'numero di traccia nel nome',
        'en': 'track number in the filename',
    },
    'order.created': {
        'it': 'data di creazione',
        'en': 'file creation date',
    },
    'order.missing_file': {
        'it': '[error]ordine.txt cita un file inesistente: {name}[/error]',
        'en': '[error]ordine.txt lists a file that does not exist: {name}[/error]',
    },

    # ── Scelta della raccolta ────────────────────────────────────────────────
    'collection.none_found': {
        'it': '[error]Nessuna raccolta trovata in {base}[/error]',
        'en': '[error]No collection found in {base}[/error]',
    },
    'collection.column': {'it': 'Raccolta', 'en': 'Collection'},
    'collection.tracks': {'it': 'Tracce', 'en': 'Tracks'},
    'collection.duration': {'it': 'Durata', 'en': 'Duration'},
    'collection.scanning': {
        'it': '[dim]Analisi delle raccolte...[/dim]',
        'en': '[dim]Scanning collections...[/dim]',
    },
    'collection.singles': {
        'it': '[dim]brani singoli[/dim]',
        'en': '[dim]single tracks[/dim]',
    },
    'collection.prompt': {
        'it': '\n{disc} [bold]Quale raccolta? (numero, invio per uscire) > [/bold]',
        'en': '\n{disc} [bold]Which collection? (number, Enter to quit) > [/bold]',
    },
    'collection.default_name': {'it': 'Raccolta', 'en': 'Collection'},
    'collection.no_audio': {
        'it': '[error]Nessun file audio in {path}[/error]',
        'en': '[error]No audio file in {path}[/error]',
    },
    'collection.selection_suffix': {
        'it': '{name} · selezione',
        'en': '{name} · selection',
    },

    # ── Scaletta ─────────────────────────────────────────────────────────────
    'tracklist.column': {'it': 'Traccia', 'en': 'Track'},
    'tracklist.duration': {'it': 'Durata', 'en': 'Duration'},
    'tracklist.count': {
        'it': '[dim]{n} tracce[/dim]',
        'en': '[dim]{n} tracks[/dim]',
    },
    'tracklist.order_note': {
        'it': '[dim]Ordine: {criterion}  ·  stacchi da 2 s inclusi nel totale[/dim]',
        'en': '[dim]Order: {criterion}  ·  2 s gaps included in the total[/dim]',
    },
    'tracklist.unreadable': {
        'it': '[error]File illeggibili: {files}[/error]',
        'en': '[error]Unreadable files: {files}[/error]',
    },

    # ── Selezione delle tracce ───────────────────────────────────────────────
    'select.hint': {
        'it': '\n[dim_label]Quali tracce:[/dim_label] numero singolo ([accent]3[/accent]), '
              'intervallo ([accent]1-5[/accent]), multipli ([accent]1,3,7[/accent]), '
              '[accent]invio[/accent] per tutte, [accent]q[/accent] per annullare',
        'en': '\n[dim_label]Which tracks:[/dim_label] a single number ([accent]3[/accent]), '
              'a range ([accent]1-5[/accent]), a list ([accent]1,3,7[/accent]), '
              '[accent]Enter[/accent] for all, [accent]q[/accent] to cancel',
    },
    'select.prompt': {
        'it': '\n[bold]Scegli > [/bold]',
        'en': '\n[bold]Choose > [/bold]',
    },
    'select.too_long_pick': {
        'it': '[warning]Non ci stanno tutte: {over} min oltre il limite di {limit}. '
              'Scegli quali masterizzare.[/warning]',
        'en': '[warning]They do not all fit: {over} min over the {limit} limit. '
              'Pick which ones to burn.[/warning]',
    },

    # ── Unita' e disco ───────────────────────────────────────────────────────
    'drive.panel_title': {
        'it': '[bold bright_blue]Unita\' pronta[/bold bright_blue]',
        'en': '[bold bright_blue]Drive ready[/bold bright_blue]',
    },
    'drive.burner': {'it': 'Masterizzatore', 'en': 'Burner'},
    'drive.disc': {'it': 'Disco', 'en': 'Disc'},
    'drive.speed': {'it': 'Velocita\'', 'en': 'Speed'},
    'drive.capacity': {
        'it': '[dim]vuoto · {min} min di capienza[/dim]',
        'en': '[dim]empty · {min} min capacity[/dim]',
    },
    'drive.none_detected': {
        'it': '[error]Nessun masterizzatore rilevato. Collegalo e riprova.[/error]',
        'en': '[error]No burner detected. Connect one and try again.[/error]',
    },
    'drive.index_missing': {
        'it': '[error]Unita\' {index} inesistente (ne risultano {total}).[/error]',
        'en': '[error]Drive {index} does not exist ({total} found).[/error]',
    },
    'drive.available': {
        'it': '\n[dim_label]Masterizzatori disponibili:[/dim_label]',
        'en': '\n[dim_label]Available burners:[/dim_label]',
    },
    'drive.which': {
        'it': '[bold]Quale? > [/bold]',
        'en': '[bold]Which one? > [/bold]',
    },
    'drive.no_readable_disc': {
        'it': '\n[error]Nessun disco leggibile nell\'unita\'.[/error]',
        'en': '\n[error]No readable disc in the drive.[/error]',
    },
    'drive.insert_blank': {
        'it': '[dim]Inserisci un CD-R vuoto e riprova.[/dim]\n',
        'en': '[dim]Insert a blank CD-R and try again.[/dim]\n',
    },
    'drive.external_warning': {
        'it': '[dim]Unita\' esterna: se la scrittura si interrompe a meta\', '
              'e\' quasi sempre\nla porta USB che non regge l\'assorbimento del '
              'laser.[/dim]',
        'en': '[dim]External drive: if writing stops halfway, it is almost always\n'
              'the USB port failing to supply what the laser draws.[/dim]',
    },

    # ── Scelta della velocita' ───────────────────────────────────────────────
    'speed.column': {'it': 'Velocita\'', 'en': 'Speed'},
    'speed.result': {'it': 'Resa', 'en': 'Result'},
    'speed.recommended': {
        'it': '[success]consigliata[/success][dim] — incisione piu\' netta, '
              'la piu\' sicura per autoradio e stereo datati[/dim]',
        'en': '[success]recommended[/success][dim] — cleaner burn, the safest '
              'for car stereos and older players[/dim]',
    },
    'speed.fastest': {
        'it': '[dim]la piu\' rapida, ma qualche lettore vecchio puo\' faticare[/dim]',
        'en': '[dim]the fastest, but some old players may struggle[/dim]',
    },
    'speed.middle': {
        'it': '[dim]via di mezzo[/dim]',
        'en': '[dim]a middle ground[/dim]',
    },
    'speed.prompt': {
        'it': '\n[bold]A che velocita\' scrivo? (1-{n} · invio = {default}): [/bold]',
        'en': '\n[bold]At what speed should I write? (1-{n} · Enter = {default}): [/bold]',
    },
    'speed.writing_at': {
        'it': '{arrow} [dim_label]Velocita\' di scrittura:[/dim_label] [info]{speed}[/info]',
        'en': '{arrow} [dim_label]Write speed:[/dim_label] [info]{speed}[/info]',
    },
    'speed.refused': {
        'it': '[warning]L\'unita\' rifiuta l\'impostazione: uso la velocita\' '
              'automatica.[/warning]',
        'en': '[warning]The drive refuses the setting: falling back to automatic '
              'speed.[/warning]',
    },
    'speed.would_use': {
        'it': '\n{arrow} [dim_label]Velocita\' che verrebbe usata:[/dim_label] '
              '[info]{speed}[/info] [dim](supportate: {supported})[/dim]',
        'en': '\n{arrow} [dim_label]Speed that would be used:[/dim_label] '
              '[info]{speed}[/info] [dim](supported: {supported})[/dim]',
    },
    'speed.none': {'it': 'n/d', 'en': 'n/a'},

    # ── Conferma finale ──────────────────────────────────────────────────────
    'confirm.title': {
        'it': '[bold bright_magenta]💿  Pronto a masterizzare[/bold bright_magenta]',
        'en': '[bold bright_magenta]💿  Ready to burn[/bold bright_magenta]',
    },
    'confirm.subtitle': {
        'it': '[bold red]la scrittura su CD-R e\' irreversibile[/bold red]',
        'en': '[bold red]writing to a CD-R cannot be undone[/bold red]',
    },
    'confirm.drive': {'it': 'Unita\'', 'en': 'Drive'},
    'confirm.disc': {'it': 'Disco', 'en': 'Disc'},
    'confirm.speed': {'it': 'Velocita\'', 'en': 'Speed'},
    'confirm.tracks': {'it': 'Tracce', 'en': 'Tracks'},
    'confirm.audio': {'it': 'Audio', 'en': 'Audio'},
    'confirm.levelled': {
        'it': '[bright_green]volume livellato[/bright_green]',
        'en': '[bright_green]volume levelled[/bright_green]',
    },
    'confirm.trimmed': {
        'it': '[bright_green]silenzi rifilati[/bright_green]',
        'en': '[bright_green]silence trimmed[/bright_green]',
    },
    'confirm.audio_untouched': {
        'it': 'nessuna modifica, solo dither a 16 bit',
        'en': 'untouched, only 16-bit dithering',
    },
    'confirm.duration': {'it': 'Durata', 'en': 'Duration'},
    'confirm.free_after': {
        'it': '[dim]({min} min liberi dopo)[/dim]',
        'en': '[dim]({min} min free afterwards)[/dim]',
    },
    'confirm.prompt': {
        'it': '\n[bold]Procedo con la masterizzazione? (s/n): [/bold]',
        'en': '\n[bold]Go ahead and burn? (y/n): [/bold]',
    },
    'confirm.disc_intact': {
        'it': '[dim]Annullato. Il disco e\' intatto.[/dim]\n',
        'en': '[dim]Cancelled. The disc is untouched.[/dim]\n',
    },

    # ── Ricognizione del sistema ─────────────────────────────────────────────
    'system.panel_title': {
        'it': '[bold bright_blue]Il tuo sistema[/bold bright_blue]',
        'en': '[bold bright_blue]Your system[/bold bright_blue]',
    },
    'system.computer': {'it': 'Computer', 'en': 'Computer'},
    'system.laptop': {'it': 'PC portatile', 'en': 'Laptop'},
    'system.desktop': {'it': 'PC fisso', 'en': 'Desktop PC'},
    'system.unknown_type': {
        'it': 'tipo non riconosciuto',
        'en': 'type not recognised',
    },
    'system.cd_drive': {'it': 'Lettore CD', 'en': 'CD drive'},
    'system.none_detected': {
        'it': '[error]nessuno rilevato[/error]',
        'en': '[error]none detected[/error]',
    },
    'system.drive_label': {'it': 'Unita\' {letter}', 'en': 'Drive {letter}'},
    'system.usb_external': {
        'it': '[warning]collegata in USB (esterna)[/warning]',
        'en': '[warning]connected over USB (external)[/warning]',
    },
    'system.internal': {
        'it': '[success]interna[/success]',
        'en': '[success]internal[/success]',
    },
    'system.advice_none': {
        'it': '[error]Questo computer non ha nessun lettore CD.[/error]\n'
              '[dim]Per masterizzare serve un masterizzatore esterno USB. Su un '
              'portatile\nrecente e\' la norma: i lettori interni non si montano '
              'piu\' da anni.[/dim]',
        'en': '[error]This computer has no CD drive at all.[/error]\n'
              '[dim]Burning needs an external USB burner. On a recent laptop that '
              'is\nnormal: internal drives have not been fitted for years.[/dim]',
    },
    'system.advice_usb': {
        'it': '[warning]L\'unita\' e\' esterna e si alimenta dalla porta USB.[/warning]\n'
              '[dim]In scrittura il laser assorbe molto piu\' che in lettura, e una '
              'porta al limite\nfa riavviare l\'unita\' a meta\' masterizzazione. '
              'Se una scrittura fallisce:\n'
              '  1. collega entrambi gli spinotti, se il cavo ne ha due\n'
              '  2. usa una porta diretta sul PC, mai un hub non alimentato[/dim]',
        'en': '[warning]The drive is external and powered from the USB port.[/warning]\n'
              '[dim]Writing draws far more current than reading, and a marginal port\n'
              'makes the drive reboot halfway through. If a burn fails:\n'
              '  1. plug in both connectors, if the cable has two\n'
              '  2. use a port directly on the PC, never an unpowered hub[/dim]',
    },
    'system.advice_internal': {
        'it': '[success]Unita\' interna: alimentazione stabile, nessuna '
              'precauzione particolare.[/success]',
        'en': '[success]Internal drive: stable power, no particular '
              'precautions needed.[/success]',
    },

    # ── Valutazione del disco inserito ───────────────────────────────────────
    'disc.unusable': {
        'it': '\n[error]Disco non utilizzabile: {reason}.[/error]',
        'en': '\n[error]Disc cannot be used: {reason}.[/error]',
    },
    'disc.unknown_type': {
        'it': 'tipo non riconosciuto',
        'en': 'type not recognised',
    },
    'disc.unknown_type_why': {
        'it': 'L\'unita\' non e\' riuscita a identificare il disco. Puo\' essere '
              'graffiato,\ninserito male, oppure di un tipo che questo '
              'masterizzatore non gestisce.\nProva a estrarlo e reinserirlo.',
        'en': 'The drive could not identify the disc. It may be scratched, badly\n'
              'inserted, or of a type this burner does not handle.\n'
              'Try ejecting it and putting it back in.',
    },
    'disc.not_a_cd_why': {
        'it': 'Il CD audio esiste solo sui CD: lo standard Red Book non e\' '
              'definito\nper DVD e Blu-ray, e nessun lettore da auto saprebbe '
              'leggerlo.\nServe un CD-R, anche se questo disco ha molto piu\' '
              'spazio.',
        'en': 'Audio CDs exist only on CDs: the Red Book standard is not defined\n'
              'for DVDs and Blu-rays, and no car player could read one.\n'
              'You need a CD-R, even though this disc holds far more.',
    },
    'disc.pressed_cdrom': {
        'it': 'CD-ROM stampato',
        'en': 'pressed CD-ROM',
    },
    'disc.pressed_cdrom_why': {
        'it': 'E\' un CD prodotto in fabbrica, di sola lettura. Serve un CD-R vuoto.',
        'en': 'This is a factory-pressed, read-only CD. You need a blank CD-R.',
    },
    'disc.cdrw_written': {
        'it': 'CD-RW gia\' scritto',
        'en': 'CD-RW already written',
    },
    'disc.cdrw_written_why': {
        'it': 'Essendo riscrivibile puoi svuotarlo: Esplora risorse, tasto destro\n'
              'sull\'unita\', "Cancella questo disco". Poi rilancia BurnDex.',
        'en': 'Being rewritable you can wipe it: File Explorer, right-click the\n'
              'drive, "Erase this disc". Then run BurnDex again.',
    },
    'disc.cdr_written': {
        'it': 'CD-R gia\' scritto',
        'en': 'CD-R already written',
    },
    'disc.cdr_written_why': {
        'it': 'Su un CD-R la scrittura e\' definitiva: non si cancella. Serve un '
              'disco nuovo.',
        'en': 'On a CD-R writing is final: it cannot be erased. You need a new disc.',
    },
    'disc.cdrw_blank': {
        'it': 'CD-RW vuoto',
        'en': 'blank CD-RW',
    },
    'disc.cdrw_blank_why': {
        'it': 'Riscrivibile, ma riflette meno luce di un CD-R: molte autoradio e\n'
              'gli stereo datati non lo leggono. Per l\'auto conviene un CD-R.',
        'en': 'Rewritable, but it reflects less light than a CD-R: many car stereos\n'
              'and older systems will not read it. For the car, prefer a CD-R.',
    },
    'disc.cdr_blank': {
        'it': 'CD-R vuoto',
        'en': 'blank CD-R',
    },
    'disc.not_writable_audio': {
        'it': '\n[error]Questo disco non e\' scrivibile come CD audio.[/error]',
        'en': '\n[error]This disc cannot be written as an audio CD.[/error]',
    },
    'disc.too_long': {
        'it': '\n[error]Troppo lungo: il limite prudenziale e\' {limit} min '
              '({over} min di troppo).[/error]',
        'en': '\n[error]Too long: the safe limit is {limit} min '
              '({over} min over).[/error]',
    },
    'disc.trim_hint': {
        'it': '[dim]Togli qualche brano, oppure usa ordine.txt per fissare '
              'cosa masterizzare.[/dim]\n',
        'en': '[dim]Drop a few tracks, or use ordine.txt to pin down what '
              'gets burned.[/dim]\n',
    },
    'disc.does_not_fit': {
        'it': '\n[error]Non ci sta: servono {need} min ma il disco ne regge '
              '{have}.[/error]\n',
        'en': '\n[error]It does not fit: {need} min needed but the disc holds '
              '{have}.[/error]\n',
    },
    'disc.does_not_fit_exact': {
        'it': '\n[error]Non ci sta sul disco: servono {need} min ma ce ne sono '
              '{have}.[/error]',
        'en': '\n[error]It does not fit on the disc: {need} min needed but only '
              '{have} available.[/error]',
    },

    # ── Prova a vuoto ────────────────────────────────────────────────────────
    'dry.tracklist_ok': {
        'it': '\n{ok} [success]Scaletta valida: ci sta su un CD-R.[/success]',
        'en': '\n{ok} [success]Track list is valid: it fits on a CD-R.[/success]',
    },
    'dry.passed': {
        'it': '\n{ok} [success]Prova a vuoto superata: scaletta valida, disco '
              'idoneo, spazio sufficiente.[/success]',
        'en': '\n{ok} [success]Rehearsal passed: track list valid, disc suitable, '
              'enough room.[/success]',
    },
    'dry.nothing_touched': {
        'it': '[dim]Nessun disco e\' stato toccato. Togli --dry-run per '
              'masterizzare davvero.[/dim]\n',
        'en': '[dim]No disc was touched. Drop --dry-run to burn for real.[/dim]\n',
    },

    # ── Decodifica e scrittura ───────────────────────────────────────────────
    'burn.measuring': {
        'it': 'Misura del volume...',
        'en': 'Measuring loudness...',
    },
    'burn.measured': {
        'it': '[bright_green]Volume misurato[/bright_green]',
        'en': '[bright_green]Loudness measured[/bright_green]',
    },
    'burn.decoding': {
        'it': 'Decodifica in corso...',
        'en': 'Decoding...',
    },
    'burn.decoded': {
        'it': '[bright_green]Decodifica completata[/bright_green]',
        'en': '[bright_green]Decoding complete[/bright_green]',
    },
    'burn.decode_failed': {
        'it': '\n[error]Decodifica fallita: {file}[/error]',
        'en': '\n[error]Decoding failed: {file}[/error]',
    },
    'burn.starting': {
        'it': 'Avvio scrittura...',
        'en': 'Starting to write...',
    },
    'burn.all_written': {
        'it': '[bright_green]Tutte le tracce scritte[/bright_green]',
        'en': '[bright_green]All tracks written[/bright_green]',
    },
    'burn.closing': {
        'it': '\n[dim]Chiusura della sessione...[/dim]',
        'en': '\n[dim]Closing the session...[/dim]',
    },
    'burn.close_failed': {
        'it': '[warning]L\'unita\' non ha risposto nemmeno alla chiusura: '
              'scollegala e ricollegala prima di riprovare.[/warning]',
        'en': '[warning]The drive did not respond to the close either: unplug it '
              'and plug it back in before retrying.[/warning]',
    },
    'burn.timeout': {
        'it': '\n[error]L\'unita\' non ha risposto al comando di scrittura.[/error]',
        'en': '\n[error]The drive did not respond to the write command.[/error]',
    },
    'burn.timeout_why': {
        'it': '[dim]Tipico dei masterizzatori USB alimentati dalla sola porta dati: quando il\n'
              'laser passa in potenza di scrittura l\'assorbimento sale di colpo e l\'unita\'\n'
              'si riavvia. Da provare, in quest\'ordine:\n'
              '  1. se il cavo ha due spinotti USB, collegarli entrambi (uno e\' solo corrente)\n'
              '  2. porta USB diretta sul PC, mai un hub non alimentato\n'
              '  3. un hub USB con alimentatore esterno[/dim]',
        'en': '[dim]Typical of USB burners powered from the data port alone: when the laser\n'
              'switches to write power the current draw jumps and the drive reboots.\n'
              'Things to try, in this order:\n'
              '  1. if the cable has two USB plugs, connect both (one is power only)\n'
              '  2. a USB port directly on the PC, never an unpowered hub\n'
              '  3. a USB hub with its own power supply[/dim]',
    },
    'burn.write_error': {
        'it': '\n[error]Errore durante la scrittura: {error}[/error]',
        'en': '\n[error]Error while writing: {error}[/error]',
    },

    # ── Riepilogo finale ─────────────────────────────────────────────────────
    'result.ok_title': {
        'it': '[bold bright_green]✓  Masterizzazione completata[/bold bright_green]',
        'en': '[bold bright_green]✓  Burn complete[/bold bright_green]',
    },
    'result.fail_title': {
        'it': '[bold red]✗  Masterizzazione fallita[/bold red]',
        'en': '[bold red]✗  Burn failed[/bold red]',
    },
    'result.tracks_written': {'it': 'Tracce scritte', 'en': 'Tracks written'},
    'result.out_of': {
        'it': '[dim]su {total}[/dim]',
        'en': '[dim]of {total}[/dim]',
    },
    'result.total_duration': {'it': 'Durata totale', 'en': 'Total duration'},
    'result.outcome': {'it': 'Esito', 'en': 'Outcome'},
    'result.finalised': {
        'it': '[success]disco finalizzato[/success]',
        'en': '[success]disc finalised[/success]',
    },
    'result.ready_to_play': {
        'it': '[dim]pronto da provare nel lettore[/dim]',
        'en': '[dim]ready to try in the player[/dim]',
    },
    'result.aborted': {
        'it': '[error]interrotto[/error]',
        'en': '[error]aborted[/error]',
    },
    'result.disc': {'it': 'Disco', 'en': 'Disc'},
    'result.disc_still_good': {
        'it': '[info]nessun dato audio scritto: e\' ancora buono[/info]',
        'en': '[info]no audio data written: it is still good[/info]',
    },
    'result.disc_ruined': {
        'it': '[warning]scritto a meta\': non e\' recuperabile[/warning]',
        'en': '[warning]written halfway: it cannot be recovered[/warning]',
    },

    # ── Modalita' --info ─────────────────────────────────────────────────────
    'info.no_imapi_drive': {
        'it': '\n[error]Nessun masterizzatore utilizzabile da IMAPI.[/error]',
        'en': '\n[error]No burner usable through IMAPI.[/error]',
    },
    'info.check_external': {
        'it': '[dim]Se e\' esterno, controlla che sia collegato e acceso.[/dim]\n',
        'en': '[dim]If it is external, check that it is connected and powered on.[/dim]\n',
    },
    'info.drive_column': {'it': 'Unita\'', 'en': 'Drive'},
    'info.disc_column': {'it': 'Disco inserito', 'en': 'Disc inserted'},
    'info.speed_column': {'it': 'Vel.', 'en': 'Speed'},
    'info.no_disc': {
        'it': '[dim]nessun disco[/dim]',
        'en': '[dim]no disc[/dim]',
    },
    'info.blank': {
        'it': '[success]{type} vuoto[/success] [dim]{capacity}[/dim]',
        'en': '[success]blank {type}[/success] [dim]{capacity}[/dim]',
    },
    'info.written': {
        'it': '[warning]{type} gia\' scritto[/warning]',
        'en': '[warning]{type} already written[/warning]',
    },

    # ── Riga di comando ──────────────────────────────────────────────────────
    'cli.desc': {
        'it': 'BurnDex - Masterizzatore di CD audio per le raccolte di AudioDex',
        'en': 'BurnDex - Audio CD burner for AudioDex collections',
    },
    'cli.epilog': {
        'it': 'Esempi:\n'
              '  python BurnDex.py --info\n'
              '  python BurnDex.py --dir "download_audio/Molchat Doma - Etazhi" --dry-run\n'
              '  python BurnDex.py --dir "download_audio/Molchat Doma - Etazhi" --speed 4\n',
        'en': 'Examples:\n'
              '  python BurnDex.py --info\n'
              '  python BurnDex.py --dir "download_audio/Molchat Doma - Etazhi" --dry-run\n'
              '  python BurnDex.py --dir "download_audio/Molchat Doma - Etazhi" --speed 4\n',
    },
    'cli.dir': {
        'it': 'Cartella da masterizzare. Se omessa, la scegli da un elenco',
        'en': 'Folder to burn. If omitted, you pick one from a list',
    },
    'cli.base': {
        'it': 'Cartella delle raccolte (default: AudioDex/download_audio)',
        'en': 'Collections folder (default: AudioDex/download_audio)',
    },
    'cli.speed': {
        'it': 'Velocita\' di scrittura in "x". Se omessa viene chiesta '
              '(o {default}x con --yes). Piu\' bassa = piu\' compatibile con le autoradio',
        'en': 'Write speed in "x". If omitted it is asked '
              '(or {default}x with --yes). Lower = more compatible with car stereos',
    },
    'cli.drive': {
        'it': 'Indice del masterizzatore da usare (vedi --info)',
        'en': 'Index of the burner to use (see --info)',
    },
    'cli.dry_run': {
        'it': 'Mostra la scaletta e verifica che ci stia, senza toccare il disco',
        'en': 'Show the track list and check that it fits, without touching the disc',
    },
    'cli.info': {
        'it': 'Elenca i masterizzatori e il disco inserito, poi esce',
        'en': 'List the burners and the inserted disc, then exit',
    },
    'cli.yes': {
        'it': 'Nessuna domanda: tutte le tracce, velocita\' predefinita, nessuna conferma',
        'en': 'No questions: all tracks, default speed, no confirmation',
    },
    'cli.level': {
        'it': 'Livella il volume fra le tracce (misura ogni brano: piu\' lento, '
              'ma il disco non fa saltare in aria in auto a ogni cambio)',
        'en': 'Level the volume across tracks (measures every song: slower, but '
              'the disc stops making you jump at each track change in the car)',
    },
    'cli.trim': {
        'it': 'Rifila i silenzi a inizio e fine traccia, che si sommano ai 2 '
              'secondi di stacco inseriti comunque fra un brano e l\'altro',
        'en': 'Trim the silence at the start and end of each track, which adds to '
              'the 2-second gap inserted between songs anyway',
    },
    'cli.no_eject': {
        'it': 'Non espellere il disco a fine masterizzazione',
        'en': 'Do not eject the disc when burning finishes',
    },
}
