# Candidato de revisión: guardia, pose y replanificación — 2026-11-04

Base pública exacta: 204a8abf690273d603762ac6bf71b5dd1ae4048e. Cambios se preparan en clon aislado y rama experiment/guardia-pose-replan-20261104; el checkout privado con cambios anteriores se conserva. M6b y main no se promueven.

## Hallazgos comprobados por lectura

1. `_ruta_invadida` empezaba en el vértice más cercano; en la segunda mitad de un tramo podía empezar en el vértice final y omitir el obstáculo por delante. Se usa progreso del seguidor y proyección sobre el tramo activo.
2. La detección anticipada de capa no distinguía datos ya usados para planificar de observaciones nuevas. Se conserva la máscara enviada al planificador y se activa la replanificación anticipada por celdas nuevas. La guardia sigue comprobando todos los retornos, incluidos los ya conocidos; si bloquea, la recuperación existente sigue disponible. El caso de un obstáculo que vuelve a una celda ya incluida puede depender de esa guardia.
3. La pose combinaba dos consultas TF latest separadas. La corrección map<-odom se consulta ahora en la estampa del TF odom<-base. Un fallo temporal detiene navegación; no se extrapola ni se suaviza artificialmente la localización.
4. Frescura por recibo no bastaba para descartar un scan antiguo recién recibido. Se compara captura con estampa de control: rechazar si es más vieja que frescura_sensores_s o más de 0,05 s futura. Pose y TF de láser deben ser finitos.
5. Stdout no permitía discriminar guardia/pose/replan. Añadir resumen cada 2 s con comando propuesto y publicado, guardia, replanificaciones, edad de captura y máximos de corrección map/odom. Las mediciones de salto son diagnóstico; no se cambia la localización por un umbral inventado.

## Guardia y límites pendientes

Se conserva el barrido de huella y los márgenes: no se fuerza avance ni se eleva un comando tras autorizarlo. Pruebas adicionales comprueban veto a contacto y a escape desde contacto con varios giros. Esto no demuestra ausencia universal de choques. La reserva de latencia configurada debe contrastarse con retardo físico/frenado: la correlación de CSV de 0,4–0,6 s no identifica por sí sola ese parámetro. No se reduce protección para conseguir movimiento.

No hay datos crudos de scan/TF/AMCL/navegación de la corrida 2 en el paquete recibido; no se confirma cuál de estos mecanismos causó el atasco. Persisten riesgos de pose errónea, precisión de vértices, escape demasiado lento y fracaso durante regreso. Las 158 pruebas anteriores no validaron todavía el árbol público completo ni el robot.

## Pruebas y entrega

Ejecutar primero pruebas nuevas contra 204a8ab sin cambios, luego contra candidato y suites puras existentes de navegación/misión/capa/costos. Los contratos de pose ejecutan métodos reales extraídos por AST con TF/ROS simulados; no equivalen a integración TF/ROS Humble. Máximo 240 s por conjunto, un proceso y hilos numéricos limitados. No hay bancos Gazebo ni robot en este turno.

Registrar baseline/candidato, JUnit y patch en evidencia privada. Si las pruebas pasan, commit del candidato en rama aislada y publicación sólo del código/tests/esta nota en review/guardia-pose-replan-20261104, como continuación de la publicación autorizada por Sofía; sin logs privados y sin main. Si fallan, no publicar y registrar qué falta. La promoción requiere evaluación comparativa con robot, contactos, puntaje y regreso; no prometer victoria por estas pruebas.
