from utils import *
from ITab import *
from matplotlib import pyplot as plt


class TensorController(ITab):

    def __init__(self, model, view, key, t_file):
        super().__init__(model, view)
        self.plot_front = None
        self.plot_end = None
        self.plot_top = None
        self.key = key
        self.t_file = t_file

    def refresh(self):
        if self.m.tensors[self.key] is not None:
            self.refresh_view(0)
            self.refresh_view(1)
            self.refresh_view(2)

    def refresh_view(self, axis):
        if axis == 0:
            self.plot_top = self.plot_image(axis, int(self.v.values[self.key+"-frame-top"]),
                                            "Top", self.key+"-top", self.plot_top)
        elif axis == 1:
            self.plot_front = self.plot_image(axis, int(self.v.values[self.key+"-frame-front"]),
                                              "Front", self.key+"-front", self.plot_front)
        elif axis == 2:
            self.plot_end = self.plot_image(axis, int(self.v.values[self.key+"-frame-end"]),
                                            "End", self.key+"-end", self.plot_end)

    def plot_image(self, axis, frame, title, canvas_key, plot):
        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.imshow(get_slice(axis, frame, self.m.tensors[self.key], self.t_file), cmap='gray',
                  aspect=get_aspect(axis=axis, aspect=self.m.aspects[self.key]))
        ax.axis(False)
        plt.title(title)
        return draw_figure(self.v.window[canvas_key].TKCanvas, fig, plot)