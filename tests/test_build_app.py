"""Tests del catálogo curricular y de los importadores de datos.

Se ejecutan con la biblioteca estándar:

    python3 -m unittest discover -s tests -v

No hacen peticiones de red: el importador del BOE usa la caché local y, si no
existe, esas pruebas se omiten.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import build_app  # noqa: E402  (import tras ajustar sys.path)
import importar_boe  # noqa: E402
import importar_ccaa  # noqa: E402

MOJIBAKE = ("Ã", "Â", "ƒ", "â€")
IDENTIFICADORES_BOE = {
    "BOE-A-2022-1654",  # RD 95/2022, Infantil
    "BOE-A-2022-3296",  # RD 157/2022, Primaria
    "BOE-A-2022-4975",  # RD 217/2022, ESO
    "BOE-A-2022-5521",  # RD 243/2022, Bachillerato
}
ESTADOS_CCAA = {"verificado", "contrastado", "consultar"}


# ---------------------------------------------------------------------------
# Reparación de codificación (fichas heredadas)
# ---------------------------------------------------------------------------

class TestRepair(unittest.TestCase):
    def test_repara_texto_doblemente_codificado(self):
        roto = "Educaci\u00c3\u0192\u00c2\u00b3n F\u00c3\u0192\u00c2\u00adsica"
        self.assertEqual(build_app.repair(roto), "Educación Física")

    def test_deja_intacto_el_texto_correcto(self):
        limpio = "Educación Física y Química"
        self.assertEqual(build_app.repair(limpio), limpio)

    def test_normaliza_a_nfc(self):
        self.assertEqual(build_app.repair("Educacio\u0301n"), "Educación")

    def test_recorre_estructuras_anidadas(self):
        datos = {"nombre": "Biolog\u00c3\u0192\u00c2\u00ada", "lista": ["Geolog\u00c3\u0192\u00c2\u00ada"]}
        self.assertEqual(build_app.repair(datos), {"nombre": "Biología", "lista": ["Geología"]})

    def test_conserva_valores_no_texto(self):
        self.assertEqual(build_app.repair({"n": 3, "b": True, "v": None}),
                         {"n": 3, "b": True, "v": None})


# ---------------------------------------------------------------------------
# Importador del BOE
# ---------------------------------------------------------------------------

ANEXO_SINTETICO = """
<p class="anexo_num">ANEXO II</p>
<p class="anexo_tit">Materias de Bachillerato</p>
<p class="centro_negrita">Física</p>
<p class="parrafo_2">La materia de Física estudia la naturaleza.</p>
<p class="parrafo">1.&ensp;Resolver problemas de física con rigor.</p>
<p class="parrafo">Esta competencia específica se conecta con los siguientes descriptores del Perfil de salida: STEM2, STEM4.</p>
<p class="parrafo_2">Criterios de evaluación.</p>
<p class="parrafo_2">Competencia específica 1.</p>
<p class="parrafo_2">1.1&ensp;Resolver problemas aplicando las leyes de Newton.</p>
<p class="parrafo">con criterios de validez.</p>
<p class="parrafo_2">Saberes básicos.</p>
<p class="parrafo_2">A.&ensp;Mecánica.</p>
<p class="parrafo_2">–&ensp;Leyes de Newton.</p>
<p class="parrafo">−&ensp;Cinemática.</p>
<p class="anexo_num">ANEXO III</p>
"""


class TestImportadorBOE(unittest.TestCase):
    def test_limpiar_convierte_html_del_boe(self):
        self.assertEqual(importar_boe.limpiar("<p>Educaci&oacute;n&nbsp;f&iacute;sica</p>"),
                         "Educación física")

    def test_slug_quita_acentos_y_espacios(self):
        self.assertEqual(importar_boe.slug("Lengua Castellana y Literatura"),
                         "lengua-castellana-y-literatura")
        self.assertEqual(importar_boe.slug("Área 1. Crecimiento"), "area-1-crecimiento")

    def test_niveles_reconocidos(self):
        self.assertEqual(importar_boe._nivel_de("Primer ciclo")[0], "1er-ciclo")
        self.assertEqual(importar_boe._nivel_de("Cursos de primero a tercero")[0], "1-3-eso")
        self.assertEqual(importar_boe._nivel_de("Cuarto curso")[0], "4-eso")
        self.assertIsNone(importar_boe._nivel_de("Biología"))

    def test_parsea_un_anexo_completo(self):
        materias = importar_boe.parsear_anexo(ANEXO_SINTETICO, "bachillerato")
        self.assertIn("Física", materias)
        fisica = materias["Física"]
        self.assertEqual(len(fisica["ce"]), 1)
        self.assertEqual(fisica["ce"][0]["id"], "ce1")
        self.assertTrue(fisica["ce"][0]["texto"].startswith("Resolver problemas"))
        self.assertEqual(fisica["ce"][0]["descriptores"], "STEM2, STEM4.")
        nivel = fisica["niveles"]["etapa"]
        self.assertEqual(nivel["criterios"]["ce1"],
                         ["1.1 Resolver problemas aplicando las leyes de Newton. con criterios de validez."])
        self.assertEqual(nivel["saberes"], ["A. Mecánica.", "Leyes de Newton.", "Cinemática."])

    def test_construir_ficha_declara_procedencia(self):
        fichas = importar_boe.construir_fichas(
            "bachillerato", importar_boe.parsear_anexo(ANEXO_SINTETICO, "bachillerato"))
        ficha = fichas[0]
        self.assertEqual(ficha["fuente"]["identificador"], "BOE-A-2022-5521")
        self.assertEqual(ficha["fuente"]["texto"], "literal")
        self.assertTrue(ficha["fuente"]["url"].startswith("https://www.boe.es/"))
        self.assertEqual(ficha["id_materia"], "fisica")

    def test_fichas_reales_son_literales(self):
        fichas = build_app.cargar_fichas()
        self.assertTrue(fichas, "no hay fichas: ejecuta scripts/importar_boe.py")
        total = sum(len(v) for v in fichas.values())
        self.assertGreaterEqual(total, 70, f"solo {total} fichas importadas")
        for etapa, lista in fichas.items():
            for ficha in lista:
                fuente = ficha["fuente"]
                self.assertIn(fuente["identificador"], IDENTIFICADORES_BOE, ficha["nombre"])
                self.assertEqual(fuente["texto"], "literal")
                self.assertEqual(fuente["anexo"], "Anexo II")
                self.assertIn("boe.es", fuente["url"])
                if not ficha.get("remite_a"):
                    self.assertTrue(ficha["competencias_especificas"],
                                    f"{etapa}/{ficha['nombre']} sin competencias")
                    self.assertTrue(ficha["ciclos"], f"{etapa}/{ficha['nombre']} sin niveles")


class TestIntegridadCurricular(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fichas = build_app.cargar_fichas()
        cls.data = build_app.build()

    def test_numeracion_de_competencias_es_continua(self):
        for lista in self.fichas.values():
            for ficha in lista:
                if ficha.get("remite_a"):
                    continue
                ids = [ce["id"] for ce in ficha["competencias_especificas"]]
                esperado = [f"ce{i}" for i in range(1, len(ids) + 1)]
                self.assertEqual(ids, esperado, f"{ficha['nombre']} con numeración rota")

    def test_criterios_pertenecen_a_su_competencia(self):
        for lista in self.fichas.values():
            for ficha in lista:
                for clave, nivel in ficha["ciclos"].items():
                    for ce_id, criterios in nivel["criterios_evaluacion_por_competencia"].items():
                        numero = ce_id.replace("ce", "")
                        for criterio in criterios:
                            self.assertTrue(criterio.startswith(f"{numero}."),
                                            f"{ficha['nombre']}/{clave}: {criterio[:40]!r} en {ce_id}")

    def test_cada_nivel_tiene_saberes_y_etiqueta(self):
        for lista in self.fichas.values():
            for ficha in lista:
                for clave, nivel in ficha["ciclos"].items():
                    self.assertTrue(nivel.get("etiqueta"), f"{ficha['nombre']}/{clave} sin etiqueta")
                    self.assertTrue(nivel.get("saberes_basicos"),
                                    f"{ficha['nombre']}/{clave} sin saberes")

    def test_ningun_texto_vacio_ni_corrupto(self):
        for lista in self.fichas.values():
            for ficha in lista:
                textos = [ce["texto"] for ce in ficha["competencias_especificas"]]
                for nivel in ficha["ciclos"].values():
                    for criterios in nivel["criterios_evaluacion_por_competencia"].values():
                        textos.extend(criterios)
                    textos.extend(nivel["saberes_basicos"])
                for texto in textos:
                    self.assertTrue(texto.strip(), f"texto vacío en {ficha['nombre']}")
                    for marca in MOJIBAKE:
                        self.assertNotIn(marca, texto, f"mojibake en {ficha['nombre']}: {texto[:60]}")

    def test_infantil_usa_denominacion_sin_numero_de_area(self):
        nombres = [f["nombre"] for f in self.fichas["infantil"]]
        self.assertEqual(len(nombres), 3)
        for nombre in nombres:
            self.assertFalse(nombre.startswith("Área"), nombre)


# ---------------------------------------------------------------------------
# Catálogo de la aplicación
# ---------------------------------------------------------------------------

class TestCatalogo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_app.build()
        cls.materias = cls.data["materias"]

    def test_incluye_las_cinco_etapas(self):
        self.assertEqual([e["id"] for e in self.data["etapas"]],
                         ["infantil", "primaria", "eso", "bachillerato", "fp"])

    def test_cobertura_por_etapa(self):
        self.assertEqual(len(self.materias["infantil"]), 3)
        self.assertEqual(len(self.materias["primaria"]), 8)   # 7 áreas + Religión
        self.assertEqual(len(self.materias["eso"]), 21)       # 20 + Religión
        self.assertEqual(len(self.materias["bachillerato"]), 43)  # 42 + Religión
        self.assertEqual(self.materias["fp"], [])

    def test_identificadores_unicos_y_nombres(self):
        for etapa, materias in self.materias.items():
            ids = [m["id"] for m in materias]
            self.assertEqual(len(ids), len(set(ids)), f"ids duplicados en {etapa}")
            for materia in materias:
                self.assertTrue(materia["nombre"].strip())

    def test_las_materias_literales_traen_competencias_y_niveles(self):
        for etapa, materias in self.materias.items():
            for materia in materias:
                if materia["tipoFicha"] != "literal":
                    continue
                self.assertTrue(materia["competenciasEspecificas"],
                                f"{etapa}/{materia['nombre']} sin competencias")
                self.assertTrue(materia["ciclos"], f"{etapa}/{materia['nombre']} sin niveles")
                self.assertIn("boe.es", materia["fuente"]["url"])

    def test_matematicas_de_eso_se_desdobla_en_a_y_b(self):
        nombres = [m["nombre"] for m in self.materias["eso"]]
        self.assertIn("Matemáticas (1.º a 3.º de ESO)", nombres)
        self.assertIn("Matemáticas A (4.º de ESO)", nombres)
        self.assertIn("Matemáticas B (4.º de ESO)", nombres)
        for materia in self.materias["eso"]:
            if materia["nombre"].startswith("Matemáticas"):
                self.assertEqual(list(materia["ciclos"]), ["4-eso"] if "4.º" in materia["nombre"]
                                 else ["1-3-eso"])

    def test_segunda_lengua_extranjera_hereda_el_curriculo(self):
        segunda = next(m for m in self.materias["eso"] if m["nombre"] == "Segunda Lengua Extranjera")
        self.assertEqual(segunda["remiteA"], "Lengua Extranjera")
        self.assertEqual(len(segunda["competenciasEspecificas"]), 6)
        self.assertIn("Lengua Extranjera", segunda["remisionTexto"])

    def test_religion_se_marca_sin_desarrollo_estatal(self):
        for etapa in ("primaria", "eso", "bachillerato"):
            religion = next(m for m in self.materias[etapa] if m["nombre"] == "Religión")
            self.assertEqual(religion["tipoFicha"], "sin-desarrollo-estatal")
            self.assertFalse(religion["tieneFicha"])
            self.assertIn("no se establece", " ".join(religion["notas"]))

    def test_ccaa_completas_con_norma_por_etapa(self):
        ids = [c["id"] for c in self.data["ccaa"]]
        self.assertEqual(len(ids), 19)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("castilla-la-mancha", ids)
        self.assertIn("comunitat-valenciana", ids)
        self.assertIn("pais-basco", ids)
        for ccaa in self.data["ccaa"]:
            self.assertEqual(ccaa["nombre"], ccaa["nombre"].strip())
            for etapa in ("infantil", "primaria", "eso", "bachillerato"):
                datos = ccaa["etapas"].get(etapa)
                self.assertTrue(datos, f"{ccaa['nombre']} sin {etapa}")
                self.assertTrue(datos["decreto_referencia"].strip(),
                                f"{ccaa['nombre']}/{etapa} sin norma")
                self.assertIn(datos["estado"], ESTADOS_CCAA)
            self.assertTrue(ccaa.get("enlaces"), f"{ccaa['nombre']} sin enlace oficial")
            for url in ccaa["enlaces"].values():
                self.assertTrue(url.startswith("https://"), url)

    def test_competencias_clave_son_ocho(self):
        etiquetas = [c["etiqueta"] for c in self.data["competenciasClave"]]
        self.assertEqual(etiquetas, ["CCL", "CP", "STEM", "CD", "CPSAA", "CC", "CE", "CEC"])

    def test_sin_restos_de_mojibake(self):
        texto = json.dumps(self.data, ensure_ascii=False)
        for marca in MOJIBAKE:
            self.assertNotIn(marca, texto, f"queda mojibake ({marca}) en el catálogo")

    def test_etapas_tienen_decreto_o_justificacion(self):
        for etapa in self.data["etapas"]:
            self.assertTrue(etapa["decreto"] or etapa["notas"], etapa["id"])


class TestFidelidadBOE(unittest.TestCase):
    """Comprueba que el texto de las fichas está literalmente en el BOE descargado.

    Si no hay caché local (``.cache/boe``) la prueba se omite: no se hace red.
    """

    @classmethod
    def setUpClass(cls):
        cls.textos = {}
        for etapa, config in importar_boe.DECRETOS.items():
            ruta = importar_boe.CACHE / f"{config['identificador']}.xml"
            if not ruta.exists():
                continue
            xml = ruta.read_text(encoding="utf-8")
            cls.textos[etapa] = importar_boe.limpiar(re.sub(r"<[^>]+>", "", xml))
        if not cls.textos:
            raise unittest.SkipTest("sin caché del BOE: ejecuta scripts/importar_boe.py")
        cls.fichas = build_app.cargar_fichas()

    def test_competencias_especificas_aparecen_en_el_boe(self):
        for etapa, lista in self.fichas.items():
            texto_oficial = self.textos.get(etapa)
            if texto_oficial is None:
                continue
            for ficha in lista:
                for ce in ficha["competencias_especificas"]:
                    self.assertIn(ce["texto"], texto_oficial,
                                  f"{ficha['nombre']}/{ce['id']} no está literalmente en el BOE")

    def test_criterios_de_evaluacion_aparecen_en_el_boe(self):
        for etapa, lista in self.fichas.items():
            texto_oficial = self.textos.get(etapa)
            if texto_oficial is None:
                continue
            for ficha in lista:
                for clave, nivel in ficha["ciclos"].items():
                    for ce_id, criterios in nivel["criterios_evaluacion_por_competencia"].items():
                        for criterio in criterios[:2]:
                            self.assertIn(criterio, texto_oficial,
                                          f"{ficha['nombre']}/{clave}/{ce_id} no es literal")

    def test_descriptores_del_perfil_de_salida_son_literales(self):
        for etapa, lista in self.fichas.items():
            texto_oficial = self.textos.get(etapa)
            if texto_oficial is None:
                continue
            for ficha in lista:
                for ce in ficha["competencias_especificas"]:
                    if ce.get("descriptores"):
                        self.assertIn(ce["descriptores"], texto_oficial,
                                      f"descriptores de {ficha['nombre']}/{ce['id']}")


class TestFichasCCAA(unittest.TestCase):
    def test_las_diecinueve_fichas_se_generan(self):
        fichas = [importar_ccaa.construir(clave, datos) for clave, datos in importar_ccaa.CCAA.items()]
        self.assertEqual(len(fichas), 19)
        for ficha in fichas:
            self.assertEqual(len(ficha["etapas"]), 4, ficha["nombre"])
            for datos in ficha["etapas"].values():
                self.assertIn(datos["estado"], ESTADOS_CCAA)
                self.assertTrue(datos["boletin"])
                self.assertFalse(re.search(r"^\s*$", datos["decreto_referencia"]))


# ---------------------------------------------------------------------------
# Artefacto generado
# ---------------------------------------------------------------------------

class TestRender(unittest.TestCase):
    def test_render_es_js_parseable(self):
        contenido = build_app.render(build_app.build())
        self.assertTrue(contenido.startswith("/*"))
        payload = contenido.split("window.PROFE_DATA = ", 1)[1].rsplit(";", 1)[0]
        datos = json.loads(payload)
        self.assertIn("materias", datos)
        self.assertIn("ccaa", datos)

    def test_main_escribe_el_fichero(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = pathlib.Path(tmp) / "app-data.js"
            self.assertEqual(build_app.main(destino), 0)
            self.assertIn("window.PROFE_DATA", destino.read_text(encoding="utf-8"))

    def test_el_artefacto_del_repositorio_esta_actualizado(self):
        destino = build_app.DATA / "app-data.js"
        self.assertTrue(destino.exists(), "falta data/app-data.js: ejecuta scripts/build_app.py")
        self.assertEqual(destino.read_text(encoding="utf-8"), build_app.render(build_app.build()),
                         "data/app-data.js está desactualizado: ejecuta scripts/build_app.py")


if __name__ == "__main__":
    unittest.main()
