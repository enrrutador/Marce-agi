# Log de decisiones de diseño — Marce-AGI

Registro cronológico de decisiones tomadas durante la travesía. Cada decisión
apunta a los archivos donde vive implementada.

## D1 (2026-11-06) — La AGI se nutre de información, no de tokens
**Origen**: Marce, citando video Facebook (share/r/19yRHEJz5f) + análisis internacional
(`2026-11-05_analisis_tecnico_internacional_AGI.md`). Ese análisis documentó el
consenso: el preentrenamiento token-predictivo falla en OOD, razonamiento causal
y transferencia — la predicción de superficie no construye inteligencia.

**Definición operativa**:
- **Información** = proposiciones con valor de verdad + evidencia anclada +
  confianza medible, en estructuras consultables (hechos, reglas si/entonces,
  episodios, anclas de evidencia). Eso es lo que el kernel ingiere, indexa y
  razona sobre. Ya implementado: `first_model/marce_agi/memoria.py`.
- **Tokens** = superficie estadística del texto. Pueden ser un canal de ENTRADA
  (traducción de lenguaje natural a formalismo, avenida "LLM → Simbólico" del
  análisis internacional) pero nunca el método por el cual se decide o se aprende.

**Consiguientes en el código**:
1. El aprendizaje no tiene gradientes: apoya en `MemoryStore.agregar` con
   evidencia + confianza (indexado, no gradúado).
2. Toda resolución determinista termina en ancla de evidencia citable
   (`agregar_evidencia`) — la información nueva entra con linaje.
3. Los razonadores (Datalog, CAS, Planeador) trabajan contra estructuras de
   memoria, jamás contra textura estadística.
4. El entrenamiento en Kaggle (`training/README.md`) construye calibración de
   router + memoria episódica, no recalibra pesos sobre corpus.
5. Si alguna fase usa LLM: sólo traduce/propone (SMT, PDDL, MeTTa); ejecución y
   verificación son de razonadores simbólicos exactos.

**Regla**: si un camino futuro necesita "aprender de corpora de tokens", se
prefiere el camino paralelo "corpora → extracción de proposiciones con
verificación → memoria". Prohibido graduar pesos por perplejidad de tokens.

## D2 (2026-11-06) — Base técnica: ARCA-llm vivo, calibrado contra el estudio internacional

**Origen**: Marce preguntó "¿qué ARCA usás? / ¿sirven o te basás en los estudios?".
Respuesta registrada: **ARCA-llm** es la base viva (151 KB, testeado, sin pesos);
**ARCA-LLM2** (294 MB) solo como banco de técnicas extractas cuando haga falta.
La vara es el análisis internacional (`2026-11-05_analisis_tecnico_internacional_AGI.md`).

Mapeo razonadores ARCA-llm ↔ estudio (leído contra el código):

| Motor ARCA-llm | Veredicto contra el estudio | Gap a cubrir (fase) |
|---|---|---|
| Datalog (77 l, unificación + saturación, límite 10k, trazas) | Cumple Sistema 2: derivaciones garantizadas con traza (avenida neuro-simbólica) | sin negación ni confianzas graduales tipo PLN (fase 2) |
| CAS (57 l, AST seguro, whitelist de operadores) | Cumple "matemática nunca alucina" | solo numérica; expresión simbólica futura |
| A* (51 l, rejilla 2D, heurística Manhattan) | Cumple planificación exacta con presupuesto | heurística es fija: el estudio (JEPA/planeo por valor) pide `d(sA,sB) ≈ costo` aprendida de memoria (fase 2/3) |
| HDC (77 l, D=10k bits, trigramas, Hamming, sin gradientes) | Alineado: one-shot según D1 e idea importable de predicción latente no generativa | dependencia numpy: mantener core stdlib; HDC como módulo opcional (fase 2) |
| Bandit (25 l) | Débil vs estudio | YA mejorado: router Thompson (`marce_agi/router.py`); evolución = AB-MCTS con Go-Wider/Go-Deeper sobre razonadores (fase 1+) |

Plan de fase 1 derivado: portar `unify/substitute/saturación` + AST-CAS + A* con
presupuesto a `marce_agi/` (reemplazando stubs, misma interfaz), datos leídos de
`MemoryStore`: reglas si/entonces + hechos; los stubs se retiran sólo con tests verdes.
