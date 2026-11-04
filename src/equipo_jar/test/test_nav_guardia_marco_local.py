from dataclasses import replace
import numpy as np
from equipo_jar.navegacion.guardia import huella_desde_parametros,limitar_velocidad
from equipo_jar.navegacion.ida_vuelta import IdaVuelta,EntradaNavegacion
from equipo_jar.navegacion.tipos import Pose2D
from test_nav_ida_vuelta import Mundo,P_COSTO,P_SEG,HUELLA,P


def test_amcl_no_infla_el_cuerpo_contra_el_scan_local():
    m=Mundo(np.zeros((40,60),dtype=bool))
    nav=IdaVuelta(m.grilla,P_COSTO,P_SEG,HUELLA,P)
    nav.paso(EntradaNavegacion(0.,Pose2D(.5,.5,0.),True,[(3.,0.)]*30,[],std_yaw_rad=.15))
    assert abs(nav.huella_operativa['heading_uncertainty_rad']-.45)<1e-12
    assert nav.huella_guardia['heading_uncertainty_rad']==0.
    assert nav.huella_guardia['corners_base_m']==nav.huella['corners_base_m']
    assert nav.huella_guardia['margin_m']==nav.huella['margin_m']


def test_lateral_libre_deja_pasar_sin_suponer_giro_global():
    h=huella_desde_parametros(-.19,.13,.12,.02)
    points=[(3.,0.)]*30+[(i*.02,.18) for i in range(-30,31)]
    antes=limitar_velocidad(points,.10,0.,dict(h,heading_uncertainty_rad=.45),.3,.25)
    ahora=limitar_velocidad(points,.10,0.,dict(h,heading_uncertainty_rad=0.),.3,.25,reserva_anticipacion_m=0.)
    assert antes[2]['bloqueado'] and ahora[0]==.10 and not ahora[2]['bloqueado']


def test_contacto_y_datos_invalidos_siguen_frenando():
    h=dict(huella_desde_parametros(-.19,.13,.12,.02),heading_uncertainty_rad=0.)
    for points in [[],[(3.,0.)]*30+[(.125,0.)]]:
        x,y,d=limitar_velocidad(points,.1,0.,h,.3,.25,reserva_anticipacion_m=0.)
        assert x==y==0. and d['bloqueado']
