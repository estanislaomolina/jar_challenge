import math
import pytest
from equipo_jar.navegacion.guardia import limitar_velocidad,recuperar_margen,huella_desde_parametros
from equipo_jar.navegacion.ida_vuelta import ParametrosIdaVuelta


def h():
    return dict(huella_desde_parametros(-.19,.13,.12,.04),heading_uncertainty_rad=0.)


def test_reserva_reducida_deja_velocidad_sin_eliminar_frenado():
    points=[(3.,0.)]*30+[(.4,0.)]
    old=limitar_velocidad(points,.3,0.,h(),.5,.15)
    new=limitar_velocidad(points,.3,0.,h(),.5,.15,reserva_anticipacion_m=.02)
    assert old[0]<new[0] and new[0]==.3
    assert new[2]['holgura_minima_m']>0


def test_contacto_y_datos_invalidos_siguen_bloqueando():
    for points in [[],[(3.,0.)]*30+[(.16,0.)]]:
        x,y,d=limitar_velocidad(points,.3,0.,h(),.5,.15,reserva_anticipacion_m=.02)
        assert x==y==0. and d['bloqueado']


def test_escape_lateral_rapido_aumenta_separacion_sin_perder_barrido():
    points=[(3.,0.)]*30+[(.16,.14)]
    r=recuperar_margen(points,h(),.5,.15,(1.,0.),.05)
    assert r[0]>0 and r[1]<0 and math.hypot(*r[:2])<=.05+1e-12
    assert r[2]['separacion_final_m']>r[2]['separacion_inicial_m']
    assert r[2]['separacion_minima_barrido_m']>=r[2]['separacion_inicial_m']-1e-6
    assert recuperar_margen([(3.,0.)]*30+[(.12,0.)],h(),.5,.15,(1.,0.),.05) is None


@pytest.mark.parametrize('v',[-1.,float('nan'),float('inf')])
def test_reserva_invalida_no_mueve(v):
    assert limitar_velocidad([(3.,0.)]*30,.2,0.,h(),.5,.15,reserva_anticipacion_m=v)[2]['bloqueado']
    with pytest.raises(ValueError):ParametrosIdaVuelta(reserva_anticipacion_m=v)
