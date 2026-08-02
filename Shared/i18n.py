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

Chi puo' cambiare lingua
    Solo la GUI. I tre programmi da riga di comando — AudioDex, BurnDex,
    PixDex — parlano italiano e basta: nessuna domanda all'avvio, nessuna
    opzione ``--lang`` da ricordare. Chi lavora nel terminale vuole vedere
    subito il banner e cominciare, non rispondere a una domanda sulla lingua
    ogni volta che apre un progetto nuovo.

Perche' il catalogo resta bilingue
    Perche' la GUI la scelta ce l'ha, ed e' li' che ha senso: e' un menu a
    tendina, si cambia con un clic e si vede il risultato immediatamente. La
    stessa scelta come argomento da digitare era solo un ostacolo in piu'.
    Le traduzioni inglesi restano quindi tutte al loro posto e in uso.

Dove finisce la preferenza
    In ``settings.json``, accanto agli script, scritta dalla GUI quando si
    cambia voce nel menu. E' un'impostazione di chi usa il programma, non del
    progetto, e infatti il file non viene versionato.
"""
from __future__ import annotations

import json
import os

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
