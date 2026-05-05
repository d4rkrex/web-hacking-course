# Null Byte Injection (Poison Null Byte)

En C y lenguajes de bajo nivel, el carácter `\0` (null byte) marca el fin de un string. Cuando una aplicación web y el sistema de archivos interpretan un string de manera diferente, se produce una desconexión que puede ser explotada.

## El mecanismo

```
Solicitud: /ftp/package.json.bak%00.md
                                 ↑
            El sistema operativo lee hasta este punto y se detiene
```

1. La aplicacion web analiza el string completo: `package.json.bak%00.md` — determina que termina en `.md` y permite el acceso.
2. El filesystem recibe: `package.json.bak\0.md` — trunca en el null byte y abre `package.json.bak`.

## Codificacion en la URL

El null byte no puede enviarse directamente en una URL. Se utiliza doble encoding:

- `%25` es el carácter `%` codificado
- El servidor decodifica `%2500` en `%00`, y luego `%00` en `\0`

## Ejemplo practico

```bash
# Acceso directo - el servidor rechaza con 403 (extension no permitida)
curl -s https://juice.labs.manuel-roldan.cloud/ftp/package.json.bak

# Con null byte - el servidor permite el acceso (ve .md como extension)
curl -s "https://juice.labs.manuel-roldan.cloud/ftp/package.json.bak%2500.md"
```

Es una vulnerabilidad clasica de validacion de extensiones donde la verificacion de seguridad y el acceso al archivo operan con interpretaciones distintas del mismo string.
