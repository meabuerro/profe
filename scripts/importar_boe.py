#!/usr/bin/env python3
"""Importa el currículo LOMLOE directamente del texto consolidado del BOE.

Cada ficha generada contiene el texto *literal* de las competencias específicas,
los criterios de evaluación y los saberes básicos publicados en el anexo II de
cada real decreto, junto con la referencia y la URL exactas de la norma.

Fuentes (texto consolidado, XML oficial del BOE):
    Infantil      RD 95/2022   BOE-A-2022-1654
    Primaria      RD 157/2022  BOE-A-2022-3296
    ESO           RD 217/2022  BOE-A-2022-4975
    Bachillerato  RD 243/2022  BOE-A-2022-5521

Uso:
    python3 scripts/importar_boe.py            # descarga (o usa caché) y escribe fichas
    python3 scripts/importar_boe.py --offline   # solo caché local
    python3 scripts/importar_boe.py --resumen   # no escribe, informa de la cobertura
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
FICHAS = DATA / "materias"
CACHE = RAIZ / ".cache" / "boe"

DECRETOS = {
    "infantil": {
        "identificador": "BOE-A-2022-1654",
        "norma": "Real Decreto 95/2022, de 1 de febrero",
        "anexo": "Anexo II",
        "anexo_titulo": "Áreas de la Educación Infantil",
        "terminologia": "área",
    },
    "primaria": {
        "identificador": "BOE-A-2022-3296",
        "norma": "Real Decreto 157/2022, de 1 de marzo",
        "anexo": "Anexo II",
        "anexo_titulo": "Áreas de Educación Primaria",
        "terminologia": "área",
    },
    "eso": {
        "identificador": "BOE-A-2022-4975",
        "norma": "Real Decreto 217/2022, de 29 de marzo",
        "anexo": "Anexo II",
        "anexo_titulo": "Materias de Educación Secundaria Obligatoria",
        "terminologia": "materia",
    },
    "bachillerato": {
        "identificador": "BOE-A-2022-5521",
        "norma": "Real Decreto 243/2022, de 5 de abril",
        "anexo": "Anexo II",
        "anexo_titulo": "Materias de Bachillerato",
        "terminologia": "materia",
    },
}

URL_BASE = "https://www.boe.es/buscar/act.php?id={}"
URL_XML = "https://www.boe.es/diario_boe/xml.php?id={}"

# Etiquetas de nivel (ciclo o curso) que aparecen como encabezado en el anexo.
NIVELES = [
    (r"^Primer ciclo$", "1er-ciclo", "Primer ciclo"),
    (r"^Segundo ciclo$", "2o-ciclo", "Segundo ciclo"),
    (r"^Tercer ciclo$", "3er-ciclo", "Tercer ciclo"),
    (r"^Cursos? de primero a tercero$", "1-3-eso", "Cursos de primero a tercero"),
    (r"^Cursos? primero y segundo$", "1-2-eso", "Cursos primero y segundo"),
    (r"^Cursos? tercero y cuarto$", "3-4-eso", "Cursos tercero y cuarto"),
    (r"^Primer curso$", "1-eso", "Primer curso"),
    (r"^Segundo curso$", "2-eso", "Segundo curso"),
    (r"^Tercer curso$", "3-eso", "Tercer curso"),
    (r"^Cuarto curso$", "4-eso", "Cuarto curso"),
    (r"^(Primero|1\.º|1º)\s*(de\s*)?(ESO|Bachillerato)$", "1-curso", "Primer curso"),
    (r"^(Segundo|2\.º|2º)\s*(de\s*)?(ESO|Bachillerato)$", "2-curso", "Segundo curso"),
]

RE_CE = re.compile(r"^(\d{1,2})\.\s+(.*)$")
RE_CRITERIO = re.compile(r"^(\d{1,2})\.(\d{1,2})\s+(.*)$")
RE_COMPETENCIA = re.compile(r"^Competencia espec[íi]fica\s+(\d{1,2})\.?$", re.I)
RE_SABER_ITEM = re.compile(r"^[–−—•\-]\s*(.*)$")
RE_SABER_BLOQUE = re.compile(r"^([A-Z])\.\s*(.+)$")
RE_SABER_SUBBLOQUE = re.compile(r"^(\d{1,2})\.\s+(.+)$")


class ErrorImportacion(RuntimeError):
    """Fallo al descargar o interpretar el texto oficial."""


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------

def descargar(identificador: str, offline: bool = False) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    destino = CACHE / f"{identificador}.xml"
    if destino.exists():
        return destino.read_text(encoding="utf-8")
    if offline:
        raise ErrorImportacion(
            f"No hay copia en caché de {identificador}. Ejecuta sin --offline una vez."
        )
    url = URL_XML.format(identificador)
    try:
        with urllib.request.urlopen(url, timeout=60) as respuesta:
            crudo = respuesta.read()
    except (urllib.error.URLError, TimeoutError) as exc:  # pragma: no cover - red
        raise ErrorImportacion(f"No se pudo descargar {url}: {exc}") from exc
    texto = crudo.decode("utf-8", errors="strict")
    if "<documento" not in texto:
        raise ErrorImportacion(f"{url} no devolvió un documento del BOE.")
    destino.write_text(texto, encoding="utf-8")
    return texto


# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------

def limpiar(fragmento: str) -> str:
    """Convierte un fragmento HTML del BOE en texto plano normalizado."""
    texto = html.unescape(re.sub(r"<[^>]+>", "", fragmento))
    texto = texto.replace("\u2002", " ").replace("\u2003", " ").replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def slug(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    base = "".join(c for c in base if not unicodedata.combining(c))
    base = base.lower().replace("ñ", "n")
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base


# ---------------------------------------------------------------------------
# Interpretación del anexo
# ---------------------------------------------------------------------------

def _rango_anexo(xml: str, titulo: str) -> str:
    """Devuelve el fragmento del anexo II, desde su título hasta el anexo III."""
    apertura = re.search(
        r'<p class="(?:anexo|anexo_num)">ANEXO II</p>(.*?)(?=<p class="(?:anexo|anexo_num)">ANEXO III</p>)',
        xml,
        re.S,
    )
    if not apertura:
        raise ErrorImportacion(f"No se localizó el anexo II de «{titulo}».")
    return apertura.group(1)


def _es_encabezado(clase: str) -> bool:
    return clase in {"centro_redonda", "centro_cursiva", "centro_negrita", "anexo_tit"}


def _nivel_de(texto: str):
    for patron, clave, etiqueta in NIVELES:
        if re.match(patron, texto, re.I):
            return clave, etiqueta
    return None


def parsear_anexo(xml: str, etapa: str) -> dict:
    """Extrae {nombre de materia: {ce: [...], niveles: {...}}} del anexo II."""
    config = DECRETOS[etapa]
    fragmento = _rango_anexo(xml, config["anexo_titulo"])
    parrafos = [
        (m.group(1), limpiar(m.group(2)))
        for m in re.finditer(r'<p class="([^"]+)">(.*?)</p>', fragmento, re.S)
    ]

    materias: dict[str, dict] = {}
    materia = None
    nivel = None
    modo = "intro"
    ce_actual = None
    criterio_actual = None
    sin_bloque = "etapa"
    ultimo_saber = None

    def nueva_materia(nombre: str):
        nonlocal materia, nivel, modo, ce_actual, criterio_actual
        materia = materias.setdefault(nombre, {"ce": [], "niveles": {}, "intro": []})
        nivel = None
        modo = "intro"
        ce_actual = None
        criterio_actual = None
        return materia

    def nuevo_nivel(clave: str, etiqueta: str):
        nonlocal nivel, modo, ce_actual, criterio_actual
        nivel = materia["niveles"].setdefault(
            clave,
            {"etiqueta": etiqueta, "criterios": {}, "saberes": []},
        )
        modo = "intro-nivel"
        ce_actual = None
        criterio_actual = None
        return nivel

    for clase, texto in parrafos:
        if not texto:
            continue
        if clase == "anexo_tit":
            continue
        if re.match(r"^ANEXO\b", texto, re.I):
            continue
        if texto in {config["anexo_titulo"], "MATERIAS DE EDUCACIÓN SECUNDARIA OBLIGATORIA",
                     "MATERIAS DE BACHILLERATO", "ÁREAS DE EDUCACIÓN PRIMARIA",
                     "ÁREAS DE LA EDUCACIÓN INFANTIL"}:
            continue
        if re.match(r"^(ÁMBITOS|MATERIAS|ÁREAS) DE ", texto) and len(texto) < 90:
            continue

        # Los títulos de sección no siempre usan una clase de encabezado: en algunos
        # anexos «Saberes básicos.» es un párrafo normal. Se reconocen por su texto.
        if re.match(r"^Saberes b[áa]sicos\.?$", texto, re.I):
            modo = "saberes"
            ultimo_saber = None
            continue
        if re.match(r"^Criterios de evaluaci[óo]n\.?$", texto, re.I):
            modo = "criterios"
            criterio_actual = None
            continue
        if re.match(r"^Competencias espec[íi]ficas\.?$", texto, re.I):
            modo = "ce"
            continue

        if _es_encabezado(clase):
            # 1. Cambio de modo
            if re.match(r"^Criterios de evaluaci[óo]n\.?$", texto, re.I):
                modo = "criterios"
                criterio_actual = None
                continue
            if re.match(r"^Competencias espec[íi]ficas\.?$", texto, re.I):
                modo = "ce"
                continue
            if re.match(r"^Saberes b[áa]sicos\.?$", texto, re.I):
                modo = "saberes"
                ultimo_saber = None
                continue

            nivel_detectado = _nivel_de(texto)
            if nivel_detectado:
                if materia is not None:
                    nuevo_nivel(*nivel_detectado)
                continue

            # 2. Variantes de una misma materia (Matemáticas A / B en la ESO).
            if re.match(r"^MATEM[ÁA]TICAS [AB]$", texto):
                if materia is not None:
                    nuevo_nivel(slug(texto) + "-4-eso", texto.title())
                continue

            # 3. Submateria de Bachillerato: «Biología I» dentro de «Biología».
            if materia is not None and re.match(r"^(.+?)\s+(I{1,2})$", texto):
                base, romano = re.match(r"^(.+?)\s+(I{1,2})$", texto).groups()
                if slug(base) == slug(materia_nombre := _nombre_actual(materias)):
                    clave = "1-bach" if romano == "I" else "2-bach"
                    nuevo_nivel(clave, texto)
                    continue

            # 4. Nueva materia de la etapa.
            nueva_materia(texto)
            continue

        # --- párrafos de cuerpo ---
        if materia is None:
            continue

        if modo == "intro":
            m = RE_CE.match(texto)
            if m:
                ce_actual = {"id": f"ce{m.group(1)}", "texto": m.group(2), "explicacion": []}
                materia["ce"].append(ce_actual)
                modo = "ce"
            else:
                materia["intro"].append(texto)
            continue

        if modo == "ce":
            m = RE_CE.match(texto)
            if m:
                ce_actual = {"id": f"ce{m.group(1)}", "texto": m.group(2), "explicacion": []}
                materia["ce"].append(ce_actual)
                continue
            if ce_actual is None:
                continue
            if texto.lower().startswith("esta competencia específica se conecta"):
                ce_actual["descriptores"] = texto.split("Perfil de salida:", 1)[-1].strip()
            else:
                ce_actual["explicacion"].append(texto)
            continue

        if modo == "intro-nivel":
            # Algunos niveles no llevan criterios: su contenido va a saberes.
            if RE_CRITERIO.match(texto):
                modo = "criterios"
            else:
                continue

        if modo == "criterios":
            destino = nivel if nivel is not None else materia["niveles"].setdefault(
                sin_bloque, {"etiqueta": "Etapa completa", "criterios": {}, "saberes": []}
            )
            m = RE_COMPETENCIA.match(texto)
            if m:
                ce_actual = f"ce{m.group(1)}"
                criterio_actual = None
                destino["criterios"].setdefault(ce_actual, [])
                continue
            m = RE_CRITERIO.match(texto)
            if m:
                numero = f"{m.group(1)}.{m.group(2)}"
                ce_id = f"ce{m.group(1)}"
                criterio_actual = f"{numero} {m.group(3)}"
                destino["criterios"].setdefault(ce_id, []).append(criterio_actual)
                continue
            if criterio_actual is not None:
                lista = destino["criterios"]
                for clave, valores in lista.items():
                    if valores and valores[-1] == criterio_actual:
                        valores[-1] = criterio_actual + " " + texto
                        criterio_actual = valores[-1]
                        break
            continue

        if modo == "saberes":
            destino = nivel if nivel is not None else materia["niveles"].setdefault(
                sin_bloque, {"etiqueta": "Etapa completa", "criterios": {}, "saberes": []}
            )
            item = RE_SABER_ITEM.match(texto)
            if item:
                destino["saberes"].append(item.group(1).strip())
                ultimo_saber = ("item", len(destino["saberes"]) - 1)
                continue
            sub = RE_SABER_SUBBLOQUE.match(texto)
            if sub:
                destino["saberes"].append(f"{sub.group(1)}. {sub.group(2)}")
                ultimo_saber = None
                continue
            bloque = RE_SABER_BLOQUE.match(texto)
            if bloque:
                destino["saberes"].append(f"{bloque.group(1)}. {bloque.group(2)}")
                ultimo_saber = None
                continue
            if ultimo_saber:
                tipo, indice = ultimo_saber
                destino["saberes"][indice] += " " + texto
            continue

    return materias


def _nombre_actual(materias: dict) -> str:
    return next(reversed(materias)) if materias else ""


# ---------------------------------------------------------------------------
# Fichas
# ---------------------------------------------------------------------------

def _remision(etapa: str, datos: dict, nombres: list[str], propio: str) -> tuple[str, str] | None:
    """Materias que declaran compartir el currículo de otra (p. ej. Segunda Lengua Extranjera)."""
    for parrafo in datos.get("intro", []):
        if not re.search(r"competencias espec[íi]ficas", parrafo, re.I):
            continue
        for nombre in nombres:
            if nombre != propio and nombre in parrafo:
                return nombre, parrafo
    return None


def construir_fichas(etapa: str, materias: dict) -> list[dict]:
    config = DECRETOS[etapa]
    hoy = dt.date.today().isoformat()
    fichas = []

    for nombre, datos in materias.items():
        ce = []
        for competencia in datos["ce"]:
            entrada = {
                "id": competencia["id"],
                "texto": competencia["texto"],
            }
            if competencia.get("descriptores"):
                entrada["descriptores"] = competencia["descriptores"]
            if competencia.get("explicacion"):
                entrada["explicacion"] = competencia["explicacion"]
            ce.append(entrada)

        remision = _remision(etapa, datos, list(materias), nombre) if not ce else None
        if not ce and not remision:
            continue
        if not datos["niveles"] and not remision:
            continue

        niveles = {}
        for clave, nivel in datos["niveles"].items():
            niveles[clave] = {
                "etiqueta": nivel["etiqueta"],
                "criterios_evaluacion_por_competencia": nivel["criterios"],
                "saberes_basicos": nivel["saberes"],
            }

        # En Infantil el BOE titula «Área 1. Crecimiento en Armonía»: el número de
        # área no forma parte del nombre del área.
        nombre_visible = re.sub(r"^Área\s+\d+\.\s*", "", nombre)

        fichas.append({
            "id_etapa": etapa,
            "id_materia": slug(nombre_visible),
            "nombre": nombre_visible,
            "denominacion_oficial": nombre,
            "terminologia_etapa": config["terminologia"],
            "fuente": {
                "norma": config["norma"],
                "identificador": config["identificador"],
                "anexo": config["anexo"],
                "url": URL_BASE.format(config["identificador"]),
                "texto": "literal",
                "importado": hoy,
            },
            "organizacion": " ".join(datos["intro"]) or None,
            "remite_a": remision[0] if remision else None,
            "remision_texto": remision[1] if remision else None,
            "competencias_especificas": ce,
            "ciclos": niveles,
            "notas": [
                f"Texto literal del {config['anexo']} del {config['norma']} "
                f"(BOE, {config['identificador']}).",
                "Las competencias específicas son comunes a toda la etapa; los criterios de "
                "evaluación y los saberes básicos se recogen por ciclo o curso tal como los "
                "publica el real decreto.",
                "El desarrollo autonómico puede ampliar o concretar este currículo: "
                "consulta la ficha de tu comunidad autónoma.",
            ],
        })

    fichas.sort(key=lambda f: f["nombre"])
    return fichas


def escribir(fichas: list[dict]) -> None:
    FICHAS.mkdir(parents=True, exist_ok=True)
    escritas = []
    for ficha in fichas:
        destino = FICHAS / f"{ficha['id_etapa']}-{ficha['id_materia']}.json"
        destino.write_text(
            json.dumps(ficha, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        escritas.append(destino.name)
    return escritas


def resumen(etapa: str, fichas: list[dict]) -> str:
    lineas = [f"{etapa}: {len(fichas)} fichas"]
    for ficha in fichas:
        niveles = ficha["ciclos"]
        criterios = sum(len(v) for n in niveles.values() for v in n["criterios_evaluacion_por_competencia"].values())
        saberes = sum(len(n["saberes_basicos"]) for n in niveles.values())
        lineas.append(
            f"  - {ficha['nombre']}: {len(ficha['competencias_especificas'])} CE, "
            f"{len(niveles)} niveles, {criterios} criterios, {saberes} saberes"
        )
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="usar solo la caché local")
    parser.add_argument("--resumen", action="store_true", help="no escribir, solo informar")
    parser.add_argument("--etapa", choices=sorted(DECRETOS), action="append",
                        help="limitar a una etapa (repetible)")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    etapas = args.etapa or list(DECRETOS)
    total = 0
    for etapa in etapas:
        xml = descargar(DECRETOS[etapa]["identificador"], offline=args.offline)
        materias = parsear_anexo(xml, etapa)
        fichas = construir_fichas(etapa, materias)
        if not fichas:
            raise ErrorImportacion(f"{etapa}: no se extrajo ninguna materia del anexo II.")
        total += len(fichas)
        if args.resumen:
            print(resumen(etapa, fichas))
        else:
            escritas = escribir(fichas)
            print(resumen(etapa, fichas))
            print(f"  → {len(escritas)} fichas escritas en data/materias/")
    print(f"Total: {total} fichas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
