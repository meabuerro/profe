# Guía de uso local

Esta guía explica cómo usar el repositorio sin instalar nada, sin servidor y sin conexión.

## 1. Qué necesitas

- Un ordenador con un navegador moderno (Chrome, Firefox, Edge, Safari, y otros).
- Este repositorio descargado o clonado en tu ordenador.
- No necesitas internet, ni Node, ni Python, ni servidor, ni instalación.

## 2. Cómo abrirlo

1. Ve a la carpeta donde tienes el repositorio.
2. Localiza el fichero `index.html`.
3. Haz doble clic sobre él, o arrástralo a tu navegador.
4. La aplicación se abre desde tu sistema de archivos.

Eso es todo. No hay que ejecutar ningún comando.

## 3. Cómo funciona la privacidad

- Todo se guarda en el navegador, mediante `localStorage`.
- No hay peticiones de red durante el uso.
- No hay telemetría.
- No se envía nada a la nube.

Los datos que guardas son privados del navegador y del ordenador que estás usando.

## 4. Qué puedes hacer

### 4.1 Configurar el docente y el centro
Rellena la configuración inicial: centro educativo, código postal, docente responsable. Esto queda guardado localmente.

### 4.2 Crear una programación didáctica
Puedes registrar:

- etapa educativa,
- ciclo o curso,
- materia o área,
- número de unidades didácticas,
- competencias clave trabajadas,
- saberes básicos por bloques,
- unidades didácticas y situaciones de aprendizaje,
- criterios de evaluación y sus instrumentos,
- metodología, elementos transversales, atención a la diversidad y recursos.

La aplicación te ayuda a mantener la estructura, pero tú introduces el contenido pedagógico.

### 4.3 Elegir el contexto normativo
Puedes indicar:

- la etapa y ciclo,
- la materia o área,
- la Comunidad Autónoma,
- los Reales Decretos de referencia,
- el decreto autonómico de currículo,
- la convocatoria o normativa concreta, cuando exista.

Esto permite anclar la programación a la normativa que le corresponde.

### 4.4 Copias y migraciones
Puedes exportar tu programación en **JSON**. Eso te permite:

- guardar una copia de seguridad fuera del navegador,
- pasar tu programación a otro ordenador,
- compartir tu borrador con quien tú decidas.

Solo el docente decide si exporta, cuándo y a dónde.

### 4.5 Imprimir o guardar como PDF
Puedes generar una vista previa HTML pensada para imprimir o guardar como PDF desde el navegador. Así obtienes un documento listo para ser impreso sin depender de librerías externas.

## 5. Buenas prácticas

- Exporta a JSON de forma periódica si quieres conservar tu trabajo más allá de la sesión o del navegador.
- Si usas el ordenador en distintos perfiles o navegadores, recuerda que cada perfil tiene su propio `localStorage`.
- Si tu centro exige un cierto tratamiento de los datos, guarda los JSON en un lugar controlado y protegido.
- Antes de usar una programación final, verifica la normativa estatal, el decreto autonómico y, si aplica, la convocatoria.

## 6. Validación interna

La aplicación avisa cuando detecta incoherencias habituales en la estructura, como:

- criterios de evaluación sin instrumento asociado,
- unidades didácticas sin competencias asignadas,
- competencias específicas sin criterios asociados,
- elementos curriculares incompletos en secciones obligatorias.

Esto no garantiza que el contenido sea correcto, pero ayuda a la coherencia interna.

## 7. Limitaciones locales

- `localStorage` tiene límites de capacidad que varían según el navegador. Si trabajas con muchas programaciones o archivos grandes, puede ser necesario exportar a JSON y borrar lo que ya no necesites.
- Si borras la configuración local del navegador, pierdes lo guardado en esa instalación.
- Esta herramienta no sustituye la revisión profesional ni la verificación de la normativa vigente.

## 8. Trabajar en offline

Una vez abierto `index.html`, puedes desconectar de internet si quieres y seguir trabajando. La aplicación no requiere conexión para funcionar.

Si prefieres no tocar el disco más de la cuenta, puedes abrir `index.html` en modo lectura desde una copia local, trabajar, exportar a JSON cuando necesites guardar, y cerrar.
