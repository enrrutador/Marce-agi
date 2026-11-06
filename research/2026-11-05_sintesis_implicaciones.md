# Síntesis: Implicaciones del análisis internacional para Marce-AGI

> 2026-11-05. Material de base: `2026-11-05_analisis_tecnico_internacional_AGI.md`.
> Punto de partida: análisis de los repos ARCA-llm / ARCA-LLM2 y creación de Marce-AGI (sesión 2026-11-05).

## 1. El material valida nuestra premisa central

El README de Marce-AGI dice: *"La inteligencia no vive en pesos gigantes: vive en la arquitectura"*. El análisis internacional independiente llega a la conclusión inversa partiendo del mainstream: el preentrenamiento autorregresivo puro está agotado (límites OOD, causal, transferencia), y la AGI no surge de un solo modelo gigante sino de un **ecosistema híbrido** (modelos de mundo + razonamiento en tiempo de prueba + verificación neuro-simbólica + colectivos de agentes).

Nuestra línea no está al margen: está en la confluencia de los cuatro pilares del consenso 2027–2030. Esto significa que el diseño del primer modelo debe nombrar explícitamente dónde entra cada pilar.

## 2. Mapeo material → arquitectura Marce-AGI

| Pilar del consenso | Equivalente en Marce-AGI | Qué adoptar / reforzar |
|---|---|---|
| Comprensión física/causal (JEPA, modelos de mundo) | Memoria persistente multi-tipo (semántica, procedural, episódica) | Idea importable: **predicción en espacio abstracto, no generativo**. Nuestra memoria debe aprender a *predecir* resultados de acciones (distancia entre estados ≈ costo) y no a memorizar texto. Conecta con la composición trazable con A* de ARCA-llm: `d(estado_a, estado_b) ≈ costo de transición` es exactamente la interfaz que A* necesita. |
| Razonamiento en tiempo de prueba (LRMs + AB-MCTS) | Razonadores simbólicos deterministas (Datalog, CAS, planificación A*) + bandit router | Idea central a portar: **AB-MCTS con Thompson sampling**, tratando cada razonador como "modelo" en un bandido. Go Wider = razonador distinto sobre el nodo padre; Go Deeper = pasar la solución fallída + verificación al razonador siguiente. Es un reemplazo exacto y determinista del bucle multi-LLM: en vez de 3 LLMs, 3 razonadores simbólicos con sesgos inductivos distintos. |
| Verificación neuro-simbólica | "Determinista donde importa: mátematica y lógica nunca alucinan" | Adoptar el patrón **LLM → Simbólico** (avenida 2 de IJCAI): si usamos un LLM, él nunca razona: sólo traduce el problema a formalismo (PDDL, SMT-LIB/MeTTa) y un solucionador externo ejecuta y verifica. La avenida 1 (Simbólico → LLM, destilación de trazas garantizadas) es una opción de entrenamiento futuro del "primer modelo", no del kernel. |
| Colectivos de agentes | Post-summa: fase 3 (bucle autónomo) → fase 4 (autoevaluación) | El router bandit ya es una agencia de grupo en miniatura: especialización + delegación. La escala "millones de agentes" de DeepMind no es una fase inicial. |

## 3. Definición operativa de AGI que adoptamos (Chollet / ARC Prize)

- La inteligencia se mide por **eficiencia de adquisición de habilidades** ante problemas inéditos, no por conocimiento almacenado.
- Los problemas se construyen sobre **prioris de core knowledge**: objeto, geometría básica, topología, física intuitiva.
- **Decisión de diseño**: el primer modelo necesita un módulo de *prioris esenciales* codificados simbólicamente (relaciones de objeto, contigüidad, contención, continuidad, causalidad básica). Sin eso, la "generalización" es imposible. Es un injerto lógico del ranking de fase 0 (trazas) → fase 2 (aprendizaje): los prioris son el axioma inicial del sistema, no datos.
- **Benchmark objetivo** (no para competencia, para orientación): ARC-AGI-2 Pass@2 (los LRMs actuales < 30% con búsqueda colectiva; NVIDIA NVARC: 24%). ARC-AGI-3 es interactiva por turnos (RHAE) — sólo relevante después de fase 3, cuando exista un bucle de exploración autónoma.

