from utils import *
from ITab import *
from matplotlib import pyplot as plt


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
        print(axis, gui_key, tensor_key)
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
        print("key:", key, "perspective:", perspective, "ev:", (ev.xdata, ev.ydata))
        self.m.points[key].append(
            get_coordinates(ev.xdata, ev.ydata, axis, self.v.values[key+"_points"+"-frame-"+perspective],
                            self.m.tensors[key].shape, "file" if key == "avg" else "folder"))
        self.v.window["points-"+key].Update(values=self.m.points[key])

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
