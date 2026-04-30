# Skill: prep-module

## Cuándo invocar
Cuando el usuario diga cosas como:
- "preparar el módulo N"
- "armá la clase del módulo N"
- "generá todo para el módulo N"
- "dejá listo el módulo N"

## Objetivo
Orquestar la preparación completa de un módulo: deck + lista de herramientas + notas para el profesor, en un solo paso.

## Inputs requeridos
- `N` (número del módulo, 1 a 5). Si no es claro, **preguntar**.

## Procedimiento

### 1. Validaciones previas
- Verificar que existe `Modulo-N/mds/` con archivos `.md` adentro.
- Si no existe o está vacío, avisar al usuario y detener.
- Si ya existen outputs (`deck_N.md`, `herramientas_modulo_N.md`, `notas_para_el_profe.md`), preguntar si se sobrescriben o se hace backup.

### 2. Lectura única del material
- Leer **todos** los `.md` de `Modulo-N/mds/` en paralelo.
- Mantener el contenido en memoria para los 3 pasos siguientes (no releer).
- Detectar inconsistencias y guardarlas para el paso de notas.

### 3. Generar outputs en orden

**Paso A — `build-deck`**
- Aplicar el skill `build-deck` (ver `.copilot/skills/build-deck/SKILL.md`).
- Output: `Modulo-N/deck_N.md`.

**Paso B — `build-tools-list`**
- Aplicar el skill `build-tools-list`.
- Output: `Modulo-N/herramientas_modulo_N.md`.

**Paso C — `build-instructor-notes`**
- Aplicar el skill `build-instructor-notes` (necesita el deck del paso A).
- Output: `Modulo-N/notas_para_el_profe.md`.

**Paso D (opcional) — `build-deck-html`**
- Solo si el usuario pidió explícitamente generar también el HTML, o si confirma cuando se le pregunta al final.
- Aplicar el skill `build-deck-html`.
- Output: `Modulo-N/deck_N.html`.

### 4. Reporte final al usuario

Devolver un resumen con:
- Los 3 archivos creados / actualizados
- Cantidad aproximada de slides en el deck
- Cantidad de herramientas catalogadas
- Cantidad de inconsistencias detectadas en los mds (si las hubo)
- Próximos pasos sugeridos (revisar el deck, completar el "Sobre mí", convertir a HTML)

## Reglas

- **No paralelizar A, B y C** porque las notas dependen del deck. A y B sí podrían paralelizarse, pero por simplicidad de revisión dejar el orden A → B → C.
- Si un paso falla, **detener** y reportar. No continuar con outputs parciales.
- Respetar todas las reglas de `AGENTS.md` (pedagogía, naming, no-comentarios-en-deck, idioma rioplatense).

## Validación final
- [ ] Los 3 archivos existen en `Modulo-N/`
- [ ] El deck respeta el formato (slide 2 = sobre mí, receso a la mitad, demos guiadas, proyecto integrador como tarea)
- [ ] La lista de herramientas usa comandos literales del material
- [ ] Las notas reflejan el deck generado (no un deck genérico)
