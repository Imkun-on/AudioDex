"""Database SQLite globale dei download per gli scraper Audio, Manga e Anime.

Un'unica tabella 'downloads' raccoglie lo storico di tutti gli scraper:
i campi comuni (titolo, percorso, dimensione, data) più colonne specifiche
per tipo. Così lo storico è interrogabile da un punto solo e ogni scraper
può verificare cosa è già stato scaricato.

Filosofia degli errori: il database è un registro accessorio, quindi ogni
problema viene solo loggato come warning e non interrompe mai i download.
"""
from __future__ import annotations

import logging
import os
import sqlite3
import threading
from datetime import datetime, timezone

log = logging.getLogger('scraper_db')

# Il file .db vive accanto a questo modulo, condiviso da tutti gli scraper.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper_metadata.db')

# Una connessione per thread: sqlite3 vieta di usare la stessa connessione
# da thread diversi, e gli scraper scrivono dai thread di download.
_local = threading.local()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS downloads (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    scraper_type    TEXT NOT NULL,       -- 'audio', 'manga', 'anime'

    -- Campi universali
    source_id       TEXT NOT NULL,       -- YouTube video ID / MangaDex chapter UUID / AnimeUnity episode ID
    title           TEXT NOT NULL,
    source_url      TEXT DEFAULT '',
    file_path       TEXT NOT NULL,       -- Percorso relativo dal progetto
    file_size_bytes INTEGER DEFAULT 0,
    downloaded_at   TEXT NOT NULL,       -- ISO 8601

    -- Collezione (album/playlist, manga, anime)
    collection_name TEXT DEFAULT '',
    collection_id   TEXT DEFAULT '',

    -- Audio
    artist          TEXT DEFAULT '',
    duration_secs   REAL DEFAULT 0,
    audio_format    TEXT DEFAULT '',
    track_number    INTEGER DEFAULT 0,

    -- Manga
    chapter_number  TEXT DEFAULT '',
    page_count      INTEGER DEFAULT 0,
    scanlation_group TEXT DEFAULT '',
    language        TEXT DEFAULT '',
    is_cbz          INTEGER DEFAULT 0,

    -- Anime
    episode_number  TEXT DEFAULT '',
    anime_type      TEXT DEFAULT '',

    UNIQUE(scraper_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_scraper_type ON downloads(scraper_type);
CREATE INDEX IF NOT EXISTS idx_collection ON downloads(scraper_type, collection_name);
CREATE INDEX IF NOT EXISTS idx_downloaded_at ON downloads(downloaded_at);
"""


def _get_conn() -> sqlite3.Connection:
    """Restituisce la connessione SQLite del thread corrente, creandola al primo uso.

    La modalità WAL permette letture e scritture concorrenti dai vari
    thread di download senza che si blocchino a vicenda.
    """
    conn = getattr(_local, 'conn', None)
    if conn is None:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        _local.conn = conn
    return conn


def init_db() -> None:
    """Crea tabella e indici se non esistono."""
    try:
        conn = _get_conn()
        conn.executescript(_SCHEMA)
        conn.commit()
        log.debug("Database inizializzato: %s", DB_PATH)
    except Exception as e:
        log.warning("Errore init database: %s", e)


def _now_iso() -> str:
    """Timestamp corrente in UTC, formato ISO 8601 (ordinabile come testo)."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _relative_path(path: str) -> str:
    """Converte un percorso assoluto in relativo rispetto a questa cartella.

    Salvare percorsi relativi mantiene validi i riferimenti anche se la
    cartella del progetto viene spostata o rinominata. Su Windows il
    calcolo fallisce tra dischi diversi (ValueError): in quel caso si
    salva il percorso assoluto così com'è.
    """
    base = os.path.dirname(os.path.abspath(__file__))
    try:
        return os.path.relpath(path, base)
    except ValueError:
        return path


# === INSERT PER OGNI SCRAPER ===

def record_audio_download(
    source_id: str,
    title: str,
    source_url: str = '',
    file_path: str = '',
    file_size_bytes: int = 0,
    collection_name: str = '',
    collection_id: str = '',
    artist: str = '',
    duration_secs: float = 0,
    audio_format: str = '',
    track_number: int = 0,
) -> None:
    """Registra un brano audio scaricato.

    'INSERT OR REPLACE' sul vincolo UNIQUE(scraper_type, source_id):
    riscaricare la stessa traccia aggiorna la riga esistente invece di
    creare un duplicato.
    """
    try:
        conn = _get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO downloads
               (scraper_type, source_id, title, source_url, file_path,
                file_size_bytes, downloaded_at, collection_name, collection_id,
                artist, duration_secs, audio_format, track_number)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ('audio', source_id, title, source_url, _relative_path(file_path),
             file_size_bytes, _now_iso(), collection_name, collection_id,
             artist, duration_secs, audio_format, track_number),
        )
        conn.commit()
        log.debug("DB audio: %s", title)
    except Exception as e:
        log.warning("DB audio errore per '%s': %s", title, e)


def record_manga_download(
    source_id: str,
    title: str,
    source_url: str = '',
    file_path: str = '',
    file_size_bytes: int = 0,
    collection_name: str = '',
    collection_id: str = '',
    chapter_number: str = '',
    page_count: int = 0,
    scanlation_group: str = '',
    language: str = '',
    is_cbz: bool = False,
) -> None:
    """Registra un capitolo manga scaricato (stessa logica di quello audio)."""
    try:
        conn = _get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO downloads
               (scraper_type, source_id, title, source_url, file_path,
                file_size_bytes, downloaded_at, collection_name, collection_id,
                chapter_number, page_count, scanlation_group, language, is_cbz)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ('manga', source_id, title, source_url, _relative_path(file_path),
             file_size_bytes, _now_iso(), collection_name, collection_id,
             chapter_number, page_count, scanlation_group, language, int(is_cbz)),
        )
        conn.commit()
        log.debug("DB manga: %s", title)
    except Exception as e:
        log.warning("DB manga errore per '%s': %s", title, e)


