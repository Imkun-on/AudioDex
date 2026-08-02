"""Testi di AudioDex in italiano e in inglese.

Una voce per frase mostrata all'utente, nella forma
``'chiave': {'it': ..., 'en': ...}``. I segnaposto sono quelli di
``str.format``: ogni lingua puo' disporli nell'ordine che le serve, che tra
italiano e inglese quasi mai coincide.

Il markup Rich ([error], [bold], ...) resta dentro le frasi quando fa parte
della frase stessa — evidenziare una parola diversa in inglese e' spesso
necessario, e tenerlo fuori costringerebbe a spezzare le stringhe in pezzi
senza senso compiuto.

I commenti e i docstring del programma non stanno qui: restano in italiano
perche' si rivolgono a chi legge il codice, non a chi lo usa.
"""
from __future__ import annotations

TESTI: dict[str, dict[str, str]] = {

    # ── Riga di comando ──────────────────────────────────────────────────────
    'cli.desc': {
        'it': 'AudioDex - Downloader audio da YouTube',
        'en': 'AudioDex - YouTube audio downloader',
    },
    'cli.search': {
        'it': 'Cerca per nome canzone/artista',
        'en': 'Search by song or artist name',
    },
    'cli.url': {
        'it': 'URL diretto (video, playlist, album)',
        'en': 'Direct URL (video, playlist, album)',
    },
    'cli.output': {
        'it': 'Cartella output (default: AudioDex/download_audio)',
        'en': 'Output folder (default: AudioDex/download_audio)',
    },
    'cli.media': {
        'it': 'Scarica solo audio o il video intero. Se omesso, in modalita\' '
              'interattiva viene chiesto; con --search/--url il default e\' audio',
        'en': 'Download audio only or the whole video. If omitted it is asked '
              'in interactive mode; with --search/--url the default is audio',
    },
    'cli.format': {
        'it': 'Formato del file (audio: m4a/mp3/opus · video: mp4/mkv). '
              'Default: m4a per l\'audio, mp4 per il video',
        'en': 'File format (audio: m4a/mp3/opus · video: mp4/mkv). '
              'Default: m4a for audio, mp4 for video',
    },
    'cli.workers': {
        'it': 'Worker paralleli (default: {n})',
        'en': 'Parallel workers (default: {n})',
    },
    'cli.max_results': {
        'it': 'Risultati ricerca max (default: {n})',
        'en': 'Max search results (default: {n})',
    },
    'cli.no_lyrics': {
        'it': 'Non cercare i testi sincronizzati su LRCLIB',
        'en': 'Do not look up synced lyrics on LRCLIB',
    },
    'cli.cookies': {
        'it': 'Usa i cookie del browser indicato per accedere a playlist/video privati',
        'en': 'Use cookies from the given browser to reach private playlists/videos',
    },
    'cli.err_video_format': {
        'it': '--format {fmt} e\' un formato video, incompatibile con --media audio',
        'en': '--format {fmt} is a video format, incompatible with --media audio',
    },
    'cli.err_audio_format': {
        'it': '--format {fmt} e\' un formato audio, incompatibile con --media video',
        'en': '--format {fmt} is an audio format, incompatible with --media video',
    },

    # ── Avvio e controlli ────────────────────────────────────────────────────
    'start.no_mutagen': {
        'it': '[warning]mutagen non installato - tagging disabilitato[/warning]',
        'en': '[warning]mutagen not installed - tagging disabled[/warning]',
    },
    'start.install_mutagen': {
        'it': '[dim]Installa con: pip install mutagen[/dim]\n',
        'en': '[dim]Install with: pip install mutagen[/dim]\n',
    },
    'disk.low': {
        'it': '\n[warning]ATTENZIONE: solo {mb} MB liberi.[/warning]',
        'en': '\n[warning]WARNING: only {mb} MB free.[/warning]',
    },
    'disk.continue': {
        'it': '[bold]Continuare? (s/n): [/bold]',
        'en': '[bold]Continue? (y/n): [/bold]',
    },
    'common.cancelled_op': {
        'it': '[error]Operazione annullata.[/error]',
        'en': '[error]Operation cancelled.[/error]',
    },
    'common.cancelled': {
        'it': '[dim]Annullato.[/dim]',
        'en': '[dim]Cancelled.[/dim]',
    },
    'common.goodbye': {
        'it': '\n[dim]Arrivederci![/dim]\n',
        'en': '\n[dim]Goodbye![/dim]\n',
    },
    'common.invalid_choice': {
        'it': '[error]Scelta non valida. Riprova.[/error]',
        'en': '[error]Invalid choice. Try again.[/error]',
    },
    'common.invalid_selection': {
        'it': '[error]Selezione non valida. Riprova.[/error]',
        'en': '[error]Invalid selection. Try again.[/error]',
    },
    'common.unknown': {
        'it': 'Sconosciuto',
        'en': 'Unknown',
    },

    # ── Unita' di misura compatte ────────────────────────────────────────────
    # Le abbreviazioni dei grandi numeri non coincidono: 'Mrd' (miliardi) in
    # inglese non significa nulla, e 'B' (billion) in italiano si leggerebbe
    # come un errore.
    'unit.billions': {'it': 'Mrd', 'en': 'B'},
    'unit.millions': {'it': 'Mln', 'en': 'M'},
    'unit.thousands': {'it': 'K', 'en': 'K'},

    # Ordine dei campi di una data. L'italiano scrive giorno/mese/anno;
    # per l'inglese si usa la forma ISO, che e' l'unica non ambigua tra
    # convenzione americana (mese prima) e britannica (giorno prima).
    'date.format': {
        'it': '{d}/{m}/{y}',
        'en': '{y}-{m}-{d}',
    },

    # ── Nomi delle lingue nella scheda video ─────────────────────────────────
    'lang.it': {'it': 'Italiano', 'en': 'Italian'},
    'lang.en': {'it': 'Inglese', 'en': 'English'},
    'lang.es': {'it': 'Spagnolo', 'en': 'Spanish'},
    'lang.fr': {'it': 'Francese', 'en': 'French'},
    'lang.de': {'it': 'Tedesco', 'en': 'German'},
    'lang.pt': {'it': 'Portoghese', 'en': 'Portuguese'},
    'lang.ru': {'it': 'Russo', 'en': 'Russian'},
    'lang.ja': {'it': 'Giapponese', 'en': 'Japanese'},
    'lang.ko': {'it': 'Coreano', 'en': 'Korean'},
    'lang.zh': {'it': 'Cinese', 'en': 'Chinese'},
    'lang.ar': {'it': 'Arabo', 'en': 'Arabic'},
    'lang.nl': {'it': 'Olandese', 'en': 'Dutch'},
    'lang.pl': {'it': 'Polacco', 'en': 'Polish'},
    'lang.tr': {'it': 'Turco', 'en': 'Turkish'},
    'lang.hi': {'it': 'Hindi', 'en': 'Hindi'},
    'lang.sv': {'it': 'Svedese', 'en': 'Swedish'},
    'lang.ro': {'it': 'Rumeno', 'en': 'Romanian'},
    'lang.el': {'it': 'Greco', 'en': 'Greek'},
    'lang.uk': {'it': 'Ucraino', 'en': 'Ukrainian'},
    'lang.cs': {'it': 'Ceco', 'en': 'Czech'},

    # ── Scheda del video ─────────────────────────────────────────────────────
    'card.channel': {'it': 'Canale', 'en': 'Channel'},
    'card.views': {'it': 'Visualizzazioni', 'en': 'Views'},
    'card.likes': {'it': 'Mi piace', 'en': 'Likes'},
    'card.subscribers': {'it': 'Iscritti', 'en': 'Subscribers'},
    'card.category': {'it': 'Categoria', 'en': 'Category'},
    'card.language': {'it': 'Lingua', 'en': 'Language'},
    'card.published': {'it': 'Pubblicato', 'en': 'Published'},
    'card.duration': {'it': 'Durata', 'en': 'Duration'},
    'card.chapters': {'it': 'Capitoli', 'en': 'Chapters'},
    'card.sections': {
        'it': '{n} sezioni',
        'en': '{n} sections',
    },
    'card.confirm': {
        'it': '\n[bold]Procedo con il download di questo video? (s/n): [/bold]',
        'en': '\n[bold]Download this video? (y/n): [/bold]',
    },

    # ── Tabella dei risultati ────────────────────────────────────────────────
    'table.search_results': {
        'it': 'Risultati ricerca',
        'en': 'Search results',
    },
    'table.playlist_tracks': {
        'it': 'Tracce della playlist',
        'en': 'Playlist tracks',
    },
    'table.title': {'it': 'Titolo', 'en': 'Title'},
    'table.artist': {'it': 'Artista', 'en': 'Artist'},
    'table.duration': {'it': 'Durata', 'en': 'Duration'},
    'table.views': {'it': 'Views', 'en': 'Views'},

    # ── Scheda della playlist ────────────────────────────────────────────────
    'playlist.channel': {'it': 'Canale', 'en': 'Channel'},
    'playlist.tracks': {'it': 'Tracce', 'en': 'Tracks'},
    'playlist.total_duration': {'it': 'Durata totale', 'en': 'Total duration'},
    'playlist.views': {'it': 'Visualizzazioni', 'en': 'Views'},
    'playlist.updated': {'it': 'Aggiornata', 'en': 'Updated'},
    'playlist.visibility': {'it': 'Visibilita\'', 'en': 'Visibility'},
    'playlist.unavailable': {'it': 'Non disponibili', 'en': 'Unavailable'},
    'playlist.unavailable_n': {
        'it': '[warning]{n} (privati o rimossi)[/warning]',
        'en': '[warning]{n} (private or removed)[/warning]',
    },
    'visibility.public': {'it': 'Pubblica', 'en': 'Public'},
    'visibility.unlisted': {'it': 'Non in elenco', 'en': 'Unlisted'},
    'visibility.private': {'it': 'Privata', 'en': 'Private'},

    # ── Download ─────────────────────────────────────────────────────────────
    'download.threads': {'it': 'Thread:', 'en': 'Threads:'},
    'download.tracks': {'it': 'Tracce:', 'en': 'Tracks:'},
    'download.format': {'it': 'Formato:', 'en': 'Format:'},
    'download.bar_tracks': {'it': 'Tracce', 'en': 'Tracks'},
    'phase.download': {'it': 'Download', 'en': 'Download'},
    'phase.convert': {'it': 'Conversione', 'en': 'Convert'},
    'phase.lyrics': {'it': 'Testi', 'en': 'Lyrics'},
    'phase.tag': {'it': 'Tag', 'en': 'Tags'},

    # ── Riepilogo ────────────────────────────────────────────────────────────
    'summary.title': {'it': 'Riepilogo', 'en': 'Summary'},
    'summary.total': {'it': 'Tracce totali', 'en': 'Total tracks'},
    'summary.downloaded': {'it': 'Scaricate', 'en': 'Downloaded'},
    'summary.lyrics': {'it': 'Testi karaoke', 'en': 'Karaoke lyrics'},
    'summary.already': {'it': 'Gia\' presenti', 'en': 'Already there'},
    'summary.failed': {'it': 'Fallite', 'en': 'Failed'},
    'summary.failed_tracks': {'it': '  Tracce', 'en': '  Tracks'},

    # ── Tracce fallite ───────────────────────────────────────────────────────
    'failed.file_header': {
        'it': '# Tracce fallite\n'
              '# Per ritentare, copia gli URL e usa: python AudioDex.py --url <URL>\n#\n',
        'en': '# Failed tracks\n'
              '# To retry, copy the URLs and run: python AudioDex.py --url <URL>\n#\n',
    },
    'failed.saved': {
        'it': '\n  Tracce fallite salvate in: [info]{path}[/info]',
        'en': '\n  Failed tracks saved to: [info]{path}[/info]',
    },

    # ── Selezione delle tracce ───────────────────────────────────────────────
    'select.hint': {
        'it': '\n[dim_label]Seleziona:[/dim_label] numero singolo ([accent]3[/accent]), '
              'intervallo ([accent]1-5[/accent]), multipli ([accent]1,3,7[/accent]), '
              '[accent]all[/accent] per tutti, [accent]q[/accent] per uscire',
        'en': '\n[dim_label]Select:[/dim_label] a single number ([accent]3[/accent]), '
              'a range ([accent]1-5[/accent]), a list ([accent]1,3,7[/accent]), '
              '[accent]all[/accent] for everything, [accent]q[/accent] to quit',
    },
    'select.prompt': {
        'it': '\n[bold]Scegli > [/bold]',
        'en': '\n[bold]Choose > [/bold]',
    },

    # ── Audio o video ────────────────────────────────────────────────────────
    'media.column_choice': {'it': 'Scelta', 'en': 'Choice'},
    'media.audio_only': {'it': 'Solo audio', 'en': 'Audio only'},
    'media.audio_note': {
        'it': '  [dim]pochi MB, taggato, con il testo karaoke[/dim]',
        'en': '  [dim]a few MB, tagged, with karaoke lyrics[/dim]',
    },
    'media.full_video': {'it': 'Video intero', 'en': 'Full video'},
    'media.video_note': {
        'it': '  [dim]immagine + audio, file molto piu\' grande[/dim]',
        'en': '  [dim]picture + audio, much larger file[/dim]',
    },
    'media.prompt': {
        'it': '\n[bold]Cosa scarico? (1 = audio · 2 = video · q = annulla): [/bold]',
        'en': '\n[bold]What should I download? (1 = audio · 2 = video · q = cancel): [/bold]',
    },

    # ── Modalita' interattiva ────────────────────────────────────────────────
    'interactive.header': {
        'it': '\n[dim_label]Modalita\' interattiva[/dim_label]\n  '
              '{dot} Digita un [accent]nome canzone/artista[/accent] per cercare\n  '
              '{dot} Incolla un [accent]URL[/accent] (video/playlist) per download diretto\n  '
              '{dot} Digita [accent]q[/accent] per uscire\n',
        'en': '\n[dim_label]Interactive mode[/dim_label]\n  '
              '{dot} Type a [accent]song or artist name[/accent] to search\n  '
              '{dot} Paste a [accent]URL[/accent] (video/playlist) to download directly\n  '
              '{dot} Type [accent]q[/accent] to quit\n',
    },
    'interactive.prompt': {
        'it': '\n{note} [bold]Cerca o incolla URL > [/bold]',
        'en': '\n{note} [bold]Search or paste a URL > [/bold]',
    },
    'interactive.download_all': {
        'it': '\n[dim_label]Scaricare tutte le {n} tracce? (s/n)[/dim_label]',
        'en': '\n[dim_label]Download all {n} tracks? (y/n)[/dim_label]',
    },
    'interactive.answer_prompt': {
        'it': '[bold]> [/bold]',
        'en': '[bold]> [/bold]',
    },
    'interactive.fetching_video': {
        'it': '\n[dim]Recupero le informazioni del video...[/dim]',
        'en': '\n[dim]Fetching video information...[/dim]',
    },

    # ── Errori di estrazione ─────────────────────────────────────────────────
    'error.playlist_unreachable': {
        'it': '[warning]Playlist non accessibile: scarico il singolo video.[/warning]',
        'en': '[warning]Playlist not reachable: downloading the single video.[/warning]',
    },
    'error.no_tracks_playlist': {
        'it': '[error]Nessuna traccia trovata nella playlist.[/error]',
        'en': '[error]No tracks found in the playlist.[/error]',
    },
    'error.no_tracks': {
        'it': '[error]Nessuna traccia trovata.[/error]',
        'en': '[error]No tracks found.[/error]',
    },
    'error.no_results': {
        'it': '[error]Nessun risultato trovato.[/error]',
        'en': '[error]No results found.[/error]',
    },
    'error.no_info_url': {
        'it': '[error]Impossibile estrarre info dal URL.[/error]',
        'en': '[error]Could not extract info from the URL.[/error]',
    },
    'error.no_info': {
        'it': '[error]Impossibile estrarre info.[/error]',
        'en': '[error]Could not extract info.[/error]',
    },
}
