# Cómo contribuir

Este repositorio es una herramienta **open-source, offline y local** para que los docentes de España puedan elaborar programaciones didácticas alineadas a la normativa vigente. Por eso, cualquier contribución debe respetar dos principios no negociables:

- **Sin datos privados en la nube.** La herramienta no envía datos a ningún servidor. Las contribuciones no deben introducir telemetría, backends ni dependencias que rompan ese modelo.
- **Anclado a la normativa vigente.** Todo el contenido curricular debe poder trazarse a la LOMLOE y a los Reales Decreto estatales, y, cuando corresponda, al desarrollo autonómico. Evita basarte en plantillas heredadas de legislaciones derogadas (LOE como práctica corriente, LOMCE).

## Qué puedes aportar

### 1. Contenido curricular estructurado

Lo más útil que puede aportar alguien es **estructurar elementos curriculares oficiales en JSON**, para que los docentes no tengan que redactarlos desde cero.

Esto incluye, por ejemplo:

- las 8 competencias clave y sus descriptores operativos del Perfil de salida,
- los objetivos generales de etapa,
- por materia/área y etapa: competencias específicas, criterios de evaluación y saberes básicos,
- cuando exista: la versión autonómica de esos elementos (con la referencia exacta al decreto/orden de la Comunidad Autónoma).

### 2. Adaptaciones por Comunidad Autónoma

Cada CCAA desarrolla su propio currículo. Una contribución muy valiosa es:

- añadir el fichero de una comunidad autónoma en `data/ccaa/`,
- indicar los enlaces oficiales y la normativa de referencia,
- señalar qué varía respecto al marco estatal (organización de cursos, elementos transversales, denominaciones, evaluación, requisitos formales en oposiciones, etc.).

No es necesario copiar todo el texto normativo. Lo importante es que el docente pueda elegir su contexto y trabajar desde la normativa que le corresponde.

### 3. Mejoras de la aplicación local

Puedes mejorar `index.html` siempre que mantengas:

- ejecución offline desde el sistema de archivos,
- ausencia de dependencias externas en tiempo de uso docente,
- privacidad local (localStorage, import/export opcional en JSON, sin enviar datos),
- claridad y usabilidad para un docente que no es desarrollador.

Si añades funcionalidad nueva, actualiza también la documentación en `docs/`.

### 4. Documentación y orientaciones

Ayuda a dejar claro:

- qué se espera en cada apartado de una programación didáctica,
- cómo se relacionan los elementos curriculares entre sí,
- qué varia entre etapas y entre CCAA,
- qué requisitos formales son de convocatoria y cuáles no.

## Cómo añadir una materia o una etapa

1. Usa el modelo existente en `data/` como referencia.
2. Mantén la misma estructura de claves para que la aplicación local pueda cargarlo sin código adicional.
3. Incluye el código de referencia normativa (normalmente el Real Decreto estatal y, cuando exista, el decreto autonómico).
4. Añade una nota en `docs/` o en el propio JSON si algún elemento tiene interpretación variable.

## Cómo añadir una Comunidad Autónoma

1. Crea el fichero correspondiente en `data/ccaa/`.
2. Incluye:
   - nombre y código de la comunidad autónoma,
   - enlaces a los currículos oficiales por etapa,
   - referencias a los decretos de currículo y, si aplica, órdenes de evaluación,
   - observaciones sobre diferencias respecto al marco estatal.
3. No inventes campos. Si algo no está aún en el modelo, propónlo primero en una discusión o un issue antes de dispersar la estructura.

## Reglas de estructura del repo

- `data/` es la fuente de verdad curricular. Mantén los JSON válidos y consistentes.
- `templates/` es para esquemas de programación y situaciones de aprendizaje que ayuden a los docentes a estructurar su propio contenido.
- `docs/` es para orientaciones, marco legal y glosario.
- `index.html` es la aplicación local. Cualquier mejora debe seguir siendo abierta directamente sin servidor.

## Validación antes de enviar cambios

Antes de proponer una pull request, comprueba al menos:

- que los JSON editados sean sintácticamente válidos,
- que las claves usadas coincidan con el modelo existente,
- que la referencia normativa sea a legislación vigente,
- que no se haya introducido ninguna dependencia que suponga conexión externa en tiempo de uso docente.

## Cómo proponer un cambio

Puedes abrir un issue para discutir la idea antes de implementarla, especialmente si el cambio afecta a la estructura de `data/` o a la aplicación local. Si vas a añadir contenido curricular, incluye:

- la fuente normativa que justifica los datos,
- la etapa, materia/área y ciclo/nivel a los que se refiere,
- la Comunidad Autónoma, cuando aplique,
- cualquier nota de interpretación que sea útil para otros docentes o colaboradores.

## Confusiones frecuentes

- No es lo mismo “área” que “materia” ni que “módulo”. La terminología cambia según la etapa. Usa la que corresponda a la etapa que estás añadiendo.
- No uses “estándares de aprendizaje evaluables” como término propio de la LOMLOE; esa nomenclatura pertenece a la LOMCE.
- En Formación Profesional la estructura no usa “competencias específicas” ni “saberes básicos” en el mismo sentido que Primaria/ESO/Bachillerato; hay que adaptar el lenguaje.

## Principio rector

La mejor contribución es aquella que hace más fácil para un docente situarse en su etapa, su materia y su Comunidad Autónoma, trabajar desde la normativa correcta, y salir del todo sin depender de internet ni de un servidor.
