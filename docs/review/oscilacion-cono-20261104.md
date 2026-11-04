# Candidato de revisión: oscilación junto a obstáculo

2026-11-04. Publicado por pedido explícito de Sofía para revisión del equipo. Port del candidato local 138fcaa6 sobre main público ead38ffb786cec547a3ff110aeb2aee7d30c1828; el hash público es distinto porque los repositorios y el padre difieren. Se conservan los cambios existentes de localización, ráfagas de percepción y replanificación de main. No se publica el historial ni la evidencia privada.

NO VALIDADO PARA DESPLEGAR. No fusionar a main por este cambio solamente.

Cambios: piso angular configurable en alineación orientada (perfil real 0,35 rad/s), plazo de alineación de 8 s y detección de movimiento por pose en vez de comandos enviados. La guardia de colisión sigue activa.

Estado de pruebas: el intento local offline NO ejecutó pytest: faltó numpy en caché. No son pruebas aprobadas ni fallos funcionales medidos. Tampoco se probó el port sobre este head público.

Hallazgos pendientes de corregir/validar durante la auditoría:
- La guardia puede reducir el giro por debajo del piso y devolverlo a la zona muerta. No se debe aumentar velocidad después de comprobar la guardia.
- El detector puede conservar anclas de pose/tiempo de una meta anterior; revisar reinicialización al cambiar de meta.
- El plazo de alineación se reinicia al pasar momentáneamente a traslación: revisar oscilaciones en el umbral.
- El flag de atasco se revisa desde navegación, pero el seguidor por sí solo no conserva necesariamente salida cero ante una pose posterior distinta.
- FALLO durante búsqueda permite descartar una vista; durante regreso deja la misión REGRESANDO y detenida. Un fallo acotado no garantiza recuperar la marcha.
- Los vértices SE2 pueden exigir milímetros de precisión; comprobar con ruido real sin relajar la geometría a ciegas.
- Escape de margen usa 0,005–0,01 m/s: respuesta física no medida.
- Verificar edad de LiDAR/TF, ruido de pose y latencia efectiva. El relato del cono no identifica por sí solo la causa.

Próxima acción: corregir lo anterior, ejecutar suites navegación/misión en Humble y comparar baseline/candidato con zona muerta, ruido, contactos, tiempos y regreso. No se afirma que este candidato resuelva el atasco observado.
