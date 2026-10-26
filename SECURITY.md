# Seguridad y privacidad

Esta herramienta está diseñada para funcionar **completamente offline y en local**.

- No hay servidor.
- No hay peticiones de red en tiempo de uso docente.
- No hay telemetría.
- No se envían datos de ningún tipo a la red.

## Dónde se guardan los datos

Cuando un docente usa la aplicación, la información que Introduce se guarda en el navegador, mediante `localStorage`. Eso incluye:

- configuración del centro y del docente,
- los datos curriculares de la programación en curso,
- los elementos que el docente añade o modifica.

## Qué significa eso para la privacidad

- Los datos no salen del ordenador del docente.
- Solo el navegador y el propio ordenador tienen acceso a lo guardado en `localStorage`.
- Si el docente usa una navegación que no persiste datos, o borra la configuración/local data del navegador, pierde lo guardado.

## Cuándo salen datos del ordenador

Solo cuando el propio docente lo decide explícitamente:

- Exporta su programación a **JSON** para copiarla a otro equipo, hacer una copia de seguridad o compartirla controlledamente.
- Exporta una **vista previa HTML** para imprimirla o guardarla como PDF desde el navegador.

En ningún caso la herramienta envía esos archivos por sí misma.

## Buenas prácticas para los docentes

- Usa la opción de exportar JSON como copia de seguridad periódica.
- Si tu centro o tu caso requiere protección especial de datos, guarda los JSON en un lugar seguro y controlado por ti.
- No compartas archivos JSON con datos de alumnado o del centro si no quieres que se distribuyan.
- Ten en cuenta que `localStorage` es propio del perfil/navegador; si usas el ordenador en más de un perfil o navegador, cada uno tiene su propia copia local.

## Para colaboradores

Cualquier contribución que introduzca comunicaciones externas, telemetría, backend o dependencias que requieran internet en tiempo de uso docente debe rechazarse o reformularse. El uso docente tiene que poder hacerse sin conexión.

Si añades funcionalidad que implica extraer o transformar datos, asegúrate de que sigue siendo local y explícita. Por ejemplo: importación/exportación en JSON, o generación de documentos locales, son aceptables si el control permanece en el docente.

## Limites del modelo

- Esta herramienta ayuda a estructurar y generar una programación didáctica, pero no sustituye la revisión normativa por parte del docente, ni la adaptación a la convocatoria o al decreto autonómico concreto cuando exista.
- Es responsabilidad del docente verificar la normativa vigente en su etapa, materia y Comunidad Autónoma antes de usar la programación generada.
