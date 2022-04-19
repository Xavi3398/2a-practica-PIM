from atlas import *
from patient import *
from coregister import *
from view import *
from controls import *
from model import *

import PySimpleGUI as sg
import matplotlib as plt


if __name__ == "__main__":

    m = Model()
    v = View(m)
    cc = Controls(m, v)
    c_patient = TensorController(m, v, "patient")
    c_avg = TensorController(m, v, "avg")
    c_atlas = TensorController(m, v, "atlas")
    c_coregister = Coregister(m, v)

    # IGU loop: check events until end of program
    while True:

        v.read_input()
        event = v.event

        if v.tab == "patient":
            c = c_patient
        elif v.tab == "atlas":
            c = c_atlas
        elif v.tab == "avg":
            c = c_avg
        else:
            c = c_coregister

        # End of Program
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # Change of tab
        elif event == "tabgrp":
            c.refresh()

        elif event == "Color_Picker":
            m.color = [int(c * 255) for c in plt.colors.to_rgb(v.popup_color_chooser())]

        else:
            for key in m.keys:

                # DICOM info popup
                if event == "DICOM-Info-"+key:
                    sg.popup_scrolled(m.dcms[key], title=key)

                # Change slice
                elif event == key+"-set-front":
                    c.refresh_view(0)
                elif event == key+"-set-end":
                    c.refresh_view(1)
                elif event == key+"-set-top":
                    c.refresh_view(2)

                # DICOM read
                elif event == key+"_name":
                    v.window[key+"_file"].Update(value=v.values[key+"_name"])
                    if key == "patient":
                        cc.read_dcom_folder(key)
                    else:
                        cc.read_dcom_file(key)
                    c.refresh()

    v.window.close()
