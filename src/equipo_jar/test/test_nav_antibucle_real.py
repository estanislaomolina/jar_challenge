import math
from dataclasses import replace
from equipo_jar.navegacion.seguimiento import Seguidor
from equipo_jar.navegacion.planificador import Ruta
from equipo_jar.navegacion.tipos import Pose2D, Comando
from test_nav_seguimiento import P

def follower():
    s=Seguidor(replace(P,velocidad_angular_min=.35))
    s.reiniciar(Ruta([(0.,0.),(1.,0.)],1.,1.,[0.,0.]),0.)
    return s

def test_alineacion_supera_zona_muerta_y_avanza():
    s=follower();yaw=.2;avanzo=False
    for k in range(80):
        c=s.paso(k*.1,Pose2D(0.,0.,yaw),1.)
        yaw+=(c.wz if abs(c.wz)>=.3 else 0.)*.1
        avanzo |= math.hypot(c.vx,c.vy)>0
    assert avanzo and not s.atascado

def test_actuador_inmovil_no_gira_indefinidamente():
    s=follower()
    for k in range(90):c=s.paso(k*.1,Pose2D(0.,0.,.2),1.)
    assert s.atascado and c.es_cero()

def test_comandos_no_son_prueba_de_movimiento():
    from equipo_jar.navegacion.ida_vuelta import IdaVuelta, ParametrosIdaVuelta
    iv=object.__new__(IdaVuelta);iv.p=ParametrosIdaVuelta();iv.t_movimiento=None
    iv.ultima_pose=Pose2D(0.,0.,0.);iv.estado='YENDO'
    for t in (0.,10.,21.):
        iv.ahora=t;c=iv._quieto(Comando(0.,0.,.4))
    assert iv.estado=='FALLO' and c.es_cero()
