from utils import *
from ITab import *
from matplotlib import pyplot as plt
import cv2


class AlphaController(ITab):

    def __init__(self, model, view, key, tensor_key, mask_key, t_file="file"):
        super().__init__(model, view)
        self.plot_front = None
        self.plot_end = None
        self.plot_top = None
        self.key = key
        self.tensor_key = tensor_key
        self.mask_key = mask_key
        self.t_file = t_file

    def refresh(self):
        if self.m.tensors[self.tensor_key] is not None and self.m.tensors[self.mask_key] is not None:
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

        img = get_slice(axis, frame, self.m.tensors[self.tensor_key], self.t_file).astype('float')
        rgb = cv2.cvtColor((img * 255 / np.max(img)).astype("uint8"), cv2.COLOR_GRAY2RGB)  # Gray image to RGB
        mask = get_slice(axis, frame, self.m.tensors[self.mask_key], self.t_file)

        # Select regions which appear in the image and have been selected by the user
        regions = set(np.unique(mask))
        if self.m.region_ids is not None:
            selected_region_ids = [self.m.region_ids[region] for region in self.v.values["region-" + self.key]]
            regions &= set(selected_region_ids)

        # Paint all regions of interest
        for id_region in regions:
            if id_region != 0:
                mask_r = color_mask(mask == id_region, self.m.color_map[id_region])  # Color mask
                rgb = painter(rgb, mask_r, self.v.values["alpha-"+self.key])

        ax.imshow(rgb, cmap='gray', aspect=get_aspect(axis=axis, aspect=self.m.aspects[self.mask_key]))
        ax.axis(False)
        plt.title(title)
        return draw_figure(self.v.window[canvas_key].TKCanvas, fig, plot)