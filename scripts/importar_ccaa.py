#!/usr/bin/env python3
"""Genera las fichas autonómicas de data/ccaa/*.json con la normativa vigente.

Cada ficha recoge, por etapa, la norma autonómica que desarrolla el currículo
LOMLOE, su boletín oficial y el portal donde comprobarla. El campo `estado`
indica el grado de comprobación de cada referencia:

    verificado   consta en el portal oficial de la consejería o en el boletín
    contrastado  consta en dos repertorios independientes, pendiente de portal
    consultar    solo se dispone del portal oficial; hay que confirmar la norma

Uso:
    python3 scripts/importar_ccaa.py            # escribe las 19 fichas
    python3 scripts/importar_ccaa.py --resumen   # solo informa
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "data" / "ccaa"

PORTAL = "https://www.juntadeandalucia.es/boja"

# ---------------------------------------------------------------------------
# Tabla de normativa. Cada etapa: (norma, fecha, boletín, estado, observaciones)
# ---------------------------------------------------------------------------

CCAA = {
    "andalucia": {
        "nombre": "Andalucía",
        "enlaces": {"boletin": "https://www.juntadeandalucia.es/boja"},
        "etapas": {
            "infantil": ("Decreto 100/2023, de 9 de mayo", "BOJA", "verificado", ""),
            "primaria": ("Decreto 101/2023, de 9 de mayo", "BOJA", "verificado",
                         "Desarrollado por la Orden de 30 de mayo de 2023."),
            "eso": ("Decreto 102/2023, de 9 de mayo", "BOJA", "verificado",
                    "Desarrollado por la Orden de 30 de mayo de 2023."),
            "bachillerato": ("Decreto 103/2023, de 9 de mayo", "BOJA", "verificado",
                             "Desarrollado por la Orden de 30 de mayo de 2023."),
        },
    },
    "aragon": {
        "nombre": "Aragón",
        "enlaces": {"curriculo": "https://educa.aragon.es/-/desarrollo-curricular"},
        "etapas": {
            "infantil": ("Orden ECD/853/2022, de 13 de junio", "BOA", "verificado", ""),
            "primaria": ("Orden ECD/1112/2022, de 18 de julio", "BOA", "verificado", ""),
            "eso": ("Orden ECD/1172/2022, de 2 de agosto", "BOA", "contrastado", ""),
            "bachillerato": ("Orden ECD/1173/2022, de 3 de agosto", "BOA", "contrastado", ""),
        },
    },
    "asturias": {
        "nombre": "Principado de Asturias",
        "enlaces": {"curriculo": "https://www.educastur.es"},
        "etapas": {
            "infantil": ("Decreto 56/2022, de 5 de agosto", "BOPA", "verificado", ""),
            "primaria": ("Decreto 57/2022, de 5 de agosto", "BOPA", "contrastado", ""),
            "eso": ("Decreto 59/2022, de 30 de agosto", "BOPA", "verificado", ""),
            "bachillerato": ("Decreto 60/2022, de 30 de agosto", "BOPA", "verificado", ""),
        },
    },
    "islas-baleares": {
        "nombre": "Illes Balears",
        "enlaces": {"curriculo": "https://caib.es/sites/lomloe/ca/"},
        "etapas": {
            "infantil": ("Decret 40/2025, d'1 d'agost", "BOIB", "verificado", ""),
            "primaria": ("Decret 41/2025, d'1 d'agost", "BOIB", "verificado", ""),
            "eso": ("Decret 42/2025, d'1 d'agost", "BOIB", "verificado", ""),
            "bachillerato": ("Decret 43/2025, d'1 d'agost", "BOIB", "verificado", ""),
        },
    },
    "canarias": {
        "nombre": "Canarias",
        "enlaces": {"curriculo": "https://www.gobiernodecanarias.org/educacion/web/"},
        "etapas": {
            "infantil": ("Decreto 196/2022, de 13 de octubre", "BOC", "verificado", ""),
            "primaria": ("Decreto 211/2022, de 10 de noviembre", "BOC", "contrastado", ""),
            "eso": ("Decreto 30/2023, de 16 de marzo", "BOC", "contrastado",
                    "Regula conjuntamente la ESO y el Bachillerato."),
            "bachillerato": ("Decreto 30/2023, de 16 de marzo", "BOC", "contrastado",
                             "Regula conjuntamente la ESO y el Bachillerato."),
        },
    },
    "cantabria": {
        "nombre": "Cantabria",
        "enlaces": {"curriculo": "https://www.educantabria.es/informacion-general/normativa"},
        "etapas": {
            "infantil": ("Decreto 66/2022, de 7 de julio", "BOC", "verificado",
                         "Regula conjuntamente Infantil y Primaria."),
            "primaria": ("Decreto 66/2022, de 7 de julio", "BOC", "verificado",
                         "Regula conjuntamente Infantil y Primaria."),
            "eso": ("Decreto 73/2022, de 27 de julio", "BOC", "verificado",
                    "Regula conjuntamente ESO y Bachillerato."),
            "bachillerato": ("Decreto 73/2022, de 27 de julio", "BOC", "verificado",
                             "Regula conjuntamente ESO y Bachillerato."),
        },
    },
    "castilla-leon": {
        "nombre": "Castilla y León",
        "enlaces": {"curriculo": "https://www.educa.jcyl.es"},
        "etapas": {
            "infantil": ("Decreto 37/2022, de 29 de septiembre", "BOCYL", "verificado", ""),
            "primaria": ("Decreto 38/2022, de 29 de septiembre", "BOCYL", "verificado", ""),
            "eso": ("Decreto 39/2022, de 29 de septiembre", "BOCYL", "verificado", ""),
            "bachillerato": ("Decreto 40/2022, de 29 de septiembre", "BOCYL", "verificado", ""),
        },
    },
    "castilla-la-mancha": {
        "nombre": "Castilla-La Mancha",
        "enlaces": {"curriculo": "https://educacion.castillalamancha.es"},
        "etapas": {
            "infantil": ("Decreto 80/2022, de 12 de julio", "DOCM", "verificado", ""),
            "primaria": ("Decreto 81/2022, de 12 de julio", "DOCM", "verificado", ""),
            "eso": ("Decreto 82/2022, de 12 de julio", "DOCM", "contrastado", ""),
            "bachillerato": ("Decreto 83/2022, de 12 de julio", "DOCM", "verificado", ""),
        },
    },
    "catalunya": {
        "nombre": "Cataluña",
        "enlaces": {"curriculo": "https://projectes.xtec.cat/nou-curriculum/"},
        "etapas": {
            "infantil": ("Decret 21/2023, de 7 de febrer", "DOGC", "contrastado", ""),
            "primaria": ("Decret 175/2022, de 27 de setembre", "DOGC", "verificado",
                         "Ordena els ensenyaments de l'educació bàsica."),
            "eso": ("Decret 175/2022, de 27 de setembre", "DOGC", "verificado",
                    "Ordena els ensenyaments de l'educació bàsica."),
            "bachillerato": ("Decret 171/2022, de 20 de setembre", "DOGC", "verificado", ""),
        },
    },
    "comunitat-valenciana": {
        "nombre": "Comunitat Valenciana",
        "enlaces": {"curriculo": "https://ceice.gva.es/es/web/ordenacion-academica"},
        "etapas": {
            "infantil": ("Decret 100/2022, de 29 de juliol", "DOGV", "verificado", ""),
            "primaria": ("Decret 106/2022, de 5 d'agost", "DOGV", "verificado",
                         "Modificado por el Decret 96/2026, de 19 de juny."),
            "eso": ("Decret 107/2022, de 5 d'agost", "DOGV", "contrastado", ""),
            "bachillerato": ("Decret 108/2022, de 5 d'agost", "DOGV", "contrastado", ""),
        },
    },
    "extremadura": {
        "nombre": "Extremadura",
        "enlaces": {"curriculo": "https://www.educarex.es/sistema-educativo/curriculum-educacion.html"},
        "etapas": {
            "infantil": ("Decreto 98/2022, de 20 de julio", "DOE", "verificado", ""),
            "primaria": ("Decreto 107/2022, de 28 de julio", "DOE", "verificado", ""),
            "eso": ("Decreto 110/2022, de 22 de agosto", "DOE", "verificado", ""),
            "bachillerato": ("Decreto 109/2022, de 22 de agosto", "DOE", "verificado", ""),
        },
    },
    "galicia": {
        "nombre": "Galicia",
        "enlaces": {"curriculo": "https://www.edu.xunta.gal/portal/"},
        "etapas": {
            "infantil": ("Decreto 150/2022, do 8 de setembro", "DOG", "verificado", ""),
            "primaria": ("Decreto 155/2022, do 15 de setembro", "DOG", "verificado", ""),
            "eso": ("Decreto 156/2022, do 15 de setembro", "DOG", "contrastado", ""),
            "bachillerato": ("Decreto 157/2022, do 15 de setembro", "DOG", "verificado", ""),
        },
    },
    "larioja": {
        "nombre": "La Rioja",
        "enlaces": {"curriculo": "https://www.larioja.org/edu-orden-academica/en/accesos-directos/repositorio-curriculo-lomloe"},
        "etapas": {
            "infantil": ("Decreto 36/2022, de 29 de junio", "BOR", "verificado", ""),
            "primaria": ("Decreto 41/2022, de 13 de julio", "BOR", "contrastado", ""),
            "eso": ("Decreto 42/2022, de 13 de julio", "BOR", "contrastado", ""),
            "bachillerato": ("Decreto 43/2022, de 21 de julio", "BOR", "contrastado", ""),
        },
    },
    "madrid": {
        "nombre": "Comunidad de Madrid",
        "enlaces": {"curriculo": "https://www.comunidad.madrid/servicios/educacion"},
        "etapas": {
            "infantil": ("Decreto 36/2022, de 8 de junio", "BOCM", "contrastado", ""),
            "primaria": ("Decreto 61/2022, de 13 de julio", "BOCM", "contrastado", ""),
            "eso": ("Decreto 65/2022, de 20 de julio", "BOCM", "contrastado", ""),
            "bachillerato": ("Decreto 64/2022, de 20 de julio", "BOCM", "contrastado", ""),
        },
    },
    "murcia": {
        "nombre": "Región de Murcia",
        "enlaces": {"curriculo": "https://www.educarm.es"},
        "etapas": {
            "infantil": ("Decreto 196/2022, de 3 de noviembre", "BORM", "contrastado", ""),
            "primaria": ("Decreto 209/2022, de 17 de noviembre", "BORM", "contrastado", ""),
            "eso": ("Decreto 235/2022, de 7 de diciembre", "BORM", "contrastado", ""),
            "bachillerato": ("Decreto 251/2022, de 22 de diciembre", "BORM", "contrastado", ""),
        },
    },
    "navarra": {
        "nombre": "Comunidad Foral de Navarra",
        "enlaces": {"curriculo": "https://www.educacion.navarra.es"},
        "etapas": {
            "infantil": ("Decreto foral 61/2022, de 1 de junio", "BON", "contrastado", ""),
            "primaria": ("Decreto foral 67/2022, de 22 de junio", "BON", "contrastado", ""),
            "eso": ("Decreto foral 71/2022, de 29 de junio", "BON", "contrastado", ""),
            "bachillerato": ("Decreto foral 72/2022, de 29 de junio", "BON", "contrastado", ""),
        },
    },
    "pais-basco": {
        "nombre": "País Vasco",
        "enlaces": {"curriculo": "https://www.euskadi.eus/educacion/"},
        "etapas": {
            "infantil": ("Decreto 75/2023, de 30 de mayo", "BOPV", "contrastado", ""),
            "primaria": ("Decreto 77/2023, de 30 de mayo", "BOPV", "contrastado",
                         "Establece el currículo de la Educación Básica (Primaria y ESO)."),
            "eso": ("Decreto 77/2023, de 30 de mayo", "BOPV", "contrastado",
                    "Establece el currículo de la Educación Básica (Primaria y ESO)."),
            "bachillerato": ("Decreto 76/2023, de 30 de mayo", "BOPV", "contrastado", ""),
        },
    },
    "ceuta": {
        "nombre": "Ciudad Autónoma de Ceuta",
        "enlaces": {"curriculo": "https://www.ceuta.es/ceuta/educacion"},
        "etapas": {
            "infantil": ("Orden EFP/608/2022, de 29 de junio", "BOE", "contrastado",
                         "Ámbito de gestión del Ministerio de Educación."),
            "primaria": ("Orden EFP/678/2022, de 15 de julio", "BOE", "verificado",
                         "Ámbito de gestión del Ministerio de Educación."),
            "eso": ("Orden EFP/754/2022, de 28 de julio", "BOE", "verificado",
                    "Ámbito de gestión del Ministerio de Educación."),
            "bachillerato": ("Orden EFP/755/2022, de 31 de julio", "BOE", "verificado",
                             "Ámbito de gestión del Ministerio de Educación."),
        },
    },
    "melilla": {
        "nombre": "Ciudad Autónoma de Melilla",
        "enlaces": {"curriculo": "https://www.melilla.es"},
        "etapas": {
            "infantil": ("Orden EFP/608/2022, de 29 de junio", "BOE", "contrastado",
                         "Ámbito de gestión del Ministerio de Educación."),
            "primaria": ("Orden EFP/678/2022, de 15 de julio", "BOE", "verificado",
                         "Ámbito de gestión del Ministerio de Educación."),
            "eso": ("Orden EFP/754/2022, de 28 de julio", "BOE", "verificado",
                    "Ámbito de gestión del Ministerio de Educación."),
            "bachillerato": ("Orden EFP/755/2022, de 31 de julio", "BOE", "verificado",
                             "Ámbito de gestión del Ministerio de Educación."),
        },
    },
}

NOTAS_ESTADO = {
    "verificado": "Referencia comprobada en el portal oficial de la consejería o en el boletín.",
    "contrastado": (
        "Referencia contrastada en repertorios normativos; confirma el número y la fecha "
        "en el boletín oficial antes de citarla en un documento."
    ),
    "consultar": "Comprueba la norma vigente en el portal oficial de tu comunidad.",
}


def construir(clave: str, datos: dict) -> dict:
    hoy = dt.date.today().isoformat()
    etapas = {}
    for etapa, (norma, boletin, estado, observaciones) in datos["etapas"].items():
        etapas[etapa] = {
            "decreto_referencia": norma,
            "boletin": boletin,
            "estado": estado,
            "observaciones": observaciones or "",
        }
    return {
        "id_ccaa": clave,
        "nombre": datos["nombre"],
        "fuente": {
            "consultado": hoy,
            "nota": "Normativa autonómica de desarrollo del currículo LOMLOE.",
        },
        "enlaces_oficiales": datos["enlaces"],
        "etapas": etapas,
        "notas_generales": [
            "La norma autonómica desarrolla y concreta el currículo estatal; prevalece "
            "en lo que amplía o especifica.",
            "Comprueba siempre la vigencia y las modificaciones posteriores en el "
            "boletín oficial de tu comunidad.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resumen", action="store_true")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    DESTINO.mkdir(parents=True, exist_ok=True)
    estados = {"verificado": 0, "contrastado": 0, "consultar": 0}
    for clave, datos in CCAA.items():
        ficha = construir(clave, datos)
        for etapa in ficha["etapas"].values():
            estados[etapa["estado"]] = estados.get(etapa["estado"], 0) + 1
        if args.resumen:
            print(f"{ficha['nombre']}: {len(ficha['etapas'])} etapas")
            for etapa, valor in ficha["etapas"].items():
                print(f"  - {etapa}: {valor['decreto_referencia']} ({valor['estado']})")
        else:
            ruta = DESTINO / f"{clave}.json"
            ruta.write_text(json.dumps(ficha, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")

    print(f"{len(CCAA)} fichas autonómicas · etapas verificadas: {estados['verificado']}, "
          f"contrastadas: {estados['contrastado']}, sin verificar: {estados['consultar']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
