# Deck — Clase 2 · Módulo 1

> Curso de Web Hacking
> Duración: 3 horas (con pausa intermedia)
> Formato: teoría + práctica intercaladas (demos guiadas)

---


# Web Hacking
## Módulo 1 — Clase 2
### Enumeración avanzada y descubrimiento de vulnerabilidades

---

## Recap: Clase 1

- Arquitectura web: cliente-servidor, proxies, CDN
- Triada CIA, autenticación vs autorización
- HTTP: request/response, métodos, códigos, headers de seguridad
- HTTPS y TLS handshake
- Fingerprinting con WhatWeb y Wappalyzer
- Reconocimiento pasivo: Google Dorks, dig, whois, theHarvester
- Pasivo vs Activo: cuándo necesitás autorización

---

## Agenda de hoy

1. Enumeración de directorios con Gobuster
2. Correlación de fuentes y enumeración avanzada
3. Nmap en profundidad + scripts NSE
4. Descubrimiento de rutas ocultas y sensibles
5. Burp Suite: intercept, HTTP history y Repeater
6. Nikto: escaneo automatizado de vulnerabilidades

---

## Enumeración: el concepto

**Enumeración** = descubrir recursos no listados mediante fuerza bruta controlada.

Ingredientes:
1. **Wordlist**: diccionario de paths/archivos posibles
2. **Herramienta**: que pruebe cada palabra contra el servidor
3. **Interpretación**: filtrar falsos positivos, analizar códigos de respuesta

---

## ¿Qué buscamos con enumeración?

- `/admin`, `/panel`, `/dashboard` → paneles de administración
- `/api/internal/`, `/api/debug/` → endpoints internos expuestos
- `/backup.zip`, `/db.sql`, `.env` → backups y configs
- `/server-status`, `/phpinfo.php` → info del servidor
- `/logs/`, `/debug/` → archivos de log expuestos
- `.git/`, `.svn/` → repositorios de código fuente

---

## Gobuster

Herramienta escrita en Go. Rápida, multithreaded, simple.

**Modos principales:**

| Modo | Uso |
|---|---|
| `dir` | Enumerar directorios y archivos |
| `dns` | Enumerar subdominios |
| `vhost` | Enumerar virtual hosts |

---

## Gobuster — Comando típico

```bash
gobuster dir \
  -u https://target.com \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -t 50 \
  -x php,txt,bak
```

| Flag | Significado |
|---|---|
| `-u` | URL target |
| `-w` | Wordlist |
| `-t` | Threads (concurrencia) |
| `-x` | Extensiones a probar |

---

## Gobuster — Filtrado de resultados

```bash
gobuster dir -u https://target.com \
  -w wordlist.txt \
  --exclude-length 1234 \
  -b 404,403
```

| Flag | Significado |
|---|---|
| `--exclude-length` | Ignora respuestas con ese tamaño (falsos positivos) |
| `-b` | Excluir estos status codes |
| `-s` | Solo mostrar estos status codes |

Clave: si la app devuelve siempre 200 con un body genérico, filtrar por tamaño.

---

## Otras herramientas de enumeración

**Wfuzz** — Más flexible, permite fuzzear cualquier parte del request:

```bash
wfuzz -c -w wordlist.txt --hc 404 https://target.com/FUZZ
```

Puede fuzzear headers, parámetros, cookies, no solo paths.

**Dirsearch** — Alternativa en Python, amigable:

```bash
dirsearch -u https://target.com -e php,html,js
```

Hoy nos enfocamos en Gobuster. Las otras las van a encontrar en el campo.

---

## 🧪 Demo 2: Gobuster contra Juice Shop

**Target:** `https://juice.labs.manuel-roldan.cloud`

**Objetivo:** Descubrir rutas ocultas que no aparecen en la navegación normal.

---

## 🧪 Primer intento

