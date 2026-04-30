# Skill: build-deck

## Cuándo invocar
Cuando el usuario pida generar / armar / construir el deck de un módulo, o solo "el deck del módulo N", o convertir los mds en presentación.

## Objetivo
Generar `Modulo-N/deck_N.md` listo para convertir a HTML, respetando las reglas pedagógicas y de output del repo (`AGENTS.md`).

## Inputs requeridos
- `N` (número del módulo). Si no es claro, preguntar al usuario.
- Todos los archivos `.md` dentro de `Modulo-N/mds/`.
- `templates/deck.template.md` como esqueleto base.

## Procedimiento

### 1. Leer el material
- Leer **todos** los `.md` de `Modulo-N/mds/` en paralelo.
- Identificar archivos por convención de nombre:
  - `modulo_N.md` → contenido teórico principal
  - `objetivo_modulo_N.md` → objetivos de aprendizaje
  - `lab_*.md` y `lab_*_resolved.md` → laboratorios y resoluciones
  - `desafio_*.md` y `desafio_*_resolved.md` → desafíos y resoluciones
  - `proy_integrador_N.md` y `_resolved.md` → proyecto integrador

### 2. Detectar inconsistencias (no fallar, registrar)
- Preguntas / secciones duplicadas
- Resoluciones que no corresponden al enunciado
- Saltos en la numeración de objetivos
- Resoluciones vacías o con solo `…`
- Temas que parecen pertenecer a otros módulos
- Guardar la lista para `notas_para_el_profe.md` (otro skill se encarga).

### 3. Estructurar el deck

Reparto base de slides (~50 slides para clase de 3 hs):

| Sección | Slides | Notas |
|---|---|---|
| Portada + Sobre mí (mock) + Bienvenida + Reglas + Agenda + Objetivos | 1–6 | Siempre presentes |
| Bloque 1: teoría | 7–22 aprox | Conceptos del `modulo_N.md` |
| Demo 1 (en vivo) | 2 slides | Convertir el primer lab/desafío en demo guiada |
| Receso | 1 slide | Mitad de clase |
| Bloque 2: teoría | ~10 slides | Resto del `modulo_N.md` |
| Demo 2 (en vivo) | 2 slides | Segundo lab/desafío |
| Demo 3 (en vivo, opcional) | 2 slides | Tercer desafío si aplica |
| Recap + Proyecto integrador (tarea) + Próxima clase + Recursos + Q&A + Cierre | últimas 6–7 | |

### 4. Reglas críticas al armar slides

**Sí**:
- Una idea por slide
- Tablas para comparaciones, bloques de código para comandos
- Emojis para marcar tipo de slide: 🧱 (bloque teórico), 🧪 (demo), 🎯 (demo desafío), ☕ (receso), 📌 (tarea), 🔎 (bloque de exploración)
- Slide "Sobre mí" SIEMPRE como #2 con placeholders
- Receso explícito y a la mitad
- Cada demo en vivo: 1 slide de presentación + 1 slide con comandos y preguntas para el curso
- **Headings del deck sin prefijo `Slide N —`**: usar solo el título real (ej. `## HTTPS y TLS`, no `## Slide 8 — HTTPS y TLS`). El número de slide es responsabilidad del motor de presentación (HTML, reveal.js, etc.), no del contenido. Esto evita bugs en parsers que no normalicen el prefijo.

**No**:
- ❌ No incluir comentarios del agente, metadata, ni texto explicativo dirigido a vos. Solo contenido a presentar.
- ❌ No convertir labs/desafíos en "20 min de práctica silenciosa". Son **demos guiadas en vivo**.
- ❌ No mover el proyecto integrador a clase. Va como **tarea para casa** en las últimas slides.
- ❌ No inventar contenido técnico que no esté en los mds. Si agregás algo (ej. tabla de códigos HTTP) para coherencia, mencionalo después en las notas.
- ❌ No prefijar headings con `Slide N — ` ni con números secuenciales del estilo "Slide X". Romperá la conversión a HTML.
- ❌ No empaquetar más de **~7 ítems combinados** (puntos de lista + párrafos cortos + blockquotes + tablas) en una sola slide. Provoca overflow vertical en el HTML.
- ❌ No usar numeración continua entre dos `<ol>` distintos en la misma slide (ej. lista que arranca en 6). El parser HTML actual no respeta `start=N` y renderiza desde 1.

### 4.bis. Densidad por slide (anti-overflow)

Regla práctica para evitar que el contenido se desborde verticalmente en el HTML:

- Máximo ~7 ítems combinados por slide (lista + párrafo + blockquote + tabla cuentan).
- Si una sección natural tiene más, **dividila en 2 slides** agrupando lógicamente (ej. agenda → "Bloque 1" y "Bloque 2" en slides separadas).
- Cada `<ol>` arranca en 1. Si necesitás continuidad numérica, usá una sola lista o reformulá como dos listas independientes.
- Patrón específico para agendas de clase: una slide por bloque (no la agenda completa en una sola).

### 5. Convertir labs/desafíos en demos guiadas

Para cada `lab_*.md` o `desafio_*.md` del material original:
- Slide A: "🧪 Demo en vivo · {nombre}" — qué vamos a hacer juntos, target, lista de pasos
- Slide B: comandos exactos a correr + 3–5 preguntas para tirarle al curso mientras la herramienta procesa

### 6. Slide "Sobre mí" (mock)

Siempre así, con placeholders entre corchetes:

```markdown
**[Nombre y Apellido]**
[Rol / Título profesional]

- 🎓 [Formación / Certificaciones]
- 💼 [Años de experiencia · empresas / proyectos clave]
- 🔬 [Áreas de interés]
- 🔗 [LinkedIn] · [GitHub] · [Twitter/X] · [Web]
- 📩 [email de contacto]

> Espacio para foto
```

### 7. Slides finales obligatorias

- Recap
- Proyecto integrador como tarea (con comandos listos del `proy_integrador_N.md`)
- Para la próxima clase
- Recursos recomendados
- Q&A
- Cierre

### 8. Output

Escribir el resultado en `Modulo-N/deck_N.md`.
- Slides separadas por `---` en línea propia.
- Encabezado del archivo con título y nota de duración.
- Sin comentarios del agente.

## Validación final antes de devolver
- [ ] `deck_N.md` existe en `Modulo-N/`
- [ ] Slide 2 es "Sobre mí" con placeholders
- [ ] Hay slide de receso explícita
- [ ] Las prácticas en clase son demos guiadas, no labs silenciosos
- [ ] El proyecto integrador está como tarea, no como actividad de clase
- [ ] No hay comentarios del agente en el deck
- [ ] Slides separadas con `---`
- [ ] Ningún heading empieza con `Slide N — ` (regla anti-bug de parsers HTML)
- [ ] Ninguna slide supera ~7 ítems combinados (anti-overflow vertical)
- [ ] Ninguna slide tiene dos `<ol>` con numeración continua (ej. una lista 1–5 seguida de otra que arranca en 6)