def record_anime_download(
    source_id: str,
    title: str,
    source_url: str = '',
    file_path: str = '',
    file_size_bytes: int = 0,
    collection_name: str = '',
    collection_id: str = '',
    episode_number: str = '',
    anime_type: str = '',
) -> None:
    """Registra un episodio anime scaricato (stessa logica di quello audio)."""
    try:
        conn = _get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO downloads
               (scraper_type, source_id, title, source_url, file_path,
                file_size_bytes, downloaded_at, collection_name, collection_id,
                episode_number, anime_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ('anime', source_id, title, source_url, _relative_path(file_path),
             file_size_bytes, _now_iso(), collection_name, collection_id,
             episode_number, anime_type),
        )
        conn.commit()
        log.debug("DB anime: %s", title)
    except Exception as e:
        log.warning("DB anime errore per '%s': %s", title, e)


# === QUERY ===

def is_recorded(scraper_type: str, source_id: str) -> bool:
    """Indica se un download è già registrato (per saltare i duplicati)."""
    try:
        conn = _get_conn()
        row = conn.execute(
            "SELECT 1 FROM downloads WHERE scraper_type=? AND source_id=?",
            (scraper_type, source_id),
        ).fetchone()
        return row is not None
    except Exception:
        return False


def get_downloads(
    scraper_type: str | None = None,
    collection_name: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Elenca i download registrati, dal più recente, con filtri opzionali.

    Si può filtrare per tipo di scraper ('audio', 'manga', 'anime') e per
    nome della collezione (album, serie). Restituisce dizionari semplici,
    comodi da stampare o serializzare.
    """
    try:
        conn = _get_conn()
        query = "SELECT * FROM downloads WHERE 1=1"
        params: list = []
        if scraper_type:
            query += " AND scraper_type=?"
            params.append(scraper_type)
        if collection_name:
            query += " AND collection_name=?"
            params.append(collection_name)
        query += " ORDER BY downloaded_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        log.warning("DB query errore: %s", e)
        return []


def get_stats() -> dict:
    """Statistiche globali: numero di download e byte totali per ogni tipo di scraper."""
    try:
        conn = _get_conn()
        stats = {}
        for stype in ('audio', 'manga', 'anime'):
            row = conn.execute(
                "SELECT COUNT(*) as cnt, COALESCE(SUM(file_size_bytes),0) as total_bytes "
                "FROM downloads WHERE scraper_type=?",
                (stype,),
            ).fetchone()
            stats[stype] = {'count': row['cnt'], 'total_bytes': row['total_bytes']}
        return stats
    except Exception as e:
        log.warning("DB stats errore: %s", e)
        return {}