```bash
gobuster dir \
  -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

**Problema:** Juice Shop es una SPA (Single Page Application).
Todas las rutas devuelven **200 OK** con el mismo HTML del frontend.

¿Cómo distinguimos paths reales de falsos positivos?

---

## 💡 El truco: --exclude-length

```bash
gobuster dir \
  -u https://juice.labs.manuel-roldan.cloud \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  --exclude-length 75055
```

El body genérico de la SPA tiene siempre **75055 bytes**.
Excluimos ese tamaño → solo vemos respuestas reales del backend.

---

## 🧪 Hallazgos

| Path | Status | Análisis |
|---|---|---|
| `/ftp` | 200 OK | Directorio público con archivos de configuración |
| `/api` | 500 | El backend existe y responde distinto |
| `/profile` | 500 | Endpoint que espera autenticación |
| `/redirect` | 500 | Excepción no manejada → posible open redirect |

---

## 🧪 Discusión con la clase

```qa-accordion
Q: ¿Qué significa un 500 vs un 404?
A: 404 = no existe. 500 = existe pero crasheó → input no esperado.
A: Un 500 es más interesante que un 404.

Q: ¿Por qué `/ftp` es crítico?
A: Es un directorio accesible sin auth con archivos sensibles.
A: Posible fuga de credenciales, configs, backups.

Q: ¿Qué investigamos después?
A: Navegar `/ftp` manualmente.
A: Probar `/api` con diferentes métodos.
A: Buscar documentación de la API.
```

---

## Nmap: detección de servicios

```bash
nmap -sV <target>
```

El flag `-sV` envía probes específicos para identificar el **servicio y versión** detrás de cada puerto abierto.

No es un simple port scan: interroga activamente al servicio.

---

## Nmap: un comando más útil en la práctica

```bash
nmap -Pn -sV -sC -p 80,443,8080 --open <target>
```

| Flag | Qué hace |
|---|---|
| `-Pn` | Asume que el host está activo aunque no responda a ping |
| `-sV` | Detecta servicio y versión |
| `-sC` | Ejecuta scripts NSE por defecto |
| `-p` | Limita el scan a los puertos que te interesan |
| `--open` | Muestra solo puertos abiertos |

Para una **primera pasada web**, este comando ya te da puertos abiertos, versiones y chequeos básicos.

---

## NSE: qué es y dónde está

**NSE** = **Nmap Scripting Engine**.

Son scripts en **Lua** que extienden Nmap para hacer enumeración, validaciones y detecciones más específicas.

- Ubicación típica de los scripts: `/usr/share/nmap/scripts/`
- Índice de scripts: `/usr/share/nmap/scripts/script.db`
- Si agregás scripts nuevos: `nmap --script-updatedb`

---

## NSE: ejemplo práctico

```bash
nmap -Pn -sV -p 443 \
    --script=http-headers,http-methods,ssl-cert,ssl-enum-ciphers \
    <target>
```

Con este comando le pedís a Nmap que, además de detectar el servicio, use NSE para revisar:

- Headers HTTP
- Métodos HTTP permitidos
- Certificado TLS
- Cifrados soportados

---

## NSE: script propio en Lua

Un script NSE propio revisa en una sola pasada:

- Cabeceras de seguridad
- `Server`
- `X-Powered-By`

Está en el material de la clase:

`Modulo-1/lab/nmap/scripts/http-security-headers-simple.nse`

```bash
nmap -Pn -p 80,443 \
    --script Modulo-1/lab/nmap/scripts/http-security-headers-simple.nse \
    <target>
