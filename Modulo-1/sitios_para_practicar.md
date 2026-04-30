# Sitios para practicar Web Hacking

Listado de plataformas y aplicaciones vulnerables para práctica legal. Todos verificados y activos.

---

## 🌐 Plataformas online (no requieren instalación)

| Plataforma | URL | Descripción |
|-----------|-----|-------------|
| **PortSwigger Web Security Academy** | https://portswigger.net/web-security/all-labs | Labs gratuitos de los creadores de Burp Suite. Cubren todo OWASP Top 10 con labs guiados. **Recomendado.** |
| **PentesterLab** | https://pentesterlab.com | Ejercicios progresivos de web security. Algunos gratuitos, otros de pago. |
| **OWASP Juice Shop (online)** | https://juice-shop.herokuapp.com | Versión hosteada de Juice Shop (puede estar intermitente). |

---

## 🧪 Labs de prueba online (targets vulnerables legales)

| Sitio | URL | Tecnología | Qué practicar |
|-------|-----|-----------|---------------|
| **Acunetix testphp** | http://testphp.vulnweb.com | PHP | SQLi, XSS, File inclusion |
| **Acunetix testasp** | http://testasp.vulnweb.com | ASP | SQLi, XSS en foros |
| **AltoroMutual (IBM)** | https://demo.testfire.net | Java | SQLi, auth bypass, session hijacking |
| **Zero Bank** | http://zero.webappsecurity.com | Java | Auth flaws, IDOR, session mgmt |
| **Google Gruyere** | https://google-gruyere.appspot.com | Python | XSS, CSRF, path traversal |

> ⚠️ Estos sitios están diseñados para ser atacados. Solo usarlos con fines educativos.

---

## 🐳 Aplicaciones para instalar (Docker / local)

| App | Repo/Sitio | Tecnología | Nivel |
|-----|-----------|-----------|-------|
| **OWASP Juice Shop** | https://owasp.org/www-project-juice-shop/ | Node.js + Angular | Intermedio-Avanzado |
| **DVWA** | https://github.com/digininja/DVWA | PHP + MySQL | Principiante |
| **WebGoat** | https://owasp.org/www-project-webgoat/ | Java (Spring) | Principiante-Intermedio |
| **VAmPI** | https://github.com/erev0s/VAmPI | Python (Flask) | API Security |
| **DVNA** | https://github.com/appsecco/dvna | Node.js | Intermedio |
| **Mutillidae** | https://sourceforge.net/projects/mutillidae/ | PHP | Principiante |
| **WackoPicko** | https://github.com/adamdoupe/WackoPicko | PHP | Intermedio |
| **bWAPP** | http://www.itsecgames.com/ (descargar e instalar local) | PHP | Principiante |

### Instalación rápida con Docker:

```bash
# Juice Shop
docker run -d -p 3000:3000 bkimminich/juice-shop

# DVWA
docker run -d -p 8080:80 vulnerables/web-dvwa

# WebGoat
docker run -d -p 8888:8888 -p 9090:9090 webgoat/webgoat

# VAmPI
docker run -d -p 5000:5000 erev0s/vampi
```

---

## ☁️ Entornos avanzados (Cloud / Infra)

| Plataforma | URL | Enfoque |
|-----------|-----|---------|
| **CloudGoat** | https://github.com/RhinoSecurityLabs/cloudgoat | Pentesting AWS |
| **SamuraiWTF** | https://github.com/SamuraiWTF/samuraiwtf | VM completa para web pentesting |
| **OWASP BWA** | https://sourceforge.net/projects/owaspbwa/ | VM con múltiples apps vulnerables |
| **Metasploitable 2** | https://docs.rapid7.com/metasploit/metasploitable-2/ | VM general (red + web) |

---

## 📝 Recomendaciones para el curso

1. **Para empezar**: DVWA (nivel Low → Medium → High)
2. **Para la clase**: Juice Shop (nuestro lab en `juice.labs.manuel-roldan.cloud`)
3. **Para practicar solo**: PortSwigger Academy (labs guiados con solución)
4. **Para API Security**: VAmPI
5. **Para CTF/challenges**: Hack The Box, TryHackMe

---

> **Recordatorio legal**: Solo practicar en plataformas propias o que explícitamente autoricen pruebas de seguridad. Nunca contra sistemas de terceros sin autorización escrita.
