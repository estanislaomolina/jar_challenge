# Integración de revisión — cono y seguimiento

Base pública be7923d: conserva la autoría y cambios de Sofía de a16e6b8, 204a8ab y be7923d (giro con retardo, resets, sincronización TF/scan y diagnóstico).

Integra guardia configurada activa y suspensión efectiva de hasta 8 s únicamente al aplicar un rodeo libre según la capa observada. Reactiva ante nueva invasión, pérdida de datos, cambio de ruta/meta, llegada o plazo. Conserva la política de replanificación por celdas nuevas y el tramo activo del seguidor de Sofía. La guardia local no comparte la incertidumbre angular global de AMCL y la reserva lineal adicional es cero; mantiene frenado, giro futuro y huella con margen extra de 2 cm. Costo blando 0,40 m; escape con alternativas laterales y velocidad máxima 0,05 m/s comprobada mediante barrido.

VALIDACIÓN PENDIENTE: integrar estos cambios no demuestra el paso del cono real ni ausencia de contactos. Durante la suspensión de veto la protección es menor; el plan puede estar equivocado o desactualizarse. Persiste el riesgo de fallo durante regreso. No declarar mejora sobre M6b ni promover por pruebas unitarias solas. Las pruebas anteriores del worker se detuvieron en recolección por falta de rclpy en el Python host; se preparó ejecución ROS Humble en contenedor aislado.

Los logs reales y evidencia de competencia se conservan en privado. Esta rama contiene únicamente fuentes, pruebas y notas de revisión.
