"""Competencia 2026-11-04: un obstáculo fuera del mapa en la ruta obliga a replanificar."""
import math
from equipo_jar.navegacion.ida_vuelta import EntradaNavegacion
from equipo_jar.navegacion.planificador import Ruta
from equipo_jar.navegacion.tipos import Pose2D
from test_mision import nueva


def preparar(obstaculo):
    _, nav = nueva()
    nav.largada = (.5, 1.5, 0.); nav.meta = (2.5, 1.5)
    nav.ruta = Ruta([(.5, 1.5), (2.5, 1.5)], 2., 2.)
    nav.estado = 'YENDO'; nav.seguidor_ida.reiniciar(nav.ruta, 0.)
    puntos = [(obstaculo[0]+.06*math.cos(a/8*2*math.pi), obstaculo[1]+.06*math.sin(a/8*2*math.pi))
              for a in range(8)]
    nav.capa.registrar_bloqueo(1., puntos)
    return nav


def entrada(ahora=1.):
    return EntradaNavegacion(ahora, Pose2D(.5, 1.5, 0.), True, [], [], estampa_scan=(1, 0))


def test_obstaculo_en_la_ruta_replanifica_y_lo_rodea():
    nav = preparar((1.2, 1.5))
    cmd = nav._avanzar(entrada())
    assert cmd.es_cero() and nav.replanificaciones_capa == 1
    assert nav.ruta is not None
    assert min(math.dist(p, (1.2, 1.5)) for p in nav.ruta.puntos) > nav.p_costos.radio_inscripto_m
    assert not nav._ruta_invadida(Pose2D(.5, 1.5, 0.), nav.capa.ocupadas(1.))


def test_obstaculo_lejano_o_fuera_de_la_ruta_no_replanifica():
    for obstaculo in ((2.3, 1.5), (1.2, 2.3)):
        nav = preparar(obstaculo)
        nav._avanzar(entrada())
        assert nav.replanificaciones_capa == 0


def test_replanificacion_por_capa_tiene_limite_de_frecuencia():
    nav = preparar((1.2, 1.5))
    nav._avanzar(entrada(1.))
    nav.ruta = Ruta([(.5, 1.5), (2.5, 1.5)], 2., 2.); nav.seguidor_ida.reiniciar(nav.ruta, 0.)
    nav._avanzar(entrada(1.5))
    assert nav.replanificaciones_capa == 1
