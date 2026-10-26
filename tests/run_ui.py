#!/usr/bin/env python3
"""Ejecuta la auditoría de interfaz con Chrome headless.

    python3 tests/run_ui.py

Devuelve 0 si todas las comprobaciones pasan y 1 en caso contrario.
Requiere Google Chrome (o Chromium) instalado; si no lo encuentra, avisa y
sale con código 2 para no confundir "no se pudo ejecutar" con "falló".
"""

from __future__ import annotations

import os
import pathlib
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent

CANDIDATOS_CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


def buscar_chrome() -> str | None:
    for ruta in CANDIDATOS_CHROME:
        if ruta and pathlib.Path(ruta).exists():
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


def main() -> int:
    chrome = buscar_chrome()
    if not chrome:
        print("No se encontró Chrome ni Chromium: auditoría de interfaz omitida.")
        return 2

    sys.path.insert(0, str(RAIZ / "scripts"))
    import profe_server  # noqa: E402

    puerto = puerto_libre()
    servidor = profe_server.http.server.ThreadingHTTPServer(("127.0.0.1", puerto), profe_server.Handler)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    time.sleep(0.3)

    perfil = tempfile.mkdtemp(prefix="profe-chrome-")
    url = f"http://127.0.0.1:{puerto}/tests/ui.test.html"
    comando = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-first-run",
        "--disable-extensions",
        f"--user-data-dir={perfil}",
        "--virtual-time-budget=15000",
        "--dump-dom",
        url,
    ]

    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
        dom = resultado.stdout or ""
    except subprocess.TimeoutExpired:
        print("La auditoría agotó el tiempo de espera.")
        return 1
    finally:
        servidor.shutdown()
        servidor.server_close()
        shutil.rmtree(perfil, ignore_errors=True)

    coincidencia = re.search(r'<pre id="result">(.*?)</pre>', dom, re.S)
    if not coincidencia:
        print("No se pudo leer el resultado de la auditoría (¿falló la carga de la página?).")
        if resultado.stderr:
            print(resultado.stderr.strip()[:800])
        return 1

    import html as html_lib

    informe = html_lib.unescape(coincidencia.group(1)).strip()
    print(informe)

    if "SUMMARY" not in informe:
        return 1
    return 0 if re.search(r"SUMMARY \d+/\d+ OK", informe) else 1


if __name__ == "__main__":
    raise SystemExit(main())
