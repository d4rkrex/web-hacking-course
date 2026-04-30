# Curso de Web Hacking

Material de un curso de Web Hacking de **5 módulos**, cada uno dictado como una clase de **3 horas con receso de 20 minutos**.

## Estructura

```
Curso_web_hacking/
├── AGENTS.md                  # convenciones del repo (auto-cargado por Copilot CLI)
├── .copilot/skills/           # skills reusables para preparar módulos
├── templates/                 # esqueletos del deck, herramientas y notas
└── Modulo-N/
    ├── mds/                   # material crudo
    ├── pdfs/                  # PDFs originales
    ├── deck_N.md              # presentación lista para convertir a HTML
    ├── herramientas_modulo_N.md
    └── notas_para_el_profe.md
```

## Cómo preparar un módulo

Desde la raíz del repo, dentro de Copilot CLI:

```
preparar el módulo N
```

Esto invoca el skill `prep-module` que:
1. Lee todos los `.md` dentro de `Modulo-N/mds/`
2. Genera `deck_N.md` (presentación slide-por-slide)
3. Genera `herramientas_modulo_N.md` (inventario de herramientas)
4. Genera `notas_para_el_profe.md` (guía interna)

Skills individuales también disponibles:
- `build-deck` — solo el deck
- `build-tools-list` — solo herramientas
- `build-instructor-notes` — solo las notas

## Filosofía del curso

- **Teoría enseñada a través de demos guiadas en vivo**, no labs silenciosos.
- El profesor ejecuta, los alumnos razonan y proponen mientras la herramienta corre.
- **Labs y desafíos** del material → se convierten en **demos guiadas** en clase.
- **Proyecto integrador** → queda como **tarea para casa**.

Reglas detalladas en [`AGENTS.md`](./AGENTS.md).
