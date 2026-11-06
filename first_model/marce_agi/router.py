"""Router — decisión determinista de razonador vía Thompson sampling.

Es la semilla del AB-MCTS de fase 1: cada razonador es un brazo de bandido
con posterior Beta(wins, tries). Nombres de razonadores idénticos al estado
que produce training/train_state.py (comparten esquema {"wins","tries"}).
"""

from __future__ import annotations

import random
from typing import Iterable

from . import RAZONADORES


def _posterior(stats: dict, semilla: str, nombre: str) -> float:
    rng = random.Random(f"{semilla}|{nombre}")
    if not stats:
        return rng.betavariate(1, 1)
    return rng.betavariate(stats.get("wins", 0) + 1, stats.get("tries", 0) - stats.get("wins", 0) + 1)


class Router:
    def __init__(self, stats: dict[str, dict] | None = None) -> None:
        stats = stats or {}
        self._stats = {n: dict(stats.get(n) or {"wins": 0, "tries": 0}) for n in RAZONADORES}

    def decidir(self, semilla: str) -> tuple[str, dict]:
        jugadas = {n: _posterior(self._stats[n], semilla, n) for n in RAZONADORES}
        mejor = max(jugadas, key=lambda n: (jugadas[n], n))
        return mejor, jugadas

    def registrar(self, nombre: str, exito: bool) -> None:
        self._stats[nombre]["tries"] += 1
        if exito:
            self._stats[nombre]["wins"] += 1

    def estado(self) -> dict:
        return {n: dict(self._stats[n]) for n in RAZONADORES}
