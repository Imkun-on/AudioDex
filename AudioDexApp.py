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

# ── Testi propri dell'interfaccia ────────────────────────────────────────────
# Non stanno in Shared/ perche' riguardano solo questa finestra, e mescolarli
# al catalogo di AudioDex renderebbe piu' difficile capire, leggendo quel file,
# quali frasi appaiono a terminale e quali no.
TESTI_APP: dict[str, dict[str, str]] = {
    'app.title':        {'it': 'AudioDex', 'en': 'AudioDex'},
    'app.subtitle':     {'it': 'Scarica  ·  Masterizza  ·  Rimasterizza',
                         'en': 'Download  ·  Burn  ·  Remaster'},
    'app.author':       {'it': 'di Imkun-on', 'en': 'by Imkun-on'},
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
    'done.summary':     {'it': 'Scaricati {ok} su {tot}  ·  {falliti} falliti',
                         'en': 'Downloaded {ok} of {tot}  ·  {falliti} failed'},
}
i18n.register(TESTI_APP)


# ── Moduli del motore, caricati alla prima richiesta ──────────────────────────
# Importare AudioDex costa qualche secondo (yt-dlp non e' leggero): farlo qui
# invece che all'avvio fa comparire la finestra subito, che e' la prima cosa
# che si giudica di un programma.
_audiodex = None


def _motore():
    global _audiodex
    if _audiodex is None:
        import AudioDex as _ad
        _audiodex = _ad
    return _audiodex


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
        }

    def cambia_lingua(self, codice: str) -> dict:
        i18n.set_language(codice)
        i18n.save(codice)
        return {'ok': True, 'lingua': i18n.get_language()}

    def scegli_cartella(self) -> dict:
        """Apre il selettore di cartelle del sistema."""
        try:
            scelta = _finestra.create_file_dialog(webview.FOLDER_DIALOG)
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
        ad = _motore()
        cartella = (opzioni.get('cartella')
                    or os.path.join(_HERE, 'download_audio'))
        os.makedirs(cartella, exist_ok=True)

        esiti = ad.download_batch(
            self._risultati,
            cartella,
            opzioni.get('formato', 'm4a'),
            max_workers=int(opzioni.get('paralleli', 3)),
            fetch_lyrics=bool(opzioni.get('testi', True)),
            media=opzioni.get('media', 'audio'),
            dividi=bool(opzioni.get('dividi', False)),
        )
        ok = sum(1 for e in esiti if e.get('status') == 'ok')
        falliti = sum(1 for e in esiti if e.get('status') == 'fail')
        _verso_pagina('mostraRiepilogo', {
            'testo': i18n.t('done.summary', ok=ok, tot=len(esiti), falliti=falliti),
            'ok': falliti == 0,
        })

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
