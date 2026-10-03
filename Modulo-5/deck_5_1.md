
# Deck 5_1 · Módulo 5 · Clase 1

---

# Defensa & Hardening
## Módulo 5 · Clase 1 · Última hora · Cierre del curso

> Curso de Web Hacking
> Duración: 1 hora (última hora de la Clase 5)
> Del ataque a la defensa — los mismos sistemas, otra perspectiva

### ¿Ahora que saben atacar, cómo protegerían su propia app?

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

### Regla de oro: el frontend NO es seguridad

- JavaScript se puede leer, modificar y saltear
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

## SSDLC y Shift-Left

La seguridad que llega al final sale cara:

| Fase sin seguridad | Consecuencia |
| --- | --- |
| Diseño solo arquitectura | Vulnerabilidades estructurales (BOLA, Mass Assignment) |
| Código que "funciona" | SQLi, XSS, secretos hardcodeados |
| Deploy "subir y rezar" | Sin hardening, secrets en texto plano |

> **Shift-left:** detectar una vulnerabilidad en diseño cuesta 10× menos que en producción.

```
Requisitos → Diseño → Código → Tests → Deploy → Monitor
  Threat     Secure    Code    SAST/  Hardening  SIEM /
  Model      Design   Review   DAST   Secrets    Alertas
```

Con agentes de IA generando código: si el prompt no pide seguridad, el código tampoco la tendrá.

---

## HTTP Security Headers

Headers HTTP en la **respuesta** del servidor: le dicen al navegador qué conductas están permitidas. Baratos de desplegar, fáciles de verificar.

| Header | Previene | Ejemplo |
| --- | --- | --- |
| Content-Security-Policy | XSS, carga insegura | `default-src 'self'` |
| Strict-Transport-Security | Downgrade a HTTP | `max-age=31536000` |
| X-Frame-Options | Clickjacking | `DENY` |
| X-Content-Type-Options | MIME sniffing | `nosniff` |
| Referrer-Policy | Fuga de URLs sensibles | `strict-origin-when-cross-origin` |
| Permissions-Policy | Abuso de APIs del navegador | `geolocation=()` |

**En Express:** `app.use(helmet())` aplica buena parte de esto con una línea.

---

## Validación de Datos: Allowlist vs Blocklist

El cliente ayuda a la UX; **el servidor decide**. Toda validación client-side puede ser bypaseada con Burp, curl o Postman.

- **Allowlist**: solo permito formatos, tamaños y valores esperados
- **Blocklist**: intento enumerar “cosas malas” conocidas — siempre llega tarde

Ejemplo seguro para username:

```regex
^[a-zA-Z0-9_]{3,20}$
```

La allowlist parte de un modelo explícito de negocio.

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

## CORS peligroso vs seguro

**Cross-Origin Resource Sharing** define cuándo el navegador permite requests cross-origin. Protege al navegador, no al backend frente a curl o Burp.

La config realmente peligrosa no es `Access-Control-Allow-Origin: *` (el browser bloquea `*` combinado con `credentials: 'include'`) — es **reflejar el `Origin` sin validarlo**:

```http
Access-Control-Allow-Origin: https://evil.com   ← refleja el Origin sin validar
Access-Control-Allow-Credentials: true           ← las cookies viajan
```

Con sesión activa en `banco.com`, `evil.com` puede leer datos reales del usuario.

**Seguro:**

```http
Access-Control-Allow-Origin: https://app.midominio.com
Vary: Origin
```

Nunca reflejes `Origin` sin validarlo contra una lista explícita.

---

## Gestión de Secretos

El problema del hardcoding: API keys en el repo, passwords en `.js` del frontend, connection strings en código fuente, secretos filtrados en logs o commits viejos.

> Si el secreto llega al navegador, dejó de ser secreto.

Buenas prácticas:
- Variables de entorno (`.env` fuera de git) o Vault / Secrets Manager
- Rotación periódica y acceso mínimo por servicio
- Nunca secretos en frontend, ejemplos, screenshots o logs

Seguridad madura = secretos cortos de vida y fáciles de rotar.

---

## WAF & Rate Limiting

**WAF — qué hace:** inspecciona tráfico HTTP, detecta patrones conocidos de SQLi/XSS/path traversal, frena scanners básicos.
**WAF — qué NO hace:** no corrige lógica de negocio, no reemplaza validación server-side. Es una capa adicional, no la solución.

**Rate limiting:** limita requests por IP, usuario, token o endpoint. Reduce brute force, scraping y abuso automatizado. Combinado con MFA baja muchísimo el riesgo en login.

```js
app.use('/login', rateLimit({ windowMs: 15 * 60 * 1000, max: 5 }))
```

