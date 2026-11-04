import math
from dataclasses import replace
import numpy as np
from equipo_jar.navegacion.ida_vuelta import IdaVuelta,EntradaNavegacion
from equipo_jar.navegacion.planificador import Ruta
from equipo_jar.navegacion.tipos import Pose2D
from test_nav_ida_vuelta import Mundo,P_COSTO,P_SEG,HUELLA,P


def caso():
    m=Mundo(np.zeros((60,60),dtype=bool))
    nav=IdaVuelta(m.grilla,P_COSTO,P_SEG,HUELLA,replace(P,regreso_automatico=False,guardia_activa=False))
    nav.largada=(.5,1.5,0.);nav.meta=(2.5,1.5)
    nav.ruta=Ruta([(.5,1.5),(2.5,1.5)],2.,2.)
    nav.estado='YENDO';nav.seguidor_ida.reiniciar(nav.ruta,0.)
    pts=[(1.9+.06*math.cos(a*math.pi/4),1.5+.06*math.sin(a*math.pi/4)) for a in range(8)]
    nav.capa.registrar_bloqueo(1.,pts)
    e=EntradaNavegacion(1.,Pose2D(1.6,1.5,0.),True,[(3.,0.)]*30,pts,estampa_scan=(1,0))
    return nav,e


def test_no_salta_obstaculo_por_elegir_vertice_despues_de_el():
    nav,e=caso()
    assert nav._ruta_invadida(e.pose,nav.capa.ocupadas(1.),ignorar_m=0.)


def test_con_guardia_false_se_obtiene_rodeo_antes_de_avanzar():
    nav,e=caso()
    assert nav._avanzar(e).es_cero()
    assert nav.replanificaciones_capa==1 and nav.ruta is not None
    assert not nav._ruta_invadida(e.pose,nav.capa.ocupadas(1.),ignorar_m=0.)
    assert any(abs(y-1.5)>.1 for x,y in nav.ruta.puntos)


def test_durante_limite_de_replan_no_sigue_ruta_invadida():
    nav,e=caso();nav.t_replan_capa=.9
    assert nav._avanzar(e).es_cero()
    assert nav.ultima_guardia['esperando_rodeo']
    assert nav.replanificaciones_capa==0
