# Curso de Web Hacking — Instrucciones del Proyecto

Este es un repositorio de material educativo para un curso de Web Hacking con 5 módulos. Contiene presentaciones (HTML/Markdown), comandos de referencia, labs prácticos, y una infraestructura VPS con targets vulnerables.

## Arquitectura del Proyecto

### Estructura de Módulos

```
Modulo-N/
├── deck_N.html              # Presentación interactiva (FUENTE DE VERDAD)
├── deck_N.md                # Versión markdown (debe estar sincronizada)
├── comandos_clase_N.md      # Comandos demostrados en clase
├── sitios_para_practicar.md # Labs online externos
├── lab/                     # Código de demos locales (Python, scripts)
├── mds/                     # Ejercicios, desafíos resueltos, notas
└── assets/                  # Imágenes y diagramas
```

### Infraestructura (`infra/`)

- **VPS**: Ubuntu 24.04 LTS en `92.113.34.149`
- **Stack**: Docker Compose + Caddy (reverse proxy con TLS automático)
- **Targets**: Juice Shop, DVWA, bWAPP accesibles vía HTTPS
- **Seguridad**: IP allowlist en Caddy + UFW + fail2ban

**Archivos clave**:
- `docker-compose.yml`: Definición de contenedores vulnerables
- `Caddyfile`: Configuración de reverse proxy e IP allowlist
- `manage_ips.py`: Script Python para gestionar IPs autorizadas
- `IP_ALLOWLIST.md`: Guía completa de gestión de acceso
- `README.md`: Documentación de setup y operación diaria

## Reglas del Proyecto

### Decks del Curso

- **Fuente de verdad**: Cuando existen `deck_N.html` y `deck_N.md`, **el HTML es canónico** salvo que el usuario indique lo contrario
- **Sincronización obligatoria**: Todo cambio en un deck debe reflejarse tanto en HTML como en MD
- **Contenido orientado al alumno**: Las slides priorizan contenido para el estudiante, no notas operativas del docente
- **Guiones extensos**: Los procedimientos detallados del profesor van en archivos separados (e.g., `notas_para_el_profe.md`) o resumidos

### Cierre Obligatorio de Cada Deck

Cada deck **debe** cerrar con estas tres partes, en este orden:

1. **Resumen de lo aprendido**: Bullets breves y concretos
2. **Próxima clase**: Temas que siguen
3. **Gracias / cierre**: Despedida breve

**Reglas adicionales**:
- La slide de **Gracias** debe ser una **lámina separada**, no fusionada con otras
- Si el bloque de cierre queda saturado, dividir en varias slides
- No comprimir resumen + próxima clase + gracias en una sola lámina

### Criterio Editorial

- Preferir ideas claras, comparativas y mensajes de cierre memorables
- Evitar slides que sean solo secuencias de pasos del profesor si no aportan valor directo al alumno
- Usar ejemplos visuales y comparaciones para conceptos complejos

## Operación de Infraestructura

### VPS — Acceso y Comandos

- **Preferencia**: Usar **SSH por defecto** para tareas en el VPS (antes que MCP/API)
- **Configuración**: Asumir que `~/.ssh/config` ya está configurado
- **Acceso**: `ssh root@92.113.34.149` (sin pasar credenciales manualmente)
- **Uso directo**: Inspección, cambios operativos, despliegues, logs, administración de contenedores

**Comandos comunes**:
```bash
# Levantar servicios
ssh root@92.113.34.149 'cd /opt/labs && docker compose up -d'

# Ver logs de un target específico
ssh root@92.113.34.149 'cd /opt/labs && docker compose logs -f juice-shop'

# Reset entre clases
ssh root@92.113.34.149 'cd /opt/labs && docker compose restart'

# Verificar estado
ssh root@92.113.34.149 'cd /opt/labs && docker compose ps'
```

### Gestión de IP Allowlist

**Script Python**: `infra/manage_ips.py` proporciona comandos para:
- Agregar/quitar IPs de alumnos
- Reemplazar IP del profesor
- Sincronizar Caddyfile al VPS

**Workflow típico**:
```bash
cd infra
./manage_ips.py add 190.123.45.67 "Alumno Juan"
./manage_ips.py sync  # Sube al VPS y recarga Caddy
```

