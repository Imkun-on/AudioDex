# -*- coding: utf-8 -*-
"""Mette il binario della barra dentro assets/caricamento.png.

Cosa cambia nell'immagine
    Al posto del riquadro con dentro «caricamento in corso...» ci va il binario
    vuoto della barra di avvio: una linea di 190x3 pixel, la stessa che il velo
    di caricamento della pagina disegna in CSS (``.avvio-barra``).

Perche' il binario sta nell'immagine e non lo disegna il programma
    Perche' nei primi secondi dopo il doppio clic il programma non esiste
    ancora: il bootloader di PyInstaller sta riestraendo il file unico, e
    l'unica cosa sullo schermo e' questa immagine. Un binario gia' disegnato
    e' una barra vuota, che e' la verita'; senza, ci sarebbe il nulla.

    A riempirlo ci pensa poi ``Shared/avvio.py``, scrivendoci sopra una fila di
    trattini pesanti con ``pyi_splash.update_text``. Le due meta' della stessa
    barra: le misure stanno quindi in un posto solo, ed e' quel modulo.

Perche' la frase se ne va
    Perche' questa immagine e' disegnata una volta sola e non sa in che lingua
    girera' il programma, mentre una barra si legge uguale in tutte. E perche'
    una frase che dice «caricamento in corso» accanto a una barra che dice a
    che punto e' il caricamento e' la stessa cosa detta due volte, la seconda
    peggio.

Si esegue a mano quando la geometria cambia, non durante la costruzione:

    python assets/binario.py

Rilanciarlo non fa danni: ripulisce sempre la stessa fascia di pixel e ci
ridisegna sopra lo stesso binario, quindi il risultato e' identico che lo si
lanci una volta o dieci.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Shared.avvio import BINARIO          # noqa: E402

IMMAGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caricamento.png')

# La fascia da ripulire: il riquadro della frase stava fra y 232 e 262 e fra
# x 83 e 437, bordi arrotondati compresi. Si prende con abbondanza, tanto sotto
# c'e' solo il fondo.
FASCIA = (78, 226, 442, 268)

# Il fondo di questa parte dell'immagine, che per fortuna e' regolare: verde
# quasi nero, con una riga di scansione nera ogni tre. Ricostruirlo e' esatto,
# non approssimato, ed e' il motivo per cui si puo' cancellare il riquadro senza
# lasciare una toppa che si vede.
FONDO = (0x05, 0x0a, 0x06)
SCANSIONE = (0, 0, 0)

# Il colore del binario: --bordo (#7cff8c1a) posato sul fondo. Il conto e' gia'
# fatto qui perche' ImageDraw scrive le tinte cosi' come sono invece di fonderle
# con quello che trova sotto.
VUOTO = tuple(round(FONDO[c] + ((0x7c, 0xff, 0x8c)[c] - FONDO[c]) * (0x1a / 255))
              for c in range(3))


def disegna(percorso: str = IMMAGINE) -> None:
    """Toglie il riquadro della frase e ci mette il binario vuoto."""
    tela = Image.open(percorso).convert('RGB')
    pennello = ImageDraw.Draw(tela)

    x0, y0, x1, y1 = FASCIA
    for y in range(y0, y1 + 1):
        pennello.line((x0, y, x1, y),
                      fill=SCANSIONE if y % 3 == 0 else FONDO)

    x, y, largo, spesso = BINARIO
    pennello.rounded_rectangle((x, y, x + largo - 1, y + spesso - 1),
                               radius=spesso / 2, fill=VUOTO)
    tela.save(percorso)


if __name__ == '__main__':
    disegna()
    print('binario disegnato in', IMMAGINE)
