from utils import *
from ITab import *
from matplotlib import pyplot as plt


class Crop(ITab):

    def __init__(self, model, view):
        super().__init__(model, view)

    def plot(self):

        # Plot image
        fig = plt.figure(figsize=(5, 4))
        plt.title('CROPPED IMAGE')
        ax = fig.add_subplot(111)
        ax.axis(False)
        ax.imshow(self.m.img_result, cmap="gray", aspect=self.m.get_aspect())
        self.m.crop_plot = draw_figure(self.v.window["IMAGE-CROPPED"].TKCanvas, fig, self.m.crop_plot)

        # Plot lines
        ax.plot([int(self.v.values['Slider_left']), int(self.v.values['Slider_left'])],
                [0, self.m.img_result.shape[0]], color='red')
        ax.plot([int(self.v.values['Slider_right']), int(self.v.values['Slider_right'])],
                [0, self.m.img_result.shape[0]], color='yellow')
        ax.plot([0, self.m.img_result.shape[1]],
                [int(self.v.values['Slider_up']), int(self.v.values['Slider_up'])], color='green')
        ax.plot([0, self.m.img_result.shape[1]],
                [int(self.v.values['Slider_down']), int(self.v.values['Slider_down'])], color='blue')

    def cropping_slider_event(self, slider=None):

        # Fix slider values
        if slider == "Slider_up":
            if int(self.v.values["Slider_up"]) > int(self.v.values["Slider_down"]):
                self.v.window["Slider_up"].Update(value=int(self.v.values["Slider_down"]))
        elif slider == "Slider_down":
            if int(self.v.values["Slider_up"]) > int(self.v.values["Slider_down"]):
                self.v.window["Slider_down"].Update(value=int(self.v.values["Slider_up"]))
        elif slider == "Slider_left":
            if int(self.v.values["Slider_left"]) > int(self.v.values["Slider_right"]):
                self.v.window["Slider_left"].Update(value=int(self.v.values["Slider_right"]))
        elif slider == "Slider_right":
            if int(self.v.values["Slider_left"]) > int(self.v.values["Slider_right"]):
                self.v.window["Slider_right"].Update(value=int(self.v.values["Slider_left"]))

        self.plot()

    def see_changes_changed_perspective(self):
        self.see_changes(0, self.m.img_result.shape[1], 0, self.m.img_result.shape[0])

    def see_changes(self, x1=None, x2=None, y1=None, y2=None):

        self.plot()

        if x1 is None:
            x1 = int(self.v.values["Slider_left"])
            x2 = int(self.v.values["Slider_right"])
            y1 = int(self.v.values["Slider_up"])
            y2 = int(self.v.values["Slider_down"])

        if self.m.tensor is None:  # 2D
            self.m.img_result_copy = self.m.img_result[y1:y2, x1:x2]
        else:  # 3D
            if self.m.axis == 0:  # Front
                x1_aux = x1
                x2_aux = x2
                x1 = y1
                y1 = self.m.tensor_result.shape[1] - x1_aux
                x2 = y2
                y2 = self.m.tensor_result.shape[1] - x2_aux
                self.m.tensor_result_copy = self.m.tensor_result[:, y2:y1, x1:x2]
            elif self.m.axis == 1:  # End
                x1_aux = x1
                x2_aux = x2
                x1 = y1
                x2 = y2
                y1 = self.m.tensor_result.shape[0] - x1_aux
                y2 = self.m.tensor_result.shape[0] - x2_aux
                self.m.tensor_result_copy = self.m.tensor_result[y2:y1, :, x1:x2]
            else:  # Top
                x1 = self.m.tensor_result.shape[1] - x1
                x2 = self.m.tensor_result.shape[1] - x2
                y1 = self.m.tensor_result.shape[0] - y1
                y2 = self.m.tensor_result.shape[0] - y2
                self.m.tensor_result_copy = self.m.tensor_result[y2:y1, x2:x1, :]
            self.m.img_result_copy = get_slice(self.m.axis, self.m.frame, self.m.tensor_result_copy)

        # Plot
        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.axis(False)
        plt.title('RESULTING IMAGE')
        ax.imshow(self.m.img_result_copy, cmap="gray", aspect=self.m.get_aspect())
        self.m.out_img_plot = draw_figure(self.v.window["IMAGE-OUT"].TKCanvas, fig, self.m.out_img_plot)
