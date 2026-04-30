# Curso de Web Hacking — Convenciones para agentes

Este repositorio contiene el material de un curso de Web Hacking dividido en **5 módulos**. Cada módulo puede ocupar una o más clases de **2 horas** (sin receso obligatorio; se ofrece un break optativo de 5 minutos a mitad de clase).

Los agentes que trabajan en este repo deben respetar las convenciones de este archivo.

---

## Estructura del repositorio

```
Curso_web_hacking/
├── AGENTS.md                        ← este archivo
├── README.md
├── .copilot/skills/                 ← skills reusables (build-deck, prep-module, etc.)
├── templates/                       ← esqueletos editables de los outputs
├── Modulo-1/
│   ├── mds/                         ← material crudo (input)
│   ├── pdfs/                        ← PDFs originales (input)
│   ├── deck_1.md                    ← presentación slide-por-slide (output)
│   ├── deck_1.html                  ← presentación autocontenida lista para mostrar (output, opcional)
│   ├── herramientas_modulo_1.md     ← inventario de herramientas (output)
│   └── notas_para_el_profe.md       ← guía interna para el profesor (output)
├── Modulo-2/  ...  Modulo-5/
```

Inputs → `Modulo-N/mds/` y `Modulo-N/pdfs/`.
Outputs → en la raíz de `Modulo-N/`, **nunca** dentro de `mds/` ni `pdfs/`.

---

## Convención de naming

| Tipo | Patrón |
|---|---|
| Deck de la clase (markdown) | `deck_N.md` |
| Deck de la clase (HTML, opcional) | `deck_N.html` |
| Inventario de herramientas | `herramientas_modulo_N.md` |
| Notas para el profesor | `notas_para_el_profe.md` |
| MDs de input | nombres existentes (`modulo_N.md`, `lab_X.md`, `desafio_X.md`, `proy_integrador_N.md`, etc.) |

Donde `N` = número del módulo.

---

## Reglas pedagógicas (críticas)

Estas reglas determinan el **formato y contenido del deck**. Todo agente que genere un deck debe respetarlas.

1. **Duración**: 2 horas sin receso obligatorio → ~115 minutos de contenido neto. Se incluye una slide de **break optativo** (~5 min) a mitad de clase.
2. **Estilo de enseñanza**: teoría intercalada con **demos guiadas en vivo**, no labs silenciosos. El profesor ejecuta, los alumnos razonan y proponen mientras la herramienta corre.
3. **Labs y desafíos del material original** se convierten en **demos guiadas** dentro del deck. No se asignan como trabajo silencioso de 20 min en clase.
4. **Proyecto integrador** queda como **tarea para casa**, anunciado en las últimas slides con instrucciones claras y comandos listos.
5. **Slide "Sobre mí"**: siempre incluir como slide 2, con **placeholders** (`[Nombre]`, `[Rol]`, `[LinkedIn]`, etc.) que el profesor llena después.
6. **Slide de break optativo** a mitad de clase ("¿Quieren tomarse 5 minutos para estirar las piernas?").
7. **Recap + Q&A + cierre** en las últimas 3–5 slides.
8. **Módulos multi-clase**: si el contenido de un módulo no entra en 2 horas, se divide en varias clases (`deck_N.md`, `deck_N_2.md`, etc.).

---

## Reglas de output

1. El deck (`deck_N.md`) **no debe contener comentarios del agente** ni metadata interna. Es exclusivamente el contenido a presentar.
2. Cualquier comentario, observación, o sugerencia del agente va en `notas_para_el_profe.md`.
3. Las slides se separan con `---` en una línea propia (compatible con reveal.js, Marp, Slidev).
4. Una idea por slide. Tablas y bloques de código solo cuando aportan valor.
5. Emojis para marcar tipo de slide (🧪 demo, 🎯 desafío, ☕ receso) están permitidos pero deben ser opcionales.

---

## Reglas de análisis del input

Antes de generar outputs, el agente debe:

1. Leer **todos** los `.md` dentro de `Modulo-N/mds/`.
2. Detectar y reportar en `notas_para_el_profe.md` cualquier inconsistencia:
   - Preguntas o secciones duplicadas
   - Resoluciones que no corresponden al enunciado (desfase lab/resolución)
   - Saltos en la numeración de objetivos
   - Resoluciones vacías o incompletas
   - Temas que parecen pertenecer a otros módulos
3. **No inventar** contenido técnico que no esté en los mds. Si falta algo necesario para la coherencia (ej. tabla de códigos HTTP), agregarlo y mencionarlo en las notas.

---

## Skills disponibles

Los skills viven en `.copilot/skills/`. Cada uno tiene su propio `SKILL.md` con instrucciones.

| Skill | Qué hace |
|---|---|
| `build-deck` | Genera `deck_N.md` desde los mds del módulo |
| `build-tools-list` | Genera `herramientas_modulo_N.md` |
| `build-instructor-notes` | Genera `notas_para_el_profe.md` |
| `build-deck-html` | Convierte `deck_N.md` en `deck_N.html` (autocontenido) |
| `prep-module` | Ejecuta los 3 primeros en orden (one-shot por módulo) |

Cuando el usuario diga "preparar el módulo N" o equivalente → invocar `prep-module`.
Cuando pida solo el deck → `build-deck`. Cuando pida solo herramientas → `build-tools-list`.
Cuando pida "convertir a HTML" o "publicar el deck" → `build-deck-html`.

---

## Templates

Los templates en `templates/` son la **fuente de verdad del formato**. Si el formato del deck cambia, se modifica el template, no el skill. Los skills leen los templates al ejecutarse.

---

## Idioma

Todo el material del curso está en **español rioplatense** (vos, no tú). Mantenerlo consistente en outputs.

---

## Mejora continua (obligatorio)

Cada vez que el agente, durante una conversación o tarea:

- **Aprenda algo nuevo** sobre las preferencias del profesor, el formato del curso, decisiones recurrentes, o convenciones implícitas.
- **Detecte una oportunidad de mejora** en `AGENTS.md`, en algún template (`templates/*.template.md`) o en algún skill (`.copilot/skills/*/SKILL.md`).
- **Note un patrón repetido** que podría automatizarse o estandarizarse.
- **Reciba un feedback o corrección** del usuario que contradiga o complemente las reglas existentes.

…debe **proponer explícitamente al usuario** una actualización concreta del archivo correspondiente, indicando:

1. **Qué archivo** propone modificar (`AGENTS.md`, template específico, o skill específico).
2. **Qué cambio concreto** propone (diff conceptual o texto a agregar / reemplazar).
3. **Por qué**: la observación o aprendizaje que motiva el cambio.
4. **Esperar confirmación** antes de aplicarlo.

La propuesta debe hacerse **en el momento** en que se detecta la oportunidad, no postergarla a un "después".

> Esta regla aplica a este repo. El objetivo es que el sistema de preparación de módulos mejore con cada clase y se vuelva cada vez más fiel al estilo del profesor.
