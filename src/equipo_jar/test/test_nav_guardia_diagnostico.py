from dataclasses import replace
import numpy as np
from equipo_jar.navegacion.ida_vuelta import IdaVuelta,EntradaNavegacion
from equipo_jar.navegacion.tipos import Pose2D
from equipo_jar.navegacion.planificador import Ruta
from test_nav_ida_vuelta import Mundo,P_COSTO,P_SEG,HUELLA,P


def caso(active):
    m=Mundo(np.zeros((60,60),dtype=bool))
    nav=IdaVuelta(m.grilla,P_COSTO,P_SEG,HUELLA,replace(P,regreso_automatico=False,guardia_activa=active))
    nav.largada=(.7,.7,0.);nav.meta=(1.4,.7)
    nav.ruta=Ruta([(.7,.7),(1.4,.7)],.7,.7)
    nav.estado='YENDO';nav.seguidor_ida.reiniciar(nav.ruta,0.)
    e=EntradaNavegacion(1.,Pose2D(.7,.7,0.),True,[(3.,0.)]*30+[(.125,0.)],[])
    return nav,nav._avanzar(e)


def test_diagnostico_no_ignora_un_obstaculo_que_invade_el_plan():
    nav,cmd=caso(False)
    assert cmd.es_cero()
    assert nav.ultima_guardia['solo_diagnostico']
    assert not nav.ultima_guardia.get('recuperacion_margen',False)


def test_modo_activo_conserva_veto():
    nav,cmd=caso(True)
    assert cmd.es_cero() and not nav.ultima_guardia.get('solo_diagnostico',False)


def test_datos_ausentes_siguen_deteniendo():
    nav,_=caso(False)
    assert nav.paso(EntradaNavegacion(2.,None,False,None,None)).es_cero()