```

Se corre igual que cualquier script del core de Nmap: en vez de apuntar a uno de `/usr/share/nmap/scripts/`, apuntás a tu propio `.nse`. Sirve para automatizar cualquier chequeo repetitivo que armes vos mismo.

---

## Nmap: interpretación de puertos

| Puerto | Significado |
|---|---|
| 80/443 abiertos | Superficie web clásica |
| 22 (SSH) | Acceso administrativo potencial |
| 3306 (MySQL) | Base de datos expuesta (riesgo crítico) |
| 8080/8443 | Apps alternativas o paneles internos |

---

## Nmap: interpretación de riesgo

Tres señales de alerta:

- **Servicio innecesario expuesto** → superficie de ataque ampliada
- **Servicio con versión antigua** → vulnerabilidades conocidas
- **Servicio administrativo expuesto** → riesgo crítico

---

## Nmap: ejemplos concretos

| Hallazgo | Implicación |
|---|---|
| OpenSSH 7.x en sistema moderno | Versión desactualizada, CVEs públicos |
| HTTP Proxy abierto | Abuso como relay, pivoting |
| FTP sin cifrado | Credenciales viajan en texto plano |
| MySQL sin filtro de IP | Acceso directo a la base de datos |

---

## 🧪 Demo 3: Nmap + NSE contra Juice Shop

**Target:** `juice.labs.manuel-roldan.cloud`

Vamos a combinar detección de servicios con scripts NSE para extraer información detallada.

---

## 🧪 Demo 3: Comandos

```bash
# Detección de servicios y versiones
nmap -sV juice.labs.manuel-roldan.cloud

# Headers HTTP del servidor
nmap -sV --script=http-headers juice.labs.manuel-roldan.cloud

# Métodos HTTP permitidos
nmap --script=http-methods juice.labs.manuel-roldan.cloud

# Certificado SSL y cifrados soportados
nmap --script=ssl-cert,ssl-enum-ciphers -p 443 juice.labs.manuel-roldan.cloud
```

---

## 🧪 Demo 3: Discusión

- ¿Qué servicios ven corriendo?
- ¿Qué versiones reporta?
- ¿Qué información extra revelan los headers?
- ¿Cómo se relaciona con lo que encontramos con WhatWeb en la clase pasada?

---

## Correlación de fuentes

Tu meta no es "tener muchos datos", sino **responder preguntas estratégicas**.

Cruzar evidencia de múltiples herramientas para construir una imagen coherente del objetivo.

---

## ¿Qué nos dice cada fuente?

| Herramienta | Aporta |
|---|---|
| WhatWeb | Tecnología web (lenguaje, framework, CMS) |
| Nmap | Servicios de red (puertos, versiones) |
| Headers HTTP | Políticas de seguridad (o ausencia de ellas) |
| Rutas descubiertas | Funcionalidad real expuesta |

---

## Ejemplo de correlación

- **WhatWeb** detecta PHP + Apache
- **Nmap** encuentra puerto 8080 con Tomcat
- **Headers** muestran modo debug activo
- **Rutas** exponen `/manager` y `/status`

→ Múltiples aplicaciones con **niveles de hardening diferentes**

→ La pregunta clave: **¿Dónde está la mayor superficie de ataque?**

---

## Descubrimiento de rutas ocultas

¿Por qué existen rutas no documentadas?

- Endpoints legacy que nunca se eliminaron
- Features internas publicadas por error
- Entornos de staging expuestos
- APIs sin interfaz gráfica
- Funcionalidades deshabilitadas solo visualmente (el endpoint sigue activo)

---

## Impacto de las rutas ocultas

- No documentadas → no auditadas
- Sin controles de seguridad → acceso directo
- Menos testeadas → más bugs

Ejemplo crítico:

```
GET /api/v1/admin/users → 200 OK (sin autenticación)
```

→ Broken Access Control sin explotación compleja

---

## Rutas sensibles: categorías

| Categoría | Rutas típicas | Riesgo |
|---|---|---|
| Autenticación | `/login`, `/oauth`, `/reset-password` | Account takeover |
| Administración | `/admin`, `/manager`, `/dashboard` | Control total del sistema |
| Carga de archivos | `/upload`, `/import` | Remote code execution |
| Backups | `/backup`, `/dump`, `/old` | Exposición total de datos |
| Documentación | `/swagger`, `/api-docs` | Mapa completo de la API |

---

## Rutas sensibles: lo que revela la documentación

`/swagger` o `/api-docs` te da:

- Todos los endpoints disponibles
- Parámetros esperados
- Tipos de datos
- Validaciones (o falta de ellas)

Es el mapa del tesoro para un atacante.

---

## ☕ Pausa opcional

¿Quieren tomarse 5 minutos?

---

## 🔧 Burp Suite: el proxy que faltaba

`curl` nos sirvió hasta acá, pero tiene techo: no guarda historial, no compara requests, no reenvía con un clic.

**Burp Suite** es un proxy intermedio entre el browser y el servidor: ve, intercepta y te deja modificar cada request antes de que salga.

---

## Burp Suite: cómo se ubica

```
Browser → [Burp Proxy :8080] → Servidor
              ↑
      vos interceptás/modificás acá
