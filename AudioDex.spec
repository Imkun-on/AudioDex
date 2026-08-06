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
import sys

# yt-dlp carica gli estrattori uno per uno solo quando servono: PyInstaller,
# che guarda gli import scritti nel codice, non ne troverebbe nemmeno uno e
# l'eseguibile saprebbe scaricare da nessun sito.
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# La cartella di questo file. PyInstaller la passa allo spec come SPECPATH ma
# la aggiunge a sys.path solo piu' avanti, dentro Analysis(): l'import qui
# sotto serve prima, quindi ce la si mette da soli. Senza, la costruzione
# fallirebbe con un ModuleNotFoundError su 'Shared' a seconda di da dove si e'
# lanciato il comando.
sys.path.insert(0, os.path.abspath(SPECPATH))

# Dove sta la barra della schermata di caricamento e com'e' fatta. Le misure
# stanno li' e non qui perche' meta' della barra - il binario vuoto - e'
# disegnata dentro l'immagine da assets/binario.py, che legge lo stesso modulo:
# se le due meta' si scostassero anche di un pixel si vedrebbero due barre.
from Shared import avvio as _avvio

nascosti = [
    # Il motore: nessuno di questi e' importato in cima ad AudioDexApp, che
    # li carica solo quando la sezione corrispondente viene aperta.
    'AudioDex', 'BurnDex', 'PixDex', 'ClipDex',
    'Shared.i18n', 'Shared.logger_setup', 'Shared.http_client', 'Shared.percorsi',
    'Shared.spia_avanzamento', 'Shared.avvio',
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

# ── Il campo di testo appartiene alla barra, e a nessun altro ────────────────
#
# La schermata di PyInstaller ha UNA riga di testo aggiornabile, e in modalita'
# a file unico ci scrivono in due: noi, che ci disegniamo la barra, e il
# bootloader, che durante lo scompattamento ci mette il nome di ogni file che
# estrae. Il secondo arriva per primo e vince: nei primi secondi - proprio i
# piu' lunghi, quelli che la barra dovrebbe raccontare - al posto della barra
# scorrono 'Crypto\\PublicKey\\_ed25519.pyd' e 'zlib1.dll', che a chi guarda non
# dicono niente ed escono dal riquadro.
#
# E' il motivo per cui questo file, prima, teneva text_pos a None e rinunciava
# del tutto alla barra. EchoScript non ha il problema perche' e' costruito a
# cartella: senza scompattamento il bootloader non ha nomi da scrivere.
#
# Qui il file unico si tiene - e' una scelta gia' argomentata piu' sopra - e si
# chiude invece il campo di testo a chi non e' la barra. Il pezzo di Tcl qui
# sotto ridefinisce la procedura che disegna il testo perche' lasci passare solo
# le stringhe fatte di trattini U+2501 (e la stringa vuota, che e' la barra a
# zero): tutto il resto viene ignorato in silenzio. La procedura si puo'
# ridefinire dopo perche' Tcl risolve i nomi al momento della chiamata, non a
# quello della definizione.
#
# Il trattino si scrive come \\u2501 e non come se stesso di proposito: lo script
# viene salvato in UTF-8 ma Tcl 8.6 lo rilegge con la codifica di sistema, e un
# carattere fuori tabella arriverebbe come scarabocchio. Cosi' resta ASCII puro.
_SOLO_LA_BARRA = r"""
proc canvas_text_update {canvas tag _var - -} {
    upvar $_var var
    if {[string map [list \u2501 {}] $var] ne ""} { return }
    $canvas itemconfigure $tag -text $var
}
"""

from PyInstaller.building import splash_templates as _modelli

_costruisci_script = _modelli.build_script


def _script_con_filtro(*a, **k):
    return _costruisci_script(*a, **k) + _SOLO_LA_BARRA


# Se una versione futura di PyInstaller cambiasse il modello, la costruzione
# deve comunque riuscire: si perderebbe il filtro e tornerebbero i nomi dei
# file, non si romperebbe l'eseguibile.
if 'canvas_text_update' in _modelli.image_script:
    _modelli.build_script = _script_con_filtro
else:
    print('AVVISO: il modello Tcl della schermata di avvio e\' cambiato, '
          'la barra restera\' coperta dai nomi dei file durante lo scompattamento.')

# La schermata di caricamento.
#
#     Un file unico da 67 MB viene riestratto in una cartella temporanea a ogni
#     avvio, e sono diversi secondi in cui sullo schermo non succede niente:
#     chi lancia il programma pensa che il doppio clic non abbia funzionato e
#     ne fa un altro, avviando due copie.
#
#     La chiude il programma stesso quando la pagina e' pronta a mostrarsi (in
#     AudioDexApp, alla prima chiamata di dipinta()), cosi' l'immagine sparisce
#     nell'istante in cui compare la finestra e non un attimo prima.
#
#     La riga di testo e' la barra, e nient'altro. Il bootloader la userebbe
#     volentieri per scrivere il nome di ogni file che sta scompattando -
#     percorsi interni che a chi guarda non dicono niente e che escono dal
#     riquadro - ma AudioDexApp se ne impossessa alla prima riga eseguita e da
#     li' in poi ci scrive solo trattini. Il valore iniziale e' vuoto di
#     proposito: a barra ferma si deve vedere il binario disegnato
#     nell'immagine, non un riempimento che non corrisponde a niente.
caricamento = Splash(
    os.path.join('assets', 'caricamento.png'),
    binaries=a.binaries,
    datas=a.datas,
    text_pos=_avvio.POSIZIONE,
    text_size=_avvio.CORPO,
    text_font=_avvio.CARATTERE,
    text_color=_avvio.COLORE,
    text_default=_avvio.barra(0.0),
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
