"""Contratos de pose/replan y guardia. Extracción AST no sustituye integración ROS."""
import ast,json,math,os
from pathlib import Path
from types import SimpleNamespace as N
from dataclasses import replace
import numpy as np
import pytest
from equipo_jar.navegacion.tipos import Pose2D,Comando
from equipo_jar.navegacion.planificador import Ruta
from equipo_jar.navegacion.ida_vuelta import IdaVuelta,EntradaNavegacion
from equipo_jar.navegacion.guardia import limitar_velocidad,recuperar_margen,puntos_desde_scan
from test_nav_ida_vuelta import Mundo,P_COSTO,P_SEG,HUELLA,P

def nav():
    world=Mundo(np.zeros((60,60),dtype=bool))
    iv=IdaVuelta(world.grilla,P_COSTO,P_SEG,HUELLA,replace(P,regreso_automatico=False))
    iv.estado='YENDO';iv.largada=(.5,1.5,0.);iv.meta=(2.5,1.5);iv.yaw_trayecto=0.
    iv.ruta=Ruta([(.5,1.5),(2.5,1.5)],2.,2.)
    iv.seguidor.reiniciar(iv.ruta,0.)
    return iv

@pytest.mark.parametrize('orientada',[False,True])
def test_no_salta_segunda_mitad_del_segmento(orientada):
    iv=nav()
    if orientada:
        iv.ruta=Ruta([(.5,1.5),(2.5,1.5)],2.,2.,[0.,0.])
        iv.seguidor.reiniciar(iv.ruta,0.);iv.seguidor.indice_orientado=1
    occupied=np.zeros_like(iv.grilla.ocupada)
    occupied[iv.grilla.a_celda(2.2,1.5)]=True
    assert iv._ruta_invadida(Pose2D(1.8,1.5,0.),occupied)

def test_obstaculo_ya_planificado_no_reinicia_otra_vez():
    iv=nav();iv.ahora=10.;iv.capa.registrar_bloqueo(10.,[(1.2,1.5)])
    iv._capa_planificada=iv.capa.ocupadas(10.).copy()
    # Plan ya aceptado y vehículo quieto: comprobar política de replan, no autorizar movimiento.
    iv.seguidor.paso=lambda *args:Comando.cero()
    hits=[];iv._replanificar_por_capa=lambda e,fase:(hits.append(fase) or Comando.cero())
    entrada=EntradaNavegacion(10.,Pose2D(.5,1.5,0.),True,[(3.,0.)]*30,[])
    assert iv._avanzar(entrada).es_cero()
    assert not hits
    iv.capa.registrar_bloqueo(10.,[(1.7,1.5)])
    iv._avanzar(entrada)
    assert hits==['YENDO']

@pytest.mark.parametrize('w',[0.,.35,.5,-.5])
def test_guardia_no_autoriza_contacto_ni_escape_desde_contacto(w):
    points=[(3.,0.)]*30+[(0.,0.)]
    vx,vy,diag=limitar_velocidad(points,.15,0.,HUELLA,.3,.6,wz=w)
    assert diag['bloqueado'] and vx==vy==0.
    assert recuperar_margen(points,HUELLA,.3,.6) is None

class Time:
    def __init__(self,stamp=None):self.stamp=stamp
    @classmethod
    def from_msg(cls,msg):return cls(msg)
class TransformException(Exception):pass

def stamp(t):return N(sec=int(t),nanosec=round((t-int(t))*1e9))
def transform(x=0.,y=0.,yaw=0.,t=100.):
    return N(header=N(stamp=stamp(t)),transform=N(translation=N(x=x,y=y),rotation=N(yaw=yaw)))

def metodo(nombre):
    source=Path(os.environ['JAR_NODO_SOURCE']).read_text()
    tree=ast.parse(source)
    klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='NodoEquipo')
    func=next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name==nombre)
    module=ast.fix_missing_locations(ast.Module(body=[func],type_ignores=[]))
    env=dict(math=math,Time=Time,TransformException=TransformException,Pose2D=Pose2D,
             yaw=lambda q:q.yaw,puntos_desde_scan=puntos_desde_scan,json=json,
             String=lambda **kwargs:N(**kwargs),time=N(monotonic=lambda:20.))
    exec(compile(module,'<método real del candidato>','exec'),env)
    return env[nombre]

def control(scan_t=99.8,x=1.):
    requests=[]
    def lookup(target,source,time):
        requests.append((target,source,time.stamp))
        # El latest de corrección es distinto del válido en t=100.
        return transform(x=x,y=1.) if target=='odom' else transform(x=10. if time.stamp is None else 0.)
    scan=N(header=N(stamp=stamp(scan_t),frame_id='laser'),ranges=[2.]*64,
           angle_min=-math.pi,angle_increment=2*math.pi/64,range_min=.1,range_max=5.)
    node=N(tf_buffer=N(lookup_transform=lookup,lookup_transform_full=lambda *args:transform()),
           odom=N(header=N(stamp=stamp(100.))),t_odom=10.4,
           historial_scan=[(scan,10.4)],diagnostico_observacion={},valor=lambda key:1.5)
    return node,requests

def test_pose_compone_tf_del_mismo_instante():
    node,requests=control();data=metodo('datos_navegacion')(node,10.5,N())
    assert data is not None
    query=next(req for req in requests if req[0]=='map')
    assert query[2] is not None and query[2].sec==100
    assert data[0].x==pytest.approx(1.)

@pytest.mark.parametrize('scan_t',[96.,100.2])
def test_scan_recien_recibido_con_captura_invalida_no_se_usa(scan_t):
    node,_=control(scan_t=scan_t)
    assert metodo('datos_navegacion')(node,10.5,N()) is None

def test_pose_no_finita_no_alcanza_planificador():
    node,_=control(x=float('nan'))
    assert metodo('datos_navegacion')(node,10.5,N()) is None

def test_log_incluye_comando_final_y_guardia_sin_ruta_completa():
    lines=[];msgs=[]
    summary=dict(estado='BLOQUEADO',motivo='Obstáculo',pose_control=[.5,1.5,0.],
                 guardia=dict(bloqueado=True,motivo='barrido'),ruta=[[1.,2.]]*100)
    node=N(duraciones=[],numero_ciclo=2,navegacion=N(resumen=lambda:dict(summary)),
           valor=lambda key:False if key=='prueba_en_seco' else 'mision',motivo_meta='',
           pub_navegacion=N(publish=msgs.append),diagnostico_observacion={},
           get_logger=lambda:N(info=lines.append),_ultimo_cmd_publicado=[0.,0.,0.])
    metodo('publicar_navegacion')(node)
    assert lines
    result=json.loads(lines[0].split('Navegación: ',1)[1])
    assert result['comando_publicado']==[0.,0.,0.]
    assert result['guardia']['bloqueado'] is True
    assert 'ruta' not in result