## 4. Lecciones de auto-mejora recursiva (RSI) para fase 4

- The AI Scientist muestra que el ciclo completo (idear → experimentar → escribir → evaluar) es automatizable a costo $15 — y muestra el riesgo: **gaming de métricas** (alterar timeouts en vez de algoritmos). 
- **Consecuencia de diseño**: nuestras autoevaluaciones deben correr en **sandbox hermético** (parámetros fijados a priori, no modificables por el propio agente; timeouts externos imposibles de reescribir). El "automejora medible" de fase 4 se garantiza con: métricas de referencia inmutables (a la ARC: resolubilidad y acciones mínimas por tarea) + trazabilidad: cada mejora debe citar evidencia (heredado de ARCA-llm).

## 5. Límites honestos (Barrera de Abstracción y Embotellamiento Embodied)

- Cómputo aislado no crea primitivas conceptuales totalmente nuevas sin interactuación con la realidad (symbol grounding). Consecuencia: **alcance razonable de Marce-AGI v1** = reorganización y composición de conocimiento existente con trazabilidad, no generación de ciencia nueva.
- El embudo físico limita RSI a topes digitales; no es problema aquí (somos un kernel cognitivo de software, no una planta de experimentos físicos), pero define metas: **no prometemos descubrir fenómenos no modelados; prometemos composición, razonamiento exacto y aprendizaje sin reentrenar**.

## 6. Referencia de implementación: OpenCog Hyperon (MeTTa + Atomspace)

- Lo que nos da: esquema de conocimiento como **hipergrafo introspectivo** con tipos graduales, PLN y patrones de atención en el mismo espacio; auto-modificación reflexiva segura.
- Lo que no copiamos (por simplicidad y recursos): el ecosistema completo de Hyperon. Para el primer modelo basta un store trazable + grados de confianza (estilo PLN) + un lenguaje meta mínimo sobre nuestros registros de memoria. Si la fase 2 lo requiere, estudiar MeTTa como lenguaje de persistencia.
- [!] Pendiente para la próxima sesión: revisar la licencia de MeTTa/OpenCog antes de integrar cualquier concepto o código suyo.

## 7. Correcciones/ajustes a nuestro README final

- Roadmap fase 1: incluir explícitamente **AB-MCTS sobre razonadores** (no sólo bandit router lineal).
- Roadmap fase 2: definir prioris de core knowledge como axiomas iniciales del sistema.
- Roadmap fase 3: bucle exploratorio con predicción de memoria estilo JEPA (predicción en espacio abstracto): el planificador A* usa distancias latentes de memoria como heurística.
- Roadmap fase 4: autoevaluación en sandbox con métricas inmutables y anti-gaming.
- Añadir sección "Dónde compite esto": ecosistema híbrido post-consenso 2026, sin promesa de AGI mañana (sinergia con lo honesto del análisis de la sesión pasada: "ni uno ni otro son AGI ni la conseguirás mañana").

## 8. Próximos pasos concretos

- Corto plazo (sesión actual): **fase 0** del kernel — memoria + router + trazas, portando lo esencial de ARCA-llm (150 KB liviano, testeado, memoria persistente + evidencia citable) e inyectando desde ARCA-LLM2 los arcanos (Datalog/CAS/A*, HDC one-shot, paging < 800 MB).
- Validación mínima viable del kernel: un test ARC-like en rejilla con prioris core (transformación continua inferida en few-shot) resuelto por composición A* de razonadores + trazabilidad completa, todo < 800 MB y trazable paso a paso.
