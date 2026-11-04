"""Modelo sintético, no reproducción del robot ni promoción de estrategia."""
from dataclasses import replace
from collections import deque
import math, json, os
import pytest
from equipo_jar.navegacion.seguimiento import Seguidor
from equipo_jar.navegacion.planificador import Ruta
from equipo_jar.navegacion.tipos import Pose2D, Comando
from test_nav_seguimiento import P

@pytest.mark.parametrize('retardo',[0.,.4,.6,.8])
@pytest.mark.parametrize('respuesta',[.42,1.])
@pytest.mark.parametrize('inicial',[.25,.6,1.5,3.])
def test_alinea_con_retardo_y_zona_muerta(retardo,respuesta,inicial):
    dt=.05; p=replace(P,ganancia_yaw=1.5,velocidad_angular_min=.35,
        velocidad_angular_max=.5,plazo_alineacion_s=30.,
        pulso_giro_s=.2,asentamiento_giro_s=1.)
    s=Seguidor(p);s.reiniciar(Ruta([(0.,0.),(1.,0.)],1.,1.,[0.,0.]),0.)
    queue=deque([0.]*round(retardo/dt));yaw=inicial;wr=0.;paso=None
    for k in range(900):
        ruido=.005*math.sin(k*.37)
        c=s.paso(k*dt,Pose2D(0.,0.,yaw+ruido),1.)
        queue.append(c.wz);act=queue.popleft()
        destino=respuesta*act if abs(act)>=.3 else 0.
        wr+=(destino-wr)*min(1.,dt/.15);yaw+=wr*dt
        if math.hypot(c.vx,c.vy)>0:
            paso=k*dt;break
        if s.atascado:break
    row=dict(retardo_s=retardo,respuesta=respuesta,yaw_inicial=inicial,
             primer_avance_s=paso,yaw_al_avanzar=yaw,atascado=s.atascado)
    if os.environ.get('JAR_ENSAYOS'):
        with open(os.environ['JAR_ENSAYOS'],'a') as f:f.write(json.dumps(row)+'\n')
    assert paso is not None,row
    assert abs(yaw)<.10,row

def test_atasco_se_mantiene_hasta_reiniciar():
    s=Seguidor(P);r=Ruta([(0.,0.),(1.,0.)],1.,1.,[0.,0.]);s.reiniciar(r,0.)
    for k in range(100):s.paso(k*.1,Pose2D(0.,0.,.3),1.)
    assert s.atascado
    assert s.paso(11.,Pose2D(0.,0.,0.),1.).es_cero()
    s.reiniciar(r,0.);assert not s.atascado

def test_alternancia_umbral_no_borra_tiempo_acumulado():
    s=Seguidor(P);s.reiniciar(Ruta([(0.,0.),(1.,0.)],1.,1.,[0.,0.]),0.)
    # Fuera del primer vértice: el error cruza el umbral de traslación/giro.
    for k in range(400):s.paso(k*.1,Pose2D(.1,0.,.081 if k%2 else .079),1.)
    assert s.atascado

def test_nueva_meta_no_hereda_ancla_ni_plazo():
    import numpy as np
    from equipo_jar.navegacion.ida_vuelta import IdaVuelta
    from test_nav_ida_vuelta import Mundo,P_COSTO,P_SEG,HUELLA,P as PI
    world=Mundo(np.zeros((60,60),dtype=bool))
    iv=IdaVuelta(world.grilla,P_COSTO,P_SEG,HUELLA,replace(PI,regreso_automatico=False))
    iv.estado='FALLO';iv.largada_fijada=True;iv.ancla_progreso=Pose2D(0.,0.,0.)
    iv.ancla_xy=iv.ancla_progreso;iv.t_progreso_xy=0.;iv.t_movimiento=0.
    iv.continuar_meta((1.,1.));iv.ahora=100.;iv.t_movimiento=100.
    iv.ultima_pose=Pose2D(0.,0.,0.);iv._quieto(Comando(0.,0.,.4))
    assert iv.estado!='FALLO'
    assert iv.t_progreso_xy==100.
