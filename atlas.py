from utils import *
from ITab import *
from matplotlib import pyplot as plt


class Atlas(ITab):

    def __init__(self, model, view):
        super().__init__(model, view)

    def refresh(self):
        if self.m.tensor_atlas is not None:
            self.m.atlas_plot_front = self.plot_image(0, int(self.v.values["atlas-frame-front"]),
                                                      "Front", "atlas-front", self.m.atlas_plot_front)
            self.m.atlas_plot_end = self.plot_image(1, self.m.tensor_atlas.shape[1] - 1 -
                                                      int(self.v.values["atlas-frame-end"]),
                                                    "End", "atlas-end", self.m.atlas_plot_end)
            self.m.atlas_plot_top = self.plot_image(2, int(self.v.values["atlas-frame-top"]),
                                                    "Top", "atlas-top", self.m.atlas_plot_top)

    def plot_image(self, axis, frame, title, canvas_key, plot):
        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.imshow(get_slice(axis, frame, self.m.tensor_atlas), cmap='gray',
                  aspect=get_aspect(axis=axis, aspect=self.m.aspect_atlas))
        ax.axis(False)
        plt.title(title)
        return draw_figure(self.v.window[canvas_key].TKCanvas, fig, plot)

    def refresh_view(self, axis):
        if axis == 0:
            self.m.atlas_plot_front = self.plot_image(0, int(self.v.values["atlas-frame-front"]),
                                                      "Front", "atlas-front", self.m.atlas_plot_front)
        elif axis == 1:
            self.m.atlas_plot_end = self.plot_image(1, self.m.tensor_atlas.shape[1] - 1 -
                                                    int(self.v.values["atlas-frame-end"]),
                                                    "End", "atlas-end", self.m.atlas_plot_end)
        else:
            self.m.atlas_plot_top = self.plot_image(2, int(self.v.values["atlas-frame-top"]),
                                                    "Top", "atlas-top", self.m.atlas_plot_top)