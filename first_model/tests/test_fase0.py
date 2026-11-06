"""Tests fase 0: memoria, router, trazabilidad y determinismo del kernel."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from marce_agi.eventos import leer_stream
from marce_agi.kernel import CognitiveKernel
from marce_agi.memoria import MemoryStore
from marce_agi.router import Router


@pytest.fixture
def state(tmp_path) -> Path:
    return tmp_path / "state"


def test_memoria_persiste(state):
    k1 = CognitiveKernel(state_dir=state)
    k1.memoria.agregar("semantica", "el agua es H2O")
    k1.guardar()
    k2 = CognitiveKernel(state_dir=state)
    assert k2.memoria.consulta(texto="agua", tipo="semantica")


def test_cas_exacto_y_no_alucina(state):
    k = CognitiveKernel(state_dir=state)
    ciclo = k.pensar("¿cuánto es 2+2*3?", razonador="cas")
    assert ciclo["exito"] is True
    assert "8" in ciclo["respuesta"]
    assert ciclo["confianza"] == 1.0
    assert ciclo["evidencia_ids"]


def test_datalog_encadena_regla(state):
    k = CognitiveKernel(state_dir=state)
    k.memoria.agregar("procedural", "si tiene pico del ave entonces es ave voladora",
                      tags=["pico", "ave"], datos={"si_tokens": ["pico", "ave", "vuela"]})
    k.memoria.agregar("semantica", "el sparow tiene pico de ave y vuela", tags=["pico", "ave"])
    ciclo = k.pensar("el ave con pico que vuela", razonador="datalog")
    assert ciclo["exito"] is True
    assert "reglas encadenadas" in ciclo["respuesta"]


def test_router_brazo_ganador(state):
    r = Router({"cas": {"wins": 500, "tries": 500}})
    elegido, _ = r.decidir("semilla-fija")
    assert elegido == "cas"


def test_stream_de_cerebro_completo(state):
    k = CognitiveKernel(state_dir=state, seed=7)
    k.pensar("¿cuánto es 3*4?", razonador="cas")
    eventos = leer_stream(state / "cerebro.jsonl")
    tipos = {e["tipo"] for e in eventos}
    for esperado in ("ciclo.inicio", "ciclo.memoria_consulta", "ciclo.router_decision",
                     "ciclo.razonador_inicio", "ciclo.razonador_resultado",
                     "ciclo.aprendizaje", "ciclo.fin"):
        assert esperado in tipos, f"falta evento {esperado}"
    seqs = [e["seq"] for e in eventos]
    assert seqs == sorted(seqs)


def test_determinismo_same_seed(state):
    razonadores = []
    for i in (1, 2):
        d = state.parent / f"state{i}"
        k = CognitiveKernel(state_dir=d, seed=42)
        ciclo = k.pensar("¿cuánto es 7+1?", razonador="cas")
        razonadores.append((ciclo["razonador"], ciclo["exito"], ciclo["respuesta"]))
    assert razonadores[0] == razonadores[1]


def test_kernel_guarda_router_stats_compatible_entrenamiento(state):
    k = CognitiveKernel(state_dir=state)
    k.pensar("hola planeta", razonador="cas")
    stats = json.load(open(state / "kernel_state.json"))["router"]
    assert set(stats) == {"datalog", "cas", "planificador_astar"}
    assert stats["cas"]["tries"] == 1


def test_persistencia_ciclo_completo(state):
    k1 = CognitiveKernel(state_dir=state, seed=9)
    k1.pensar("¿cuánto es 10/4?", razonador="cas")
    k2 = CognitiveKernel(state_dir=state, seed=9)
    ciclo = k2.pensar("¿cuánto es 6+6?", razonador="cas")
    assert ciclo["exito"]
    assert (state / "cerebro.jsonl").exists()
    hits = k2.memoria.consulta(texto="10/4", tipo="semantica")
    assert hits


def test_memoria_sin_coincidencia_da_vacio_y_consulta_por_tipo(state):
    m = MemoryStore()
    m.agregar("semantica", "madrid capital de españa")
    assert m.consulta(texto="bananas y coconuts mundo libre", tipo="semantica") == []
