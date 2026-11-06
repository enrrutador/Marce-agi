#!/usr/bin/env python3
"""CLI de entrenamiento/estado del kernel Marce-AGI para sesiones Kaggle chunked.

Diseñado para las sesiones de Kaggle (12 h máx, GPU con cuota semanal):
bucle determinista que calibra un router de razonadores con Thompson
sampling (esqueleto del AB-MCTS de fase 1), emite episodios ARC-like
sintéticos o lee episodios reales de un archivo JSONL, registra métricas
por episodio en metrics.jsonl, guarda checkpoint.json una vez por epoch o al
cortar por presupuesto, y detiene el slice de forma segura ~1 h antes del
límite de sesión. El detalle del workflow está en training/README.md.
"""

import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

REASONERS = {
    "datalog": {"base": 0.62, "aplica": "reglas y lógica"},
    "cas": {"base": 0.55, "aplica": "matemática simbólica"},
    "planificador_astar": {"base": 0.70, "aplica": "planeación y decisiones"},
}

CHECKPOINT_VERSION = 1


def sha_int(key, mod):
    return int(hashlib.sha256(key.encode()).hexdigest()[:16], 16) % mod


def episodios_sinteticos(seed, por_epoch, epochs):
    out = []
    for epoch in range(1, epochs + 1):
        for n in range(1, por_epoch + 1):
            out.append({
                "id": f"synthetic-{epoch}-{n}",
                "epoch": epoch,
                "dificultad": 1 + sha_int(f"{seed}:{epoch}:{n}", 9),
            })
    return out


def episodios_de_archivo(path):
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            out.append({
                "id": str(e.get("id", f"real-{i}")),
                "epoch": int(e.get("epoch", 1)),
                "dificultad": int(e.get("dificultad", 5)),
            })
    return out


def elegir_razonador(estado, seed, step):
    jugadas = {}
    for nombre in REASONERS:
        st = estado["razonadores"][nombre]
        rng = random.Random(f"{seed}:{step}:{nombre}")
        jugadas[nombre] = rng.betavariate(st["wins"] + 1, st["tries"] - st["wins"] + 1)
    return max(jugadas, key=jugadas.get)


def evaluar_episodio(seed, razonador, episodio):
    base = REASONERS[razonador]["base"]
    penal = 0.02 * max(0, episodio["dificultad"] - 3)
    propio = sha_int(f"{seed}:{razonador}:{episodio['id']}", 100)
    return propio < int(100 * (base - penal))


def git_commit_ref():
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()[:40]
    except Exception:
        pass
    return "sin-git"


