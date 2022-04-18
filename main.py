from windowing import *
from crop import *
from view import *
from controls import *
from model import *

import PySimpleGUI as sg
import matplotlib as plt


if __name__ == "__main__":

    m = Model()
    v = View(m)
    cc = Controls(m, v)
    c_w = Windowing(m, v)
    c_c = Crop(m, v)
    c_s = Segmentation(m, v)

    # IGU loop: check events until end of program
    while True:

        v.read_input()
        event = v.event

        if v.tab == "Windowing":
            c = c_w
        elif v.tab == "Crop":
            c = c_c
        else:
            c = c_s

        # End of Program
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        elif event == "DICOM-Info":
            sg.popup_scrolled(m.dcm, title=m.file)

        # File read
        elif event == "File_Name":
            v.window["Text_Name"].Update(value=v.values["File_Name"])
            cc.read_dcom_file()
            c.see_changes()

        # Folder read
        elif event == "Folder_Name":
            v.window["Text_Name"].Update(value=v.values["Folder_Name"])
            cc.read_dcom_folder()
            c.see_changes()

        # Change of tab
        elif event == "tabgrp" and m.img_dcm is not None:
            c.see_changes()

        # See changes
        elif event == "See_changes" and m.img_dcm is not None:
            if v.tab == "Segmentation":
                c.calc_segmentation()
            else:
                c.see_changes()

        # Apply changes
        elif event == "Apply":
            c.see_changes()
            if v.tab != "Segmentation":
                cc.apply()
            c.plot()

        elif event == "Reset":
            cc.reset()
            if m.tensor is not None:
                cc.refresh_view()
            c.see_changes()

        elif event == "Axis":
            cc.update_frame_slider()

        elif event == "Tensor_Change":
            cc.refresh_view()
            if v.tab == "Crop":
                c.see_changes_changed_perspective()
            else:
                c.see_changes()

        elif event == "Slider_min" or event == "Slider_max":
            c_w.windowing_slider_event(event)

        elif event == "Slider_up" or event == "Slider_down" or event == "Slider_right" or event == "Slider_left":
            c_c.cropping_slider_event(event)

        elif event == "Color_Picker":
            m.color = [int(c * 255) for c in plt.colors.to_rgb(v.popup_color_chooser())]
            c.see_changes()

    v.window.close()
