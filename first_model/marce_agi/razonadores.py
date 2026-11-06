"""Razonadores de fase 0 — stubs deterministas que demuestran el mecanismo.

Cada razonador resuelve desde memoria con pasos trazados y evidencia. En
fase 1 estos se reemplazan por los motores reales portados desde ARCA-LLM2
(Datalog, CAS exacto, planificación A*) sin cambiar la interfaz.
"""

from __future__ import annotations

import ast
import operator
import re

from .memoria import MemoryStore, tokenizar


class ResultadoRazonamiento:
    def __init__(self, exito: bool, respuesta: str, pasos: list[dict],
                 evidencia_ids: list[str], confianza: float) -> None:
        self.exito = exito
        self.respuesta = respuesta
        self.pasos = pasos
        self.evidencia_ids = evidencia_ids
        self.confianza = confianza

    def dict(self) -> dict:
        return {
            "exito": self.exito,
            "respuesta": self.respuesta,
            "pasos": self.pasos,
            "evidencia_ids": self.evidencia_ids,
            "confianza": round(self.confianza, 4),
        }


class _PorPaso:
    def _paso(self, tipo: str, contenido: str, datos: dict | None = None) -> dict:
        p = {"tipo": tipo, "contenido": contenido}
        if datos:
            p["datos"] = datos
        return p


# operadores seguros para el CAS (sin eval arbitraria)
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}


class CasStub:
    """Matemática simbólica exacta sobre aritmética entera racional."""

    nombre = "cas"

    def resolver(self, objetivo: str, memoria: MemoryStore) -> ResultadoRazonamiento:
        pasos = []
        m = re.search(r"cu[aá]nto\s+es\s+([-+*/(). ()0-9]+)\s*\?$", objetivo.lower()) or \
            re.search(r"^([-+*/(). ()0-9]+)\s*\?$", objetivo.strip())
        if not m:
            return ResultadoRazonamiento(False, "no encontré expresión aritmética",
                                         [_paso_b("cas.probe", "sin expresión matemática en el objetivo")],
                                         [], 0.0)
        expresion = m.group(1)
        pasos.append(_paso_b("cas.parse", f"expresión aislada: {expresion}"))
        valor = self._evaluar(expresion)
        pasos.append(_paso_b("cas.eval", f"evaluación exacta = {valor}", {"expresion": expresion, "valor": str(valor)}))
        eid = memoria.agregar_evidencia(f"cas|{self.nombre}", f"expresión {expresion} = {valor} (rango racional exacto)")
        memoria.agregar("semantica", f"la expresión {expresion} vale {valor}",
                        tags=tokenizar(expresion) + tokenizar(target_extract(objetivo)),
                        evidencia_ids=[eid], confianza=1.0)
        return ResultadoRazonamiento(True, f"{valor} (verificado por CAS determinista)", pasos, [eid], 1.0)

    @staticmethod
    def _evaluar(expresion: str):
        arbol = ast.parse(expresion, mode="eval")
        return _paseo(arbol.body)


def _paso_b(tipo: str, contenido: str, datos: dict | None = None):
    p = {"tipo": tipo, "contenido": contenido}
    if datos:
        p["datos"] = datos
    return p


def target_extract(objetivo: str) -> str:
    return re.sub(r"cu[aá]nto\s+es", "", objetivo, flags=re.I)


def _paseo(nodo):
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)):
        return nodo.value
    if isinstance(nodo, ast.BinOp) and type(nodo.op) in _OPS:
        return _OPS[type(nodo.op)](_paseo(nodo.left), _paseo(nodo.right))
    if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.UAdd, ast.USub)):
        val = _paseo(nodo.operand)
        return val if isinstance(nodo.op, ast.UAdd) else -val
    raise ValueError(f"nodo no permitido en CAS: {ast.dump(nodo)}")


PALABRAS_PLAN = {"plan", "pasos", "secuencia", "cómo", "como", "etapas"}


class DatalogStub:
    """Encadena reglas procedurales (si/entonces) sobre hechos semánticos."""

    nombre = "datalog"

    def resolver(self, objetivo: str, memoria: MemoryStore) -> ResultadoRazonamiento:
        pasos = []
        tags = tokenizar(objetivo)
        hechos = memoria.consulta(texto=objetivo, tipo="semantica", top=8)
        pasos.append(_paso_b("datalog.carga", f"{len(hechos)} hechos consultados", {"tags": tags}))
        decisiones = []
        usados = [h["id"] for h in hechos]
        reglas = memoria.consulta(texto=objetivo, tipo="procedural", top=8)
        for regla in reglas:
            si_tokens = set(regla["datos"].get("si_tokens") or regla["tags"])
            solapamiento = si_tokens & set(tags)
            if len(solapamiento) >= 2:
                decisiones.append((regla, solapamiento))
        if not decisiones:
            return ResultadoRazonamiento(False, "sin regla aplicable sobre hechos conocidos",
                                         pasos, usados, 0.35)
        pasos_txt = []
        for regla, solapamiento in decisiones:
            pasos_txt.append(f"{sorted(solapamiento)} -> {regla['contenido']}")
        pasos.append(_paso_b("datalog.chain", "reglas satisfechas", {"reglas": pasos_txt}))
        respuesta = "por reglas encadenadas: " + "; ".join(pasos_txt)
        return ResultadoRazonamiento(True, respuesta, pasos, usados + [r["id"] for r, _ in decisiones], 0.8)


class PlanificadorStub:
    """Construye planes por búsqueda de hechos: la semilla del A* de fase 1."""

    nombre = "planificador_astar"

    def resolver(self, objetivo: str, memoria: MemoryStore) -> ResultadoRazonamiento:
        pasos = []
        tags = set(tokenizar(objetivo))
        pasos.append(_paso_b("planprobe", "objetivo en dominio de planeación?", {"tags": sorted(tags)}))
        if not (tags & PALABRAS_PLAN):
            return ResultadoRazonamiento(False, "ningún requerimiento de plan detectado",
                                         pasos, [], 0.0)
        hechos = memoria.consulta(texto=objetivo, tipo="semantica", top=6)
        plan = [h["contenido"] for h in hechos]
        pasos.append(_paso_b("planprobe.steps", f"plan de {len(plan)} etapas deducidas de memoria",
                             {"etapas": plan}))
        if not plan:
            return ResultadoRazonamiento(False, "sin etapas deducibles (memoria sin hechos)",
                                         pasos, [], 0.2)
        return ResultadoRazonamiento(True, "plan: " + " | ".join(plan), pasos,
                                     [h["id"] for h in hechos], 0.85)


def razonadores_disponibles() -> dict[str, object]:
    return {r.nombre: r for r in (DatalogStub(), CasStub(), PlanificadorStub())}
