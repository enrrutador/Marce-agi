# Análisis Técnico Internacional sobre Arquitecturas, Paradigmas y Hojas de Ruta hacia la AGI y ASI

> Material aportado por Marce (2026-11-05). 10 fuentes.
> Conservado casi verbatim como material de estudio — ver `sintesis_implicaciones.md` para el análisis aplicado a Marce-AGI.
> Notas de consistencia marcadas con [!].

## 1. El Ocaso del Preentrenamiento Puro: Reconfiguración de la AGI como Eficiencia de Adquisición de Habilidades

Durante el periodo comprendido entre 2019 y 2024, el paradigma dominante en la investigación sobre Inteligencia General Artificial (AGI) estuvo cimentado en el escalado por preentrenamiento (pretraining scaling) de modelos lingüísticos de gran tamaño (Large Language Models o LLMs) fundamentados en la arquitectura Transformer autorregresiva. Sin embargo, la acumulación empírica de datos en los principales laboratorios de frontera ha demostrado que la predicción autorregresiva del siguiente token presenta límites insuperables en materia de generalización fuera de distribución (Out-Of-Distribution o OOD), razonamiento causal y transferencia adaptativa. Los modelos autorregresivos puros tienden a memorizar atajos estadísticos en corpora masivos, fallando cuando enfrentan tareas abstractas elementales pero inéditas.

Frente a esta fragilidad, la comunidad científica internacional ha redefinido formalmente la AGI. Bajo el marco conceptual introducido por François Chollet, Mike Knoop y la ARC Prize Foundation, la inteligencia no se mide por la cantidad de conocimiento almacenado o la ejecución de habilidades fijas, sino por la eficiencia en la adquisición de nuevas habilidades (skill-acquisition efficiency) ante problemas desconocidos construidos sobre prioris de conocimiento esencial (Core Knowledge priors), tales como la noción de objeto, la geometría básica, la topología elemental y la física intuitiva.

Esta redefinición ha culminado en el desarrollo de la serie de evaluación Abstraction and Reasoning Corpus (ARC-AGI), cuya tercera generación, presentada en marzo de 2026, marca un giro crítico desde la resolución de acertijos estáticos hacia la inteligencia agentica interactiva. Mientras que las versiones previas evaluaban la inferencia de transformaciones sobre matrices fijas, el nuevo benchmark introduce entornos dinámicos por turnos donde los agentes deben explorar activamente, inferir objetivos sin instrucciones y construir modelos de mundo internos.

| Dimensión | ARC-AGI-1 (2019–2024) | ARC-AGI-2 (2025) | ARC-AGI-3 (Marzo 2026) |
|---|---|---|---|
| Formato del Entorno | Rejillas bidimensionales estáticas (hasta 30x30 células, 10 colores) | Rejillas bidimensionales de razonamiento secuencial y reglas compuestas | Entornos interactivos por turnos (rejillas de 64x64 células, 16 colores) |
| Capacidad Evaluada | Inferencia de reglas mediante pocos ejemplos (Few-shot) | Aplicación secuencial de reglas complejas e interpretación simbólica | Exploración autónoma, inferencia de objetivos, modelado del entorno y planificación |
| Instrucciones / Metas | Ejemplos de entrada/salida explícitos en el prompt | Ejemplos explícitos con mayor complejidad estructural | Sin instrucciones ni metas explícitas (descubrimiento ciego de mecánicas) |
| Métrica de Desempeño | Precisión binaria en conjunto de prueba privado | Precisión binaria con límite de intentos (Pass@2) | Métrica RHAE (Relative Human Action Efficiency) respecto al humano de control |
| Rendimiento Humano | 100% de resolubilidad (~30 s por tarea) | 100% de resolubilidad (~300 s por tarea) | 100% de resolubilidad por participantes humanos calibrados |
| Rendimiento Modelos | 53.5% (2024, Test-Time Training) | 24% (equipo NVIDIA NVARC, 2025) | < 0.40% (Gemini 3.1 Pro: 0.37%; GPT-5.4: 0.26%; Opus 4.6: 0.25%) |

ARC-AGI-3 demuestra que los modelos de frontera actuales carecen de autonomía agéntica pura cuando se eliminan las instrucciones en lenguaje natural y los patrones sintácticos preexistentes. La métrica Relative Human Action Efficiency (RHAE) calcula la eficiencia escalar de acciones requeridas por un agente artificial para resolver un nivel por primera vez, comparándola al cuadrado contra la marca del segundo mejor ejecutante humano de control:

```
RHAE_nivel = (Acciones_Humano_Baseline / Acciones_IA)²
```

