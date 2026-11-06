"""CognitiveKernel — orquestador del bucle cognitivo básico (fase 0).

Ciclo por un objetivo: registros episódicos → consulta de memoria →
router decide razonador (Thompson) → razonador resuelve deterministamente
→ evaluación y aprendizaje (indexa la experiencia) → respuesta trazable
con evidencia. Todo queda en el stream de eventos cerebro.jsonl para el
futuro frontend observador.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

from . import TIPO_EPISODICA, TIPO_SEMANTICA
from .eventos import EventBus
from .memoria import MemoryStore, tokenizar
from .razonadores import razonadores_disponibles
from .router import Router

NOMBRE = "marce-agi-kernel"
VERSION_ESTADO = 1


class CognitiveKernel:
    def __init__(self, state_dir: Optional[Path] = None, seed: int = 20261105) -> None:
        self.state_dir = Path(state_dir) if state_dir else Path("first_model/state")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.seed = int(seed)
        self.memoria = MemoryStore()
        self.memoria.cargar(self.state_dir / "memoria.json")
        self.router = Router()
        self._cargar_router()
        self.eventos = EventBus(self.state_dir / "cerebro.jsonl")
        self.razonadores = razonadores_disponibles()
        self.expedientes: list[dict] = []

    # ----- ciclo cognitivo -------------------------------------------
    def pensar(self, objetivo: str, razonador: Optional[str] = None) -> dict:
        t0 = time.time()
        exp_id = self._hash_exp(objetivo)
        self.eventos.emitir("ciclo.inicio", {"objetivo": objetivo, "exp_id": exp_id}, NOMBRE)
        self.memoria.agregar("episodica", f"objetivo: {objetivo}", tags=tokenizar(objetivo))

        hits = self.memoria.consulta(texto=objetivo, top=8)
        self.eventos.emitir("ciclo.memoria_consulta",
                            {"objetivo": objetivo, "hits": [h["id"] for h in hits]}, NOMBRE)

        semilla_router = f"{self.seed}|{exp_id}"
        if razonador is None:
            elegido, posteriores = self.router.decidir(semilla_router)
        else:
            if razonador not in self.razonadores:
                raise ValueError(f"razonador inexistente: {razonador}")
            elegido, posteriores = razonador, {}
        self.eventos.emitir("ciclo.router_decision",
                            {"razonador": elegido, "posteriores": posteriores}, NOMBRE)

        self.eventos.emitir("ciclo.razonador_inicio", {"razonador": elegido}, NOMBRE)
        resultado = self.razonadores[elegido].resolver(objetivo, self.memoria)
        self.eventos.emitir("ciclo.razonador_resultado", resultado.dict(), f"razonador:{elegido}")

        self.router.registrar(elegido, resultado.exito)
        aprendizaje = self._aprender(objetivo, elegido, resultado)
        self.eventos.emitir("ciclo.aprendizaje", aprendizaje, NOMBRE)

        ciclo_resultado = {
            "exp_id": exp_id,
            "objetivo": objetivo,
            "razonador": elegido,
            "exito": resultado.exito,
            "respuesta": resultado.respuesta,
            "confianza": resultado.confianza,
            "evidencia_ids": resultado.evidencia_ids,
            "pasos": resultado.pasos,
            "duracion_s": round(time.time() - t0, 4),
        }
        self.eventos.emitir("ciclo.fin", ciclo_resultado, NOMBRE)
        self.expedientes.append(ciclo_resultado)
        self.guardar()
        return ciclo_resultado

    def _aprender(self, objetivo: str, razonador: str, resultado) -> dict:
        if resultado.exito:
            eid = self.memoria.agregar_evidencia(f"{razonador}|{self._hash_exp(objetivo)}",
                                                 f"resolución determinista por {razonador}")
            mid = self.memoria.agregar("semantica", f"resultado de '{objetivo}': {resultado.respuesta}",
                                       tags=tokenizar(objetivo), evidencia_ids=[eid],
                                       datos={"razonador": razonador})
            return {"aprendio": True, "memoria_id": mid, "evidencia_id": eid}
        self.memoria.agregar("episodica", f"sin resolución: {objetivo}", tags=tokenizar(objetivo),
                             datos={"razonador": razonador, "pendiente": True})
        return {"aprendio": False, "pendiente": True}

    # ----- estado -----------------------------------------------------
    def guardar(self) -> None:
        state = {
            "version": VERSION_ESTADO,
            "seed": self.seed,
            "memoria": self.memoria.estado(),
            "router": self.router.estado(),
            "expedientes": self.expedientes[-50:],
        }
        ruta = self.state_dir / "kernel_state.json"
        tmp = ruta.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
        os.replace(tmp, ruta)
        self.memoria.guardar(self.state_dir / "memoria.json")

    def _cargar_router(self) -> None:
        ruta = self.state_dir / "kernel_state.json"
        if not ruta.exists():
            return
        with open(ruta, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("version") == VERSION_ESTADO:
            self.router = Router(state.get("router") or {})

    @staticmethod
    def _hash_exp(objetivo: str) -> str:
        return hashlib.sha1((objetivo.strip().lower()).encode("utf-8")).hexdigest()[:10]
