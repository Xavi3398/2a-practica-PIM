import numpy as np
import time
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TookTooLongException(Exception):
    def __init__(self, img):
        self.img = img


class Point:

    neighbors_2d = [
        [-1, -1], [-1, 0], [-1, 1],
        [0, -1], [0, 1],
        [1, -1], [1, 0], [1, 1]
    ]

    close_neighbors_2d = [
        [-1, 0], [0, -1],
        [0, 1], [1, 0]
    ]

    close_neighbors_3d = [
        [-1, 0, 0], [0, -1, 0],
        [0, 0, -1], [1, 0, 0],
        [0, 1, 0], [0, 0, 1],
    ]

    neighbors_3d = [
        [-1, -1, -1], [-1, -1, 0], [-1, -1, 1],
        [-1, 0, -1], [-1, 0, 0], [-1, 0, 1],
        [-1, 1, -1], [-1, 1, 0], [-1, 1, 1],

        [0, -1, -1], [0, -1, 0], [0, -1, 1],
        [0, 0, -1], [0, 0, 1],
        [0, 1, -1], [0, 1, 0], [0, 1, 1],

        [1, -1, -1], [1, -1, 0], [1, -1, 1],
        [1, 0, -1], [1, 0, 0], [1, 0, 1],
        [1, 1, -1], [1, 1, 0], [1, 1, 1],
    ]


def color_mask(mask, color):
    mask_rgb = np.zeros(shape=(mask.shape[0], mask.shape[1], 3), dtype='uint8')
    for channel in range(3):
        mask_rgb[:, :, channel] = (mask * color[channel]).astype('int')
    return mask_rgb


def painter(img1, img2, alpha2):
    return (img1.astype('float') * (1 - alpha2) + img2.astype('float') * alpha2).astype('uint8')


def get_aspect(aspect, axis):
    if axis == 0:
        return aspect[2] / aspect[1]
    elif axis == 1:
        return aspect[2] / aspect[0]
    elif axis == 2:
        return aspect[0] / aspect[1]


# Convert from screen coordinates to tensor coordinates
# Rotations of the slices have to be reverted
def get_coordinates(x1, y1, axis, frame, shape):

    if axis == 0:  # Front
        x2 = y1
        y2 = shape[1] - x1
        x = y2
        z = x2
        y = frame
    elif axis == 1:  # End
        x2 = y1
        y2 = shape[0] - x1
        y = y2
        z = x2
        x = frame
    else:  # Top
        x2 = shape[1] - x1
        y2 = shape[0] - y1
        x = x2
        y = y2
        z = frame

    return [x, y, z]


def to_hounsfield(value):
    return value * 4096 - 1024


def from_hounsfield(value):
    return (value + 1024) / 4096


# Get current slice of the tensor
def get_slice(axis, frame, tensor):
    if axis == 0:
        img = np.rot90(tensor[frame, :, :], axes=(1, 0))
    elif axis == 1:
        img = np.rot90(tensor[:, frame, :], axes=(1, 0))
    else:
        img = np.rot90(tensor[:, :, frame], k=2)

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
