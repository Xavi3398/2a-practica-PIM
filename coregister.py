import time

from utils import *
from ITab import *
from matplotlib import pyplot as plt
from scipy.optimize import least_squares
from threading import Thread

class Coregister(ITab):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.plots = {
            "patient": {
                "top": None,
                "front": None,
                "end": None
            },
            "avg": {
                "top": None,
                "front": None,
                "end": None
            }
        }

    def refresh(self):
        if self.m.tensors["patient"] is not None:
            self.refresh_view(0, "patient_points", "patient")
            self.refresh_view(1, "patient_points", "patient")
            self.refresh_view(2, "patient_points", "patient")
        if self.m.tensors["avg"] is not None:
            self.refresh_view(0, "avg_points", "avg")
            self.refresh_view(1, "avg_points", "avg")
            self.refresh_view(2, "avg_points", "avg")

    def refresh_view(self, axis, gui_key, tensor_key):
        if axis == 0:
            self.plots[tensor_key]["top"] = self.plot_image(axis, int(self.v.values[gui_key+"-frame-top"]),
                                            "Top", gui_key+"-top", self.plots[tensor_key]["top"], tensor_key)
        elif axis == 1:
            self.plots[tensor_key]["front"] = self.plot_image(axis, int(self.v.values[gui_key+"-frame-front"]),
                                              "Front", gui_key+"-front", self.plots[tensor_key]["front"], tensor_key)
        elif axis == 2:
            self.plots[tensor_key]["end"] = self.plot_image(axis, int(self.v.values[gui_key+"-frame-end"]),
                                            "End", gui_key+"-end", self.plots[tensor_key]["end"], tensor_key)

    def plot_image(self, axis, frame, title, canvas_key, plot, tensor_key):
        fig = plt.figure(figsize=(3, 3))
        ax = fig.add_subplot(111)
        ax.imshow(get_slice(axis, frame, self.m.tensors[tensor_key], "file" if tensor_key == "avg" else "folder"),
                  cmap='gray', aspect=get_aspect(axis=axis, aspect=self.m.aspects[tensor_key]))
        ax.axis(False)
        plt.title(tensor_key.capitalize() + ", " + title)

        if tensor_key == "patient":
            if title == "Top":
                fig.canvas.mpl_connect('button_press_event', self.click_event_patient_top)
            elif title == "Front":
                fig.canvas.mpl_connect('button_press_event', self.click_event_patient_front)
            elif title == "End":
                fig.canvas.mpl_connect('button_press_event', self.click_event_patient_end)
        elif tensor_key == "avg":
            if title == "Top":
                fig.canvas.mpl_connect('button_press_event', self.click_event_avg_top)
            elif title == "Front":
                fig.canvas.mpl_connect('button_press_event', self.click_event_avg_front)
            elif title == "End":
                fig.canvas.mpl_connect('button_press_event', self.click_event_avg_end)

        return draw_figure(self.v.window[canvas_key].TKCanvas, fig, plot)

    def click_event(self, key, perspective, axis, ev):

        if ev.xdata is not None and ev.ydata is not None:
            self.m.points[key].append(
                get_coordinates(ev.xdata, ev.ydata, axis, self.v.values[key+"_points"+"-frame-"+perspective],
                                self.m.tensors[key].shape, "file" if key == "avg" else "folder"))
            self.v.window["points-"+key].Update(values=print_points_list(self.m.points[key]))

    def click_event_patient_top(self, ev):
        self.click_event("patient", "top", 0, ev)

    def click_event_patient_front(self, ev):
        self.click_event("patient", "front", 1, ev)

    def click_event_patient_end(self, ev):
        self.click_event("patient", "end", 2, ev)

    def click_event_avg_top(self, ev):
        self.click_event("avg", "top", 0, ev)

    def click_event_avg_front(self, ev):
        self.click_event("avg", "front", 1, ev)

    def click_event_avg_end(self, ev):
        self.click_event("avg", "end", 2, ev)



    def compute_coregister(self):
        landmarks_inp = self.m.points["patient"]
        landmarks_ref = self.m.points["avg"]

        landmarks_inp = [[0,1,1],
                         [0,1,0],
                         [0,0,1],
                         [0,0,0],
                         [1,1,1],
                         [1,1,0],
                         [1,0,1],
                         [1,0,0]]

        landmarks_ref = [[95,90,20],
                         [95,89,158],
                         [95,157,34],
                         [95,161,139],
                         [25,50,43],
                         [25,50,134],
                         [25,149,51],
                         [25,148,128]]

        # MSE before
        self.v.window["mse-before"].Update(value=mse(landmarks_ref, landmarks_inp))

        # Parameter initialization
        parametros_iniciales = [0, 0, 0, 0, 1, 0, 0]
        for i in range(3):
            centroide_ref = sum([punto[i] for punto in landmarks_ref]) / len(landmarks_ref)
            centroide_inp = sum([punto[i] for punto in landmarks_inp]) / len(landmarks_inp)
            parametros_iniciales[i] = centroide_ref - centroide_inp

        # MSE after initializing parameters
        self.v.window["mse-init"].Update(
            value=mse(landmarks_ref, [transformacion_rigida_3D(l, parametros_iniciales) for l in landmarks_inp]))

        def funcion_a_minimizar(parametros):
            landmarks_inp_transf = [transformacion_rigida_3D(landmark, parametros) for landmark in landmarks_inp]
            # Debe devolver una array 1-dimensional con los errores cuadráticos medios.
            return residuos_cuadraticos(landmarks_ref, landmarks_inp_transf)

        # Optimize transformation
        self.m.transform_params = least_squares(funcion_a_minimizar, x0=parametros_iniciales, verbose=1).x

        # MSE after optimization
        self.v.window["mse-after"].Update(
            value=mse(landmarks_ref, [transformacion_rigida_3D(l, self.m.transform_params) for l in landmarks_inp]))

        # Transformation results
        self.v.window["translation-x"].Update(value=self.m.transform_params[0])
        self.v.window["translation-y"].Update(value=self.m.transform_params[1])
        self.v.window["translation-z"].Update(value=self.m.transform_params[2])
        self.v.window["rotation-v"].Update(value=self.m.transform_params[3])
        self.v.window["rotation-x"].Update(value=self.m.transform_params[4])
        self.v.window["rotation-y"].Update(value=self.m.transform_params[5])
        self.v.window["rotation-z"].Update(value=self.m.transform_params[6])

    def compute_patient_to_avg(self):
        self.m.tensors["patient->avg"] = Coregister.transform_tensor(tensor1=self.m.tensors["patient"],
                                                                     tensor2=self.m.tensors["avg"],
                                                                     transf_params=self.m.transform_params)

    def compute_atlas_to_patient(self):

        transform_params = self.m.transform_params
        transform_params[0:3] = -transform_params[0:3]
        print(transform_params[0:3])

        self.m.tensors["atlas->patient"] = Coregister.transform_tensor(tensor1=self.m.tensors["atlas"],
                                                                       tensor2=self.m.tensors["patient"],
                                                                       transf_params=transform_params)

    @staticmethod
    def transform_tensor(tensor1, tensor2, transf_params):

        result = np.zeros(shape=tensor2.shape)
        counter = 0
        finish = tensor1.shape[0] * tensor1.shape[1] * tensor1.shape[2]
        t1 = time.time()

        for y in range(tensor1.shape[0]):
            for z in range(tensor1.shape[1]):
                for x in range(tensor1.shape[2]):
                    x2, y2, z2 = [int(i) for i in transformacion_rigida_3D((x, y, z), transf_params)]
                    if 0 <= y2 < tensor2.shape[0] and 0 <= z2 < tensor2.shape[1] and 0 <= x2 < tensor2.shape[2]:
                        result[int(y2), int(z2), int(x2)] = tensor1[y, z, x]

                    if time.time() - t1 > 5:
                        print(counter, "/", finish)
                        t1 = time.time()

                    counter += 1

        return result
