"""Configurazione del logging e tema/simboli Rich condivisi da tutti gli scraper.

Centralizza ciò che ogni scraper deve avere identico: la console Rich con i
nomi di stile usati nei markup (es. [error], [accent]), i simboli Unicode di
esito e la creazione del logger su file.
"""
from __future__ import annotations

import logging
import os

from rich.console import Console
from rich.theme import Theme

# ── Tema Rich condiviso ───────────────────────────────────────
# Associa un nome semantico a ogni colore: nel codice si scrive
# [warning]...[/warning] invece del colore concreto, così la palette
# si cambia in un punto solo per tutti gli scraper.
THEME = Theme({
    "info":      "cyan",
    "success":   "bold green",
    "warning":   "bold yellow",
    "error":     "bold red",
    "title":     "bold bright_magenta",
    "dim_label": "dim white",
    "accent":    "bright_blue",
    "ok":        "green",
    "fail":      "red",
})

console = Console(theme=THEME)

# ── Simboli Unicode di esito (già colorati col markup del tema) ───────────────────────────────────────────
SYM_OK    = "[ok]\u2713[/ok]"
SYM_FAIL  = "[fail]\u2717[/fail]"
SYM_ARROW = "[accent]\u25b6[/accent]"
SYM_DOT   = "[accent]\u2022[/accent]"


def setup_logger(
    name: str,
    filename: str,
    *,
    level: int = logging.DEBUG,
    ytdlp: bool = False,
) -> logging.Logger:
    """Crea un logger che scrive solo su file, nella cartella logs/ del progetto.

    Niente handler verso il terminale: l'output a video è gestito da Rich
    (tabelle, pannelli, barre live) e righe di log in mezzo lo rovinerebbero.
    Il controllo ``if not log.handlers`` evita di aggiungere handler doppi
    se la funzione viene chiamata più volte con lo stesso nome.

    Parametri
    ---------
    name : str
        Nome del logger.
    filename : str
        Nome del file di log (verrà creato in ``logs/``).
    level : int
        Livello minimo di logging (default DEBUG).
    ytdlp : bool
        Se True crea anche il sub-logger ``<name>.ytdlp``, limitato ai
        WARNING per non riempire il file con l'output verboso di yt-dlp.
    """
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log = logging.getLogger(name)
    log.setLevel(level)

    if not log.handlers:
        fh = logging.FileHandler(
            os.path.join(log_dir, filename),
            encoding='utf-8',
        )
        fh.setLevel(level)
        fmt = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        fh.setFormatter(fmt)
        log.addHandler(fh)

    if ytdlp:
        ytdlp_log = logging.getLogger(f'{name}.ytdlp')
        ytdlp_log.setLevel(logging.WARNING)

    return log
