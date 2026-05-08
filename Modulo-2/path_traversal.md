# Path Traversal / File Inclusion — Apunte para alumno

## ¿Qué es Path Traversal?

Path Traversal es una vulnerabilidad en la que la aplicación toma una ruta controlada por el usuario y la usa para leer archivos del sistema.

El problema aparece cuando la app confía en algo como:

```python
open("pages/" + user_input)
```

o

```php
include($_GET['file']);
```

Si el usuario puede mandar secuencias como `../`, puede salir del directorio esperado y pedir otros archivos.

---

## Idea simple

La aplicación espera algo como:

```text
pages/home.html
```

Pero el atacante prueba algo como:

```text
../secrets/db_password.txt
```

Entonces el servidor deja de interpretar el valor como “una página válida” y pasa a interpretarlo como “una ruta del filesystem”.

---

## Ejemplos de explotación

### Traversal básico

```text
?page=../../../../etc/passwd
```

### Variante con otra forma de separación

```text
?page=....//....//....//etc/passwd
```

### URL encoding

```text
?page=..%2f..%2f..%2fetc%2fpasswd
```

### Doble encoding

```text
?page=..%252f..%252f..%252fetc%252fpasswd
```

---

## Archivos que suelen ser interesantes

| Tipo | Ejemplo |
|---|---|
| Linux | `/etc/passwd` |
| Variables del proceso | `/proc/self/environ` |
| Logs | `/var/log/apache2/access.log` |
| Configuración | `.env`, `config.php`, `settings.py` |
| Windows | `C:\Windows\win.ini` |

---

## ¿Qué impacto tiene?

- lectura de archivos sensibles,
- exposición de credenciales o secretos,
- acceso a configuración interna,
- obtención de rutas, usuarios y detalles del servidor,
- posible encadenamiento con otras vulnerabilidades.

En algunos casos, si la app además **incluye** o **ejecuta** archivos, el impacto puede crecer hasta ejecución de código.

---

## Diferencia entre Path Traversal y File Inclusion

- **Path Traversal**: la app permite leer archivos fuera del directorio previsto.
- **File Inclusion**: la app no solo lee, sino que también incluye/procesa el archivo como parte de la aplicación.

En la práctica, suelen explicarse juntos porque ambos parten de confiar en rutas controladas por el usuario.

---

## ¿Cómo se protege?

La defensa fuerte no es “bloquear `../`”.

La defensa fuerte es:

1. **No dejar que el usuario elija rutas reales**
2. **Usar allowlists**
3. **Normalizar y validar la ruta final**
4. **Mantener secretos fuera del webroot**
5. **Aplicar mínimo privilegio al proceso**

---

## Patrón inseguro

```python
target = webroot / user_input
content = target.read_text()
```

Ese código concatena la ruta y confía en el input del usuario.

---

## Patrón más seguro en Python

```python
from pathlib import Path

BASE_DIR = Path("/app/webroot/pages").resolve()

def safe_read(user_input: str) -> str:
    candidate = (BASE_DIR / user_input).resolve()
    candidate.relative_to(BASE_DIR)
    return candidate.read_text(encoding="utf-8")
```

### ¿Qué hace esto?

- `resolve()` convierte la ruta en su forma absoluta y normalizada
- `relative_to(BASE_DIR)` verifica que la ruta final siga dentro del directorio permitido

Si el usuario intenta salir con `../`, la validación falla.

---

## Mejor todavía: no usar rutas libres

En vez de aceptar:

```text
?file=../secrets/db_password.txt
```

conviene aceptar algo como:

```text
?page=home
```

y mapearlo internamente:

```python
allowed = {
    "home": "home.html",
    "help": "help.html",
}
```

Eso reduce muchísimo la superficie de ataque.

---

## Resumen

- Path Traversal ocurre cuando el usuario controla una ruta del sistema
- `../` permite salir del directorio esperado
- URL encoding puede ayudar a bypass de filtros débiles
- la mitigación buena usa **allowlist + normalización + validación de ruta final**

> La idea clave: el problema no es solo `../`; el problema es dejar que el usuario controle rutas reales del servidor.
