"""Selezione della lingua e catalogo dei testi mostrati all'utente.

A cosa serve
    Tenere in un posto solo tutte le frasi che finiscono sotto gli occhi di
    chi usa i programmi, in italiano e in inglese, e decidere quale delle due
    versioni stampare. Il codice chiama ``t('chiave')`` e non sa in che lingua
    sta scrivendo: la scelta e' fatta una volta all'avvio.

Cosa NON viene tradotto
    I commenti, i docstring e le righe di log su file restano in italiano.
    Servono a chi legge o mantiene il codice, non a chi lo usa, e tradurli
    raddoppierebbe il lavoro di manutenzione senza aiutare nessuno.

Come si sceglie la lingua
    Tre livelli, dal piu' forte al piu' debole:
      1. ``--lang it|en`` sulla riga di comando: vale per quel solo lancio e
         non tocca la preferenza salvata (serve agli script);
      2. la preferenza salvata in ``settings.json``, scritta la prima volta
         che si risponde alla domanda;
      3. la domanda vera e propria, posta in inglese perche' e' l'unica
         lingua che chi non parla italiano puo' leggere di sicuro.
    Con ``--lang ask`` la domanda si ripropone e la risposta viene risalvata.

Perche' la domanda solo in modalita' interattiva
    Un lancio con ``--url`` o dentro uno script non ha nessuno davanti a
    rispondere: restare appesi a un prompt sarebbe un blocco. Senza risposta
    possibile si usa l'italiano, cioe' il comportamento che i due programmi
    hanno sempre avuto.
"""
from __future__ import annotations

import json
import os
import sys

from rich.box import ROUNDED
from rich.table import Table

from Shared.logger_setup import console

# Lingue disponibili, nell'ordine in cui compaiono nella domanda. L'inglese
# e' primo perche' la domanda e' in inglese: chi non capisce l'italiano deve
# trovare subito la voce che gli serve.
LANGUAGES = (('en', 'English'), ('it', 'Italiano'))
LANGUAGE_CODES = tuple(code for code, _ in LANGUAGES)

# Lingua di ripiego: e' quella in cui i due programmi hanno sempre parlato,
# quindi un aggiornamento non cambia il comportamento a chi non fa nulla.
DEFAULT_LANG = 'it'

# File della preferenza, accanto agli script. Non e' il database globale:
# quello raccoglie i download, questa e' un'impostazione dell'interfaccia.
_SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'settings.json',
)

_lingua = DEFAULT_LANG
_catalogo: dict[str, dict[str, str]] = {}


# ── Catalogo e traduzione ────────────────────────────────────────────────────

def register(catalogo: dict[str, dict[str, str]]) -> None:
    """Aggiunge al catalogo comune le frasi di un programma.

    Ogni tool tiene le proprie in un modulo a parte (``strings_audiodex``,
    ``strings_burndex``) e le registra all'import. Cosi' i due cataloghi
    restano separati da leggere ma condividono la stessa macchina, e le voci
    comuni — "Annullato", "Scelta non valida" — si scrivono una volta sola.
    """
    _catalogo.update(catalogo)


def t(chiave: str, **kwargs) -> str:
    """Restituisce la frase ``chiave`` nella lingua corrente, formattata.

    I segnaposto sono quelli di ``str.format`` (``{nome}``): passandoli come
    argomenti nominati la frase resta leggibile nel catalogo e ogni lingua
    puo' metterli nell'ordine che le serve, che tra italiano e inglese quasi
    mai coincide.

    Una chiave assente non fa cadere il programma: viene restituita cosi'
    com'e', in modo che un errore di battitura si veda a schermo come stringa
    strana invece di interrompere un download a meta'.
    """
    voce = _catalogo.get(chiave)
    if voce is None:
        return chiave
    testo = voce.get(_lingua) or voce.get(DEFAULT_LANG) or chiave
    return testo.format(**kwargs) if kwargs else testo


def set_language(codice: str) -> None:
    """Imposta la lingua corrente, ignorando i codici sconosciuti."""
    global _lingua
    if codice in LANGUAGE_CODES:
        _lingua = codice


def get_language() -> str:
    """Codice della lingua corrente ('it' o 'en')."""
    return _lingua


