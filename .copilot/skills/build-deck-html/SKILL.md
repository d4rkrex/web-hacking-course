# Skill: build-deck-html

## Cuándo invocar
Cuando el usuario pida:
- "convertí el deck a HTML"
- "armá el HTML del módulo N"
- "generá el deck_N.html"
- "publicá el deck"

También puede invocarse al final de `prep-module` si el usuario lo pidió explícitamente.

## Objetivo
Generar `Modulo-N/deck_N.html` a partir de `Modulo-N/deck_N.md` usando `templates/deck.template.html` como esqueleto. El HTML resultante es autocontenido (un solo archivo, sin dependencias externas más allá de Google Fonts vía CDN) y abre directamente en el navegador.

## Inputs requeridos
- `N` (número del módulo). Si no es claro, preguntar.
- `Modulo-N/deck_N.md` (debe existir; si no, sugerir correr `build-deck` primero).
- `templates/deck.template.html` (esqueleto con placeholders `{{DECK_TITLE}}` y `{{DECK_MARKDOWN}}`).

## Procedimiento

### 1. Validaciones previas
- Verificar que `Modulo-N/deck_N.md` existe y tiene contenido.
- Verificar que `templates/deck.template.html` existe.
- Si ya existe `Modulo-N/deck_N.html`, preguntar si se sobrescribe.

### 2. Validar el deck markdown contra reglas de parseo

Antes de inlinear, chequear que el markdown cumple lo que el parser HTML espera (definido en `AGENTS.md` y `build-deck`):

- [ ] Slides separadas por `---` en línea propia.
- [ ] Headings **sin** prefijo `Slide N — ` (regla anti-bug). Si aparece, avisar y sugerir correr `build-deck` primero o limpiarlo.
- [ ] Bloques de código cerrados correctamente (\`\`\` apareados).
- [ ] Tablas con sintaxis pipe completas (cabecera + separador + filas).

Si hay problemas, **detener** y reportar antes de generar el HTML.

### 3. Construir el título del documento

Patrón: `Deck N · Módulo N · Curso de Web Hacking`

Reemplaza `{{DECK_TITLE}}` en el template.

### 4. Inlinear el markdown

- Leer `Modulo-N/deck_N.md` completo.
- Reemplazar el placeholder `{{DECK_MARKDOWN}}` del template **literalmente** (sin escape — va dentro de `<script type="text/plain">` que no interpreta HTML).
- Importante: si el markdown contuviera la cadena literal `</script>` (improbable pero posible en código de ejemplo), reemplazarla por `<\/script>` para no cerrar el bloque antes de tiempo.

### 5. Escribir el output

Guardar en `Modulo-N/deck_N.html`.

### 6. Verificación post-generación

- [ ] El archivo existe y tiene tamaño > 30 KB (template + contenido).
- [ ] Contiene exactamente una vez `id="deck-source"`.
- [ ] No contiene `{{DECK_MARKDOWN}}` ni `{{DECK_TITLE}}` (placeholders sin reemplazar).
- [ ] El bloque `<script id="deck-source" type="text/plain">` cierra con un único `</script>`.

### 7. Reporte al usuario

Devolver:
- Ruta absoluta del HTML generado
- Cantidad de slides detectadas (contar `^---$` en el markdown menos 1, o contar headings de slide)
- Sugerencia: `xdg-open Modulo-N/deck_N.html` o equivalente para previsualizar

## Reglas

- **No modificar** el motor JS/CSS del template salvo que el usuario lo pida explícitamente. Si detectás un bug del parser, proponé una actualización al template (regla de mejora continua de `AGENTS.md`) y esperá confirmación.
- **No regenerar** el `deck_N.md`. Este skill **solo** convierte; si hay errores en el markdown, derivar a `build-deck`.
- El HTML resultante debe ser **autocontenido** (sin assets externos salvo Google Fonts ya referenciado en el template).

## Implementación sugerida (referencia)

```python
import sys
from pathlib import Path

n = sys.argv[1]
root = Path(__file__).resolve().parents[3]  # repo root
deck_md = root / f"Modulo-{n}" / f"deck_{n}.md"
template = root / "templates" / "deck.template.html"
out = root / f"Modulo-{n}" / f"deck_{n}.html"

md = deck_md.read_text(encoding="utf-8")
# Proteger </script> dentro del markdown
md = md.replace("</script>", "<\\/script>")

html = template.read_text(encoding="utf-8")
html = html.replace("{{DECK_TITLE}}", f"Deck {n} · Módulo {n} · Curso de Web Hacking")
html = html.replace("{{DECK_MARKDOWN}}", md)

# Verificación de placeholders
assert "{{DECK_MARKDOWN}}" not in html and "{{DECK_TITLE}}" not in html

out.write_text(html, encoding="utf-8")
print(f"OK: {out} ({out.stat().st_size} bytes)")
```

## Validación final
- [ ] `Modulo-N/deck_N.html` existe
- [ ] No quedan placeholders sin reemplazar
- [ ] Abre en el navegador y muestra la primera slide correctamente
