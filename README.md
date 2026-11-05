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

## Roadmap del primer modelo

| Fase | Meta | Estado |
|---|---|---|
| 0 | Esqueleto del kernel cognitivo (memoria + router + trazas) | en desarrollo |
| 1 | Port de razonadores simbólicos desde ARCA-LLM2 | pendiente |
| 2 | Aprendizaje continuo (HDC one-shot + Memoria semantic) | pendiente |
| 3 | Bucle autónomo: planificar → ejecutar → evaluar → aprender | pendiente |
| 4 | Autoevaluación y automejora medible | pendiente |

## Estructura

```
first_model/   # el primer modelo, en desarrollo
research/      # notas e ideas de base (desde los repos ARCA)
```

## Principios

1. **Determinista donde importa**: mátemática y lógica nunca alucinan.
2. **Trazable**: cada respuesta expone su razonamiento.
3. **Aprende sin reentrenar**: la experiencia se indexa, no se gradúa.
4. **Recursos mínimos**: corre en hardware modesto.

## Licencia

MIT.

---

*Proyecto de Marce. Travesía empezada: 2026-11-05.*
