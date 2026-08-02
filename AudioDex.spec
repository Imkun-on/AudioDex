# Istruzioni per costruire AudioDex.exe con PyInstaller.
#
#     pyinstaller AudioDex.spec --noconfirm
#
# Cosa entra e cosa no
#     Entra tutto il programma: i quattro moduli del motore, la pagina web,
#     e l'interprete Python. Chi riceve l'eseguibile fa doppio clic: non
#     installa Python, non vede un file .py, non sa nemmeno che c'e' dentro.
#
#     NON entra FFmpeg, ed e' una scelta, non una dimenticanza. Sulla macchina
#     su cui e' stato costruito i due binari pesano 400 MB, e in modalita' a
#     file unico il contenuto viene riestratto in una cartella temporanea *a
#     ogni avvio*: mezzo gigabyte da scompattare ogni volta che si apre il
#     programma renderebbe l'attesa insopportabile, per una cosa che si
#     installa una volta sola con un comando.
#
#     Il programma se ne accorge da solo se manca e dice esattamente cosa
#     digitare, quindi il caso e' gia' gestito nel modo giusto.
#
# Perche' un file .spec e non una riga di comando
#     Perche' le scelte qui dentro vanno spiegate, e una riga di comando lunga
#     duecento caratteri non ha posto per farlo.

import os

# yt-dlp carica gli estrattori uno per uno solo quando servono: PyInstaller,
# che guarda gli import scritti nel codice, non ne troverebbe nemmeno uno e
# l'eseguibile saprebbe scaricare da nessun sito.
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

nascosti = [
    # Il motore: nessuno di questi e' importato in cima ad AudioDexApp, che
    # li carica solo quando la sezione corrispondente viene aperta.
    'AudioDex', 'BurnDex', 'PixDex', 'ClipDex',
    'Shared.i18n', 'Shared.logger_setup', 'Shared.http_client', 'Shared.percorsi',
    'Shared.strings_audiodex', 'Shared.strings_burndex',
    'Shared.strings_pixdex', 'Shared.strings_clipdex',
    'Database_Globale.scraper_db',
    # pywebview sceglie il motore grafico a runtime: quello di Windows non
    # compare in nessun import statico.
    'webview.platforms.winforms',
    'clr_loader', 'pythonnet',
    # BurnDex parla in COM con IMAPI2 attraverso questi.
    'win32com', 'win32com.client', 'pythoncom', 'pywintypes',
    # mutagen scrive i tag nel contenitore MP4.
    'mutagen', 'mutagen.mp4',
]
nascosti += collect_submodules('yt_dlp')

dati = [
    # La pagina: e' l'interfaccia vera e propria.
    ('web', 'web'),
]
dati += collect_data_files('yt_dlp')

a = Analysis(
    ['AudioDexApp.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=dati,
    hiddenimports=nascosti,
    hookspath=[],
    runtime_hooks=[],
    # Fuori cio' che non serve: sono decine di megabyte che non verrebbero
    # mai eseguiti.
    #
    # setuptools NON si puo' escludere, per quanto sembri inutile in un
    # programma finito: qualcosa nella catena carica ``pkg_resources``, che e'
    # parte di setuptools e si porta dietro le proprie dipendenze interne.
    # Toglierlo faceva morire l'eseguibile all'avvio, prima ancora di aprire
    # la finestra, con un ModuleNotFoundError su 'jaraco'.
    excludes=['tkinter', 'unittest', 'pydoc', 'doctest', 'test',
              'matplotlib', 'numpy', 'PIL'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AudioDex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # comprimere allunga l'avvio e insospettisce gli antivirus
    runtime_tmpdir=None,
    # Senza finestra di terminale alle spalle: e' un programma con
    # un'interfaccia, non uno script.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