```

Todo el tráfico HTTP/HTTPS pasa por el proxy antes de llegar al target. Para HTTPS, el browser tiene que confiar en el certificado CA de Burp.

---

## Burp Suite: setup rápido

| Paso | Acción |
|---|---|
| 1 | Burp Suite Community, Proxy escuchando en `127.0.0.1:8080` |
| 2 | Configurar el browser (o FoxyProxy) para usar ese proxy |
| 3 | Visitar `http://burp` para descargar el certificado CA |
| 4 | Importar el certificado como autoridad confiable en el browser |

Sin el certificado importado, HTTPS no funciona con Intercept activo.

---

## Burp Suite: módulos que usamos hoy

| Módulo | Para qué sirve |
|---|---|
| Proxy / Intercept | Pausa cada request antes de que salga, para editarlo a mano |
| HTTP history | Guarda todo el tráfico pasado, con request y response completos |
| Repeater | Reenvía un request modificado las veces que quieras, sin tocar el browser |
| Target / Site map | Arma automáticamente un mapa del sitio con lo que vas navegando |

**Intruder** (automatización de payloads) lo vemos en el Módulo 2.

---

## 🧪 Demo 4: Intercept en vivo contra Juice Shop

**Target:** `https://juice.labs.manuel-roldan.cloud`

Secuencia sugerida en vivo:
1. Activar Intercept
2. Hacer login en la UI con un usuario cualquiera
3. Pausar el request en Burp antes de que llegue al servidor
4. Mostrar el body: email + password viajando en JSON plano
5. Soltar el request (Forward) y ver la respuesta completa en HTTP history

---

## 🧪 Demo 5: de curl a Repeater

Clase pasada encontramos con `curl` que `/ftp/package.json.bak` da 403, pero con Null Byte (`%2500.md`) el servidor lo sirve igual (ver `NullByte.md`).

Repetimos el mismo hallazgo con Repeater, sin reescribir el comando cada vez:
1. Capturar en HTTP history el `GET` a `/ftp/package.json.bak`
2. Enviarlo a Repeater (clic derecho → *Send to Repeater*)
3. Editar la URL ahí mismo, agregando `%2500.md`
4. Reenviar con un clic y comparar las dos respuestas lado a lado

---

## 🧪 Discusión: ¿por qué no solo con curl?

```qa-accordion
Q: ¿Qué gana Repeater que curl no te da?
A: Historial visual, comparación lado a lado, no reescribir comandos.
A: Editás cualquier parte del request (headers, cookies, body) sin reconstruir la sintaxis a mano.

Q: ¿Para qué sirve ver el request crudo en Intercept?
A: Para ver exactamente qué manda el browser, sin asumir nada.
A: Muchas veces hay headers o cookies que agrega el frontend solo, no vos.

Q: ¿Dónde entra esto en el flujo de ataque?
A: Primero identificás el punto de interés con recon (Gobuster, Nmap, Nikto).
A: Después usás Burp para manipular ese punto con precisión.
```

---

## Burp Suite: gancho a Módulo 2

Todo lo que armaste hoy con Repeater (interceptar, editar, reenviar) es la base para lo que viene.

En el Módulo 2 vas a usar **Intruder** para automatizar el envío de payloads de SQL Injection sobre el mismo tipo de request que acabás de manipular a mano.

