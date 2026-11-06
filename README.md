# Marce-AGI

Travesía hacia una **AGI**: el primer modelo en desarrollo de una arquitectura cognitiva general.

## Qué es

No un LLM. Una arquitectura cognitiva que razona de forma determinista, aprende
de la experiencia y guarda memoria persistente trazable. La inteligencia no vive
en pesos gigantes: vive en la **arquitectura** — razonamiento simbólico exacto,
aprendizaje continuo y memoria creciente.

## Base

- **ARCA-llm** (enrrutador/ARCA-llm): memoria persistente (semántica, procedural,
  episódica, evidencia), composición trazable con A*, degradación elegante.
- **ARCA-LLM2**: razonadores simbólicos deterministas (Datalog, CAS, planificación
  A*), aprendizaje one-shot vía HDC, bandit router, paging < 800 MB RAM.

## Entrenamiento

El modelo se entrenará en **Kaggle** en sesiones chunked de 12 h con estado
versionado en Kaggle Datasets (resume exacto, trazabilidad por commit de git).
Ver [`training/README.md`](training/README.md).

## Roadmap del primer modelo

| Fase | Meta | Estado |
|---|---|---|
| 0 | Esqueleto del kernel cognitivo (memoria + router + trazas) | ✔ base (9 tests; razonadores stub; port real = fase 1) |
| 1 | Port de razonadores simbólicos desde ARCA-LLM2 | pendiente |
| 2 | Aprendizaje continuo (HDC one-shot + Memoria semántica) | pendiente |
| 3 | Bucle autónomo: planificar → ejecutar → evaluar → aprender | pendiente |
| 4 | Autoevaluación y automejora medible | pendiente |

> Fase 0 emite **`cerebro.jsonl`** (stream de eventos por ciclo cognitivo): es el
> contrato para el futuro frontend observador del cerebro.

## Estructura

```
first_model/   # el primer modelo, en desarrollo
research/      # notas e ideas de base (repos ARCA + análisis internacional AGI/ASI 2026)
training/      # plan y implementación del entrenamiento en Kaggle
```

## Principios

1. **Determinista donde importa**: matemática y lógica nunca alucinan.
2. **Trazable**: cada respuesta expone su razonamiento.
3. **Aprende sin reentrenar**: la experiencia se indexa, no se gradúa.
4. **Recursos mínimos**: corre en hardware modesto.

## Licencia

MIT.

---

*Proyecto de Marce. Travesía empezada: 2026-11-05.*
