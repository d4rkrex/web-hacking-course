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
DEFAULT_PORT = 8000


def ensure_demo_files() -> None:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)

    (PAGES_DIR / "home.html").write_text(
        """<h2>Home</h2>
<p>Esta es la pagina normal del laboratorio.</p>
<p>Probá con <code>?file=pages/home.html</code> y después con rutas relativas.</p>
""",
        encoding="utf-8",
    )
    (PAGES_DIR / "help.html").write_text(
        """<h2>Ayuda</h2>
<p>El parametro vulnerable es <code>file</code>.</p>
<p>Ejemplo legitimo: <code>?file=pages/help.html</code></p>
""",
        encoding="utf-8",
    )
    (SECRETS_DIR / "db_password.txt").write_text(
        "DB_PASSWORD=super-secreto-demo-123\n",
        encoding="utf-8",
    )
    (BASE_DIR / "notas_internas.txt").write_text(
        "Estas notas no deberian ser accesibles desde la app web.\n",
        encoding="utf-8",
    )


def render_page(selected_file: str, content: str) -> bytes:
    examples = [
        "pages/home.html",
        "pages/help.html",
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
  <title>File Inclusion Demo</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.5; }}
    code, pre {{ background: #f4f4f4; padding: 0.2rem 0.4rem; }}
    pre {{ padding: 1rem; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>Laboratorio vulnerable — File Inclusion</h1>
  <p>Archivo solicitado: <code>{html.escape(selected_file)}</code></p>
  <p>La app concatena el valor de <code>file</code> a <code>webroot/</code> sin validar traversal.</p>

  <h3>Ejemplos</h3>
  <ul>{links}</ul>

  <h3>Contenido devuelto</h3>
  <pre>{html.escape(content)}</pre>
 </body>
</html>
"""
    return body.encode("utf-8")


class FileInclusionHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        selected_file = query.get("file", ["pages/home.html"])[0]

        try:
            # Vulnerabilidad intencional: toma la ruta relativa sin normalizar ni restringir.
            target_path = WEBROOT / selected_file
            content = target_path.read_text(encoding="utf-8", errors="replace")
            payload = render_page(selected_file, content)
            self.send_response(200)
        except FileNotFoundError:
            payload = render_page(
                selected_file,
                f"ERROR: No se encontro el archivo.\nRuta intentada: {(WEBROOT / selected_file)!s}",
            )
            self.send_response(404)

        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        print(f"[{self.address_string()}] {format % args}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lab vulnerable de file inclusion/path traversal")
    parser.add_argument("--host", default=HOST, help="Host a bindear")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Puerto HTTP")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_demo_files()
    server = HTTPServer((args.host, args.port), FileInclusionHandler)
    print(f"Lab listo en http://{args.host}:{args.port}")
    print(f"Ejemplo legitimo:  http://{args.host}:{args.port}/?file=pages/home.html")
    print(f"Traversal demo:    http://{args.host}:{args.port}/?file=../secrets/db_password.txt")
    server.serve_forever()


if __name__ == "__main__":
    main()
