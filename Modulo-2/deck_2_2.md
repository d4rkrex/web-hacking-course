# Deck — Clase 2 · Módulo 2

> Curso de Web Hacking
> Duración: ~1h35m (segunda mitad de Clase 3, después de la pausa)
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

> Después de la pausa, seguimos con **Burp Suite** (ya lo usaron en Módulo 1 para interceptar y repetir requests con Proxy + Repeater) y SQLi con herramientas profesionales.

---

## De interceptar a explotar

Ya saben:
- Interceptar un request con **Proxy** y modificarlo antes de que salga
- Reenviarlo con variaciones usando **Repeater**
- Por qué Burp te da más control que `curl` para esto

Lo que falta:
- **Target**: definir el alcance (scope) de un análisis real
- **Intruder**: automatizar ataques — fuzzing, fuerza bruta — en vez de repetir a mano request por request
- Usar todo esto junto para explotar **SQLi de punta a punta**

**Burp Suite sigue siendo la navaja suiza del pentesting web.** Hoy aprendés a usar el resto de la navaja.

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **1** | Burp Suite: recap + Target (Scope) | ~15 min |
| 🧪 | Demo 1: Interceptar y modificar requests | ~15 min |
| **2** | SQLi con Burp en WebGoat | ~35 min |
| 🧪 | Demo 2: Blind SQLi con Intruder | ~20 min |
| **3** | Preview: XSS y próxima clase | ~10 min |

---

## Burp Suite: recap rápido

Ya instalaron Burp y configuraron el proxy en Módulo 1 — no lo repetimos.

- **Qué es:** plataforma de análisis de seguridad para explotación manual de apps web, actuando como intermediario entre navegador y servidor
- **Manual vs automático:** no "encuentra vulnerabilidades por sí solo" — facilita el razonamiento del analista. No es un botón mágico
- **Ya usado en M1:** Proxy (interceptar/modificar tráfico) + Repeater (reenviar con variaciones), con certificado CA instalado

Hoy sumamos **Target** e **Intruder** para llevarlo a explotación real.

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

## Tabs de Burp: panorama rápido

| Tab | ¿Ya la vimos? | Para qué sirve |
|-----|----------------|-----------------|
| **Dashboard** | — | Estado del proyecto; no hace falta tocarla hoy |
| **Proxy** | ✅ M1 | Interceptar y modificar tráfico HTTP/HTTPS |
| **Target** | 🆕 | Definir alcance (scope) de la prueba |
| **Repeater** | ✅ M1 | Reenviar requests manualmente con modificaciones |
| **Intruder** | 🆕 | Automatizar ataques controlados (fuzzing, fuerza bruta) |

Las que NO vamos a usar hoy (las veremos en M3): Decoder, Comparer, Extensions.

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

**Target de hoy:** WebGoat → SQL Injection (Intro y Advanced)

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
- **Target** define el scope; **Proxy** y **Repeater** ya los usábamos de M1, **Intruder** automatiza ataques
- SQLi con Burp: Repeater para payloads manuales, Intruder para blind SQLi
- Blind SQLi boolean y time-based: extraer datos sin output directo
- XSS es el siguiente tema (lo profundizamos próxima clase)

---

## Próxima clase

Próxima clase: XSS a fondo (Reflected/Stored/DOM) + BeEF Framework, y después APIs modernas (BOLA, JWT, Mass Assignment, File Upload, Metasploit).

---

## Gracias

**¿Preguntas?**

Recuerden practicar en WebGoat y DVWA.

Burp Suite es una herramienta **que se aprende usándola**.

Nos vemos la próxima clase 🚀
