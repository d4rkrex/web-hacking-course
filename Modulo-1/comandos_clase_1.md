# Comandos usados en Clase 1 — Módulo 1

Referencia rápida de los comandos ejecutados durante la clase con explicación de flags.

---

## 🔍 Reconocimiento pasivo

### dig — Consultas DNS

```bash
# Consulta básica: resuelve los registros A del dominio
dig educacionit.com

# Solo la IP (sin headers ni sección de autoridad)
dig +short educacionit.com
```

| Flag | Descripción |
|------|-------------|
| `+short` | Muestra solo la respuesta (sin secciones QUESTION, AUTHORITY, ADDITIONAL) |
| `ANY` | Solicita todos los tipos de registro disponibles (A, MX, TXT, etc.) |

---

### curl + ipinfo.io — Geolocalización de IPs

```bash
# Averiguar a quién pertenece una IP (ASN, ISP, país, ciudad)
curl https://ipinfo.io/3.163.139.82
curl https://ipinfo.io/3.163.139.118
curl https://ipinfo.io/18.239.36.45
curl https://ipinfo.io/54.207.106.237
```


---

### theHarvester — Recolección de subdominios, emails y hosts

```bash

# Buscar en Google
theHarvester -d educacionit.com -b google

# Buscar en múltiples fuentes pasivas
theHarvester -d educacionit.com -b crtsh,dnsdumpster,duckduckgo,urlscan,hackertarget
```

| Flag | Descripción |
|------|-------------|
| `-d` | Dominio objetivo (target) |
| `-b` | Fuentes de datos a consultar (separadas por coma) |

**Fuentes usadas:**

| Fuente | Qué busca |
|--------|-----------|
| `crtsh` | Certificados SSL emitidos (Certificate Transparency logs) |
| `dnsdumpster` | Subdominios y registros DNS públicos |
| `duckduckgo` | Resultados de búsqueda (emails, subdominios) |
| `urlscan` | Escaneos web previos realizados por otros |
| `hackertarget` | Registros DNS y subdominios vía API pública |

---

## 🧪 Fingerprinting activo

### curl -I — Headers HTTP

```bash
# Obtener solo los headers de respuesta (HEAD request)
curl -I https://juice.labs.manuel-roldan.cloud
```

| Flag | Descripción |
|------|-------------|
| `-I` | Realiza un request HTTP HEAD (solo headers, no descarga el body) |
| `-s` | Modo silencioso (sin barra de progreso) |
| `-k` | Ignora errores de certificado SSL (útil en labs con certs autofirmados) |

---

### whatweb — Identificación de tecnologías

```bash
# Escaneo básico (nivel de agresividad 1, por defecto)
whatweb https://juice.labs.manuel-roldan.cloud

# Modo verbose: muestra detalles de cada plugin que matchea
whatweb -v https://juice.labs.manuel-roldan.cloud

# Agresividad nivel 3: hace requests adicionales para confirmar tecnologías
whatweb -a 3 https://juice.labs.manuel-roldan.cloud

# Agresividad nivel 4: máxima (más ruidoso, más requests)
whatweb -a 4 https://juice.labs.manuel-roldan.cloud
```

| Flag | Descripción |
|------|-------------|
| `-v` | Verbose — muestra detalle de cada plugin que detectó algo |
| `-a N` | Nivel de agresividad (1=pasivo/stealth, 3=agresivo, 4=heavy) |

**Niveles de agresividad:**

| Nivel | Comportamiento |
|-------|---------------|
| 1 (default) | Un solo request GET, analiza solo esa respuesta |
| 3 | Requests adicionales a paths comunes para confirmar tecnologías |
| 4 | Prueba todos los plugins agresivos (genera mucho tráfico) |

---

---


## 📝 Notas

- Todos los comandos activos (whatweb, gobuster, curl a nuestro lab) requieren autorización del dueño del target.
- Los comandos pasivos (dig, ipinfo, theHarvester con fuentes públicas) no tocan el target directamente.
- `educacionit.com` se usó como ejemplo de reconocimiento pasivo con autorización del instituto.
