"""Cambia la paleta en vivo (tema oscuro, claro o mezcla).

Todas las escenas leen los colores de config.C en cada fotograma, así que
basta con reemplazar sus valores. El logo usa sus colores del SVG oficial
(negativo) o la versión positiva del manual (letras Kiro Black).
"""
import config as cfg
from lib import ease as E
from lib import logo as L

_actual = None


def apply(nombre):
    global _actual
    if nombre == _actual:
        return
    cfg.C.update(cfg.PALETA_CLARA if nombre == "claro" else cfg.PALETA_OSCURA)
    if nombre == "claro":
        L.COLORS.update(word=L.COLORS_POSITIVO_WORD, solutions=L.COLORS_POSITIVO_SOL)
    else:
        L.COLORS.update(L.COLORS_NEGATIVO)
    _actual = nombre


def luz(t):
    """Avance de la apertura de luz (0 = todo oscuro, 1 = todo claro)."""
    if cfg.TEMA == "claro":
        return 1.0
    if cfg.TEMA == "oscuro":
        return 0.0
    return E.in_out_sine(E.prog(t, *cfg.LUZ))   # amanece: empieza despacio, sin estallido