def nuevo_estado(seed, commit_ref):
    return {
        "version": CHECKPOINT_VERSION,
        "seed": seed,
        "step": 0,
        "epochs_done": 0,
        "razonadores": {n: {"wins": 0, "tries": 0} for n in REASONERS},
        "memoria": {"hechos": 0, "reglas": 0, "episodios": 0},
        "checkpoints_escritos": 0,
        "commit_ref": commit_ref,
        "creado": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def guardar_checkpoint(estado, state_dir, nota):
    p = Path(state_dir)
    p.mkdir(parents=True, exist_ok=True)
    estado["checkpoints_escritos"] += 1
    estado["guardado"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    tmp = p / "checkpoint.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p / "checkpoint.json")
    with open(p / "checkpoint_meta.txt", "a", encoding="utf-8") as f:
        f.write(f'{estado["guardado"]} ckpt#{estado["checkpoints_escritos"]} step={estado["step"]} {nota}\n')


def registrar_metrica(estado, state_dir, fila):
    p = Path(state_dir)
    p.mkdir(parents=True, exist_ok=True)
    fila["commit_ref"] = estado["commit_ref"]
    with open(p / "metrics.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def cargar_estado(args):
    if not args.resume:
        return nuevo_estado(args.seed, git_commit_ref()), "nuevo"
    with open(args.resume, "r", encoding="utf-8") as f:
        st = json.load(f)
    if st.get("version") != CHECKPOINT_VERSION:
        raise SystemExit(f"checkpoint v{st.get('version')} incompatible (esperado v{CHECKPOINT_VERSION})")
    if args.seed and args.seed != st.get("seed"):
        raise SystemExit(f"seed {args.seed} != seed del checkpoint {st.get('seed')}")
    st["commit_ref"] = git_commit_ref()
    return st, f"resume step={st['step']} ckpts={st['checkpoints_escritos']}"


def entrenar(estado, episodios, state_dir, safe_stop_seconds):
    inicio = time.time()
    restantes = []
    visto = {e["id"] for e in episodios[:0]}
    step_inicial = estado["step"]
    total = len(episodios)
    n = 0
    for e in episodios:
        n += 1
        if estado["step"] >= step_inicial + total:
            break
        if time.time() - inicio > safe_stop_seconds:
            return estado, f"safe-stop en episodio {n}/{total} (presupuesto {safe_stop_seconds}s)"
        step = estado["step"] + 1
        razonador = elegir_razonador(estado, estado["seed"], step)
        ok = evaluar_episodio(estado["seed"], razonador, e)
        st = estado["razonadores"][razonador]
        st["tries"] += 1
        if ok:
            st["wins"] += 1
            estado["memoria"]["hechos"] += e["dificultad"]
            estado["memoria"]["reglas"] += 1 if e["dificultad"] > 6 else 0
        estado["memoria"]["episodios"] += 1
        estado["step"] = step
        registrar_metrica(estado, state_dir, {
            "paso": step,
            "episodio": e["id"],
            "epoch": e["epoch"],
            "dificultad": e["dificultad"],
            "razonador": razonador,
            "exito": bool(ok),
            "t": round(time.time() - inicio, 2),
        })
        restantes.append(razonador)
    return estado, "slice completo"


def main():
    ap = argparse.ArgumentParser(description="Entrenamiento/estado del kernel Marce-AGI (sesiones Kaggle chunked)")
    ap.add_argument("--state-dir", default=os.environ.get("MA_STATE_DIR", "/kaggle/working/state"))
    ap.add_argument("--resume", default="", help="ruta a checkpoint.json de la sesión anterior")
    ap.add_argument("--episodes", default="", help="JSONL propio de episodios (id, epoch, dificultad)")
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--episodes-per-epoch", type=int, default=250)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--safe-stop-seconds", type=int, default=39600, help="parada segura (default 39600 s = 11 h)")
    args = ap.parse_args()

    if args.episodes:
        episodios = episodios_de_archivo(args.episodes)
    else:
        episodios = episodios_sinteticos(args.seed, args.episodes_per_epoch, args.epochs)

    estado, modo = cargar_estado(args)
    print(f"[marce-agi] modo={modo} commit={estado['commit_ref']} state-dir={args.state_dir}")

    cp_cada = max(1, len(episodios) // 4)
    inicio = time.time()
    salida = ""
    for i, e in enumerate(episodios, 1):
        if time.time() - inicio > args.safe_stop_seconds:
            salida = f"safe-stop en episodio {i}/{len(episodios)} (presupuesto {args.safe_stop_seconds}s)"
            break
        step = estado["step"] + 1
        razonador = elegir_razonador(estado, estado["seed"], step)
        ok = evaluar_episodio(estado["seed"], razonador, e)
        st = estado["razonadores"][razonador]
        st["tries"] += 1
        if ok:
            st["wins"] += 1
            estado["memoria"]["hechos"] += e["dificultad"]
            estado["memoria"]["reglas"] += 1 if e["dificultad"] > 6 else 0
        estado["memoria"]["episodios"] += 1
        estado["step"] = step
        registrar_metrica(estado, args.state_dir, {
            "paso": step,
            "episodio": e["id"],
            "epoch": e.get("epoch", 0),
            "dificultad": e["dificultad"],
            "razonador": razonador,
            "exito": bool(ok),
            "t": round(time.time() - inicio, 2),
        })
        if i % cp_cada == 0:
            guardar_checkpoint(estado, args.state_dir, f"estado medio episodio {i}/{len(episodios)}")
    else:
        salida = "slice completo"

    guardar_checkpoint(estado, args.state_dir, salida)
    stats = {n: s["wins"] for n, s in estado["razonadores"].items()}
    print(f"[marce-agi] {salida}: step={estado['step']} memoria={estado['memoria']} razonadores={stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
