# Skill: build-instructor-notes

## Cuándo invocar
Cuando el usuario pida las notas / guía / comentarios para el profesor de un módulo. También se invoca automáticamente desde `prep-module` después de generar el deck.

## Objetivo
Generar `Modulo-N/notas_para_el_profe.md` con la guía interna del profesor: reparto temporal, cómo conducir cada demo, decisiones de diseño tomadas e inconsistencias detectadas en los mds.

## Inputs requeridos
- `N` (número del módulo). Si no es claro, preguntar.
- `Modulo-N/deck_N.md` (debe existir; si no, sugerir correr `build-deck` primero).
- Todos los `.md` dentro de `Modulo-N/mds/`.
- `templates/notas.template.md` como esqueleto.

## Procedimiento

### 1. Reparto temporal

Total: 180 min - 20 min de receso = **160 min de contenido**.

Construir tabla con columnas: **Bloque | Slides | Min | Detalle**.

Tiempos sugeridos por tipo de bloque:
- Apertura (portada, sobre mí, reglas, agenda, objetivos): ~15 min
- Bloque teórico denso: ~30–35 min
- Bloque teórico ligero: ~10–15 min
- Demo guiada en vivo: ~15 min
- Receso: 20 min
- Recap + tarea + cierre: ~15 min

Sumar y verificar que el total ≤ 180 min (idealmente con margen de 5–15 min).

### 2. Cómo conducir cada demo

Para cada slide marcada como demo en el deck, escribir un párrafo con:
- **Preparación previa**: qué tener abierto antes de la demo (terminales, browser, wordlists)
- **Durante la demo**: qué decir, qué preguntar al curso, en qué momento mostrar el resultado
- **Plan B**: qué hacer si la herramienta falla / la red está caída (output guardado, screenshot)
- **Cierre**: qué construir junto al curso (tabla, mitigaciones, modelo)

### 3. Decisiones de diseño

Listar las decisiones que se tomaron al armar el deck:
- Qué labs/desafíos se convirtieron en demos
- Qué quedó como tarea
- Posición del receso
- Slides agregadas para coherencia que no estaban en los mds
- Slides "Sobre mí" como mock

### 4. Inconsistencias detectadas en los mds

Listar **todo** lo que detectaste durante el análisis:
- Preguntas o secciones duplicadas
- Resoluciones que no corresponden al enunciado
- Saltos numéricos en objetivos
- Resoluciones vacías o solo con `…`
- Temas que parecen ser de otros módulos
- Lab/resolución desfasados

Cada hallazgo: archivo + descripción breve + sugerencia de qué hacer.

### 5. Sugerencias adicionales

- Backup de outputs por si falla la red
- Modelos pre-armados (Threat Dragon, Burp, etc.) como plan B
- Ejemplos de informe si hay entregable
- Demos cortas previas al lab si ayuda

### 6. Notas para conversión a HTML

Recordar:
- 1 idea por slide
- `---` separa slides
- Emojis pueden romper en algunos motores

### 7. Output

Escribir en `Modulo-N/notas_para_el_profe.md` siguiendo `templates/notas.template.md`.

## Reglas

- Este archivo **sí** lleva tono conversacional y observaciones del agente.
- No mezclar este contenido con `deck_N.md`.
- Si el deck cambia (rerun de `build-deck`), regenerar también las notas.

## Validación final
- [ ] Existe `Modulo-N/notas_para_el_profe.md`
- [ ] La tabla de reparto temporal suma ≤ 180 min
- [ ] Hay guía concreta para cada demo
- [ ] Las inconsistencias detectadas están listadas
- [ ] Hay sección de decisiones de diseño
