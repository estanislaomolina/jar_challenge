"""El giro de recuperación tolera un hueco breve de datos/TF, pero nunca gira sin guardia."""
from equipo_jar.localizacion_activa import LocalizacionActiva, Observacion


def en_giro_de_recuperacion():
    c = LocalizacionActiva(recuperacion_activa=True)
    c.secuencia_lista = 0
    c.estado, c.giro_activo, c.direccion_activa = 'GIRANDO', True, 1
    c.inicio = c.inicio_giro = c.yaw_inicial = c.ultimo_ahora = 0.0
    return c


def obs(giro_seguro):
    return Observacion(yaw_odom=0.0, pose=(0., 0., 0.), secuencia_pose=1, std_xy=0.05,
                       std_yaw=0.05, concordancia=1.0, distancia_min=1.0, giro_seguro=giro_seguro)


def test_hueco_breve_de_datos_no_aborta_ni_gira():
    c = en_giro_de_recuperacion()
    assert c.paso(0.1, True, None) == 0.0
    assert c.estado == 'GIRANDO'
    assert c.paso(0.9, True, None) == 0.0
    assert c.estado == 'GIRANDO'


def test_vuelven_los_datos_y_el_giro_continua():
    c = en_giro_de_recuperacion()
    c.paso(0.1, True, None)
    assert c.paso(0.4, True, obs(True)) == c.direccion_activa*c.velocidad
    assert c.t_guardia_sin_datos is None


def test_hueco_largo_aborta():
    c = en_giro_de_recuperacion()
    c.paso(0.1, True, None)
    assert c.paso(1.3, True, None) == 0.0
    assert c.estado == 'RECUPERANDO'


def test_guardia_que_dice_no_seguro_aborta_de_inmediato():
    c = en_giro_de_recuperacion()
    assert c.paso(0.1, True, obs(False)) == 0.0
    assert c.estado == 'RECUPERANDO'
