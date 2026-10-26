<div align="center">

# Profe

### La programación didáctica, en una tarde y no en un mes

Aplicación local para docentes de España: programa, desarrolla y exporta la programación didáctica y las situaciones de aprendizaje con el currículo **literal** de la LOMLOE. Sin conexión, sin cuentas y sin instalar nada más que Python.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](#requisitos)
[![Dependencias](https://img.shields.io/badge/dependencias-0-brightgreen)](#requisitos)
[![Offline](https://img.shields.io/badge/100%25-offline-2f6f4e)](#privacidad)
[![Currículo literal del BOE](https://img.shields.io/badge/curr%C3%ADculo-literal%20del%20BOE-6b4c9a)](#de-d%C3%B3nde-salen-los-datos)
[![Tests](https://img.shields.io/badge/tests-34%20unitarios%20%C2%B7%2075%20UI-success)](#verificaci%C3%B3n)
[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-blue)](#licencia)

[Empezar](#empezar-en-30-segundos) · [Qué hace](#qué-hace) · [Los datos](#de-dónde-salen-los-datos) · [Desarrollo](#desarrollo) · [Verificación](#verificación) · [Limitaciones](#limitaciones-y-hoja-de-ruta)

</div>

---

## El problema

Cada curso, miles de docentes dedican semanas a un documento que no enseña a nadie: copiar competencias específicas de un PDF, pegar criterios que se cortan al pasar a Word, cuadrar pesos que no suman 100 %, y volver a hacerlo cuando cambia el curso o la materia.

Y el PDF del que se copia suele estar desactualizado, mal codificado o directamente inventado en alguna web de apuntes.

**Profe hace ese trabajo desde el texto oficial**, en el ordenador del docente y sin enviar nada a ningún servidor.

## La idea

- **El currículo no se redacta: se importa.** Las competencias específicas, los criterios de evaluación y los saberes básicos salen literalmente del anexo II del real decreto de cada etapa, con su norma, su identificador del BOE y su URL en la propia ficha.
- **El folio en blanco se elimina.** Un botón rellena el expediente completo con el currículo del curso elegido; el docente revisa, contextualiza y firma.
- **Lo que se entrega cuadra.** Cobertura de competencias, pesos al 100 %, criterios ligados a su competencia y un documento final con portada, índice y anexos.

## Empezar en 30 segundos

### Requisitos

- **Python 3.9 o superior** (ya viene en macOS y Linux; en Windows se descarga de [python.org](https://www.python.org/downloads/)).
- Un navegador moderno. Probado con Chrome.
- Nada más: ni `pip install`, ni Node, ni base de datos.

```bash
git clone https://github.com/meabuerro/profe.git profe
cd profe
./Profe
```

`Profe` levanta un servidor local en un puerto libre, abre la app en el navegador y espera. `Ctrl+C` lo detiene.

| Sistema | Lanzador |
|---|---|
| macOS / Linux / Git Bash | `./Profe` |
| Windows (CMD o PowerShell) | `Profe.cmd` |

Para escribirlo desde cualquier carpeta, añade la del repositorio al `PATH`:

```bash
# macOS / Linux (bash o zsh)
echo "export PATH=\"$PWD:\$PATH\"" >> ~/.bashrc   # o ~/.zshrc
source ~/.bashrc
```

```powershell
# Windows (PowerShell)
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";$PWD",
  "User"
)
```

Opciones del lanzador:

```bash
Profe --port 9000     # empezar a buscar puerto libre desde 9000
Profe --no-browser    # arrancar sin abrir el navegador
Profe --host 0.0.0.0  # exponer en la red local (por defecto, solo 127.0.0.1)
```

También funciona con doble clic en `index.html`: la app es un único archivo autónomo y se abre con `file://`.

## Qué hace

### Borrador completo en un clic

Rellena competencias específicas, criterios, saberes, metodología, atención a la diversidad, evaluación de la práctica docente, justificación normativa y las unidades de la programación anual **con el texto de la ficha del curso**. No sobrescribe lo que ya hayas escrito y no inventa el contexto del centro: eso lo pones tú.

### Programación anual

Unidades por evaluación con competencias específicas, criterios, instrumentos, sesiones y peso en la calificación.

- Las unidades se generan **ya repartidas** con las CE y los criterios de tu curso.
- **Indicador de cobertura**: «CE trabajadas: 6/6», lista de las que faltan y un botón para repartirlas.
- Los **pesos suman 100 %** siempre, también al añadir o borrar unidades.
- Cada unidad se **desarrolla** con objetivos, actividades por sesión, diversidad y evaluación, y se exporta como anexo.

### Programación didáctica

Nueve apartados con la estructura que se pide en las convocatorias:

1. Identificación y marco normativo (estatal y autonómico).
2. Justificación, con la norma y el anexo citados.
3. Contextualización.
4. Competencias específicas, con sus descriptores del perfil de salida.
5. Criterios de evaluación y saberes básicos.
6. Metodología.
7. Atención a la diversidad.
8. Recursos y actividades complementarias.
9. Evaluación: calificación y práctica docente.

Los criterios y saberes se cargan con un botón, todos o **solo los de las competencias que hayas marcado**.

### Situaciones de aprendizaje

Reto, producto final, competencias clave y específicas, criterios, secuencia en cuatro fases, agrupamientos, recursos y evaluación. El botón **Cargar del curso** trae las CE y los criterios oficiales; se pueden duplicar y **enviar a la programación anual** conservando criterios e instrumentos.

### Documento final

Vista previa real del expediente (portada, índice, once apartados, anexos y firma) y salida en:

- **Word (.doc)**
- **PDF** mediante la vista imprimible
- **HTML** autónomo

Cita la norma estatal, el anexo del BOE del que procede el texto y el desarrollo autonómico aplicable.

### Catálogo curricular

Por etapa y materia, con las competencias específicas y sus descriptores, y los criterios y saberes **por ciclo o curso** en desplegables. Cada ficha muestra su procedencia («Texto literal · RD 157/2022 · Anexo II») y enlaza al BOE.

### Panel de trabajo

Contexto (etapa, curso, materia y comunidad), datos de cabecera, checklist de entrega con doce requisitos que suele revisar la inspección, porcentaje de avance y enlaces al apartado que falta.

### Extras

- Autoguardado en el navegador y copia de seguridad en JSON.
- Importación del expediente en otro equipo.
- Diseño adaptable, modo impresión y navegación por teclado.

## De dónde salen los datos

`scripts/importar_boe.py` descarga el XML consolidado del BOE y extrae del anexo II de cada real decreto las competencias específicas, los criterios y los saberes.

| Etapa | Norma | BOE | Fichas |
|---|---|---|---|
| Educación Infantil | Real Decreto 95/2022, de 1 de febrero | `BOE-A-2022-1654` | 3 |
| Educación Primaria | Real Decreto 157/2022, de 1 de marzo | `BOE-A-2022-3296` | 7 |
| ESO | Real Decreto 217/2022, de 29 de marzo | `BOE-A-2022-4975` | 18 |
| Bachillerato | Real Decreto 243/2022, de 5 de abril | `BOE-A-2022-5521` | 42 |

En total: **70 fichas**, **423 competencias específicas**, **1 612 criterios de evaluación** y **3 888 saberes básicos** en 106 niveles (ciclos o cursos).

Cada ficha de `data/materias/` contiene:

```json
{
  "fuente": {
    "norma": "Real Decreto 157/2022, de 1 de marzo",
    "identificador": "BOE-A-2022-3296",
    "anexo": "Anexo II",
    "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2022-3296",
    "texto": "literal"
  },
  "competencias_especificas": [
    {"id": "ce1", "texto": "…", "descriptores": "CCL1, STEM2…", "explicacion": ["…"]}
  ],
  "ciclos": {
    "1er-ciclo": {
      "etiqueta": "Primer ciclo",
      "criterios_evaluacion_por_competencia": {"ce1": ["1.1 …", "1.2 …"]},
      "saberes_basicos": ["A. Sentido numérico.", "…"]
    }
  }
}
```

Los tests comprueban, contra el XML oficial descargado, que **cada competencia, sus descriptores y los criterios aparecen literalmente** en el BOE. No hay texto curricular escrito a mano.

### Casos que el propio real decreto resuelve

- **Segunda Lengua Extranjera (ESO)** comparte las competencias de Lengua Extranjera: la ficha reproduce el párrafo oficial y hereda su currículo.
- **Matemáticas de 4.º de ESO** se desdobla en A y B, como las publica el anexo.
- **Religión** no se fija en estos reales decretos: se declara sin desarrollo estatal y se remite a la autoridad religiosa y a la normativa autonómica, sin inventar contenido.

### Fichas autonómicas

`scripts/importar_ccaa.py` genera las 19 fichas de `data/ccaa/` con la norma de cada etapa, su boletín y su portal oficial. Cada referencia lleva su estado de comprobación:

| Estado | Significado | Referencias |
|---|---|---|
| `verificado` | Consta en el portal oficial de la consejería o en el boletín. | 44 |
| `contrastado` | Consta en repertorios normativos; conviene confirmar número y fecha en el boletín. La app lo avisa. | 32 |

`scripts/verificar_enlaces.py` comprueba que los 19 portales responden (última ejecución: **19/19 con HTTP 200**).

## Flujo recomendado

1. **Configura** etapa, curso, materia y comunidad en el panel.
2. Pulsa **Generar borrador completo**: aparecen competencias, criterios, saberes, propuestas y unidades.
3. **Revisa y contextualiza**: centro, grupo, realidad del aula. Es lo único que la herramienta no puede saber.
4. Ajusta la **programación anual**: títulos, sesiones, instrumentos y pesos.
5. Crea **situaciones de aprendizaje** (o parte del borrador y adáptalas) y envíalas a la anual.
6. Abre **Documento final**, revisa la vista previa y descarga Word o PDF.

## Estructura del repositorio

```
profe/
├── Profe                     # Lanzador macOS/Linux/Git Bash
├── Profe.cmd                 # Lanzador Windows
├── index.html                # Toda la app: HTML + CSS + JS, sin dependencias
├── data/
│   ├── app-data.js           # Catálogo generado que consume la app
│   ├── etapas.json           # Etapas, ciclos y referencias normativas
│   ├── competencias-clave.json
│   ├── ccaa-index.json       # 17 comunidades + 2 ciudades autónomas
│   ├── ccaa/                 # 19 fichas autonómicas
│   └── materias/             # 70 fichas con el texto literal del BOE
├── scripts/
│   ├── importar_boe.py       # Descarga el BOE y escribe las fichas
│   ├── importar_ccaa.py      # Genera las fichas autonómicas
│   ├── verificar_enlaces.py  # Comprueba los portales oficiales
│   ├── build_app.py          # Construye data/app-data.js
│   ├── profe_server.py       # Servidor local y apertura del navegador
│   └── validate_data.sh      # Validación de los JSON
├── tests/
│   ├── test_build_app.py     # Datos, importadores y generador (unittest)
│   ├── ui.test.html          # Auditoría de interfaz
│   └── run_ui.py             # Ejecutor en Chrome headless
├── docs/
├── templates/
├── CONTRIBUTING.md
└── LICENSE
```

## Desarrollo

El proyecto no tiene dependencias ni paso de compilación. Todo es biblioteca estándar de Python y un `index.html` sin frameworks.

### Regenerar los datos

```bash
python3 scripts/importar_boe.py      # descarga los cuatro reales decretos
python3 scripts/importar_ccaa.py     # regenera las fichas autonómicas
python3 scripts/build_app.py         # construye data/app-data.js
```

El importador guarda el XML en `.cache/boe/` (ignorado por git) y lo reutiliza:

```bash
python3 scripts/importar_boe.py --offline   # solo caché, sin red
python3 scripts/importar_boe.py --resumen   # informa sin escribir
python3 scripts/importar_boe.py --etapa eso # limita a una etapa
```

### Añadir una norma o una etapa

Basta con ampliar la tabla `DECRETOS` de `scripts/importar_boe.py` o `CCAA` de `scripts/importar_ccaa.py`. El catálogo de la app se construye solo a partir de las fichas de `data/`: no hay listas que mantener a mano.

### Servidor de desarrollo

```bash
python3 scripts/profe_server.py --no-browser   # sin abrir el navegador
```

## Verificación

```bash
python3 -m unittest discover -s tests -v   # 34 tests de datos, importadores y generador
python3 tests/run_ui.py                    # 75 comprobaciones de interfaz en Chrome
bash scripts/validate_data.sh              # JSON del repositorio
python3 scripts/verificar_enlaces.py       # portales oficiales de las CCAA
```

| Comprobación | Resultado |
|---|---|
| Datos, importadores y generador | **34/34** |
| Auditoría de interfaz (Chrome real) | **75/75** |
| Fidelidad al BOE (CE, descriptores y criterios literales) | OK |
| JSON del repositorio | Todos válidos |
| Enlaces autonómicos | 19/19 responden |
| Arranque con `Profe` y con `file://` | OK |

Qué cubre cada una:

- **Datos**: cada competencia con numeración continua, cada criterio perteneciente a su competencia, ningún nivel sin saberes, identificadores únicos, 19 comunidades y **fidelidad literal frente al XML del BOE**.
- **Interfaz**: onboarding, borrador completo, carga de criterios, cobertura de la anual, unidad desarrollada, situaciones, documento final, exportaciones, catálogo y ficha autonómica. Además: etiquetas de formulario, nombres accesibles, jerarquía de encabezados, sin duplicados de `id`, sin desbordamiento horizontal a 380 px y sin errores de script.

El test de interfaz requiere Chrome o Chromium; si no está instalado, avisa y termina con código 2 (omitido, no fallido).

## Limitaciones y hoja de ruta

- **32 de las 76 referencias autonómicas están «contrastadas»**, no verificadas en el portal oficial. Están marcadas así a propósito, y tanto el catálogo como el documento final lo advierten.
- **Formación Profesional** no tiene currículo importado: se regula por el real decreto de cada título, no por un anexo único.
- **Religión** queda fuera de los reales decretos de enseñanzas mínimas; la app lo indica en lugar de rellenarlo.
- El PDF se obtiene por la vista imprimible del navegador, no con un generador propio.
- Los datos viven en el `localStorage`: si se borran los datos del sitio o se usa el modo incógnito, se pierden. Para eso está la copia de seguridad en JSON.

Ideas abiertas: importar el currículo de FP por título, añadir el perfil de salida completo por etapa, y una vista de comparación entre la norma estatal y la autonómica.

## Privacidad

- **Sin conexión**: la app no hace peticiones a servicios externos.
- **Sin cuentas ni telemetría.**
- **Sin servidores**: los datos se quedan en el navegador del docente.

Los únicos procesos que salen a la red son los scripts de importación y verificación, y solo cuando los ejecutas tú.

## Contribuir

Las aportaciones más útiles son las que mantienen la trazabilidad normativa: nuevas fichas con su referencia exacta, correcciones de datos y mejoras de accesibilidad. Lee [CONTRIBUTING.md](CONTRIBUTING.md) antes de abrir un *pull request*.

Principios no negociables:

1. Nada de datos privados en la nube ni telemetría.
2. Todo el contenido curricular debe poder rastrearse a la norma vigente.

## Licencia

[MIT](LICENSE). Puedes usarlo, modificarlo y distribuirlo citando la autoría.
