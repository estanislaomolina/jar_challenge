from dataclasses import replace
from test_nav_rodeo_antes_avance import caso
from equipo_jar.navegacion.ida_vuelta import EntradaNavegacion


def preparar():
    nav,e=caso()
    nav.p=replace(nav.p,guardia_activa=True,rodeo_sin_veto=True,plazo_rodeo_sin_veto_s=8.)
    return nav,e


def test_true_hasta_plan_rodeo_y_false_solo_con_ruta_validada():
    nav,e=preparar()
    assert nav.guardia_activa_efectiva and not nav.rodeo_sin_veto
    assert nav._avanzar(e).es_cero()
    assert nav.p.guardia_activa and nav.rodeo_sin_veto
    assert not nav.guardia_activa_efectiva
    assert nav.ruta is nav._rodeo_ruta
    assert not nav._ruta_invadida(e.pose,nav.capa.ocupadas(e.ahora),alcance_m=float('inf'),ignorar_m=0.)


def test_expiracion_reactiva_guardia():
    nav,e=preparar();nav._avanzar(e)
    assert nav.rodeo_sin_veto
    nav._avanzar(replace(e,ahora=10.))
    assert nav.guardia_activa_efectiva and not nav.rodeo_sin_veto


def test_sin_datos_reactiva_antes_de_detener():
    nav,e=preparar();nav._avanzar(e)
    assert nav.paso(EntradaNavegacion(2.,None,False,None,None)).es_cero()
    assert nav.guardia_activa_efectiva


def test_no_hay_false_si_no_hay_plan_valido():
    nav,e=preparar();nav._planificar=lambda *args:False
    assert nav._avanzar(e).es_cero()
    assert nav.guardia_activa_efectiva and not nav.rodeo_sin_veto


def test_nueva_meta_no_hereda_suspension():
    nav,e=preparar();nav._avanzar(e)
    nav.estado='EN_META';nav.largada_fijada=True
    nav.continuar_meta((2.,2.))
    assert nav.guardia_activa_efectiva and not nav.rodeo_sin_veto
