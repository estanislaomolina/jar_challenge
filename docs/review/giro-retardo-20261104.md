# Candidato experimental: giro con retardo

2026-11-04. Port del commit local 788fbb70 sobre el candidato público a16e6b8. Publicado por pedido de Sofía para revisión del equipo; main no se modifica. El hash público difiere porque parte del historial del fork público.

Cambios: perfil real con ganancia yaw 1,5, máximo 0,5 rad/s y piso 0,35; a menos de 0,20 rad del rumbo deseado, pulsos de 0,20 s separados por asentamiento de 1 s. Alineación con tiempo acumulado y latch de atasco, límite real 30 s. Reset de progreso entre metas/fases. Guardia no acepta escalas inferiores al piso para giro puro: nunca se aumenta el comando después de comprobar el barrido. Se preservan replanificación y cambios previos del fork.

Validación del commit local 788fbb70: 158 pruebas pasaron en Python 3.13, numpy/scipy/pytest, incluidas 32 combinaciones sintéticas de retardo 0/0,4/0,6/0,8 s, respuesta 0,42/1 y ángulo inicial 0,25/0,6/1,5/3 rad; zona muerta 0,3, ruido ±0,005 y dinámica sintética de 0,15 s. Incluye regresiones de seguimiento, planificación, guardia y misión. No es la suite ROS 2 Humble ni una validación física. El port público pasa comprobación de sintaxis; no se ejecutó aún esa suite sobre el árbol público completo.

Riesgos pendientes: pulsos pueden ser insuficientes bajo carga; tiempos reales y ruido pueden exceder el modelo; precisión milimétrica de vértices y escape lineal muy lento siguen pendientes. Un fallo durante regreso puede dejar la misión detenida. No se promete escape de cualquier obstáculo ni puntaje. Faltan comparación dinámica, contactos y regreso en robot antes de promover a main.

La nota anterior docs/review/oscilacion-cono-20261104.md describe a16e6b8: los problemas de reset de anclas, tiempo acumulado, latch y escalas submínimas se abordan aquí; sus observaciones sobre regreso, precisión y límites de evidencia continúan abiertas. No publicar logs reales privados como parte de este cambio.
