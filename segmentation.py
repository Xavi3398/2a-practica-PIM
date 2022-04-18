from utils import *
from ITab import *
import cv2
from matplotlib import pyplot as plt


class Segmentation(ITab):

    def __init__(self, model, view):
        super().__init__(model, view)

    def plot(self):
        self.plot_pointer_img()
        self.plot_segmentation_img()

    def plot_pointer_img(self):
        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        plt.title('SEGMENTATION')
        ax.imshow(self.m.img_result, cmap='gray', aspect=self.m.get_aspect())
        ax.axis(False)

        if self.m.point is not None:
            plt.plot(self.m.point[0], self.m.point[1], marker="o", markersize=5,
                     markeredgecolor=np.array(self.m.color).astype('float') / 255,
                     markerfacecolor=np.array(self.m.color).astype('float') / 255)

        fig.canvas.mpl_connect('button_press_event', self.segmentation_clicked_event)

        self.m.seg_plot = draw_figure(self.v.window["Segmentation_Canvas"].TKCanvas, fig, self.m.seg_plot)

    def plot_segmentation_img(self):

        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.axis(False)
        plt.title('RESULTING IMAGE')

        # Case of not yet computed segmentation
        if self.m.tensor_mask is None and self.m.img_mask is None:
            ax.imshow(self.m.img_result, cmap="gray", aspect=self.m.get_aspect())

        # Case of computed segmentation and 3d image
        elif self.m.tensor_mask is not None:
            img, mask = self.get_current_image_and_mask()
            mask_r = color_mask(mask, self.m.color)  # Color mask
            img = img.astype('float')
            rgb = cv2.cvtColor((img * 255 / np.max(img)).astype("uint8"), cv2.COLOR_GRAY2RGB)  # Gray image to RGB
            ax.imshow(painter(rgb, mask_r, self.v.values["Slider_alpha"]),
                      aspect=self.m.get_aspect())  # Merge layers

        # Case of computed segmentation and 2d image
        else:
            mask_r = color_mask(self.m.img_mask, self.m.color)  # Color mask
            img = self.m.img_result.astype('float')
            rgb = cv2.cvtColor((img * 255 / np.max(img)).astype("uint8"), cv2.COLOR_GRAY2RGB)  # Gray to RGB
            ax.imshow(painter(rgb, mask_r, self.v.values["Slider_alpha"]),
                      aspect=self.m.get_aspect())  # Merge layers
        self.m.out_img_plot = draw_figure(self.v.window["IMAGE-OUT"].TKCanvas, fig, self.m.out_img_plot)  # Plot

    def see_changes(self):
        self.plot()

    def calc_segmentation(self):
        if self.m.point is not None:
            if self.m.tensor is None:
                self.calc_segmentation_2d()
            else:
                self.calc_segmentation_3d()
        self.plot_segmentation_img()

    def calc_segmentation_2d(self):

        thresh = self.v.values["Slider_segmentation"]
        x, y = self.m.point
        img_thresh = self.m.img_result.copy()
        value = img_thresh[y, x]

        # Apply Threshold
        img_thresh[img_thresh < value - thresh] = 0
        img_thresh[img_thresh > value + thresh] = 0
        img_thresh[img_thresh > 0] = 1

        # Segmentation
        try:
            if self.v.values["thresh"]:
                self.m.img_mask = img_thresh
            elif self.v.values["thresh_weak"]:
                self.m.img_mask = connected_thresh(img_thresh, (x, y), method="2d_close")
            elif self.v.values["thresh_strong"]:
                self.m.img_mask = connected_thresh(img_thresh, (x, y), method="2d")
        except TookTooLongException as e:
            self.v.show_alert_message("Computation took too long and was aborted!")
            self.m.img_mask = e.img

    def calc_segmentation_3d(self):

        thresh = self.v.values["Slider_segmentation"]
        x, y, z = get_coordinates(self.m.point[0], self.m.point[1],
                                  self.m.axis, self.m.frame, self.m.tensor_result.shape)
        value = self.m.tensor_result[y, x, z]

        # Apply Threshold
        tensor_thresh = self.m.tensor_result.copy()
        tensor_thresh[tensor_thresh < value - thresh] = 0
        tensor_thresh[tensor_thresh > value + thresh] = 0
        tensor_thresh[tensor_thresh > 0] = 1

        # Segmentation
        try:
            if self.v.values["thresh"]:
                self.m.tensor_mask = tensor_thresh
            elif self.v.values["thresh_weak"]:
                self.m.tensor_mask = connected_thresh(tensor_thresh, (x, y, z), method="3d_close")
            elif self.v.values["thresh_strong"]:
                self.m.tensor_mask = connected_thresh(tensor_thresh, (x, y, z), method="3d")
        except TookTooLongException as e:
            self.v.show_alert_message("Computation took too long and was aborted!")
            self.m.tensor_mask = e.img

    def get_current_image_and_mask(self):

        img = None
        mask = None

        if self.m.axis == 0:  # Front
            img = np.rot90(self.m.tensor_result[self.m.frame, :, :], axes=(1, 0))
            mask = np.rot90(self.m.tensor_mask[self.m.frame, :, :], axes=(1, 0))
        elif self.m.axis == 1:  # End
            img = np.rot90(self.m.tensor_result[:, self.m.frame, :], axes=(1, 0))
            mask = np.rot90(self.m.tensor_mask[:, self.m.frame, :], axes=(1, 0))
        elif self.m.axis == 2:  # Top
            img = np.rot90(self.m.tensor_result[:, :, self.m.frame], k=2)
            mask = np.rot90(self.m.tensor_mask[:, :, self.m.frame], k=2)

        return img, mask

    def segmentation_clicked_event(self, ev):
        if ev is not None and ev.xdata is not None and ev.ydata is not None:
            self.m.point = [round(ev.xdata), round(ev.ydata)]
            self.plot_pointer_img()
