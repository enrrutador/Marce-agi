# Log de slices de entrenamiento (Kaggle)

Una entrada por slice ejecutado. Formato:

```
## YYYY-MM-DD | <nombre dataset versión> | kernel <commit_ref> | seed <seed>
- origen: [kaggle notebook] / [local] / [VM]
- qué se corrió: train_state.py --resume ... --epochs ...
- resultado: episodios, victorias por rasonador, hallazgos
- estado push: [link a versión del dataset]
- notas: problemas, decisiones
```

## Convenciones

- Resumen del mensaje de push = corto (<= 72 chars), incluye número slice.
- Cualquier desvío vs training/README.md se documenta en "notas" en el mismo momento.
- Nunca push de estado sin checkpoint íntegro (parada segura < 11 h).