---

## JWT Seguro

**Errores comunes:** `alg: none`, secreto HS256 débil, sin `exp`, sin validación de firma en el servidor, secreto hardcodeado en el frontend.

> En M4 explotamos estas debilidades. Ahora sabemos cómo cerrarlas.

**Cómo implementarlo bien:**

| Buena práctica | Por qué importa |
| --- | --- |
| RS256 en producción | La clave privada nunca sale del servidor |
| Secreto HS256 ≥ 32 bytes random | Resiste ataques de diccionario |
| Incluir `exp`, `iat`, `nbf` | Limita ventana de validez |
| Validar firma siempre en backend | No confiar en claims sin verificar |
| Rotar y revocar tokens | Cierra sesiones comprometidas |

---

## Autenticación Segura

**Hashing de contraseñas:**

| Algoritmo | ¿Seguro? | Problema |
| --- | --- | --- |
| MD5 / SHA-1 | ❌ | Roto, tablas rainbow |
| SHA-256 (solo) | ❌ | Rápido = crackeable con GPU |
| bcrypt / Argon2 | ✅ | Work factor configurable |

**Nunca** contraseñas en texto plano, MD5 ni SHA-1.

**Account lockout + MFA:**
- Limitar intentos fallidos por cuenta, con delay exponencial
- TOTP o WebAuthn/passkeys — SMS solo como último recurso

> Un atacante con la contraseña aún necesita el segundo factor.

---

## File Upload — Defensa

En M4 bypasseamos `getimagesize()`, magic bytes y extensiones. La defensa real requiere capas simultáneas:

| Control | Implementación |
| --- | --- |
| Renombrar archivo | UUID + extensión controlada |
| Almacenar fuera del webroot | `/var/uploads/` no `/public/` |
| Sin permisos de ejecución | `chmod 644` en uploads |
| Validar MIME real | `finfo_file()`, no `$_FILES['type']` |
| Allowlist de extensiones | Solo `.jpg`, `.png`, `.pdf` |
| Limitar tamaño | Evita DoS por storage |

**Principio:** el archivo nunca debe ser ejecutable ni accesible como código.

---

## Logging & Alertas

**Logear siempre:** intentos de login, cambios de contraseña/email, acciones administrativas, errores de validación, rate limit disparado.
**Nunca logear:** contraseñas, tokens/API keys completos, datos de tarjetas (PCI DSS), datos personales sensibles (GDPR).

> Un log con passwords es un segundo vector de compromiso.

**Alertas útiles:**

| Evento | Señal |
| --- | --- |
| 5+ logins fallidos / cuenta / minuto | Posible brute force |
| Login exitoso desde país nuevo | Anomalía geográfica |
| Exportación masiva de datos | Exfiltración potencial |
| Cambio de rol o privilegios | Revisión urgente |

**Herramientas:** ELK Stack, Grafana + Loki, Datadog, Splunk, CloudWatch

---

## Checklist del desarrollador seguro

- HTTPS en todos los entornos reales
- Security headers mínimos + cookies con `HttpOnly`, `Secure`, `SameSite`
- Validación server-side con allowlists + prepared statements en toda query
- Output encoding contextual + CSP donde aplique
- MFA para paneles y cuentas críticas + rate limiting en login
- File upload con validación estricta + dependencias actualizadas
- WAF como capa extra + logging y alertas útiles
- CORS con lista explícita + secrets fuera del código

---

## Resumen de lo aprendido

- **M1**: HTTP, requests, responses, cookies, sesiones
- **M2**: SQLi, XSS inicial, CSRF, Burp básico
- **M3**: recon activo, fuzzing, Burp avanzado
- **M4**: APIs, BOLA, JWT, file upload, Metasploit
- **M5**: hardening, headers, validación, secretos y defensa en profundidad

Ahora ya pueden pensar como atacante **y** como defensor.

---

## El ciclo no termina

No hay próxima clase — el curso termina, pero la práctica recién empieza:

- Nuevas vulnerabilidades aparecen cada año; los frameworks cambian, tus errores también
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/) para consultar patrones de defensa
- Hack The Box, TryHackMe y labs propios (Juice Shop, DVWA, bWAPP) para seguir practicando
- Pentesting periódico y bug bounty aportan mirada externa y descubren regresiones
- Leer writeups, CVEs y postmortems reales — seguir CVEs evita quedar expuesto por dependencias

# La seguridad no es un estado.
### Es un proceso continuo.

---

## Gracias

### “La seguridad es responsabilidad de todos”

- Ahora saben atacar
- Úsenlo para defender mejor
- Piensen en controles antes del incidente
- Hagan de la seguridad un hábito de ingeniería
