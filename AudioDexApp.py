"""AudioDexApp — interfaccia grafica in HTML, con Python come padrone di casa.

Perche' esiste, accanto ad AudioDexGUI
    E' la stessa interfaccia riscritta sostituendo Flet con una pagina web
    mostrata dentro il WebView che Windows ha gia' installato. Il motore non
    cambia di una riga: ``AudioDex.py``, ``BurnDex.py``, ``PixDex.py`` e
    ``ClipDex.py`` non sanno nemmeno che esiste un'interfaccia.

Cosa ci si guadagna
    Lo sfondo animato non e' piu' un file video da 74 megabyte scaricato da
    una Release al primo avvio, con il ripiego a gradiente per quando il
    plugin non parte: sono venti righe di CSS e pesa zero. Non c'e' nessun
    motore grafico da scaricare, perche' WebView2 e' gia' nel sistema. E le
    cose che un'interfaccia deve fare — bagliori, sfocature, transizioni,
    testo che scorre — sono esattamente cio' per cui il CSS e' nato.

Come parlano fra loro i due mondi
    In una sola direzione ciascuno, ed e' questo che tiene il tutto semplice:

      JavaScript -> Python   ``pywebview.api.nome(...)`` chiama direttamente
                             un metodo di ``Api``. Nessun protocollo, nessun
                             server, nessuna porta aperta.

      Python -> JavaScript   ``_verso_pagina(...)`` esegue una funzione della
                             pagina. Serve per cio' che arriva quando vuole
                             lui: righe di log, avanzamento, fine lavoro.

Il lavoro lungo non blocca la finestra
    Ogni operazione che dura piu' di un istante gira in un thread suo e
    riferisce alla pagina mentre procede. La finestra resta viva: si puo'
    leggere il log, e soprattutto si vede che sta succedendo qualcosa.

Stato
    Per ora c'e' la sola sezione Audio. E' un confronto voluto: si mette
    accanto a quella Flet, si guardano tutt'e due sulla stessa macchina, e
    solo dopo si decide se proseguire con le altre.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import threading
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import webview

from Shared import i18n
from Shared.strings_audiodex import TESTI as TESTI_AUDIO

i18n.register(TESTI_AUDIO)

# La finestra e' l'unica: la si tiene qui perche' i thread di lavoro devono
# poterla raggiungere per spingere gli aggiornamenti alla pagina.
_finestra: webview.Window | None = None

# pywebview 6 ha rinominato le costanti dei selettori di file. Si prendono le
# nuove quando esistono e si ricade sulle vecchie: cosi' il programma non
# stampa avvisi di deprecazione sulle versioni recenti e continua a girare su
# quelle precedenti.
_DLG_CARTELLA = getattr(getattr(webview, 'FileDialog', None), 'FOLDER',
                        getattr(webview, 'FOLDER_DIALOG', 2))
_DLG_APRI = getattr(getattr(webview, 'FileDialog', None), 'OPEN',
                    getattr(webview, 'OPEN_DIALOG', 10))

# ── Testi propri dell'interfaccia ────────────────────────────────────────────
# Non stanno in Shared/ perche' riguardano solo questa finestra, e mescolarli
# al catalogo di AudioDex renderebbe piu' difficile capire, leggendo quel file,
# quali frasi appaiono a terminale e quali no.
TESTI_APP: dict[str, dict[str, str]] = {
    'app.title':        {'it': 'AudioDex', 'en': 'AudioDex'},
    'app.subtitle':     {'it': 'Scarica  ·  Masterizza  ·  Rimasterizza',
                         'en': 'Download  ·  Burn  ·  Remaster'},
    'app.language':     {'it': 'Lingua', 'en': 'Language'},
    'menu.audio':       {'it': 'Audio', 'en': 'Audio'},
    'menu.burn':        {'it': 'Masterizzazione', 'en': 'Burning'},
    'menu.pix':         {'it': 'Rimasterizza', 'en': 'Remaster'},
    'menu.clip':        {'it': 'Montaggio', 'en': 'Editing'},
    'menu.soon':        {'it': 'in arrivo', 'en': 'coming'},
    'audio.title':      {'it': 'Scarica da YouTube', 'en': 'Download from YouTube'},
    'audio.desc':       {'it': 'Incolla un link, o cerca per nome. Playlist e album interi '
                               'finiscono in una cartella ordinata.',
                         'en': 'Paste a link, or search by name. Playlists and whole albums '
                               'land in a tidy folder.'},
    'audio.mode':       {'it': 'Come cerco', 'en': 'How to look'},
    'audio.mode.url':   {'it': 'Ho un link', 'en': 'I have a link'},
    'audio.mode.search': {'it': 'Cerca per nome', 'en': 'Search by name'},
    'audio.input.url':  {'it': 'Link del video, della playlist o dell\'album',
                         'en': 'Link to the video, playlist or album'},
    'audio.input.search': {'it': 'Nome del brano o dell\'artista',
                           'en': 'Song or artist name'},
    'audio.output':     {'it': 'Dove salvare', 'en': 'Where to save'},
    'audio.format':     {'it': 'Formato', 'en': 'Format'},
    'audio.media':      {'it': 'Cosa scarico', 'en': 'What to download'},
    'audio.media.audio': {'it': 'Solo audio', 'en': 'Audio only'},
    'audio.media.video': {'it': 'Video intero', 'en': 'Whole video'},
    'audio.workers':    {'it': 'Download in parallelo', 'en': 'Parallel downloads'},
    'audio.lyrics':     {'it': 'Cerca i testi sincronizzati su LRCLIB',
                         'en': 'Look up synced lyrics on LRCLIB'},
    'audio.split':      {'it': 'Dividi in tracce gli album caricati come video unico',
                         'en': 'Split into tracks the albums uploaded as a single video'},
    'audio.analyze':    {'it': 'Guarda cosa c\'è', 'en': 'See what is there'},
    'audio.start':      {'it': 'Scarica', 'en': 'Download'},
    'audio.results':    {'it': 'Cosa ho trovato', 'en': 'What I found'},
    'audio.results.empty': {'it': 'Incolla un link e premi «Guarda cosa c\'è».',
                            'en': 'Paste a link and press "See what is there".'},
    'log.title':        {'it': 'Diario', 'en': 'Log'},
    'log.clear':        {'it': 'Svuota', 'en': 'Clear'},
    'log.empty':        {'it': 'Qui compare quello che sta succedendo.',
                         'en': 'What is happening shows up here.'},
    'status.idle':      {'it': 'In attesa', 'en': 'Idle'},
    'status.working':   {'it': 'In corso', 'en': 'Working'},
    'status.done':      {'it': 'Fatto', 'en': 'Done'},
    'status.error':     {'it': 'Errore', 'en': 'Error'},
    'err.no_input':     {'it': 'Prima incolla un link o scrivi cosa cercare.',
                         'en': 'First paste a link or type what to search for.'},
    'err.nothing':      {'it': 'Non ho trovato niente.', 'en': 'I found nothing.'},
    'err.busy':         {'it': 'C\'è già qualcosa in corso.', 'en': 'Something is already running.'},
    'res.playlist':     {'it': '{n} brani  ·  {titolo}', 'en': '{n} tracks  ·  {titolo}'},
    'res.single':       {'it': 'Un video  ·  {titolo}', 'en': 'One video  ·  {titolo}'},
    'res.search':       {'it': '{n} risultati', 'en': '{n} results'},
    'sel.all':          {'it': 'Tutti', 'en': 'All'},
    'sel.none':         {'it': 'Nessuno', 'en': 'None'},
    'sel.count':        {'it': '{n} scelti', 'en': '{n} selected'},
    'fase.attesa':      {'it': 'in coda', 'en': 'queued'},
    'fase.download':    {'it': 'scarico', 'en': 'downloading'},
    'fase.convert':     {'it': 'converto', 'en': 'converting'},
    'fase.lyrics':      {'it': 'cerco il testo', 'en': 'fetching lyrics'},
    'fase.tag':         {'it': 'scrivo i tag', 'en': 'writing tags'},
    'fase.ok':          {'it': 'fatto', 'en': 'done'},
    'fase.skip':        {'it': 'c\'era già', 'en': 'already there'},
    'fase.fail':        {'it': 'fallito', 'en': 'failed'},
    'lavoro.avanzo':    {'it': '{fatte} di {totale}', 'en': '{fatte} of {totale}'},
    'scorciatoie':      {'it': 'Invio per cercare  ·  Ctrl+Invio per scaricare',
                         'en': 'Enter to search  ·  Ctrl+Enter to download'},
    'trascina':         {'it': 'Lascia qui il link', 'en': 'Drop the link here'},
    'err.no_file':      {'it': 'Prima scegli un file.', 'en': 'Pick a file first.'},
    'comune.sfoglia':   {'it': 'Sfoglia', 'en': 'Browse'},

    # ── Masterizzazione ──────────────────────────────────────────────────────
    'burn.title':       {'it': 'Masterizza un CD audio', 'en': 'Burn an audio CD'},
    'burn.desc':        {'it': 'Trasforma una cartella di brani in un CD vero, di quelli che '
                               'legge qualunque autoradio. Su un CD-R non si torna indietro.',
                         'en': 'Turns a folder of songs into a real CD, the kind any car stereo '
                               'reads. On a CD-R there is no going back.'},
    'burn.folder':      {'it': 'Cartella dei brani', 'en': 'Folder with the songs'},
    'burn.scan':        {'it': 'Leggi la cartella', 'en': 'Read the folder'},
    'burn.start':       {'it': 'Masterizza', 'en': 'Burn'},
    'burn.speed':       {'it': 'Velocità', 'en': 'Speed'},
    'burn.speed.auto':  {'it': 'Automatica', 'en': 'Automatic'},
    'burn.drive':       {'it': 'Unità', 'en': 'Drive'},
    'burn.drive.auto':  {'it': 'La prima libera', 'en': 'First available'},
    'burn.dry':         {'it': 'Prova senza incidere: verifica tutto e non tocca il disco',
                         'en': 'Rehearse: checks everything and does not touch the disc'},
    'burn.noeject':     {'it': 'Non espellere il disco alla fine',
                         'en': 'Do not eject the disc when finished'},
    'burn.level':       {'it': 'Livella il volume fra le tracce',
                         'en': 'Even out the volume across tracks'},
    'burn.trim':        {'it': 'Rifila i silenzi a inizio e fine traccia',
                         'en': 'Trim the silence at the start and end of each track'},
    'burn.tracks':      {'it': 'Scaletta', 'en': 'Running order'},
    'burn.empty':       {'it': 'Scegli una cartella e premi «Leggi la cartella».',
                         'en': 'Pick a folder and press "Read the folder".'},
    'burn.capacity':    {'it': '{minuti} di {limite} minuti', 'en': '{minuti} of {limite} minutes'},
    'burn.over':        {'it': 'Non ci sta: togli qualche traccia',
                         'en': 'It does not fit: remove some tracks'},
    'burn.order':       {'it': 'Ordine: {criterio}  ·  trascina per cambiarlo',
                         'en': 'Order: {criterio}  ·  drag to change it'},
    'burn.no_folder':   {'it': 'Quella cartella non esiste.', 'en': 'That folder does not exist.'},
    'burn.no_audio':    {'it': 'Nessun file audio in quella cartella.',
                         'en': 'No audio files in that folder.'},
    'burn.no_pywin32':  {'it': 'Manca pywin32: pip install pywin32',
                         'en': 'pywin32 is missing: pip install pywin32'},
    'burn.no_drive':    {'it': 'Nessun masterizzatore collegato.', 'en': 'No burner connected.'},
    'burn.only_windows': {'it': 'La masterizzazione funziona solo su Windows.',
                          'en': 'Burning only works on Windows.'},
    'burn.reordered':   {'it': 'Ordine cambiato: preparo la scaletta.',
                         'en': 'Order changed: preparing the running order.'},

    # ── Rimasterizzazione ────────────────────────────────────────────────────
    'pix.title':        {'it': 'Rimasterizza un video', 'en': 'Remaster a video'},
    'pix.desc':         {'it': 'Toglie i difetti della compressione e ingrandisce. Non inventa '
                               'dettaglio: lavora in sottrazione.',
                         'en': 'Removes compression artifacts and upscales. It invents no detail: '
                               'it works by subtraction.'},
    'pix.file':         {'it': 'Video da rimasterizzare', 'en': 'Video to remaster'},
    'pix.analyze':      {'it': 'Analizza', 'en': 'Analyse'},
    'pix.start':        {'it': 'Rimasterizza', 'en': 'Remaster'},
    'pix.diagnosis':    {'it': 'Diagnosi', 'en': 'Diagnosis'},
    'pix.empty':        {'it': "Scegli un video e premi «Analizza»: qui compare cosa c'è da sistemare.",
                         'en': 'Pick a video and press "Analyse": what needs fixing shows up here.'},
    'pix.preset':       {'it': 'Trattamento', 'en': 'Treatment'},
    'pix.preset.auto':  {'it': 'Dalla diagnosi', 'en': 'From the diagnosis'},
    'pix.resolution':   {'it': "Risoluzione d'arrivo", 'en': 'Target resolution'},
    'pix.suggested':    {'it': 'consigliata', 'en': 'suggested'},
    'pix.gpu':          {'it': 'Codifica sulla GPU: più veloce, ma rimette parte dei quadretti',
                         'en': 'Encode on the GPU: faster, but it puts some blocking back'},
    'pix.compare':      {'it': 'Salva il confronto prima/dopo', 'en': 'Save the before/after comparison'},
    'pix.preview':      {'it': 'Prima e dopo', 'en': 'Before and after'},
    'pix.preview.empty': {'it': 'A lavoro finito compare qui, a sinistra il file di partenza.',
                          'en': 'When it is done it shows up here, source on the left.'},
    'pix.unreadable':   {'it': 'Nessun flusso video leggibile in quel file.',
                         'en': 'No readable video stream in that file.'},
    'pix.done':         {'it': 'Fatto: {file}', 'en': 'Done: {file}'},
    'pix.failed':       {'it': 'La rimasterizzazione non è riuscita.', 'en': 'The remaster failed.'},

    # ── Montaggio ────────────────────────────────────────────────────────────
    'clip.title':       {'it': 'Monta e converti', 'en': 'Edit and convert'},
    'clip.desc':        {'it': 'Sei operazioni. Dove può, copia invece di ricodificare: '
                               'costa secondi e non perde un bit.',
                         'en': 'Six operations. Where it can, it copies instead of re-encoding: '
                               'it costs seconds and loses nothing.'},
    'clip.op':          {'it': 'Operazione', 'en': 'Operation'},
    'clip.file':        {'it': 'File di partenza', 'en': 'Source file'},
    'clip.files':       {'it': "File da unire, nell'ordine", 'en': 'Files to join, in order'},
    'clip.start':       {'it': 'Esegui', 'en': 'Run'},
    'clip.from':        {'it': 'Da', 'en': 'From'},
    'clip.to':          {'it': 'A', 'en': 'To'},
    'clip.duration':    {'it': 'Durata', 'en': 'Length'},
    'clip.preciso':     {'it': 'Taglio preciso al fotogramma (ricodifica, molto più lento)',
                         'en': 'Frame-accurate cut (re-encodes, much slower)'},
    'clip.capitoli':    {'it': 'Un capitolo per ogni file unito',
                         'en': 'One chapter per joined file'},
    'clip.grid':        {'it': 'Griglia', 'en': 'Grid'},
    'clip.result':      {'it': 'Risultato', 'en': 'Result'},
    'clip.result.empty': {'it': "Qui compare ciò che esce dall'operazione.",
                          'en': 'What comes out of the operation shows up here.'},
    'clip.need_two':    {'it': 'Per unire servono almeno due file.',
                         'en': 'Joining needs at least two files.'},
    'clip.done':        {'it': 'Fatto: {file}', 'en': 'Done: {file}'},
    'clip.failed':      {'it': 'Non è riuscita: {file}', 'en': 'It failed: {file}'},
    'clip.op.taglia':   {'it': 'Taglia uno spezzone', 'en': 'Cut a segment'},
    'clip.op.unisci':   {'it': 'Unisci più file', 'en': 'Join several files'},
    'clip.op.gif':      {'it': 'Ricava una GIF', 'en': 'Make a GIF'},
    'clip.op.webp':     {'it': 'Ricava un WebP (nove volte più leggero)',
                         'en': 'Make a WebP (nine times lighter)'},
    'clip.op.provino':  {'it': 'Provino a griglia', 'en': 'Contact sheet'},
    'clip.op.compat':   {'it': 'Rendi leggibile da apparecchi datati',
                         'en': 'Make it readable by old devices'},
    'done.summary':     {'it': 'Scaricati {ok} su {tot}  ·  {falliti} falliti',
                         'en': 'Downloaded {ok} of {tot}  ·  {falliti} failed'},
}
i18n.register(TESTI_APP)


# ── Moduli del motore, caricati alla prima richiesta ──────────────────────────
# Importare AudioDex costa qualche secondo (yt-dlp non e' leggero): farlo qui
# invece che all'avvio fa comparire la finestra subito, che e' la prima cosa
# che si giudica di un programma.
_audiodex = None
_burn = None
_pix = None
_clip = None


def _motore():
    global _audiodex
    if _audiodex is None:
        import AudioDex as _ad
        _audiodex = _ad
    return _audiodex


def _burndex():
    global _burn
    if _burn is None:
        import BurnDex as _bd
        _burn = _bd
    return _burn


def _pixdex():
    global _pix
    if _pix is None:
        import PixDex as _px
        _pix = _px
    return _pix


def _clipdex():
    global _clip
    if _clip is None:
        import ClipDex as _cd
        _clip = _cd
    return _clip


def _verso_pagina(funzione: str, *argomenti) -> None:
    """Esegue una funzione JavaScript della pagina, da qualunque thread.

    Gli argomenti passano per JSON: e' l'unico modo di trasportare un
    dizionario Python dentro la pagina senza inventarsi una codifica, e
    protegge da apici e accenti che altrimenti spezzerebbero la chiamata.
    """
    if _finestra is None:
        return
    try:
        args = ', '.join(json.dumps(a, ensure_ascii=False) for a in argomenti)
        _finestra.evaluate_js(f'window.{funzione}({args})')
    except Exception:
        # Una finestra chiusa mentre un thread stava ancora riferendo non e'
        # un errore: e' il normale ordine di spegnimento.
        pass


class Diario(io.TextIOBase):
    """Raccoglie cio' che i moduli stampano e lo manda alla pagina, riga a riga.

    I moduli del motore parlano con Rich, che colora scrivendo sequenze di
    controllo ANSI: dentro una pagina web quelle diventerebbero caratteri
    strani in mezzo al testo, quindi si tolgono. Il colore lo rimette la
    pagina, in base a cosa dice la riga.
    """

    _ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')

    def __init__(self):
        self._resto = ''
        self._lucchetto = threading.Lock()

    def write(self, s: str) -> int:      # type: ignore[override]
        if not s:
            return 0
        with self._lucchetto:
            self._resto += s
            while '\n' in self._resto:
                riga, self._resto = self._resto.split('\n', 1)
                self._manda(riga)
        return len(s)

    def flush(self) -> None:
        with self._lucchetto:
            if self._resto:
                self._manda(self._resto)
                self._resto = ''

    def _manda(self, grezza: str) -> None:
        testo = self._ANSI.sub('', grezza).rstrip()
        if testo:
            _verso_pagina('aggiungiRiga', testo)


class Api:
    """I metodi che la pagina puo' chiamare, e nient'altro.

    Ogni metodo restituisce un dizionario con almeno ``ok``: la pagina non
    deve mai ricevere un'eccezione Python, che in JavaScript arriverebbe come
    un rifiuto senza spiegazione.
    """

    def __init__(self):
        self._occupato = False
        self._risultati: list[dict] = []

    # ── Avvio ────────────────────────────────────────────────────────────────

    def avvio(self) -> dict:
        """Tutto cio' che serve alla pagina per disegnarsi la prima volta."""
        return {
            'ok': True,
            'lingua': i18n.get_language(),
            'testi': {k: v for k, v in
                      {**TESTI_AUDIO, **TESTI_APP}.items()},
            'cartella': os.path.join(_HERE, 'download_audio'),
            'sfondo': self._video_sfondo(),
        }

    @staticmethod
    def _video_sfondo() -> str:
        """Indirizzo del video di sfondo, se e' gia' sul disco.

        E' lo stesso file della GUI Flet, che lo scarica al primo avvio da una
        Release. Qui non lo si scarica: se c'e' lo si mostra, altrimenti
        restano i gradienti animati, che a differenza del ripiego di Flet non
        sono un ripiego mesto ma uno sfondo a sua volta guardabile.
        """
        percorso = os.path.join(_HERE, 'assets', 'cyberpunk-citadel.mp4')
        try:
            if os.path.getsize(percorso) < 1_000_000:
                return ''
        except OSError:
            return ''
        return Api._url_file(percorso)

    def cambia_lingua(self, codice: str) -> dict:
        i18n.set_language(codice)
        i18n.save(codice)
        return {'ok': True, 'lingua': i18n.get_language()}

    def scegli_cartella(self) -> dict:
        """Apre il selettore di cartelle del sistema."""
        try:
            scelta = _finestra.create_file_dialog(_DLG_CARTELLA)
        except Exception as exc:
            return {'ok': False, 'errore': str(exc)}
        return {'ok': True, 'cartella': scelta[0] if scelta else ''}

    # ── Ricerca e analisi ────────────────────────────────────────────────────

    def analizza(self, testo: str, modo: str) -> dict:
        """Guarda cosa c'e' dietro un link o una ricerca, senza scaricare nulla.

        Torna subito: il lavoro vero avviene in un thread, e la pagina viene
        avvisata a cose fatte. Cosi' la finestra non si congela nei secondi in
        cui yt-dlp interroga YouTube.
        """
        if self._occupato:
            return {'ok': False, 'errore': i18n.t('err.busy')}
        testo = (testo or '').strip()
        if not testo:
            return {'ok': False, 'errore': i18n.t('err.no_input')}

        self._in_thread(self._analizza_davvero, testo, modo)
        return {'ok': True, 'avviato': True}

    def _analizza_davvero(self, testo: str, modo: str) -> None:
        ad = _motore()
        if modo == 'search':
            trovati = ad.search_youtube(testo)
            titolo = i18n.t('res.search', n=len(trovati))
        elif ad._is_playlist_url(testo):
            nome, trovati, _meta = ad.get_playlist_entries(testo)
            titolo = i18n.t('res.playlist', n=len(trovati), titolo=nome)
        else:
            info = ad.get_video_details(testo)
            trovati = [ad._entry_from_info(info, testo)] if info else []
            titolo = i18n.t('res.single',
                            titolo=(info or {}).get('title', '')) if info else ''

        self._risultati = trovati or []
        _verso_pagina('mostraRisultati', {
            'titolo': titolo,
            'voci': [{
                'titolo': v.get('title', ''),
                'durata': self._durata(v.get('duration')),
                'canale': v.get('uploader') or v.get('channel') or '',
                'viste': self._viste(v.get('views')),
                'miniatura': self._miniatura(v.get('id')),
            } for v in self._risultati],
        })

    # ── Download ─────────────────────────────────────────────────────────────

    def scarica(self, opzioni: dict) -> dict:
        """Avvia il download di cio' che l'analisi ha trovato."""
        if self._occupato:
            return {'ok': False, 'errore': i18n.t('err.busy')}
        if not self._risultati:
            return {'ok': False, 'errore': i18n.t('err.nothing')}

        self._in_thread(self._scarica_davvero, opzioni)
        return {'ok': True, 'avviato': True}

    def _scarica_davvero(self, opzioni: dict) -> None:
        """Scarica le tracce scelte, raccontando alla pagina cosa succede a
        ciascuna mentre succede.

        Non si usa ``download_batch``, che disegna da se' le proprie barre con
        Rich: qui il ciclo lo si tiene in mano per poter dire alla pagina, per
        ogni singola traccia, se sta scaricando, convertendo, cercando il
        testo o scrivendo i tag. E' la differenza fra una barra che gira e
        un'interfaccia che dice cosa sta facendo.

        ``download_single`` protegge ogni uso di Rich con un controllo, quindi
        passandogli ``progress=None`` lavora in silenzio.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        ad = _motore()
        cartella = (opzioni.get('cartella')
                    or os.path.join(_HERE, 'download_audio'))
        os.makedirs(cartella, exist_ok=True)

        scelti = opzioni.get('scelti')
        indici = ([i for i in scelti if 0 <= i < len(self._risultati)]
                  if scelti else list(range(len(self._risultati))))
        if not indici:
            _verso_pagina('mostraRiepilogo',
                          {'testo': i18n.t('err.nothing'), 'ok': False})
            return

        totale = len(indici)
        fatte = [0]
        _verso_pagina('iniziaLavoro', totale)

        def una(indice: int) -> dict:
            entry = self._risultati[indice]
            _verso_pagina('tracciaFase', indice, 'download')
            esito = ad.download_single(
                entry, cartella, opzioni.get('formato', 'm4a'),
                track_num=indice + 1,
                total_tracks=totale,
                fetch_lyrics=bool(opzioni.get('testi', True)),
                media=opzioni.get('media', 'audio'),
                dividi=bool(opzioni.get('dividi', False)),
                on_phase=lambda fase, k=indice: _verso_pagina('tracciaFase', k, fase),
            )
            fatte[0] += 1
            _verso_pagina('tracciaFinita', indice, esito.get('status', 'fail'),
                          esito.get('error', ''))
            _verso_pagina('avanzaLavoro', fatte[0], totale)
            return esito

        esiti: list[dict] = []
        with ThreadPoolExecutor(max_workers=int(opzioni.get('paralleli', 3))) as pool:
            lavori = {pool.submit(una, i): i for i in indici}
            for lavoro in as_completed(lavori):
                try:
                    esiti.append(lavoro.result())
                except Exception as exc:      # noqa: BLE001
                    indice = lavori[lavoro]
                    _verso_pagina('tracciaFinita', indice, 'fail', str(exc))
                    esiti.append({'status': 'fail'})

        ok = sum(1 for e in esiti if e.get('status') == 'ok')
        falliti = sum(1 for e in esiti if e.get('status') == 'fail')
        _verso_pagina('mostraRiepilogo', {
            'testo': i18n.t('done.summary', ok=ok, tot=len(esiti), falliti=falliti),
            'ok': falliti == 0,
        })

    # ── Masterizzazione ──────────────────────────────────────────────────────

    def burn_scansiona(self, cartella: str) -> dict:
        """Elenca i brani di una cartella nell'ordine in cui finirebbero sul CD.

        L'ordine non e' alfabetico: e' quello che decide BurnDex, che sa
        riconoscere la numerazione nei nomi e rispettarla. Mostrarne uno
        diverso qui vorrebbe dire mentire su cosa verra' inciso.
        """
        cartella = (cartella or '').strip().strip('"')
        if not os.path.isdir(cartella):
            return {'ok': False, 'errore': i18n.t('burn.no_folder')}

        bd = _burndex()
        percorsi, criterio = bd._ordina_tracce(cartella)
        if not percorsi:
            return {'ok': False, 'errore': i18n.t('burn.no_audio')}

        durate = [bd._durata(p) for p in percorsi]
        settori = bd._settori_totali(durate)
        minuti = bd._sectors_to_minutes(settori)
        return {
            'ok': True,
            'criterio': bd.t(criterio) if criterio.startswith('order.') else criterio,
            'minuti': round(minuti, 1),
            'limite': bd.SAFE_MINUTES,
            'ci_sta': minuti <= bd.SAFE_MINUTES,
            'tracce': [{
                'percorso': p,
                'nome': os.path.basename(p),
                'durata': self._durata(d),
                'peso': round(os.path.getsize(p) / 1024 / 1024, 1),
            } for p, d in zip(percorsi, durate)],
        }

    def burn_unita(self) -> dict:
        """Elenca i masterizzatori collegati. Su sistemi non Windows dice perche' no."""
        if sys.platform != 'win32':
            return {'ok': False, 'errore': i18n.t('burn.only_windows'), 'unita': []}
        try:
            bd = _burndex()
            if not bd._HAS_PYWIN32:
                return {'ok': False, 'errore': i18n.t('burn.no_pywin32'), 'unita': []}
            import pythoncom
            pythoncom.CoInitialize()
            unita = [{'indice': i, 'nome': bd._nome_unita(r)}
                     for i, r in enumerate(bd._elenca_unita())]
            return {'ok': True, 'unita': unita,
                    'errore': '' if unita else i18n.t('burn.no_drive')}
        except Exception as exc:                       # noqa: BLE001
            return {'ok': False, 'errore': str(exc), 'unita': []}

    def burn_masterizza(self, opzioni: dict) -> dict:
        if self._occupato:
            return {'ok': False, 'errore': i18n.t('err.busy')}
        if not (opzioni.get('cartella') or '').strip():
            return {'ok': False, 'errore': i18n.t('burn.no_folder')}
        self._in_thread(self._burn_davvero, opzioni)
        return {'ok': True, 'avviato': True}

    def _burn_davvero(self, opzioni: dict) -> None:
        """Prepara l'ordine scelto e passa la palla a BurnDex.

        Se le tracce sono state riordinate, si costruisce una cartella
        temporanea di collegamenti numerati: BurnDex ordina per nome, quindi i
        prefissi impongono l'ordine voluto senza copiare un solo byte e senza
        toccare i file originali.
        """
        import shutil as _shutil
        import tempfile as _tempfile

        bd = _burndex()
        cartella = opzioni['cartella'].strip().strip('"')
        ordine = opzioni.get('ordine') or []

        temporanea = None
        da_incidere = cartella
        originali, _crit = bd._ordina_tracce(cartella)
        if ordine and ordine != [os.path.basename(p) for p in originali]:
            temporanea = _tempfile.mkdtemp(prefix='audiodexapp_burn_')
            cifre = max(2, len(str(len(ordine))))
            for i, nome in enumerate(ordine, 1):
                src = os.path.join(cartella, nome)
                dst = os.path.join(temporanea, f'{i:0{cifre}d} - {nome}')
                try:
                    os.link(src, dst)
                except OSError:
                    _shutil.copy2(src, dst)
            da_incidere = temporanea
            _verso_pagina('aggiungiRiga', i18n.t('burn.reordered'))

        _verso_pagina('iniziaLavoro', 0)      # avanzamento indeterminato
        try:
            velocita = opzioni.get('velocita')
            unita = opzioni.get('unita')
            bd.masterizza_cartella(
                da_incidere,
                speed_x=int(velocita) if velocita not in (None, '', 'auto') else None,
                dry_run=bool(opzioni.get('prova')),
                auto_si=True,
                espelli=not bool(opzioni.get('no_eject')),
                indice_unita=int(unita) if unita not in (None, '', 'auto') else None,
                livella=bool(opzioni.get('livella', True)),
                rifila=bool(opzioni.get('rifila')),
            )
        finally:
            if temporanea:
                _shutil.rmtree(temporanea, ignore_errors=True)

    # ── Rimasterizzazione ────────────────────────────────────────────────────

    def pix_analizza(self, percorso: str) -> dict:
        """Diagnosi di un video piu' le risoluzioni possibili, ognuna col suo giudizio.

        Le opzioni non sono un elenco fisso: il fattore di ingrandimento e il
        commento dipendono da *questo* file. E' il punto in cui il programma e'
        piu' onesto - la stessa riga che offre il 4K dice, quando e' il caso,
        che da quella sorgente non aggiunge un solo dettaglio.
        """
        percorso = (percorso or '').strip().strip('"')
        if not os.path.isfile(percorso):
            return {'ok': False, 'errore': i18n.t('err.no_file')}

        px = _pixdex()
        info = px.probe(percorso)
        if not info:
            return {'ok': False, 'errore': i18n.t('pix.unreadable')}

        problemi, consigliato = px.diagnosi(info)
        automatica = px.altezza_obiettivo(info, None, consigliato)

        def voce(chiave, altezza):
            fattore = px._fattore(info, altezza)
            _colore, nota = px._giudizio_fattore(fattore)
            return {'chiave': chiave, 'altezza': altezza,
                    'etichetta': px.t(chiave), 'fattore': round(fattore, 2),
                    'nota': px.t(nota),
                    'livello': ('ok' if fattore <= px.FATTORE_BUONO
                                else 'molle' if fattore <= px.FATTORE_MOLLE else 'finto'),
                    'consigliata': altezza == automatica}

        return {
            'ok': True,
            'nome': os.path.basename(percorso),
            'scheda': (f"{info['width']}×{info['height']}  ·  {info['fps']:.0f} fps"
                       f"  ·  {info['bitrate'] // 1000} kbit/s"
                       f"  ·  {self._durata(info['duration'])}"),
            'problemi': problemi,
            'preset': consigliato,
            'preset_nome': px.PRESETS[consigliato]['nome'](),
            'presets': [{'chiave': k, 'nome': px.PRESETS[k]['nome'](),
                         'desc': px.PRESETS[k]['desc']()}
                        for k in ('pulito', 'standard', 'forte', 'animazione', 'vecchio')],
            'risoluzioni': [voce('quality.auto', automatica),
                            voce('quality.none', info['height']),
                            voce('quality.hd', 1080),
                            voce('quality.2k', 1440),
                            voce('quality.4k', 2160)],
        }

    def pix_rimasterizza(self, opzioni: dict) -> dict:
        if self._occupato:
            return {'ok': False, 'errore': i18n.t('err.busy')}
        if not (opzioni.get('file') or '').strip():
            return {'ok': False, 'errore': i18n.t('err.no_file')}
        self._in_thread(self._pix_davvero, opzioni)
        return {'ok': True, 'avviato': True}

    def _pix_davvero(self, opzioni: dict) -> None:
        px = _pixdex()
        percorso = opzioni['file'].strip().strip('"')
        info = px.probe(percorso)
        if not info:
            _verso_pagina('aggiungiRiga', i18n.t('pix.unreadable'))
            return

        preset = opzioni.get('preset') or px.diagnosi(info)[1]
        richiesta = opzioni.get('altezza')
        altezza = px.altezza_obiettivo(
            info, int(richiesta) if richiesta not in (None, '', 'auto') else None, preset)
        catena = px.catena_filtri(preset, info, altezza)
        dst = px.nome_uscita(percorso, altezza or info['height'], None)

        totale = info['frames'] or 0
        _verso_pagina('iniziaLavoro', totale)
        ultimo = [0.0]

        def avanzamento(n, tot, velocita):
            import time as _time
            adesso = _time.monotonic()
            if adesso - ultimo[0] < .4 and (not tot or n < tot):
                return
            ultimo[0] = adesso
            _verso_pagina('avanzaLavoro', n, tot or totale or n or 1)

        ok = px.rimasterizza(info, dst, catena, bool(opzioni.get('gpu')),
                             px.CRF_DEFAULT, avanzamento=avanzamento)
        if not ok:
            _verso_pagina('mostraRiepilogo', {'testo': i18n.t('pix.failed'), 'ok': False})
            return

        png = ''
        if opzioni.get('confronto', True):
            png = px.confronto(percorso, dst,
                               os.path.splitext(dst)[0] + ' [confronto].png',
                               max(info['duration'] / 3, 0.0)) or ''
        _verso_pagina('pixFinito', {
            'file': os.path.basename(dst),
            'confronto': self._url_file(png) if png else '',
            'testo': i18n.t('pix.done', file=os.path.basename(dst)),
        })

    # ── Montaggio ────────────────────────────────────────────────────────────

    def clip_esegui(self, opzioni: dict) -> dict:
        if self._occupato:
            return {'ok': False, 'errore': i18n.t('err.busy')}
        self._in_thread(self._clip_davvero, opzioni)
        return {'ok': True, 'avviato': True}

    def _clip_davvero(self, opzioni: dict) -> None:
        cd = _clipdex()
        azione = opzioni.get('azione', 'taglia')
        sorgenti = [s.strip().strip('"') for s in (opzioni.get('file') or []) if s.strip()]
        if not sorgenti:
            _verso_pagina('aggiungiRiga', i18n.t('err.no_file'))
            return

        _verso_pagina('iniziaLavoro', 0)
        primo = sorgenti[0]
        esito = False

        if azione == 'unisci':
            if len(sorgenti) < 2:
                _verso_pagina('aggiungiRiga', i18n.t('clip.need_two'))
                return
            dst = cd._nome_uscita(primo, 'ClipDex unito', '.mp4')
            esito = cd.unisci(sorgenti, dst, capitoli=bool(opzioni.get('capitoli', True)))
        elif azione == 'taglia':
            inizio = cd.leggi_tempo(opzioni.get('da')) or 0.0
            fine = cd.leggi_tempo(opzioni.get('a'))
            dst = cd._nome_uscita(primo, 'ClipDex taglio')
            esito = cd.taglia(primo, dst, inizio, fine, preciso=bool(opzioni.get('preciso')))
        elif azione in ('gif', 'webp'):
            dst = cd._nome_uscita(primo, f'ClipDex {azione}',
                                  '.gif' if azione == 'gif' else '.webp')
            funzione = cd.gif if azione == 'gif' else cd.webp
            esito = funzione(primo, dst, cd.leggi_tempo(opzioni.get('da')),
                             cd.leggi_tempo(opzioni.get('durata')),
                             int(opzioni.get('fps') or cd.GIF_FPS),
                             int(opzioni.get('larghezza') or cd.GIF_LARGHEZZA))
        elif azione == 'provino':
            dst = cd._nome_uscita(primo, 'ClipDex provino', '.png')
            esito = cd.provino(primo, dst,
                               int(opzioni.get('righe') or cd.PROVINO_RIGHE),
                               int(opzioni.get('colonne') or cd.PROVINO_COLONNE))
        else:                                   # compat
            dst = cd._nome_uscita(primo, 'ClipDex compat', '.mp4')
            esito = cd.compat(primo, dst)

        # Il provino e' un'immagine: si mostra, invece di limitarsi a dire
        # dov'e' finita. E' tutto il senso di un provino.
        anteprima = (self._url_file(dst)
                     if esito and dst.lower().endswith(('.png', '.gif', '.webp')) else '')
        _verso_pagina('clipFinito', {
            'ok': bool(esito),
            'file': os.path.basename(dst),
            'anteprima': anteprima,
            'testo': i18n.t('clip.done' if esito else 'clip.failed',
                            file=os.path.basename(dst)),
        })

    # ── Selettori di file ────────────────────────────────────────────────────

    def scegli_file(self, multi: bool = False) -> dict:
        """Apre il selettore di file del sistema, per uno o piu' video."""
        try:
            cd = _clipdex()
            tipi = ('Video (' + ' '.join(f'*{e}' for e in sorted(cd.VIDEO_EXTS)) + ')',
                    'Audio (*.m4a;*.mp3;*.opus;*.wav;*.flac)', 'Tutti (*.*)')
            scelti = _finestra.create_file_dialog(
                _DLG_APRI, allow_multiple=bool(multi), file_types=tipi)
        except Exception as exc:                # noqa: BLE001
            return {'ok': False, 'errore': str(exc), 'file': []}
        return {'ok': True, 'file': list(scelti) if scelti else []}

    @staticmethod
    def _url_file(percorso: str) -> str:
        """Trasforma un percorso di Windows in un indirizzo che la pagina apre.

        Il cancelletto va protetto perche' in un indirizzo separa l'ancora:
        un file che ne contiene uno nel nome verrebbe troncato li'.
        """
        if not percorso:
            return ''
        pieno = os.path.abspath(percorso).replace('\\', '/')
        return 'file:///' + pieno.replace('#', '%23').replace('?', '%3F')

    # ── Utilita' interne ─────────────────────────────────────────────────────

    def _in_thread(self, funzione, *argomenti) -> None:
        """Fa girare il lavoro fuori dal thread della finestra.

        L'output dei moduli viene dirottato al diario solo per la durata del
        lavoro: farlo per sempre catturerebbe anche i messaggi di pywebview,
        che alla pagina non servono.
        """
        def guscio():
            self._occupato = True
            _verso_pagina('cambiaStato', 'working')
            diario = Diario()
            vecchio_out, vecchio_err = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = diario
            try:
                funzione(*argomenti)
                _verso_pagina('cambiaStato', 'done')
            except Exception as exc:
                _verso_pagina('aggiungiRiga', f'{exc}')
                _verso_pagina('aggiungiRiga', traceback.format_exc())
                _verso_pagina('cambiaStato', 'error')
            finally:
                diario.flush()
                sys.stdout, sys.stderr = vecchio_out, vecchio_err
                self._occupato = False

        threading.Thread(target=guscio, daemon=True).start()

    @staticmethod
    def _miniatura(video_id) -> str:
        """Indirizzo della miniatura, ricavato dall'identificativo del video.

        YouTube le serve a un indirizzo prevedibile, quindi non serve nessuna
        chiamata in piu': l'identificativo sta gia' dentro la entry che il
        motore produce, e il motore non va toccato per averla.
        """
        return f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg' if video_id else ''

    @staticmethod
    def _viste(numero) -> str:
        """Abbrevia il numero di visualizzazioni: 1.243.905 diventa 1,2 Mln."""
        try:
            n = int(numero or 0)
        except (TypeError, ValueError):
            return ''
        if n >= 1_000_000_000:
            return f'{n / 1_000_000_000:.1f}'.replace('.', ',') + ' Mrd'
        if n >= 1_000_000:
            return f'{n / 1_000_000:.1f}'.replace('.', ',') + ' Mln'
        if n >= 1_000:
            return f'{n / 1_000:.0f} K'
        return str(n) if n else ''

    @staticmethod
    def _durata(secondi) -> str:
        try:
            s = int(secondi or 0)
        except (TypeError, ValueError):
            return ''
        if not s:
            return ''
        ore, resto = divmod(s, 3600)
        minuti, sec = divmod(resto, 60)
        return f'{ore}:{minuti:02d}:{sec:02d}' if ore else f'{minuti}:{sec:02d}'


def main() -> None:
    global _finestra
    # La lingua e' quella salvata dalla GUI Flet: le due interfacce condividono
    # settings.json, cosi' passare dall'una all'altra non fa ripartire da capo.
    i18n.set_language(i18n.load_saved() or 'it')

    _finestra = webview.create_window(
        'AudioDex',
        os.path.join(_HERE, 'web', 'index.html'),
        js_api=Api(),
        width=1180,
        height=780,
        min_size=(900, 620),
        background_color='#0d0620',
        text_select=False,
    )
    webview.start()


if __name__ == '__main__':
    main()