---

## 🧪 Demo 6: Nikto contra Juice Shop

**Nikto** es un escáner de vulnerabilidades web que busca configuraciones inseguras, archivos peligrosos y versiones conocidas.

```bash
nikto -h https://juice.labs.manuel-roldan.cloud
```

---

## 🧪 Demo 6: ¿Qué detecta Nikto?

- Archivos peligrosos expuestos
- Configuraciones inseguras
- Versiones con vulnerabilidades conocidas
- Rutas administrativas comunes
- Headers de seguridad faltantes

---

## 🧪 Demo 6: Interpretando resultados

| Hallazgo | Significado |
|---|---|
| Missing X-Content-Type-Options | Riesgo de MIME sniffing |
| Headers inusuales (x-recruiting, diagnostics) | Information disclosure |
| `/ftp/` accesible (200 OK desde robots.txt) | Exposición de archivos |
| Archivos .tgz, .pem, .jks, .war | Backups y certificados expuestos |
| Access-Control-Allow-Origin: * | CORS permisivo (cualquier origen) |

---

## 🧪 Demo 6: Discusión

¿Cuál es el hallazgo más crítico y por qué?

Criterios para priorizar:

- ¿Qué impacto tiene si se explota?
- ¿Qué tan fácil es de explotar?
- ¿Cuántos usuarios se ven afectados?

---

## Marco mental para vulnerabilidades

Una vulnerabilidad no es un bug aislado.

Es el **resultado de una decisión incorrecta** (o una decisión nunca tomada).

---

## Causas comunes de vulnerabilidades

- Validar solo en el cliente (el atacante usa curl)
- Confiar en parámetros que vienen del browser
- Separar autenticación de autorización
- Dejar configuraciones por defecto
- No actualizar dependencias

---

## Esquema de análisis: Condición → Acción → Impacto → Evidencia

Usalo como una **plantilla para explicar una vulnerabilidad**. No se refiere a un framework de desarrollo.

| Paso | Pregunta |
|---|---|
| Condición | ¿Qué está mal configurado o implementado? |
| Acción | ¿Qué puede hacer un atacante? |
| Impacto | ¿Qué consecuencia tiene? |
| Evidencia | ¿Cómo lo demostrás? |

---

## Esquema de análisis: ejemplo concreto

| Paso | Valor |
|---|---|
| Condición | Endpoint acepta ID arbitrario sin validar ownership |
| Acción | Cambiar `userId=1` por `userId=2` en el request |
| Impacto | Acceso a datos de otro usuario (violación de confidencialidad) |
| Evidencia | Request + response mostrando datos ajenos |

---

## OWASP Top 10 Web

Es la **lista de riesgos web más usada** para clasificar y comunicar hallazgos de seguridad.

---

## OWASP Top 10 Web: edición 2021

Es la **última edición completa publicada**. La vamos a usar como referencia base para clasificar hallazgos.

No es para memorizar.

Es un **marco mental** para:

- Clasificar hallazgos
- Justificar riesgo ante stakeholders
- Comunicar a gente no técnica
- Estructurar auditorías

---

## OWASP Top 10 Web 2021: mapeo práctico

Estas categorías siguen siendo la referencia más estable para trabajo práctico y reporte.

| Categoría OWASP | Se manifiesta como... |
|---|---|
| A01 - Control de acceso roto | IDOR, bypass de roles, acceso sin autenticación |
| A02 - Fallas criptográficas | HTTPS débil, datos sin cifrar, hashes rotos |
| A03 - Inyección | SQLi, command injection, XSS |
| A05 - Configuración insegura | Debug activo, headers faltantes, defaults |

---

## OWASP Top 10: cómo usarlo

Cuando encontrás algo, pensás:

1. ¿A qué categoría OWASP pertenece?
2. ¿Por qué? ¿Cuál es la causa raíz?
3. ¿Qué impacto describe OWASP para esa categoría?

