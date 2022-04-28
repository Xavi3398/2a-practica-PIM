import numpy as np
import time
import math
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TookTooLongException(Exception):
    def __init__(self, img):
        self.img = img


def color_mask(mask, color):
    mask_rgb = np.zeros(shape=(mask.shape[0], mask.shape[1], 3), dtype='uint8')
    for channel in range(3):
        mask_rgb[:, :, channel] = (mask * color[channel]).astype('int')
    return mask_rgb


def painter(img1, img2, alpha2):
    # Apply alpha to image and mask
    img = (img1.astype('float') * (1 - alpha2) + img2.astype('float') * alpha2).astype('uint8')

    # Remove alpha where mask is black
    # Avoids losing color when adding more layers
    img[img2 == 0] = img1[img2 == 0]
    return img


def get_color_map(ids):
    color_map = {}
    for id_region in ids:
        color_map[id_region] = list(np.random.choice(range(256), size=3))
    return color_map


def set_color_map(ids, color):
    color_map = {}
    for id_region in ids:
        color_map[id_region] = color
    return color_map


def get_aspect(aspect, axis):
    if axis == 0:
        return aspect[2] / aspect[1]
    elif axis == 1:
        return aspect[0] / aspect[2]
    elif axis == 2:
        return aspect[0] / aspect[1]


def to_hounsfield(value):
    return value * 4096 - 1024


def from_hounsfield(value):
    return (value + 1024) / 4096


# Get current slice of the tensor
def get_slice(axis, frame, tensor, t_file):
    if t_file == "file":
        if axis == 0:
            img = tensor[frame, :, :]
        elif axis == 1:
            img = np.rot90(tensor[:, tensor.shape[1] - 1 - frame, :], k=2)
        else:
            img = np.rot90(tensor[:, :, frame], k=2)
    else:
        if axis == 0:
            img = np.rot90(tensor[tensor.shape[0] - 1 - frame, :, :], k=2)
        elif axis == 1:
            img = tensor[:, frame, :]
        else:
            img = tensor[:, :, frame]

    return img


def draw_figure(canvas, figure, tk_agg):
    delete_figure_agg(tk_agg)
    tk_agg = FigureCanvasTkAgg(figure, canvas)
    tk_agg.draw()
    tk_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return tk_agg


def delete_figure_agg(tk_agg):
    if tk_agg is not None:
        tk_agg.get_tk_widget().forget()
        plt.close('all')


# Convert from screen coordinates to tensor coordinates
# Rotations of the slices have to be reverted
def get_coordinates(x1, y1, axis, frame, shape, t_file):
    if t_file == "file":  # Avg and atlas
        if axis == 0:  # Top
            x = x1
            z = y1
            y = frame
        elif axis == 1:  # Front
            x = shape[2] - x1
            y = shape[0] - y1
            z = shape[1] - 1 - frame
        else:  # End
            z = shape[1] - x1
            y = shape[0] - y1
            x = frame
    else:  # Patient
        if axis == 0:  # Top
            x = shape[2] - x1
            z = shape[1] - y1
            y = shape[0] - 1 - frame
        elif axis == 1:  # Front
            x = x1
            y = y1
            z = frame
        else:  # End
            z = x1
            y = y1
            x = frame

    return [int(round(i)) for i in [y, z, x]]


def print_points_list(points_list):
    return ["(" + str(point[0]) + ", " + str(point[1]) + ", " + str(point[2]) + ")" for point in points_list]


def traslacion(punto, vector_traslacion):
    x, y, z = punto
    t_1, t_2, t_3 = vector_traslacion
    punto_transformado = (x+t_1, y+t_2, z+t_3)
    return punto_transformado


def rotacion_axial(punto, angulo_en_radianes, eje_traslacion):
    x, y, z = punto
    v_1, v_2, v_3 = eje_traslacion
    #   Vamos a normalizarlo para evitar introducir restricciones en el optimizador
    v_norm = math.sqrt(sum([coord ** 2 for coord in [v_1, v_2, v_3]]))
    v_1, v_2, v_3 = v_1 / v_norm, v_2 / v_norm, v_3 / v_norm
    #   Calcula cuaternión del punto
    p = (0, x, y, z)
    #   Calcula cuaternión de la rotación
    cos, sin = math.cos(angulo_en_radianes / 2), math.sin(angulo_en_radianes / 2)
    q = (cos, sin * v_1, sin * v_2, sin * v_3)
    #   Calcula el conjugado
    q_conjugado = (cos, -sin * v_1, -sin * v_2, -sin * v_3)
    #   Calcula el cuaternión correspondiente al punto rotado
    p_prima = multiplicar_quaterniones(q, multiplicar_quaterniones(p, q_conjugado))
    # Devuelve el punto rotado
    punto_transformado = p_prima[1], p_prima[2], p_prima[3]
    return punto_transformado


def transformacion_rigida_3D(punto, parametros):
    x, y, z = punto
    t_11, t_12, t_13, alpha_in_rad, v_1, v_2, v_3 = parametros
    #   Aplicar una primera traslación
    x, y, z = traslacion(punto=(x, y, z), vector_traslacion=(t_11, t_12, t_13))
    #   Aplicar una rotación axial traslación
    x, y, z = rotacion_axial(punto=(x, y, z), angulo_en_radianes=alpha_in_rad, eje_traslacion=(v_1, v_2, v_3))
    return x, y, z


def transformacion_rigida_3D_invertida(punto, parametros):
    x, y, z = punto
    t_11, t_12, t_13, alpha_in_rad, v_1, v_2, v_3 = parametros

    # invertir parámetros de translación y ángulo de rotación
    t_11 = -t_11
    t_12 = -t_12
    t_13 = -t_13
    alpha_in_rad = -alpha_in_rad

    # Aplicar primero la  rotación axial
    x, y, z = rotacion_axial(punto=(x, y, z), angulo_en_radianes=alpha_in_rad, eje_traslacion=(v_1, v_2, v_3))

    # Aplicar segundo la traslación
    x, y, z = traslacion(punto=(x, y, z), vector_traslacion=(t_11, t_12, t_13))

    return x, y, z


def multiplicar_quaterniones(q1, q2):
    """Multiplica cuaterniones expresados como (1, i, j, k)."""
    return (
        q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3],
        q1[0] * q2[1] + q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2],
        q1[0] * q2[2] - q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1],
        q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0]
    )


def cuaternion_conjugado(q):
    """Conjuga un cuaternión expresado como (1, i, j, k)."""
    return (
        q[0], -q[1], -q[2], -q[3]
    )


def residuos_cuadraticos(lista_puntos_ref, lista_puntos_inp):
    """Devuelve un array con los residuos cuadráticos del ajuste."""
    residuos = []
    for p1, p2 in zip(lista_puntos_ref, lista_puntos_inp):
        p1 = np.asarray(p1, dtype='float')
        p2 = np.asarray(p2, dtype='float')
        residuos.append(np.sqrt(np.sum(np.power(p1-p2, 2))))
    return np.power(residuos, 2)


def mse(lista_puntos_ref, lista_puntos_inp):
    residuos = residuos_cuadraticos(lista_puntos_ref, lista_puntos_inp)
    return sum(residuos) / len(residuos)
