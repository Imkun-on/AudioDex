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
    'Shared.spia_avanzamento',
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
# L'icona della finestra: la stessa dell'eseguibile, ma pywebview la vuole
# come file, non incorporata nelle risorse del .exe.
if os.path.exists(os.path.join('assets', 'AudioDex.ico')):
    dati.append((os.path.join('assets', 'AudioDex.ico'), 'assets'))
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
    #
    # tkinter NON si puo' piu' escludere: la schermata di caricamento qui sotto
    # e' disegnata da Tcl/Tk, ed e' l'unico modo di mostrare qualcosa mentre il
    # file unico si scompatta - in quel momento il programma vero non e' ancora
    # partito e nessuna riga di codice nostro puo' girare.
    #
    # Qt e IPython pesavano insieme 52 MB su 165, e non ne veniva eseguita
    # una riga:
    #   PySide6  pywebview sa parlare con piu' motori grafici e PyInstaller
    #            li impacchetta tutti. Su Windows si usa winforms, quello di
    #            sistema; Qt era 45 MB scompattati a ogni avvio per niente.
    #   IPython  rich, per capire se sta scrivendo dentro un notebook, prova
    #            a importarlo dentro un try. PyInstaller vede l'import e si
    #            porta dietro IPython, jedi e traitlets: qui non c'e' nessun
    #            notebook, e il try regge benissimo l'assenza.
    excludes=['unittest', 'pydoc', 'doctest', 'test',
              'matplotlib', 'numpy', 'PIL',
              'PySide6', 'PySide2', 'PyQt5', 'PyQt6', 'qtpy', 'shiboken6',
              'IPython', 'jedi'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# La schermata di caricamento.
#
#     Un file unico da 67 MB viene riestratto in una cartella temporanea a ogni
#     avvio, e sono diversi secondi in cui sullo schermo non succede niente:
#     chi lancia il programma pensa che il doppio clic non abbia funzionato e
#     ne fa un altro, avviando due copie.
#
#     La chiude il programma stesso quando la pagina e' pronta a mostrarsi (in
#     AudioDexApp, alla prima chiamata di avvio()), cosi' l'immagine sparisce
#     nell'istante in cui compare la finestra e non un attimo prima.
#     text_pos resta None di proposito. Dandogli una posizione, il bootloader
#     ci scrive dentro il nome di ogni file che sta scompattando: percorsi
#     interni come 'jedi\\third_party\\typeshed\\...' che a chi guarda non
#     dicono niente e che escono dal riquadro. La frase e' gia' disegnata
#     nell'immagine.
caricamento = Splash(
    os.path.join('assets', 'caricamento.png'),
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    minify_script=True,
    always_on_top=False,        # stare davanti a tutto e' da finestra di errore
)

exe = EXE(
    pyz,
    caricamento,
    caricamento.binaries,
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
    # Il marchio: il disco con le barre del livello, verde su nero come
    # l'interfaccia. Senza questa riga Windows mostra l'icona di ripiego di
    # PyInstaller, che non c'entra niente con il programma.
    icon=os.path.join('assets', 'AudioDex.ico'),
)
