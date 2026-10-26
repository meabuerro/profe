#!/usr/bin/env python3
"""Servidor local de Profe.

Sirve la aplicación en un puerto libre de localhost y abre el navegador
predeterminado. Sin dependencias externas: solo biblioteca estándar.

Uso:
    python3 scripts/profe_server.py [--port 8000] [--no-browser] [--host 127.0.0.1]
"""

from __future__ import annotations

import argparse
import http.server
import pathlib
import socket
import sys
import threading
import webbrowser

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA_JS = RAIZ / "data" / "app-data.js"


def asegurar_datos() -> None:
    """Regenera el catálogo embebido si falta o si algún fichero de datos es más reciente."""
    fuentes = [RAIZ / "data" / "etapas.json", RAIZ / "data" / "competencias-clave.json",
               RAIZ / "data" / "ccaa-index.json"]
    fuentes += list((RAIZ / "data" / "materias").glob("*.json"))
    fuentes += list((RAIZ / "data" / "ccaa").glob("*.json"))

    if DATA_JS.exists():
        generado = DATA_JS.stat().st_mtime
        if all(f.exists() and f.stat().st_mtime <= generado for f in fuentes):
            return

    try:
        sys.path.insert(0, str(RAIZ / "scripts"))
        import build_app  # noqa: WPS433 (import local intencional)

        build_app.main()
    except Exception as exc:  # pragma: no cover - aviso no bloqueante
        print(f"Aviso: no se pudo regenerar data/app-data.js ({exc}).", file=sys.stderr)


def puerto_libre(inicial: int, host: str, intentos: int = 25) -> int:
    for offset in range(intentos):
        puerto = inicial + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, puerto))
            except OSError:
                continue
        return puerto
    raise SystemExit(f"No hay puertos libres entre {inicial} y {inicial + intentos - 1}.")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def log_message(self, fmt, *args):  # silencia el log por petición
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sirve la app Profe en localhost.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if not (RAIZ / "index.html").exists():
        print("No se encuentra index.html en la raíz del repositorio.", file=sys.stderr)
        return 1

    asegurar_datos()
    puerto = puerto_libre(args.port, args.host)
    url = f"http://localhost:{puerto}/"

    servidor = http.server.ThreadingHTTPServer((args.host, puerto), Handler)

    print("")
    print("  Profe · programación docente LOMLOE")
    print(f"  {url}")
    print("  Ctrl+C para detener el servidor.")
    print("", flush=True)

    def abrir_navegador():
        try:
            webbrowser.open(url)
        except Exception as exc:  # pragma: no cover - depende del escritorio
            print(f"No se pudo abrir el navegador ({exc}). Abre {url} manualmente.", file=sys.stderr)

    if not args.no_browser:
        threading.Timer(0.4, abrir_navegador).start()

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
