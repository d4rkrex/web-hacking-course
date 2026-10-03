# Fuzzing y enumeración — Gobuster vs dirsearch vs wfuzz

Referencia rápida de comandos útiles de fuzzing/enumeración, comparando las tres herramientas. Complementa `comandos_clase_2.md` (que cubre el uso básico de Gobuster dado en clase).

---

## 1. Brute-force básico de directorios/archivos

| Tool | Comando |
|---|---|
| Gobuster | `gobuster dir -u https://target.com -w wordlist.txt -t 50` |
| dirsearch | `dirsearch -u https://target.com -t 50` |
| wfuzz | `wfuzz -c -w wordlist.txt -t 50 --hc 404 https://target.com/FUZZ` |

## 2. Con extensiones (php, bak, config, etc.)

| Tool | Comando |
|---|---|
| Gobuster | `gobuster dir -u https://target.com -w wordlist.txt -x php,bak,txt,config` |
| dirsearch | `dirsearch -u https://target.com -e php,bak,txt,config` |
| wfuzz | `wfuzz -c -w wordlist.txt -z list,php-bak-txt-config --hc 404 https://target.com/FUZZ.FUZ2Z` |

## 3. Filtrar por status code / tamaño (truco SPA — ver demo Juice Shop en Clase 2)

| Tool | Comando |
|---|---|
| Gobuster | `gobuster dir -u https://target.com -w wordlist.txt -b 404,403 --exclude-length 9393` |
| dirsearch | `dirsearch -u https://target.com -i 200,301,500 --exclude-sizes 9393B` |
| wfuzz | `wfuzz -c -w wordlist.txt --hc 404,403 --hh 9393 https://target.com/FUZZ` |

`--hh` en wfuzz = "hide by HTML/response size" (equivalente a `--exclude-length`).

## 4. Enumeración de subdominios (DNS)

| Tool | Comando |
|---|---|
| Gobuster | `gobuster dns -d target.com -w subdomains.txt` |
| dirsearch | No hace DNS — no es su propósito |
| wfuzz | `wfuzz -c -w subdomains.txt --hc 404 -u https://FUZZ.target.com` (no resuelve DNS, solo arma el Host) |

## 5. Virtual host enumeration (mismo IP, distintos vhosts)

| Tool | Comando |
|---|---|
| Gobuster | `gobuster vhost -u https://target.com -w subdomains.txt --append-domain` |
| dirsearch | N/A |
| wfuzz | `wfuzz -c -w subdomains.txt --hc 404 -H "Host: FUZZ.target.com" https://target.com/` |

## 6. Fuzzing de parámetros GET

| Tool | Comando |
|---|---|
| Gobuster | `gobuster fuzz -u "https://target.com/search?q=FUZZ" -w wordlist.txt -mc 200` |
| dirsearch | N/A (no fuzzea parámetros, solo paths) |
| wfuzz | `wfuzz -c -w wordlist.txt --hc 404 "https://target.com/search?q=FUZZ"` |

## 7. Fuzzing de body POST (login, formularios)

| Tool | Comando |
|---|---|
| Gobuster | `gobuster fuzz -u https://target.com/login -m POST -b "user=admin&pass=FUZZ" -w passwords.txt -mc 200` |
| dirsearch | N/A |
| wfuzz | `wfuzz -c -w passwords.txt -d "user=admin&pass=FUZZ" --hc 403 https://target.com/login` |

## 8. Fuzzing de headers (ej. `X-Forwarded-For` para bypass de IP allowlist)

| Tool | Comando |
|---|---|
| Gobuster | `gobuster fuzz -u https://target.com -w ips.txt -H "X-Forwarded-For: FUZZ" -mc 200` |
| dirsearch | `dirsearch -u https://target.com -H "X-Forwarded-For: 127.0.0.1"` (header fijo, no fuzzea) |
| wfuzz | `wfuzz -c -w ips.txt -H "X-Forwarded-For: FUZZ" --hc 403 https://target.com` |

## 9. Dos payloads simultáneos (ej. usuario + password cruzados)

| Tool | Comando |
|---|---|
| Gobuster | N/A (no soporta multi-FUZZ) |
| dirsearch | N/A |
| wfuzz | `wfuzz -c -w users.txt -w passwords.txt -d "user=FUZZ&pass=FUZ2Z" --hc 403 https://target.com/login` |

## 10. Recursivo (bajar un nivel automáticamente a cada dir encontrado)

| Tool | Comando |
|---|---|
| Gobuster | No tiene flag nativo (hay que re-invocar manualmente sobre cada hallazgo) |
| dirsearch | `dirsearch -u https://target.com -r --recursion-depth 2` |
| wfuzz | No tiene recursión nativa |

## 11. Stealth / rate limiting (evitar tumbar el target o saltar un WAF)

| Tool | Comando |
|---|---|
| Gobuster | `gobuster dir -u https://target.com -w wordlist.txt -t 5 --delay 300ms --random-agent` |
| dirsearch | `dirsearch -u https://target.com -t 5 --delay 0.3 --random-agent` |
| wfuzz | `wfuzz -c -w wordlist.txt -t 5 -s 0.3 --hc 404 https://target.com/FUZZ` |

---

## Resumen de fortalezas

- **Gobuster** → rápido, DNS/vhost nativos, `fuzz` mode cubre headers/body en un pellizco. Débil en recursión y multi-wordlist.
- **dirsearch** → mejor UX para brute-force de paths puro (recursión nativa, reportes), pero no fuzzea parámetros/headers/body.
- **wfuzz** → el más flexible (multi-FUZZ, cualquier parte del request), a costa de sintaxis más verbosa y sin DNS/vhost nativo.
