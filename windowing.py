from utils import *
from ITab import *
import cv2
from matplotlib import pyplot as plt


class Windowing(ITab):

    def __init__(self, model, view):
        super().__init__(model, view)

    def plot(self):

        if self.m.dcm is not None:

            # Calculate histogram
            if self.m.tensor is not None:
                hist, _ = np.histogram(self.m.tensor_result.flatten(), range=(0,4096), bins=100)
                # hist = cv2.calcHist([self.m.tensor_result], [0], None, [101], (0, 4096)).flatten()
            else:
                hist, _ = np.histogram(self.m.img_result.flatten(), range=(0,4096), bins=100)
                # hist = cv2.calcHist([self.m.img_result], [0], None, [101], (0, 4096)).flatten()

            fig = plt.figure(figsize=(5, 4))
            # plt.title('Histogram')
            ax = fig.add_subplot(111)
            ax.fill_between(range(100), hist, color='blue')
            plt.xticks(range(0, 110, 20), ["{:.0f}".format(el) for el in np.arange(-1024, 3071 + 4095/5, 4095/5)])

            # Deleted areas
            ax.fill_between([0, int(from_hounsfield(self.v.values["Slider_min"]) * 100)], [int(max(hist))] * 2,
                            alpha=.3, color="red")
            ax.fill_between([int(from_hounsfield(self.v.values["Slider_max"]) * 100), 100], [int(max(hist))] * 2,
                            alpha=.3, color="red")

            # Plot figure
            self.m.windowing_hist_plot = draw_figure(self.v.window["Histogram"].TKCanvas, fig,
                                                     self.m.windowing_hist_plot)

    def windowing_slider_event(self, slider):
        if int(self.v.values["Slider_max"]) < int(self.v.values["Slider_min"]):
            if slider == "Slider_min":
                self.v.window["Slider_min"].Update(value=int(self.v.values["Slider_max"]))
            else:
                self.v.window["Slider_max"].Update(value=int(self.v.values["Slider_min"]))

        self.plot()

    def see_changes(self):

        # Update histogram
        self.plot()

        # Calc windowed tensor or img
        if self.m.tensor is None:
            self.windowing_2d()
        else:
            self.windowing_3d()

        # Plot
        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.axis(False)
        plt.title('RESULTING IMAGE')
        ax.imshow(self.m.img_result_copy, cmap="gray", aspect=self.m.get_aspect())
        self.m.out_img_plot = draw_figure(self.v.window["IMAGE-OUT"].TKCanvas, fig, self.m.out_img_plot)

    def windowing_2d(self):

        # New minimum amb maximum values
        min_s = self.v.values["Slider_min"] + 1024
        max_s = self.v.values["Slider_max"] + 1024

        # Compute for all image
        self.m.img_result_copy = (self.m.img_result - min_s) * (3071 + 1024) / (max_s - min_s) + 0

        # Set values out of bounds
        self.m.img_result_copy[self.m.img_result_copy < 0] = 0
        self.m.img_result_copy[self.m.img_result_copy > 4095] = 4095

    def windowing_3d(self):

        # New minimum amb maximum values
        min_s = self.v.values["Slider_min"] + 1024  # From (-1024, 3071) to (0, 4095)
        max_s = self.v.values["Slider_max"] + 1024  # From (-1024, 3071) to (0, 4095)

        # Compute for all image. (Unit = Hounsfield)
        self.m.tensor_result_copy = (self.m.tensor_result - min_s) * (3071 + 1024) / (max_s - min_s) + 0

        # Set values out of bounds
        self.m.tensor_result_copy[self.m.tensor_result_copy < 0] = 0
        self.m.tensor_result_copy[self.m.tensor_result_copy > 4095] = 4095

        self.m.img_result_copy = get_slice(self.m.axis, self.m.frame, self.m.tensor_result_copy)
