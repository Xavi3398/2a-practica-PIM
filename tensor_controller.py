from utils import *
from ITab import *
from matplotlib import pyplot as plt


class TensorController(ITab):

    def __init__(self, model, view, key):
        super().__init__(model, view)
        self.plot_front = None
        self.plot_end = None
        self.plot_top = None
        self.key = key

    def refresh(self):
        if self.m.tensors[self.key] is not None:
            self.refresh_view(0)
            self.refresh_view(1)
            self.refresh_view(2)

    def refresh_view(self, axis):
        if axis == 0:
            self.plot_front = self.plot_image(0, int(self.v.values[self.key+"-frame-front"]),
                                              "Front", self.key+"-front", self.plot_front)
        elif axis == 1:
            self.plot_end = self.plot_image(1, self.m.tensors[self.key].shape[1] - 1 -
                                            int(self.v.values[self.key+"-frame-end"]),
                                            "End", self.key+"-end", self.plot_end)
        else:
            self.plot_top = self.plot_image(2, int(self.v.values[self.key+"-frame-top"]),
                                            "Top", self.key+"-top", self.plot_top)

    def plot_image(self, axis, frame, title, canvas_key, plot):
        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.imshow(get_slice(axis, frame, self.m.tensors[self.key]), cmap='gray',
                  aspect=get_aspect(axis=axis, aspect=self.m.aspects[self.key]))
        ax.axis(False)
        plt.title(title)
        return draw_figure(self.v.window[canvas_key].TKCanvas, fig, plot)