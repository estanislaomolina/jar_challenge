# Márgenes adicionales y ensanchado en cero

2026-11-04. Cambio solicitado expresamente por el usuario por indicación comunicada de la organización.

nav_margen_m, nav_alcance_blando_m, nav_reserva_anticipacion_m, margen_giro_m y reserva_detencion_giro_rad: 0.0. El perfil opcional Nav2 también deja inflation_radius y footprint_padding en 0.0. Se conservan dimensiones físicas del chasis/ruedas, cálculo de frenado, detección, replanificación y guardia temporal previamente integrada.

Se habilita cero en validadores y se evita división por cero en costos XY/SE2. Alcance blando cero desactiva esa preferencia. Publicación solicitada sin más chequeos ni comparaciones: no afirmar validación física ni suite completa aprobada.
