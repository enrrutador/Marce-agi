# Entrenamiento de Marce-AGI en Kaggle

> 2026-11-05. Estado: plan + implementación base (el kernel aún no existe; esto es la infraestructura de entrenamiento para cuando la fase 0 dé la primera base entrenable).
> Convención del repo: todo lo que hagamos se documenta al instante y se commitea a GitHub en el mismo momento.

## 1. Objetivo

Cuando el primer modelo tenga una base (fase 0–1 funcional), entrenarlo y evolucionarlo usando hardware gratuito de Kaggle, con un workflow que **sobreviva a las sesiones de 12h**: estado versionado en Kaggle Datasets, checkpointing determinista y reanudación exacta.

## 2. Qué se "entrena" en Marce-AGI

No hay gradientes ni pesos gigantes (principio 3 del README: la experiencia se indexa, no se gradúa). Entrenar aquí significa construir y calibrar el **estado del kernel**:

| Componente | Qué se ajusta | Hardware |
|---|---|---|
| Memoria persistente (semántica, procedural, episódica, evidencia) | Índices, referencias, grados de confianza tipo PLN | CPU es suficiente |
| Router (bandit → AB-MCTS) | Estadísticas de Thompson por razonador (Datalog / CAS / A*): victorias y ensayos | CPU |
| Episodios ARC-like | Ejecuciones del bucle planificar → ejecutar → evaluar; trazas guardadas como evidencia | CPU (GPU opcional en fases tardías) |
| Aprendizaje one-shot HDC | Codificación hiperdimensional de nuevas reglas | CPU (GPU para acelerar en fase 2+) |
| Futuro: destilación de trazas / modelos latentes | Sólo si la fase 2+ lo justifica | GPU/TPU |

**Regla operativa**: sesiones CPU por defecto; encender GPU sólo cuando haya código que la aproveche (cuota semanal separada y limitada).

## 3. Límites vigentes de Kaggle (verificados en doc oficial; leído 2026-11)

| Recurso | Límite |
|---|---|
| Sesión max | 12 h (CPU y GPU), 9 h (TPU) |
| CPU | 4 núcleos, ~30 GB RAM |
| GPU | 1× P100 o 2× T4 (4 núcleos, 29 GB RAM) — en cola en horas pico |
| TPU | TPU v3-8: 96 núcleos, 330 GB RAM |
| Cuota semanal GPU | ~30 h compartidas (a veces más según demanda; el dato exacto en Settings → Quota). TPU ~20 h según usuarios |
| Disco guardado `/kaggle/working` | 20 GB (lo demás es scratch y se pierde al cerrar la sesión) |
| Idle timeout interactiva | 20 min sin ejecución → corta la sesión |
| Datasets | 200 GB máximo por dataset y por total privado (sin límite práctico de versiones) |
| Internet | Activable (nuevos notebooks: on por defecto); exigible de apagar en algunas competencias |
| Requisito | Verificación de teléfono para GPU/internet |
| Bonus opcional | Colab Pro linkado suma 15 h GPU/semana (Pro), 30 h (Pro+) — promoción temporal |
| Salida reproducible | "Save & Run All" ejecuta el notebook completo de arriba a abajo en sesión limpia (hasta 12 h) |
| API | Kaggle API + MCP server de Kaggle pueden empujar versiones de notebooks sin abrir el editor |

Fuentes: kaggle.com/docs/notebooks, kaggle.com/docs/efficient-gpu-usage, kaggle.com/docs/datasets (fecha de lectura: 2026-11-05). Re-verificar antes de operar si pasa mucho tiempo.

## 4. Estrategia: sesiones chunked con estado versionado

Cada sesión de Kaggle es **un slice de entrenamiento** de ≤12 h. El estado vive en un dataset privado versionado, no en la sesión:

```
sesión n (≤ 12 h en Kaggle)
  1. attach del dataset de estado: <usuario>/marce-agi-state (versión v_n)
  2. git clone https://github.com/enrrutador/Marce-agi        <- código siempre fresco
  3. python3 training/train_state.py --resume /kaggle/input/marce-agi-state/checkpoint.json
  4. parada segura ~ a las 11 h (SAFE_STOP)
  5. resultado: /kaggle/working/state/ con checkpoint.json + metrics.jsonl
  6. kaggle datasets version -p /kaggle/working/state -m "slice n: <resumen>"
-> el push crea la versión v_(n+1) -> repetir en la sesión siguiente
```

Configuración del notebook/sesión:
- Código: no está en Kaggle cuando empieza la sesión — clonar `enrrutador/Marce-agi` al inicio de cada sesión (es chico) para ejecutar siempre lo último que está en el repo.
- Dataset de estado: attach `marce-agi-state` (monta en `/kaggle/input/marce-agi-state/...`).
- Output: `/kaggle/working/state/` con checkpoint y métricas.