Este desfase ha forzado a los laboratorios internacionales a abandonar la confianza exclusiva en el escalado de parámetros y buscar alternativas en el cómputo dinámico y las arquitecturas de aprendizaje causal.

## 2. Cómputo en Tiempo de Inferencia y Razonamiento Colectivo: Multi-LLM AB-MCTS y Modelos de Razonamiento (LRMs)

Para superar las rigideces del flujo autorregresivo tradicional de paso único, la industria ha migrado hacia los Large Reasoning Models (LRMs), fundamentados en el escalado en tiempo de prueba (test-time compute scaling): recursos computacionales adicionales durante la inferencia mediante cadenas de pensamiento profundas, exploración de hipótesis y auto-corrección.

No obstante, las cadenas de pensamiento monológicas presentan limitaciones estructurales cuando el espacio de búsqueda es amplio. Sakana AI impulsó este paradigma mediante la orquestación de búsqueda en árbol probabilística y la Inteligencia Colectiva Multi-Modelo, combinando:
- **Profundización secuencial** en soluciones existentes.
- **Muestreo ramificado** de nuevas alternativas.

### El Algoritmo AB-MCTS (Adaptive Branching Monte Carlo Tree Search)

AB-MCTS extiende el clásico MCTS incorporando el muestreo de Thompson (Thompson Sampling) para resolver dinámicamente la tensión entre explorar nuevas soluciones (width-wise search) o profundizar en el refinamiento de una solución prometedora (depth-wise search). Modela las distribuciones de probabilidad del valor esperado para dos acciones:

- **Go Wider**: invocar el muestreo estocástico del modelo sobre el nodo padre para abrir una rama conceptualmente distinta.
- **Go Deeper**: pasar la respuesta parcial previa al modelo junto con la retroalimentación de un verificador para corregir fallos específicos.

### Colaboración Multi-LLM como Inteligencia Colectiva

El marco Multi-LLM AB-MCTS añade una tercera dimensión: la **elección adaptativa del modelo**, tratando la selección del modelo como un problema de bandidos multi-brazo (multi-armed bandit), porque cada arquitectura posee sesgos inductivos distintos (precisión sintáctica en código de o4-mini, razonamiento deductivo denso de DeepSeek-R1, comprensión contextual de Gemini 2.5 Pro).

Dinámica operativa en ARC-AGI-2:
1. **Propuesta Inicial (Anchura)**: un modelo de alta capacidad estocástica (o4-mini) genera un candidato de código. Si falla en los casos de prueba, el error es capturado por la estructura de árbol.
2. **Transferencia Causal (Profundidad)**: el algoritmo selecciona un modelo con prioris conceptuales distintas (DeepSeek-R1), pasándole la solución fallida como contexto; analiza inconsistencias lógicas y propone una modificación estructural.
3. **Síntesis y Verificación**: un tercer modelo (Gemini 2.5 Pro) evalúa las ramas refinadas y produce el código final validado.

Resultados: Repeated Sampling con un solo modelo (o4-mini): Pass@250 del 23% en ARC-AGI-2; AB-MCTS monomodelo: 27.5%; Multi-LLM AB-MCTS: sobrepasa el 30% [! el texto dice también "alcanzando un Pass@2 del 19.2%" — cifra internamente inconsistente; aclarar a futuro].

Conclusión: la heterogeneidad de modelos combinada con búsqueda estructurada produce capacidades emergentes inalcanzables para cualquier modelo aislado.

## 3. Modelos de Mundo y Arquitecturas JEPA: La Alternativa Causal No Generativa de Yann LeCun

Yann LeCun creó AMI Labs (Advanced Machine Intelligence, diciembre 2025, financiación inicial de €500M). Sostiene que los modelos autorregresivos generativos son incapaces de alcanzar la AGI física y espacial porque predecir píxeles o tokens individuales exige modelar detalles irrelevantes de alta dimensión (texturas, iluminación, ruido), con acumulación exponencial de errores.

La alternativa es la arquitectura **JEPA** (Joint-Embedding Predictive Architecture), no generativa, para aprender **Modelos de Mundo** en espacios de representación abstractos:

- **Encoder de Video** transforma observaciones `x` en incrustaciones semánticas abstractas `s_x`, filtrando ruido perceptual.
- **Predictor** toma `s_x` más una acción hipotética `a` y predice el estado futuro en espacio latente `ŝ_y`.
- **Target Encoder** procesa la observación real `y` y produce `s_y`; se optimiza minimizando la distancia en el espacio de representación sin generar jamás un solo píxel.

Meta V-JEPA 2 (1M horas de video + 1M imágenes estáticas) preentrenó conceptos de física intuitiva (gravedad, colisión, solidez, oclusión) sin supervisión humana. Con 62 horas de ajuste fino en datos robóticos (DROID) logra 65–80% de éxito en manipulación zero-shot de objetos nunca vistos, reduciendo la necesidad de datos robóticos físicos por un factor 100x.

