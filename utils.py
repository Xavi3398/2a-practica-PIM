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


def get_3d_neighbors(point, shape, points):

    neighbors = []
    y, x, z = point
    shape_x = shape[1]
    shape_y = shape[0]
    shape_z = shape[2]

    for y1, x1, z1 in points:
        x2 = x + x1
        y2 = y + y1
        z2 = z + z1
        if 0 <= x2 < shape_x and 0 <= y2 < shape_y and 0 <= z2 < shape_z:
            neighbors.append((y2, x2, z2))

    return neighbors


def get_2d_neighbors(point, shape, points):

    neighbors = []
    y, x = point
    shape_x = shape[1]
    shape_y = shape[0]

    for y1, x1 in points:
        x2 = x + x1
        y2 = y + y1
        if 0 <= x2 < shape_x and 0 <= y2 < shape_y:
            neighbors.append((y2, x2))

    return neighbors


def connected_thresh(img, origin, method="3d_close"):
    t1 = time.time()
    res = np.zeros(shape=img.shape, dtype=img.dtype)
    processed = set()

    # Check number of dimensions and set neighbors method
    if img.ndim == 2:
        x, y = origin
        pending = [(y, x)]
        get_neighbors = get_2d_neighbors
    else:
        x, y, z = origin
        pending = [(y, x, z)]
        get_neighbors = get_3d_neighbors

    # Select neighbors depending on method
    if method == "3d_close":
        points = Point.close_neighbors_3d
    elif method == "3d":
        points = Point.neighbors_3d
    elif method == "2d_close":
        points = Point.close_neighbors_2d
    else:
        points = Point.neighbors_2d

    while len(pending) > 0:

        # Abort if it takes too long
        if time.time() - t1 > 5:
            raise TookTooLongException(res)

        point = pending.pop(0)
        res[point] = 1

        # Add neighbors
        for p in get_neighbors(point, img.shape, points):
            if p not in processed:
                processed.add(p)
                if img[p]:
                    pending.append(p)

    return res


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
