#!/usr/bin/env python3
"""Genera las capturas de pantalla del README.

    python3 scripts/capturas.py                # todas, en docs/img/
    python3 scripts/capturas.py --solo panel   # una sola
    python3 scripts/capturas.py --ancho 1280 --alto 800 --dpr 2

Usa Chrome (o Chromium) en modo headless, igual que tests/run_ui.py, y la página
de apoyo scripts/capturas.html, que rellena un expediente de ejemplo. Las
imágenes se guardan en docs/img/ y se pueden reconstruir en cualquier momento.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parent.parent

CANDIDATOS_CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]

# Cada captura: nombre del fichero, parámetros de la vista y, si hace falta, un
# tamaño de ventana propio (la tabla de la programación anual pide más ancho).
CAPTURAS = [
    {"nombre": "panel", "params": {"vista": "panel"}},
    {"nombre": "catalogo", "params": {"vista": "catalogo"}},
    {"nombre": "anual", "params": {"vista": "anual"}},
    {"nombre": "situaciones", "params": {"vista": "situaciones"}},
    {"nombre": "documento", "params": {"vista": "documento"}},
]


def buscar_chrome() -> str | None:
    import os

    for ruta in CANDIDATOS_CHROME:
        if pathlib.Path(ruta).exists():
            return ruta
    for nombre in ("google-chrome", "chrome", "chromium", "chromium-browser"):
        encontrado = shutil.which(nombre)
        if encontrado:
            return encontrado
    return None


def puerto_libre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def asegurar_datos() -> None:
    data_js = RAIZ / "data" / "app-data.js"
    fuentes = [RAIZ / "data" / "etapas.json", RAIZ / "data" / "ccaa-index.json"]
    fuentes += list((RAIZ / "data" / "materias").glob("*.json"))
    if data_js.exists() and all(f.stat().st_mtime <= data_js.stat().st_mtime for f in fuentes):
        return
    sys.path.insert(0, str(RAIZ / "scripts"))
    import build_app

    build_app.main()


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera las capturas del README.")
    parser.add_argument("--ancho", type=int, default=1440)
    parser.add_argument("--alto", type=int, default=900)
    parser.add_argument("--dpr", type=float, default=2.0, help="factor de escala (2 = retina)")
    parser.add_argument("--salida", default="docs/img")
    parser.add_argument("--solo", nargs="*", help="nombres de captura a generar")
    parser.add_argument("--espera", type=int, default=20000, help="presupuesto de tiempo virtual (ms)")
    args = parser.parse_args()

    chrome = buscar_chrome()
    if not chrome:
        print("No se encontró Chrome ni Chromium: no se pueden generar las capturas.")
        return 2

    destino = RAIZ / args.salida
    destino.mkdir(parents=True, exist_ok=True)

    asegurar_datos()

    sys.path.insert(0, str(RAIZ / "scripts"))
    import profe_server

    puerto = puerto_libre()
    servidor = profe_server.http.server.ThreadingHTTPServer(("127.0.0.1", puerto), profe_server.Handler)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()

    pendientes = [c for c in CAPTURAS if not args.solo or c["nombre"] in args.solo]
    fallos = 0

    try:
        for captura in pendientes:
            nombre = captura["nombre"]
            params = captura["params"]
            ancho = captura.get("ancho", args.ancho)
            alto = captura.get("alto", args.alto)
            url = f"http://127.0.0.1:{puerto}/scripts/capturas.html?" + urllib.parse.urlencode(params)
            salida = destino / f"{nombre}.png"
            perfil = tempfile.mkdtemp(prefix="profe-captura-")
            comando = [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-first-run",
                "--disable-extensions",
                "--hide-scrollbars",
                "--force-device-scale-factor=" + str(args.dpr),
                f"--window-size={ancho},{alto}",
                f"--virtual-time-budget={args.espera}",
                f"--user-data-dir={perfil}",
                f"--screenshot={salida}",
                url,
            ]
            try:
                subprocess.run(comando, capture_output=True, timeout=180)
            except subprocess.TimeoutExpired:
                print(f"  FALLO {nombre}: tiempo de espera agotado")
                fallos += 1
                shutil.rmtree(perfil, ignore_errors=True)
                continue
            finally:
                shutil.rmtree(perfil, ignore_errors=True)

            if salida.exists() and salida.stat().st_size > 10_000:
                print(f"  ok    {nombre:<12} {salida.relative_to(RAIZ)} - {salida.stat().st_size // 1024} KB")
            else:
                print(f"  FALLO {nombre}: no se generó la imagen")
                fallos += 1
    finally:
        servidor.shutdown()
        servidor.server_close()

    if fallos:
        print(f"\n{fallos} captura(s) sin generar.")
    else:
        print(f"\n{len(pendientes)} captura(s) en {args.salida}/")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