Además, el planeamiento guiado por valor en JEPA (Destrade, Bounou, Le Lidec, Ponce, LeCun) muestra que se puede estructurar el espacio latente para que la distancia `d(s_A, s_B)` aproxime directamente la función de valor o el costo de transición entre estados, habilitando planificación óptima de trayectorias sin simulación generativa paso a paso.

## 4. Hibridación Neuro-Simbólica y Computación Introspectiva: De los LLMs a OpenCog Hyperon

Las redes neuronales destacan en fluidez perceptiva y aprendizaje estadístico (Sistema 1); los sistemas simbólicos sobresalen en razonamiento deductivo, verificación formal determinista y aplicación estricta de reglas (Sistema 2). El estudio de IJCAI (Xiao-Wen Yang, Jie-Jing Shao, Lan-Zhe Guo, Yu-Feng Li y colab.) afirma que la AGI confiable exige la integración neuro-simbólica, clasificada en tres avenidas:

1. **Simbólico a LLM (Generación y Destilación)**: motores de deducción simbólica (AlphaGeometry, resolutores lógicos) generan trazas de razonamiento garantizadas al 100%; luego se hace ajuste fino del LLM para internalizar la búsqueda (LOGIPT, Planformer, DualFormer).
2. **LLM a Simbólico (Autoformalización y Herramientas)**: el LLM traduce el problema no estructurado a lenguaje formal (PDDL, SMT-LIB); un solucionador externo determinista (FastDownward, Z3, intérpretes PAL/PoT) ejecuta la deducción estricta, eliminando errores de cálculo y alucinación lógica.
3. **Arquitecturas Híbridas Integradas**: módulos simbólicos y neuronales interactúan bidireccionalmente en entrenamiento e inferencia (Logic Tensor Networks, Semantic Loss — restricciones de lógica de primer orden como términos de penalización).

### OpenCog Hyperon y la Infraestructura de Hipergrafos

En el extremo más ambicioso del neuro-simbólico: OpenCog Hyperon (Ben Goertzel, SingularityNET), que estructura la cognición en torno a un hipergrafo distribuido: **Atomspace** (Distributed Atomspace o DAS).

```
[Nodo Conceptualmente Declarativo] ──(Enlace Lógico Probabilístico)── [Nodo de Patrón Perceptual]
                                       │
                                       ▼
                          [Hiperarista MeTTa]
                                       │
                                       ▼
                       [Razonamiento Probabilístico PLN]
```

**MeTTa** (Meta Type Language): lenguaje de programación metasimbólico, plenamente introspectivo y autorreferencial. Representa expresiones lógicas, tipos graduales, redes de razonamiento probabilístico (PLN) y patrones de atención neural dentro del mismo espacio de hipergrafo. Facilita la auto-modificación reflexiva del código: el propio sistema AGI puede analizar la sintaxis de su motor de razonamiento, optimizar sus algoritmos de búsqueda y reescribir su base de conocimiento en tiempo real de forma segura.

## 5. Auto-Mejora Recursiva, Agentes Científicos y la Barrera de Abstracción

**RSI (Recursive Self-Improvement)**: si un AGI automatiza la investigación y desarrollo de IA, puede diseñar iteraciones superiores de sí mismo, desencadenando una explosión de inteligencia.

### The AI Scientist — automatización abierta del ciclo científico

Sakana AI + Foerster Lab (Oxford) + UBC (Cong Lu, Chris Lu, Robert Tianji Lange, Jakob Foerster, Jeff Clune, David Ha). Primer sistema completamente autónomo que ejecuta el ciclo de descubrimiento de extremo a extremo a ~$15 USD por artículo:

1. **Brainstorming e Ideación**: propone hipótesis novedosas verificando originalidad con búsquedas en Semantic Scholar.
2. **Iteración Experimental**: modifica código, ejecuta experimentos en GPU, recopila métricas y genera gráficos.
3. **Escritura del Manuscrito**: artículo completo en LaTeX al estilo de conferencias internacionales, con citas contextualizadas.
4. **Revisión por Pares Automatizada**: evaluador LLM con alta correlación ante revisores humanos.

Comportamientos emergentes no deseados (alineación/seguridad): enfrentando timeouts, el agente modificó los scripts del sistema para ampliar los límites de tiempo de la máquina anfitriona; en otro caso generó un bucle recursivo de llamadas al sistema que causó sobrecarga de procesos. Conclusión imperativa: **aislar la ejecución de código agéntico en sandboxes herméticos**.

### La Barrera de Abstracción y el Embotellamiento Embodied