## 5. Implementación

```
training/
├── README.md              # este documento
├── train_state.py         # CLI de entrenamiento/estado del kernel (determinista, resume/checkpoint, métricas JSONL, parada segura)
└── kaggle_push_state.sh   # push del estado hacia (o creación de) el dataset de estado vía Kaggle API
```

### 5.1 `train_state.py`

Bucle determinista (seed fija) que:
- emite episodios ARC-like sintéticos (seedeados) o acepta un archivo propio de episodios JSONL,
- rota razonadores con Thompson sampling (Beta win/tries) — ya es esqueleto del AB-MCTS de fase 1,
- registra métricas por episodio en `metrics.jsonl` (paso, razonador, éxito, tiempo),
- mantiene parada segura: `--safe-stop-seconds` (por defecto 39_600 s = 11 h) antes de que Kaggle mate la sesión, para que el checkpoint sea íntegro,
- escribe `state/checkpoint.json` (con `commit_ref` de git embebido para trazabilidad cruzada repo↔entrenamiento) y `state/metrics.jsonl`.

```bash
# en la sesión de Kaggle (o en una VM cualquiera):
git config --global user.name enrrutador && git config --global user.email <correo>
git clone https://github.com/enrrutador/Marce-agi /kaggle/working/marce-agi
cp -r /kaggle/input/marce-agi-state/* /kaggle/working/state    # estado de la sesión anterior
python3 /kaggle/working/marce-agi/training/train_state.py \
    --resume /kaggle/working/state/checkpoint.json \
    --epochs 8
```

### 5.2 `kaggle_push_state.sh`

```bash
# Primera vez: crear el dataset de estado
cd /kaggle/working/state && kaggle datasets init -p .
# editar dataset-metadata.json → {"title": "marce-agi-state", "id": "<usuario>/marce-agi-state", "licenses":[{"name":"CC0-1.0"}]}
kaggle datasets create -p .

# Cada cierre de slice (al final de cada sesión de Kaggle):
bash marce-agi/training/kaggle_push_state.sh "slice 1: router calibrado con 500 episodios"
```

Credenciales: `~/.kaggle/kaggle.json` (portal Kaggle → Settings → API → Create New Token). En la sesión de Kaggle ya viene preconfigurado; en una VM/notebook propia, copiarlo con `chmod 600`.

## 6. Trazabilidad y reproducibilidad

- **Seed fija** en checkpoint; reejecución con la misma seed produce el mismo resultado esperado (rutas hash-based, sin muestreo estocástico).
- **`commit_ref`** del repo dentro de cada checkpoint: cualquier inteligencia generada es rastreable al código exacto que la produjo (principio 2 de trazabilidad, ahora a nivel de infraestructura).
- **metrics.jsonl** por episodio → input del análisis de calibración del router y de la futura fase 4 (autoevaluación inmutable).
- Los cambios de código durante un entrenamiento NO se meten a la mitad del slice si violan trazabilidad: primero commit, después se corre en Kaggle con el commit exacto.

## 7. Calendario por fase

| Fase | Qué se entrena en Kaggle | Notas |
|---|---|---|
| 0 (kernel estático) | nada aún / pruebas del script | validación del pipeline chunked |
| 1 (razonadores portados) | calibración del router: episodios sintéticos → progresivamente reales | CPU; el AB-MCTS aparece primero como estadísticas de bandit |
| 2 (aprendizaje continuo) | HDC one-shot sobre episodios reales; índices de memoria crecientes | CPU con bursts GPU opcionales |
| 3 (bucle autónomo) | corridas largas de exploración en ARC-like; modelo mínimo de mundo | candidata plataforma principal |
| 4 (autoevaluación/automejora) | sandbox de autoevaluación con métricas inmutables (anti-gaming, según análisis internacional) | slice diario + reporte de métricas al repo |

## 8. Checklist por sesión de entrenamiento

1. [ ] Sesión nueva attach dataset `marce-agi-state` (última versión)
2. [ ] `git clone` del repo fresco
3. [ ] `train_state.py --resume …` y dejarlo correr
4. [ ] ~11 h: parada segura automática → checkpoint íntegro en `/kaggle/working/state`
5. [ ] `kaggle_push_state.sh "slice N: <resumen>"` (quedan en versiones del dataset)
6. [ ] Commit + push al repo (código cambiado, notas del slice en `training/log_slices.md`)
7. [ ] Verificar en GitHub + Kaggle que AMBAS fuentes quedaron actualizadas (código + estado)
