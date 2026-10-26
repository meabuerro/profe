#!/usr/bin/env python3
"""Genera data/app-data.js con el catálogo curricular que consume la app Profe.

El catálogo se construye a partir de las fichas de data/materias/*.json, que
contienen el texto literal de los anexos del BOE (ver scripts/importar_boe.py)
y de las fichas autonómicas de data/ccaa/*.json.

- No usa red ni dependencias externas: solo la biblioteca estándar.
- El resultado se carga con <script src> para que la app funcione también con file://
"""

from __future__ import annotations

import json
import pathlib
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"

# Alias de ficheros de CCAA duplicados -> id canónico de ccaa-index.json
ALIAS_CCAA = {
    "castilla-mancha": "castilla-la-mancha",
    "comunidad-valenciana": "comunitat-valenciana",
    "pais-vasco": "pais-basco",
    "baleares": "islas-baleares",
    "rioja": "larioja",
}

NOTA_FICHA = (
    "El texto curricular de cada ficha es literal: procede del anexo II del real decreto "
    "indicado (BOE). El desarrollo autonómico puede ampliarlo o concretarlo; comprueba "
    "siempre la norma vigente de tu comunidad antes de entregar el documento."
)

# Áreas y materias que no se fijan en los reales decretos de enseñanzas mínimas.
SIN_DESARROLLO_ESTATAL = {
    "primaria": [{
        "nombre": "Religión",
        "nota": (
            "El currículo de la enseñanza de Religión no se establece en el Real Decreto "
            "157/2022: corresponde a la autoridad religiosa correspondiente y a la "
            "normativa de cada comunidad autónoma."
        ),
    }],
    "eso": [{
        "nombre": "Religión",
        "nota": (
            "El currículo de la enseñanza de Religión no se establece en el Real Decreto "
            "217/2022: corresponde a la autoridad religiosa correspondiente y a la "
            "normativa de cada comunidad autónoma."
        ),
    }],
    "bachillerato": [{
        "nombre": "Religión",
        "nota": (
            "El currículo de la enseñanza de Religión no se establece en el Real Decreto "
            "243/2022: corresponde a la autoridad religiosa correspondiente y a la "
            "normativa de cada comunidad autónoma."
        ),
    }],
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

MARCAS_MOJIBAKE = ("\u00c3", "\u00c2", "\u0192", "\u00e2\u20ac", "\ufffd")


def _residuos(text: str) -> int:
    """Cuenta los indicios de codificación rota que quedan en una cadena."""
    total = sum(text.count(marca) for marca in MARCAS_MOJIBAKE)
    total += sum(1 for c in text if 0x80 <= ord(c) <= 0x9F)
    return total


def _candidatos(text: str):
    """Genera decodificaciones alternativas aplicando 1, 2 y 3 pasadas."""
    vistos = {text}
    frontera = [text]
    for _ in range(3):
        siguientes = []
        for actual in frontera:
            for codec in ("cp1252", "latin-1"):
                try:
                    candidato = actual.encode(codec).decode("utf-8")
                except (UnicodeEncodeError, UnicodeDecodeError):
                    continue
                if candidato not in vistos:
                    vistos.add(candidato)
                    siguientes.append(candidato)
        if not siguientes:
            break
        yield from siguientes
        frontera = siguientes


def repair(value):
    """Deshace el doble/triple mojibake cp1252<->utf-8 de fichas antiguas."""
    if isinstance(value, dict):
        return {k: repair(v) for k, v in value.items()}
    if isinstance(value, list):
        return [repair(v) for v in value]
    if not isinstance(value, str):
        return value

    texto = unicodedata.normalize("NFC", value)
    if _residuos(texto) == 0:
        return texto

    mejor, peor = texto, _residuos(texto)
    for candidato in _candidatos(texto):
        puntuacion = _residuos(candidato)
        if puntuacion < peor or (puntuacion == peor and len(candidato) < len(mejor)):
            mejor, peor = candidato, puntuacion

    limpio = "".join(c for c in mejor if c != "\ufffd" and not (0x80 <= ord(c) <= 0x9F))
    return unicodedata.normalize("NFC", limpio)


def load_json(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as handle:
        return repair(json.load(handle))


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().replace(" ", "-")


# ---------------------------------------------------------------------------
# Fichas
# ---------------------------------------------------------------------------

def cargar_fichas() -> dict[str, list[dict]]:
    """Agrupa por etapa las fichas con texto literal del BOE (fuente verificable)."""
    por_etapa: dict[str, list[dict]] = {}
    for ruta in sorted((DATA / "materias").glob("*.json")):
        ficha = load_json(ruta)
        if not isinstance(ficha, dict) or not ficha.get("fuente"):
            continue
        if not ficha.get("id_etapa") or not ficha.get("nombre"):
            continue
        ficha["_origen"] = ruta.name
        por_etapa.setdefault(ficha["id_etapa"], []).append(ficha)
    for lista in por_etapa.values():
        lista.sort(key=lambda f: f["nombre"])
    return por_etapa


def resolver_remision(ficha: dict, etapa: list[dict]) -> dict:
    """Rellena una ficha que remite a otra materia (p. ej. Segunda Lengua Extranjera)."""
    if not ficha.get("remite_a"):
        return ficha
    destino = next((f for f in etapa if f["nombre"] == ficha["remite_a"]), None)
    if destino is None:
        return ficha
    return {
        **ficha,
        "competencias_especificas": destino.get("competencias_especificas", []),
        "ciclos": destino.get("ciclos", {}),
        "remision_resuelta": True,
    }


def entrada(ficha: dict) -> dict:
    return {
        "id": slug(ficha["nombre"]),
        "nombre": ficha["nombre"],
        "tieneFicha": True,
        "tipoFicha": "literal",
        "organizacion": ficha.get("organizacion"),
        "decreto": (ficha.get("fuente") or {}).get("norma"),
        "fuente": ficha.get("fuente"),
        "remiteA": ficha.get("remite_a"),
        "remisionTexto": ficha.get("remision_texto"),
        "competenciasEspecificas": ficha.get("competencias_especificas", []),
        "ciclos": ficha.get("ciclos", {}),
        "notas": ficha.get("notas", []),
        "origen": ficha.get("_origen"),
    }


def materias_de_etapa(etapa: str, fichas: list[dict]) -> list[dict]:
    lista = [entrada(resolver_remision(ficha, fichas)) for ficha in fichas]

    # En la ESO, Matemáticas se publica con dos variantes en cuarto curso.
    if etapa == "eso":
        comunes = [m for m in lista if m["nombre"] == "Matemáticas"]
        if comunes:
            base = comunes[0]
            variantes = {}
            for clave, nivel in base["ciclos"].items():
                if clave.endswith("4-eso") and clave != "4-eso":
                    variantes[clave] = nivel
            if variantes:
                lista.remove(base)
                lista.append({**base, "id": "matematicas",
                              "nombre": "Matemáticas (1.º a 3.º de ESO)",
                              "ciclos": {k: v for k, v in base["ciclos"].items()
                                         if k not in variantes}})
                for clave, nivel in variantes.items():
                    sufijo = clave.split("-")[1].upper()
                    nombre = f"Matemáticas {sufijo} (4.º de ESO)"
                    lista.append({**base,
                                  "id": slug(nombre),
                                  "nombre": nombre,
                                  "ciclos": {"4-eso": {**nivel, "etiqueta": "Cuarto curso"}}})

    for pendiente in SIN_DESARROLLO_ESTATAL.get(etapa, []):
        lista.append({
            "id": slug(pendiente["nombre"]),
            "nombre": pendiente["nombre"],
            "tieneFicha": False,
            "tipoFicha": "sin-desarrollo-estatal",
            "decreto": None,
            "fuente": None,
            "remiteA": None,
            "remisionTexto": None,
            "competenciasEspecificas": [],
            "ciclos": {},
            "notas": [pendiente["nota"]],
        })

    lista.sort(key=lambda m: m["nombre"])
    return lista


# ---------------------------------------------------------------------------
# Construcción
# ---------------------------------------------------------------------------

def build() -> dict:
    etapas_raw = load_json(DATA / "etapas.json")
    competencias_raw = load_json(DATA / "competencias-clave.json")
    ccaa_index = load_json(DATA / "ccaa-index.json")
    fichas = cargar_fichas()

    etapas = []
    for etapa in etapas_raw.get("etapas", []):
        etapas.append({
            "id": etapa.get("id"),
            "nombre": etapa.get("nombre"),
            "ciclos": etapa.get("ciclos", []),
            "terminologia": etapa.get("terminologia"),
            "decreto": etapa.get("decreto_estatal_referencia"),
            "notas": etapa.get("notas_etapa", []),
        })

    ccaa = []
    for item in ccaa_index.get("ccaa", []):
        cid = item.get("id_ccaa")
        detalle = None
        candidatos = [cid] + [k for k, v in ALIAS_CCAA.items() if v == cid]
        for nombre_fichero in candidatos:
            ruta = DATA / "ccaa" / f"{nombre_fichero}.json"
            if ruta.exists():
                detalle = load_json(ruta)
                break
        entry = {"id": cid, "nombre": item.get("nombre")}
        if detalle:
            entry["enlaces"] = detalle.get("enlaces_oficiales", {})
            entry["etapas"] = detalle.get("etapas", {})
            entry["notas"] = detalle.get("notas_generales", [])
            entry["fuente"] = detalle.get("fuente")
        ccaa.append(entry)
    ccaa.sort(key=lambda c: c["nombre"])

    materias = {etapa: materias_de_etapa(etapa, fichas.get(etapa, []))
                for etapa in ("infantil", "primaria", "eso", "bachillerato", "fp")}

    return {
        "version": "2.0.0",
        "generado": "build_app.py",
        "notaFicha": NOTA_FICHA,
        "etapas": etapas,
        "competenciasClave": competencias_raw.get("competencias_clave", []),
        "notasCompetencias": competencias_raw.get("notas", []),
        "ccaa": ccaa,
        "materias": materias,
        "fuente": "LOMLOE (LO 3/2020) y anexos II de los RD 95/2022, RD 157/2022, "
                  "RD 217/2022 y RD 243/2022, importados del texto consolidado del BOE.",
    }


def render(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return (
        "/* Generado por scripts/build_app.py — no editar a mano. */\n"
        f"window.PROFE_DATA = {payload};\n"
    )


def main(destino: pathlib.Path | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    destino = destino or (DATA / "app-data.js")
    destino.write_text(render(data), encoding="utf-8")

    total = sum(len(v) for v in data["materias"].values())
    con_ficha = sum(1 for v in data["materias"].values() for m in v if m["tieneFicha"])
    literales = sum(1 for v in data["materias"].values() for m in v if m["tipoFicha"] == "literal")
    print(f"app-data.js generado: {total} materias/áreas, {con_ficha} con ficha "
          f"({literales} literales del BOE), {len(data['ccaa'])} CCAA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
