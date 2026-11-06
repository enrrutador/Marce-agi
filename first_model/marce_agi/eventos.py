"""EventBus — flujo observable del cerebro (contrato con el frontend futuro).

Cada ciclo cognitivo emite eventos en orden con secuencia monótona. El
frontend que vamos a construir se conecta a este stream: no hay otra
fuente de verdad sobre cómo trabaja el cerebro.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

TIPOS_EVENTO = (
    "ciclo.inicio",
    "ciclo.memoria_consulta",
    "ciclo.router_decision",
    "ciclo.razonador_inicio",
    "ciclo.razonador_resultado",
    "ciclo.aprendizaje",
    "ciclo.fin",
    "ciclo.error",
)


class EventBus:
    def __init__(self, archivo: Path | None = None) -> None:
        self._seq = 0
        self._archivo = Path(archivo) if archivo else None
        if self._archivo:
            self._archivo.parent.mkdir(parents=True, exist_ok=True)

    def emitir(self, tipo: str, payload: dict, origen: str) -> dict:
        self._seq += 1
        evento = {
            "seq": self._seq,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tipo": tipo,
            "origen": origen,
            "payload": payload,
        }
        if self._archivo:
            with open(self._archivo, "a", encoding="utf-8") as f:
                f.write(json.dumps(evento, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
        return evento

    @property
    def seq(self) -> int:
        return self._seq

    def replicar(self, archivo: Path) -> None:
        self._archivo = Path(archivo)
        self._archivo.parent.mkdir(parents=True, exist_ok=True)


def leer_stream(archivo: Path, max_eventos: int | None = None) -> list[dict]:
    eventos = []
    with open(archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                eventos.append(json.loads(linea))
    if max_eventos is not None:
        eventos = eventos[-max_eventos:]
    return eventos
