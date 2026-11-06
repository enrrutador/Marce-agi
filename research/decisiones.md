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