# ── Risposte dell'utente ─────────────────────────────────────────────────────
#
# Le risposte vengono accettate in entrambe le lingue a prescindere da quella
# scelta: chi ha l'interfaccia in inglese ma digita 's' per abitudine non deve
# vedersi annullare l'operazione, e viceversa. Costa nulla ed elimina una
# categoria intera di errori.

_SI = frozenset({'s', 'si', 'sì', 'y', 'yes'})
_NO = frozenset({'n', 'no'})
_USCITA = frozenset({'q', 'quit', 'esci', 'exit'})
_TUTTI = frozenset({'all', 'a', 'tutti', 'tutte'})


def is_yes(risposta: str) -> bool:
    """True se la risposta e' un si', in italiano o in inglese."""
    return risposta.strip().lower() in _SI


def is_no(risposta: str) -> bool:
    """True se la risposta e' un no esplicito."""
    return risposta.strip().lower() in _NO


def is_quit(risposta: str) -> bool:
    """True se la risposta chiede di uscire."""
    return risposta.strip().lower() in _USCITA


def is_all(risposta: str) -> bool:
    """True se la risposta significa "tutti gli elementi"."""
    return risposta.strip().lower() in _TUTTI


# ── Preferenza salvata ───────────────────────────────────────────────────────

def load_saved() -> str | None:
    """Legge la lingua salvata, o None se non c'e' o il file e' illeggibile.

    Qualsiasi problema — file assente, JSON rotto, permessi — vale come
    "nessuna preferenza": si torna a chiedere, che e' sempre recuperabile.
    Un'impostazione dell'interfaccia non deve mai impedire un download.
    """
    try:
        with open(_SETTINGS_FILE, encoding='utf-8') as fh:
            codice = json.load(fh).get('lang')
    except (OSError, ValueError):
        return None
    return codice if codice in LANGUAGE_CODES else None


def save(codice: str) -> None:
    """Salva la lingua scelta, conservando le altre chiavi del file.

    La rilettura preventiva serve a non cancellare impostazioni che versioni
    future potrebbero aggiungere accanto a questa. Un errore di scrittura
    viene ignorato: si perde solo la memoria della scelta, e la domanda
    ricompare al lancio successivo.
    """
    if codice not in LANGUAGE_CODES:
        return
    dati = {}
    try:
        with open(_SETTINGS_FILE, encoding='utf-8') as fh:
            letto = json.load(fh)
        if isinstance(letto, dict):
            dati = letto
    except (OSError, ValueError):
        pass

    dati['lang'] = codice
    try:
        with open(_SETTINGS_FILE, 'w', encoding='utf-8') as fh:
            json.dump(dati, fh, indent=2)
    except OSError:
        pass


# ── Domanda all'avvio ────────────────────────────────────────────────────────