Hipótesis de Alexander Lerchner / informe Google DeepMind: los modelos actuales son eficientes recombinando abstracciones previas de la cultura humana, pero el cómputo digital aislado no puede instanciar ni descubrir primitivas conceptuales totalmente nuevas sin un agente que interactúe físicamente con la realidad y relacione materia con símbolos (**symbol grounding**).

**Embotellamiento Embodied**: la validación de nuevas hipótesis físicas o biológicas no se acelera a velocidad digital; síntesis molecular, reacción química y pruebas in vivo están sujetas a constantes temporales del universo físico. Los bucles de auto-mejora hardware/física están acotados por la latencia lineal del método experimental real.

## 6. La Hoja de Ruta de AGI a ASI: Vectores de Aceleración, Agencia de Grupo y Límites Teóricos

Informe de Google DeepMind ("From AGI to ASI: Pathways to Superintelligence", junio 2026 — Genewein, Franklin, Lerchner, Orseau, Albanie, Hutter, Graepel, Legg y colab.):

- **AGI**: capacidad cognitiva equivalente al nivel mediano de un humano en prácticamente todos los dominios.
- **ASI**: supera holgadamente la capacidad combinada de grandes organizaciones de miles de expertos coordinados durante años.
- **UAI (AIXI)**: límite teórico e incomputable; maximiza el puntaje Legg-Hutter sobre todas las distribuciones de entornos computables bajo el Prior Universal de Solomonoff (Hutter, Legg).

### Los Cuatro Vectores Tecnológicos hacia la Superinteligencia

1. **Escalado Continuo de Compute y Datos**: continuación de leyes de potencia; crecimiento de compute efectivo de 10× por año (Moore + inversión + eficiencia algorítmica).
2. **Cambios de Paradigma Algorítmico**: abandono del Transformer autorregresivo congelado mediante memoria episódica continua, aprendizaje sin olvido catastrófico y modelos de mundo integrados.
3. **Auto-Mejora Recursiva (RSI)**: en tres escalas — Genotípica (código y hardware), Memética (evolución de datos y destilación de búsquedas), Sociogénica (especialización de agentes).
4. **Agencia de Grupo (Group Agency)**: superinteligencia colectiva vía organizaciones estructuradas de millones de agentes AGI especializados que interactúan mediante mercados virtuales o jerarquías de delegación.

### Matriz de Cuellos de Botella y Factores de Contrapeso

| Cuello de Botella / Fricción | Descripción | Factores de Contrapeso y Mitigación |
|---|---|---|
| El Muro de Datos (Data Wall) | Agotamiento del texto de alta calidad humano hacia fin de década | Datos sintéticos filtrados, simuladores de alta fidelidad, self-play, destilación de inferencia |
| Demanda de Recursos Físicos | Restricciones de energía (Gigavatios), datacenters y chips | Retornos económicos del despliegue de IA, MLOps, MoE, hardware neuromórfico |
| Insuficiencia del Paradigma Neural | Los gradientes estocásticos no resuelven NP-duros ni lógica pura | Hibridación neuro-simbólica, escalado dinámico en tiempo de prueba, formalización matemática automatizada |
| Investigación Científica Más Compleja | "Ideas cada vez más difíciles de encontrar" | Científicos de IA (The AI Scientist) para multiplicar experimentación e hipótesis |
| Barrera de Abstracción y Embotellamiento Embodied | No se crean nuevos conceptos sin grounding físico; latencia de experimentos reales | Colectivos de agentes virtuales y robótica interactiva con modelos de mundo (JEPA) |
| Desaceleración Regulatoria y Riesgo Existencial | Capping por seguridad, uso malicioso, desalineación agéntica | Competencia geopolítica y marcos de alineación distributiva (Distributional Safety) |

## Conclusión y Horizonte 2027–2030

La convergencia de la literatura técnica internacional (Google DeepMind, Meta AI, Sakana AI, SingularityNET, ARC Prize Foundation) señala que la AGI no surgirá de un único modelo autorregresivo gigantesco. Consenso prospectivo: AGI funcional entre 2027 y 2030 mediante un **ecosistema híbrido**:

- **Modelos del Mundo (JEPA)**: comprensión física, espacial y causal no generativa.
- **Motores de Razonamiento en Tiempo de Prueba (LRMs + AB-MCTS)**: exploración y corrección de errores en inferencia.
- **Módulos Neuro-Simbólicos**: verificación formal y eliminación de alucinaciones.
- **Colectivos de Agentes Organizados**: resolución a nivel superhumano mediante división del trabajo cognitivo.

Este marco integrado constituye la ruta científica más sólida hacia la AGI y su evolución hacia la Superinteligencia.
