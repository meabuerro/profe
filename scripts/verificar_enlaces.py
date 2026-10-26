#!/usr/bin/env python3
"""Comprueba que los enlaces oficiales de las fichas autonómicas responden.

Uso:
    python3 scripts/verificar_enlaces.py            # comprueba enlaces de CCAA
    python3 scripts/verificar_enlaces.py --offline   # solo valida el formato

Sin red, el script no falla: informa de que no se pudo comprobar.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CCAA = RAIZ / "data" / "ccaa"

CABECERAS = {"User-Agent": "Mozilla/5.0 (compatible; Profe/2.0; verificacion de enlaces)"}


def estado(url: str) -> int | None:
    """Devuelve el código HTTP final, o None si no hay respuesta."""
    peticion = urllib.request.Request(url, headers=CABECERAS)
    try:
        with urllib.request.urlopen(peticion, timeout=25) as respuesta:
            return respuesta.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="no hacer peticiones de red")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    fallos = 0
    for ruta in sorted(CCAA.glob("*.json")):
        ficha = json.loads(ruta.read_text(encoding="utf-8"))
        nombre = ficha.get("nombre", ruta.stem)
        enlaces = ficha.get("enlaces_oficiales", {})
        if not enlaces:
            print(f"· {nombre}: sin enlaces")
            fallos += 1
            continue
        for clave, url in enlaces.items():
            if not url.startswith("https://"):
                print(f"✗ {nombre} [{clave}]: no es https → {url}")
                fallos += 1
                continue
            if args.offline:
                print(f"· {nombre} [{clave}]: {url}")
                continue
            codigo = estado(url)
            if codigo is None or codigo >= 400:
                print(f"✗ {nombre} [{clave}]: {codigo or 'sin respuesta'} → {url}")
                fallos += 1
            else:
                print(f"✔ {nombre} [{clave}]: {codigo} → {url}")

    print(f"\n{fallos} problema(s) de enlaces." if fallos else "\nTodos los enlaces responden.")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