def ask() -> str:
    """Chiede la lingua e restituisce il codice scelto.

    La domanda e' in inglese di proposito: e' l'unica che chi non parla
    italiano puo' leggere, e chi parla italiano la capisce comunque. Il nome
    di ogni lingua e' scritto nella lingua stessa ("Italiano", non "Italian"),
    cosi' si riconosce senza sapere in che lingua e' l'elenco.

    L'invio a vuoto vale English, la prima voce: e' la scelta piu' probabile
    per chi si trova davanti una domanda in inglese senza averla cercata.
    """
    tabella = Table(show_header=False, box=ROUNDED, border_style='bright_blue',
                    padding=(0, 2), expand=False)
    tabella.add_column('N', style='bold yellow', justify='right', width=3)
    tabella.add_column('Lingua', style='white')
    for i, (_, nome) in enumerate(LANGUAGES, 1):
        tabella.add_row(str(i), f'[bold]{nome}[/bold]')

    console.print()
    console.print(tabella)

    while True:
        try:
            scelta = console.input(
                '\n[bold]Language / Lingua (1-'
                f'{len(LANGUAGES)}, Enter = English): [/bold]'
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return DEFAULT_LANG

        if not scelta:
            return LANGUAGE_CODES[0]
        if scelta in LANGUAGE_CODES:
            return scelta
        try:
            n = int(scelta)
            if 1 <= n <= len(LANGUAGES):
                return LANGUAGE_CODES[n - 1]
        except ValueError:
            pass
        console.print('[error]Invalid choice / Scelta non valida.[/error]')


def peek_lang_arg(argv: list[str] | None = None) -> str | None:
    """Cerca ``--lang`` negli argomenti prima che argparse entri in gioco.

    Serve perche' i testi di ``--help`` vengono composti mentre il parser si
    costruisce: aspettare ``parse_args()`` per sapere la lingua vorrebbe dire
    stampare un aiuto sempre nella lingua sbagliata. Qui si guarda la riga di
    comando grezza, si imposta la lingua, e solo dopo si costruisce il parser
    — che dichiara comunque ``--lang``, cosi' compare nell'aiuto e i valori
    fuori elenco vengono respinti con il messaggio di argparse.

    Riconosce sia ``--lang en`` sia ``--lang=en``, e ``-l`` nelle stesse due
    forme. Ritorna None se l'opzione non c'e'.
    """
    argomenti = list(sys.argv[1:] if argv is None else argv)
    for i, a in enumerate(argomenti):
        if a in ('--lang', '-l'):
            if i + 1 < len(argomenti):
                return argomenti[i + 1].strip().lower()
            return None
        for prefisso in ('--lang=', '-l='):
            if a.startswith(prefisso):
                return a[len(prefisso):].strip().lower()
    return None


def resolve() -> tuple[str, bool]:
    """Decide la lingua del lancio in corso, prima di costruire il parser.

    Ritorna (codice, domanda_in_sospeso). Il secondo valore esiste perche' la
    domanda non si puo' porre qui: ``--help`` deve poter essere stampato e
    uscire senza che nessuno debba rispondere a nulla, e il banner va mostrato
    prima di qualsiasi prompt. Il chiamante chiama quindi ``confirm()`` piu'
    avanti, quando ha gia' letto gli argomenti e sa se c'e' davvero qualcuno
    davanti allo schermo.

    Finche' la domanda resta in sospeso vale la lingua di ripiego, cosi' un
    eventuale messaggio d'errore di argparse esce comunque in una lingua
    sensata invece che a vuoto.
    """
    richiesta = peek_lang_arg()

    if richiesta in LANGUAGE_CODES:
        # Flag esplicito: vale per questo lancio soltanto e non sovrascrive la
        # preferenza salvata. Un'opzione passata da uno script non deve
        # cambiare in silenzio cosa vedra' la persona al lancio successivo.
        set_language(richiesta)
        return richiesta, False

    salvata = load_saved()

    if richiesta == 'ask':
        # Richiesta esplicita di riscegliere: si chiede anche quando una
        # preferenza c'e' gia', e la risposta la sostituisce.
        set_language(salvata or DEFAULT_LANG)
        return get_language(), True

    if salvata:
        set_language(salvata)
        return salvata, False

    set_language(DEFAULT_LANG)
    return DEFAULT_LANG, True


def confirm(in_sospeso: bool) -> str:
    """Pone la domanda rimasta in sospeso, se ha senso porla, e salva.

    Va chiamata dopo il banner e prima di qualunque altro output: da li' in
    poi tutto il programma parla nella lingua scelta.

    Il chiamante passa False quando gli argomenti escludono la presenza di una
    persona (``--url``, ``--search``, ``--yes``): in quei casi restare appesi a
    un prompt bloccherebbe uno script. Il controllo sul terminale e' fatto qui
    perche' vale allo stesso modo per tutti i programmi.
    """
    if not in_sospeso or not _stdin_utilizzabile():
        return get_language()
    codice = ask()
    set_language(codice)
    save(codice)
    return codice


def _stdin_utilizzabile() -> bool:
    """True se c'e' davvero un terminale da cui leggere una risposta.

    Con l'input rediretto da file o da pipe — come nelle prove automatiche —
    un prompt riceverebbe subito EOF, e la domanda si risolverebbe da sola in
    modo invisibile. Meglio non porla affatto e restare sul ripiego.
    """
    try:
        return bool(sys.stdin) and sys.stdin.isatty()
    except (AttributeError, ValueError):
        return False
