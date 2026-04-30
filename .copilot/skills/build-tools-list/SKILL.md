# Skill: build-tools-list

## Cuándo invocar
Cuando el usuario pida una lista / inventario de herramientas usadas en un módulo, o "las herramientas del módulo N".

## Objetivo
Generar `Modulo-N/herramientas_modulo_N.md` con todas las herramientas mencionadas en el material del módulo, agrupadas por categoría funcional.

## Inputs requeridos
- `N` (número del módulo). Si no es claro, preguntar.
- Todos los `.md` dentro de `Modulo-N/mds/`.
- `templates/herramientas.template.md` como esqueleto.

## Procedimiento

### 1. Extraer herramientas
Recorrer todos los mds del módulo y detectar:
- CLIs mencionadas (ej. `whatweb`, `nmap`, `gobuster`, `nikto`, `wfuzz`, `dirsearch`, `sqlmap`, `burp`, etc.)
- Extensiones de navegador (Wappalyzer, FoxyProxy, etc.)
- Apps web / frameworks (OWASP Threat Dragon, Juice Shop, DVWA, etc.)
- Wordlists referenciadas (con su path si aparece)
- Marcos teóricos (OWASP Top 10, STRIDE, DREAD, Proactive Controls, etc.)

### 2. Agrupar por categoría funcional

Categorías sugeridas (usar las que apliquen al módulo):
- Reconocimiento e identificación de tecnologías
- Enumeración (directorios, archivos, subdominios)
- Auditoría de servidor web y configuración
- Inyecciones (SQLi, XSS, etc.)
- Interceptación / proxies
- Modelado de amenazas
- Recursos y wordlists
- Targets de prácticas
- Referencias / marcos teóricos

### 3. Para cada herramienta documentar

```markdown
### NombreHerramienta
- **Tipo**: CLI / extensión / app web / etc.
- **Uso**: para qué sirve en el contexto del módulo
- **Detecta por / características**: criterios técnicos relevantes
- **Comandos clave**: extraídos LITERALMENTE de los mds (no inventar)
- **Cuándo usar**: criterio de selección frente a alternativas
```

### 4. Reglas

- **No inventar comandos** que no estén en los mds. Si una herramienta se menciona pero no hay comando, listar solo nombre y uso.
- **Citar comandos exactamente** como aparecen, incluyendo flags y rutas.
- Incluir wordlists con su **ubicación** si aparece en los mds (ej. `/usr/share/wordlists/dirbuster/...`).
- Incluir **target principal** del módulo (ej. `juice-shop.herokuapp.com`).
- Incluir **marcos teóricos** referenciados (OWASP Top 10, STRIDE, etc.) con una línea descriptiva.

### 5. Output

Escribir en `Modulo-N/herramientas_modulo_N.md` siguiendo `templates/herramientas.template.md`.

## Validación final
- [ ] Existe `Modulo-N/herramientas_modulo_N.md`
- [ ] Toda herramienta mencionada en los mds aparece listada
- [ ] Comandos extraídos son literales del material
- [ ] Hay sección de wordlists, target y marcos teóricos
- [ ] Agrupación por categoría es coherente
