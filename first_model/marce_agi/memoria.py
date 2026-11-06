"""MemoryStore — memoria persistente multi-tipo con evidencia citable.

Tipos: semantica (hechos), procedural (reglas si/entonces), episodica
(experiencias) y evidencia (anclas citables). Determinista, hash-addressed
y persistente en JSON: la experiencia se indexa, no se gradúa.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path

TIPOS_VALIDOS = ("semantica", "procedural", "episodica", "evidencia")


def tokenizar(texto: str) -> list[str]:
    return [t for t in re.findall(r"[a-záéíóúüñ0-9]+", (texto or "").lower()) if len(t) > 2]


def _identificador(conenido: str, tipo: str, extra: str = "") -> str:
    base = f"{tipo}|{extra}|{conenido}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    def agregar(self, tipo: str, contenido: str, tags: list[str] | None = None,
                evidencia_ids: list[str] | None = None, datos: dict | None = None,
                confianza: float = 0.6) -> str:
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(f"tipo inexistente: {tipo}")
        mid = _identificador(contenido, tipo, json.dumps(datos or {}, sort_keys=True))
        if mid in self._items:
            return mid
        self._items[mid] = {
            "id": mid,
            "tipo": tipo,
            "contenido": contenido,
            "tags": sorted(set(tags or []) | set(tokenizar(contenido))),
            "evidencia_ids": sorted(set(evidencia_ids or [])),
            "datos": datos or {},
            "confianza": round(float(confianza), 4),
            "creado": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        return mid

    def agregar_evidencia(self, fuente: str, nota: str) -> str:
        return self.agregar("evidencia", nota, tags=[], datos={"fuente": fuente}, confianza=1.0)

    def ver(self, mid: str) -> dict | None:
        return self._items.get(mid)

    def consulta(self, texto: str | None = None, tags: list[str] | None = None,
                 tipo: str | None = None, top: int = 8) -> list[dict]:
        universo = [i for i in self._items.values() if tipo is None or i["tipo"] == tipo]
        hechos_buscados = set(tokenizar(texto or "")) | set(tags or [])
        if not hechos_buscados:
            universo = sorted(universo, key=lambda i: i["id"])
            return universo[:top]
        puntuados = []
        for i in universo:
            etiquetas = set(i["tags"])
            if i["tipo"] == "evidencia":
                etiquetas |= set(tokenizar(i["datos"].get("fuente", "")))
            solap = hechos_buscados & etiquetas
            if not solap:
                continue
            puntuados.append((len(solap), i["id"], i))
        puntuados.sort(key=lambda t: (-t[0], t[1]))
        return [i for _, _, i in puntuados[:top]]

    def conteo_por_tipo(self) -> dict[str, int]:
        c = {t: 0 for t in TIPOS_VALIDOS}
        for i in self._items.values():
            c[i["tipo"]] += 1
        return c

    def estado(self) -> dict:
        return {"items": dict(self._items)}

    def restablecer(self, estado: dict) -> None:
        self._items = {k: v for k, v in (estado.get("items") or {}).items()}

    def guardar(self, ruta: Path) -> None:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        base = ruta.with_name(ruta.name)
        tmp = ruta.with_suffix(ruta.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.estado(), f, ensure_ascii=False, indent=1)
        os.replace(tmp, ruta)

    def cargar(self, ruta: Path) -> None:
        ruta = Path(ruta)
        if not ruta.exists():
            return
        with open(ruta, "r", encoding="utf-8") as f:
            self.restablecer(json.load(f))
