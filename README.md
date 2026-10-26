# Programación Didáctica Local para Docentes de España

Herramienta offline, 100% local, para ayudar a los docentes españoles a elaborar programaciones didácticas conforme a la normativa nacional (LOMLOE) y autonómica, sin que los datos privados salgan de su equipo.

## Estructura del proyecto

```
spain-programmes
├── README.md
├── LICENSE
├── index.html              # Aplicación principal (offline, single-file)
├── docs
│   ├── estructura-legal.md
│   └── guia-uso-local.md
└── templates
    └── competencias clave LOMLOE.json
```

## Características principales

- **Ejecución totalmente offline**: abre `index.html` directamente en el navegador, sin servidor ni internet.
- **Guardado local**: usa `localStorage` del navegador para que ningún dato salga de tu máquina.
- **Exportación de datos**: puedes exportar tu programación en formato JSON para copiarla a otro ordenador o recuperarla después; también se puede exportar vista previa HTML para imprimir o guardar como PDF desde el navegador.
- **Contenido normativo integrado**: incluye los elementos curriculares de la LOMLOE (competencias clave, saberes básicos, criterios de evaluación, situaciones de aprendizaje) y referencia a los Reales Decretos estatales y a los decretos autonómicos.

## Cómo usarla

1. Descarga o clona este repositorio en tu ordenador.
2. Haz doble clic en `index.html` o ábrelo con el navegador que quieras (Chrome, Firefox, Edge, Safari…).
3. Conecta los campos de configuración y programación; todo se guarda en tu navegador.
4. Exporta a JSON cuando quieras mover o hacer copia de seguridad de tu trabajo.

## Entorno de ejecución y privacidad

- No requiere instalar nada.
- No envía datos a ninguna red: no hay peticiones HTTP, ni seguimiento, ni servicios externos.
- Los datos se almacenan en el navegador del docente; si usas modo incógnito o borras datos locales, perderás lo guardado.

## Contenido legal y competencias

El modelo está diseñado en torno a los elementos curriculares de la LOMLOE y a los Reales Decretos que desarrollan el currículo en cada etapa:

- LO 3/2020, de 29 de diciembre (LOMLOE)
- RD 157/2022 (Educación Primaria)
- RD 217/2022 (ESO)
- RD 243/2022 (Bachillerato)
- RD 984/2021 y RD 985/2021 (evaluación en Primaria y ESO)
- Decretos de currículo de cada Comunidad Autónoma

Los 8 competencias clave del Perfil de Salida están presentes en la aplicación para que la programación los integre de forma transversal.

## Extensiones previstas

- Plantillas de 단위 didácticas por materia y etapa.
- Fichas de situaciones de aprendizaje.
- Soporte para normativa autonómica específica por CCAA (en versión futura).

## Licencia

Este repositorio es de código abierto. Consulta el archivo `LICENSE` para los términos de uso, modificación y distribución.

## Colaboración

Puedes proponer mejoras, añadir plantillas de otras materias o etapas, o adaptar el contenido a la normativa de tu Comunidad Autónoma. Al ser un proyecto 100% local y offline, cada docente o equipo docente puede mantener su propia copia y adaptarla.

---

He enviado tres archivos iniciales: la aplicación offline `index.html`, el `README.md` y el script de scaffold que permitirá continuar el diseño y la extensión del proyecto. Según la ejecución que hayas necesitado, puede hacer falta añadir plantillas, normativa por CCAA y opciones de exportación avanzada (PDF nativo, ODT).