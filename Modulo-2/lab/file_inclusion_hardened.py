#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse


BASE_DIR = Path(__file__).resolve().parent
WEBROOT = BASE_DIR / "webroot"
PAGES_DIR = WEBROOT / "pages"
SECRETS_DIR = BASE_DIR / "secrets"
HOST = "127.0.0.1"
DEFAULT_PORT = 8001


def ensure_demo_files() -> None:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)

    (PAGES_DIR / "home.html").write_text(
        """<h2>Home</h2>
<p>Esta es la pagina segura del laboratorio.</p>
<p>La aplicacion solo sirve archivos ubicados dentro de <code>webroot/pages/</code>.</p>
""",
        encoding="utf-8",
    )
    (PAGES_DIR / "help.html").write_text(
        """<h2>Ayuda</h2>
<p>Probá con <code>?file=pages/help.html</code> o <code>?file=help.html</code>.</p>
<p>Las rutas relativas fuera de <code>pages/</code> deben ser rechazadas.</p>
""",
        encoding="utf-8",
    )
    (SECRETS_DIR / "db_password.txt").write_text(
        "DB_PASSWORD=super-secreto-demo-123\n",
        encoding="utf-8",
    )
    (BASE_DIR / "notas_internas.txt").write_text(
        "Estas notas existen para demostrar que el hardened no las expone.\n",
        encoding="utf-8",
    )


def render_page(selected_file: str, content: str, status: str) -> bytes:
    examples = [
        "pages/home.html",
        "help.html",
        "../notas_internas.txt",
        "../secrets/db_password.txt",
    ]
    links = "".join(
        f'<li><a href="/?file={quote(item)}">{html.escape(item)}</a></li>'
        for item in examples
    )
    body = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>File Inclusion Hardened</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.5; }}
    code, pre {{ background: #f4f4f4; padding: 0.2rem 0.4rem; }}
    pre {{ padding: 1rem; overflow-x: auto; }}
    .ok {{ color: #166534; }}
    .warn {{ color: #991b1b; }}
  </style>
</head>
<body>
  <h1>Laboratorio hardened — File Inclusion</h1>
  <p class="{'ok' if status == 'OK' else 'warn'}">Estado: <strong>{html.escape(status)}</strong></p>
  <p>Archivo solicitado: <code>{html.escape(selected_file)}</code></p>
  <p>La app normaliza la ruta y solo permite archivos dentro de <code>webroot/pages/</code>.</p>

  <h3>Ejemplos</h3>
  <ul>{links}</ul>

  <h3>Resultado</h3>
  <pre>{html.escape(content)}</pre>
</body>
</html>
"""
    return body.encode("utf-8")


def resolve_allowed_path(raw_value: str) -> Path:
    requested = raw_value.removeprefix("pages/")
    candidate = (PAGES_DIR / requested).resolve()
    candidate.relative_to(PAGES_DIR.resolve())
    return candidate


class FileInclusionHardenedHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        selected_file = query.get("file", ["pages/home.html"])[0]

        try:
            target_path = resolve_allowed_path(selected_file)
            content = target_path.read_text(encoding="utf-8", errors="replace")
            payload = render_page(selected_file, content, "OK")
            self.send_response(200)
        except ValueError:
            payload = render_page(
                selected_file,
                "ERROR: Ruta fuera del directorio permitido.",
                "BLOCKED",
            )
            self.send_response(403)
        except FileNotFoundError:
            payload = render_page(
                selected_file,
                "ERROR: El archivo solicitado no existe dentro de webroot/pages/.",
                "NOT FOUND",
            )
            self.send_response(404)

        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        print(f"[{self.address_string()}] {format % args}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lab hardened de file inclusion/path traversal")
    parser.add_argument("--host", default=HOST, help="Host a bindear")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Puerto HTTP")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_demo_files()
    server = HTTPServer((args.host, args.port), FileInclusionHardenedHandler)
    print(f"Lab hardened listo en http://{args.host}:{args.port}")
    print(f"Ejemplo legitimo:  http://{args.host}:{args.port}/?file=pages/home.html")
    print(f"Traversal bloqueado: http://{args.host}:{args.port}/?file=../secrets/db_password.txt")
    server.serve_forever()


if __name__ == "__main__":
    main()
