"""CLI del kernel Marce-AGI (fase 0).

Uso:
    python -m marce_agi.cli --state state "¿cuánto es 2+2*3?"
    python -m marce_agi.cli --state state --reiniciar

Cada pregunta corre un ciclo cognitivo completo y muestra el stream
de eventos del cerebro (los mismos que escuchará el frontend observador).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .kernel import CognitiveKernel
from .eventos import leer_stream


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="marce-agi")
    ap.add_argument("objetivo", nargs="*", help="objetivo a procesar (cada arg = un ciclo)")
    ap.add_argument("--state", default="first_model/state", help="directorio de estado")
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--razonador", choices=["datalog", "cas", "planificador_astar"], default=None)
    ap.add_argument("--reiniciar", action="store_true", help="borra el estado del kernel")
    ap.add_argument("--stream", action="store_true", help="solo imprime ciclos previos del cerebro.jsonl")
    args = ap.parse_args(argv)

    state = Path(args.state)
    if args.reiniciar and state.exists():
        shutil.rmtree(state)
        print(f"[marce-agi] estado reiniciado: {state}")

    if args.stream:
        for e in leer_stream(state / "cerebro.jsonl"):
            _imprimir_evento(e)
        return 0

    kernel = CognitiveKernel(state_dir=state, seed=args.seed)
    objetivos = args.objetivo or sys.stdin.read().splitlines()
    for objetivo in [o.strip() for o in objetivos if o.strip()]:
        ciclo = kernel.pensar(objetivo, razonador=args.razonador)
        print(f"\n== objetivo: {objetivo}")
        for paso in ciclo["pasos"]:
            print(f"  {paso['tipo']:<14} {paso['contenido']}")
        if ciclo["evidencia_ids"]:
            print(f"  {'evidencia':<14} {ciclo['evidencia_ids']}")
        print(f"\n[marce-agi] razonador={ciclo['razonador']} éxito={ciclo['exito']}")
        print(f"[marce-agi] {ciclo['respuesta']}")
    return 0


def _imprimir_evento(e: dict) -> None:
    payload = json.dumps(e["payload"], ensure_ascii=False)
    print(f"{e['seq']:>5} {e['tipo']:<26} {e['origen']:<16} {payload[:120]}")


if __name__ == "__main__":
    sys.exit(main())
