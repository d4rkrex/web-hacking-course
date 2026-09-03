# Scripts NSE locales del curso

Este directorio guarda ejemplos simples para clase sin tocar `/usr/share/nmap/scripts/`.

## Archivos

- `http-security-headers-simple.nse`: revisa cabeceras HTTP/HTTPS basicas y muestra dos headers utiles para fingerprinting.
- `script.db`: ejemplo local de indice para mostrar como Nmap clasifica scripts.

## Uso rapido

```bash
nmap -Pn -p 80,443 --script ./Modulo-1/lab/nmap/scripts/http-security-headers-simple.nse <target>
```

El script reporta dos bloques:

- Cabeceras de seguridad presentes o ausentes
- Headers de fingerprinting como `Server` y `X-Powered-By`

Si copiás el script a la carpeta global de Nmap, luego actualizás el indice con:

```bash
nmap --script-updatedb
```