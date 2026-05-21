# Burp Intruder — Tipos de Ataque

## Request de ejemplo

```http
username=§pos1§&password=§pos2§
```

Listas de payloads:
- **Lista 1:** `admin, root, test`
- **Lista 2:** `123, abc`

---

## Sniper — Una posición a la vez

Prueba cada payload en **una posición**, dejando la otra con su valor original.

| Request | pos1 | pos2 |
|---------|------|------|
| 1 | **admin** | (original) |
| 2 | **root** | (original) |
| 3 | **test** | (original) |
| 4 | (original) | **123** |
| 5 | (original) | **abc** |

**Uso:** Detectar cuál campo es vulnerable.  
**Total:** 5 requests.

---

## Battering Ram — Mismo payload en todas

Pone el **mismo valor** en todas las posiciones a la vez.

| Request | pos1 | pos2 |
|---------|------|------|
| 1 | **admin** | **admin** |
| 2 | **root** | **root** |
| 3 | **test** | **test** |

**Uso:** Cuando usuario = password (credenciales espejo).  
**Total:** 3 requests.

---

## Pitchfork — Listas en paralelo (1 a 1)

Avanza las listas **en sincronía**, par a par.

| Request | pos1 | pos2 |
|---------|------|------|
| 1 | **admin** | **123** |
| 2 | **root** | **abc** |

**Uso:** Tenés pares conocidos (user:pass de un leak).  
**Total:** 2 requests (se corta en la lista más corta).

---

## Cluster Bomb — Todas las combinaciones

Producto cartesiano: **cada payload × cada payload**.

| Request | pos1 | pos2 |
|---------|------|------|
| 1 | **admin** | **123** |
| 2 | **admin** | **abc** |
| 3 | **root** | **123** |
| 4 | **root** | **abc** |
| 5 | **test** | **123** |
| 6 | **test** | **abc** |

**Uso:** Brute force completo, blind SQLi (posición × carácter).  
**Total:** 3 × 2 = 6 requests.

---

## Resumen

| Tipo | Qué hace | Requests | Cuándo usar |
|------|----------|----------|-------------|
| **Sniper** | Una posición a la vez | N × posiciones | Fuzzing puntual |
| **Battering Ram** | Mismo en todas | N | user = password |
| **Pitchfork** | Par a par | min(lista1, lista2) | Pares conocidos |
| **Cluster Bomb** | Todas las combinaciones | N × M | Brute force total |