**Alternativa manual**: Editar `infra/Caddyfile` directamente, luego:
```bash
scp -i ~/.ssh/id_ed25519 Caddyfile root@92.113.34.149:/etc/caddy/Caddyfile
ssh root@92.113.34.149 'caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy'
```

Ver `infra/IP_ALLOWLIST.md` para guía completa.

## Formato de Presentaciones

Las presentaciones HTML son **standalone** (CSS/JS inline, sin dependencias externas como Reveal.js). Usan:
- Vanilla JavaScript para navegación (flechas ← →)
- Grid CSS responsive
- Tema oscuro por defecto (modo claro disponible)
- Fuente: Inter (Google Fonts)

**Estructura HTML típica**:
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <title>Deck N · Módulo N · Clase N · Curso de Web Hacking</title>
    <style>/* CSS inline completo */</style>
</head>
<body>
    <div class="presentation">
        <section class="slide active">...</section>
        <section class="slide">...</section>
    </div>
    <script>/* JS navegación inline */</script>
</body>
</html>
```

## Duración y Formato de Clases

- **Duración**: Cada clase dura **2 horas**
- **Formato**: Teoría + demos guiadas en vivo
- **Estructura típica**: 60-70% teoría/demos, 20-30% práctica guiada, 10% cierre

## Tipos de Archivos

### Por módulo
- **Presentaciones**: `deck_N.html` (canónico), `deck_N.md` (sincronizado)
  - Nomenclatura: `deck_N_M.html` donde N=módulo, M=clase dentro del módulo
  - Ejemplo: `deck_2_1.html` = Módulo 2, Clase 1
- **Comandos**: `comandos_clase_N.md`, `comandos_SQL_SQLi.md`, `comandos_sqlmap.md`
- **Labs**: Directorio `lab/` con demos en Python (e.g., `file_inclusion_demo.py`)
- **Recursos**: `sitios_para_practicar.md`, `herramientas_modulo_N.md`
- **Ejercicios**: `mds/desafio_N.md`, `mds/lab_N.md`, variantes `_resolved`

### Infraestructura
- **Configuración**: `docker-compose.yml`, `Caddyfile`
- **Scripts**: `manage_ips.py`, `reset.sh`
- **Documentación**: `README.md`, `IP_ALLOWLIST.md`

## Convenciones

- **Idioma**: Todo el contenido está en español
- **Nomenclatura**: Archivos en `snake_case` (e.g., `comandos_clase_1.md`)
- **Versionado deck**: Usar `deck_N_M.html` para subdivisiones (e.g., `deck_1_2.html` = Módulo 1, Clase 2)
- **Labs resueltos**: Agregar sufijo `_resolved` (e.g., `desafio_1_resolved.md`)

## Recursos Externos

**Targets vulnerables hosteados**:
- OWASP Juice Shop: `https://juice.labs.manuel-roldan.cloud`
- DVWA: `https://dvwa.labs.manuel-roldan.cloud`
- bWAPP: `https://bwapp.labs.manuel-roldan.cloud`

**Labs públicos recomendados**: Ver `Modulo-N/sitios_para_practicar.md` en cada módulo

## Notas sobre Burp Suite en el Curso

**Cambio pedagógico importante**: Burp Suite se introduce en **Módulo 2, Clase 2** (adelantado desde M3 por demanda de los alumnos).

### Roadmap actualizado:
- **M2 Clase 1**: Command Injection, File Inclusion, CSRF, SQLi manual con DVWA, SQLMap
- **M2 Clase 2**: Introducción a Burp Suite (Proxy, Repeater, Intruder) + SQLi con Burp en WebGoat + Blind SQLi + Preview XSS
- **M2 Clase 3**: XSS profundo (Reflected, Stored, DOM), bypass de filtros, BeEF Framework
- **M3**: Burp avanzado (técnicas de explotación, extensiones, automatización con Python)

### Estructura de M2:
- `deck_2_1.html/.md`: Clase 1 (ya dictada, sin cambios)
- `deck_2_2.html/.md`: **Reestructurada** - Burp intro + SQLi con Burp
- `deck_2_3.html/.md`: **Nueva** - XSS profundo (contenido que salió de deck_2_2_old)
- `deck_2_2_old.html/.md`: Backup del deck original antes de la reestructuración