Esto te permite **hablar el mismo idioma** que el equipo de desarrollo y management.

---

## OWASP Web Top 10: actualización 2025

Referencia visual para mostrar por dónde viene evolucionando la lista web de OWASP.

![OWASP Top 10 Web 2025](https://blog.secureflag.com/assets/images/owasp-top-ten-updates.png)

Tomalo como **update / preview** de la edición web. Para clase usamos **OWASP Top 10 Web 2021** porque sigue siendo la última edición completa publicada.

---

## Otras listas OWASP para tener en radar

| Lista | Última versión / edición |
|---|---|
| OWASP Top 10 Web | 2021 publicada · update 2025 en circulación |
| OWASP API Security Top 10 | 2023 |
| OWASP Mobile Top 10 | 2024 |
| OWASP Top 10 for LLM Applications | 2025 |

No hay una sola lista OWASP para todo. **Depende del tipo de sistema que estés evaluando**.

---

## Threat Modeling: ¿qué es?

Analizar **antes de atacar** (o antes de construir):

- ¿Qué activos protegemos?
- ¿Quién los quiere comprometer?
- ¿Por dónde podrían entrar?
- ¿Qué pasa si lo logran?

Si OWASP te ayuda a **clasificar lo que ya encontraste**, threat modeling te ayuda a **pensar lo que todavía no viste**.

---

## SDLC vs SSDLC (breve)

**SDLC clásico** aprueba el deploy si:
- La funcionalidad anda ✓
- Los tests pasan ✓
- El cliente acepta ✓

**SSDLC** bloquea el deploy si detecta:
- Passwords hasheados con MD5
- HTTP o TLS 1.0
- Credenciales hardcodeadas en el código
- Modo debug activo en producción

---

## SSDLC: seguridad en cada fase

```ssdlc-flow
```

La diferencia real: **la seguridad no aparece al final**. Se integra desde requirements hasta maintain.

---

## Security Gate

Un **security gate** es un punto de control obligatorio en el pipeline donde se validan requisitos de seguridad antes de avanzar.

Si no pasa → no se despliega.

No importa si "funciona perfecto".

---

## 📌 Proyecto integrador — Tarea para casa

**Etapa 1: Análisis Web Corporativo con Scripts NSE**

Target: `juice.labs.manuel-roldan.cloud`

---

## 📌 Tarea: Comandos a ejecutar

```bash
# Headers HTTP
nmap --script=http-headers -p 443 juice.labs.manuel-roldan.cloud

# Métodos HTTP permitidos
nmap --script=http-methods -p 443 juice.labs.manuel-roldan.cloud

# Certificado SSL y cifrados
nmap --script=ssl-cert,ssl-enum-ciphers -p 443 juice.labs.manuel-roldan.cloud
```

---

## 📌 Tarea: Entregable

**Reporte ejecutivo** que incluya:

- Hallazgos de cada script NSE
- Clasificación de riesgo (alto/medio/bajo)
- Mitigaciones propuestas para cada hallazgo
- Conclusión: ¿cuál es el estado general de seguridad del target?

---

## Recap del Módulo 1 completo

| Clase 1 | Clase 2 |
|---|---|
| Fundamentos HTTP | Correlación de fuentes |
| Fingerprinting (WhatWeb) | Nmap en profundidad + NSE |
| Enumeración (Gobuster) | Rutas ocultas y sensibles |
| Primera foto del target | Burp Suite: intercept + Repeater |
| — | Nikto, OWASP Top 10, Threat Modeling |

---

## Lo que llevás del Módulo 1

Ahora tenés el **marco mental completo** para la fase de reconocimiento:

1. Identificar tecnologías
2. Enumerar servicios y rutas
3. Manipular requests con Burp Suite (Proxy + Repeater)
4. Correlacionar hallazgos
5. Clasificar riesgos con OWASP
6. Modelar amenazas con STRIDE

---

## ¿Preguntas?

---

## ¡Gracias!

Nos vemos en el **Módulo 2**.

