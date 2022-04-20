from coregister import *
from tensor_controller import *
from alpha_controller import *
from view import *
from controls import *
from model import *

import PySimpleGUI as sg
import matplotlib as plt


if __name__ == "__main__":

    m = Model()
    v = View(m)
    cc = Controls(m, v)
    c_patient = TensorController(m, v, key="patient", t_file="folder")
    c_avg = TensorController(m, v, key="avg", t_file="file")
    c_atlas = TensorController(m, v, key="atlas", t_file="file")
    c_avg_atlas = AlphaController(m, v, tensor_key="avg", mask_key="atlas")
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
        elif v.tab == "avg_atlas":
            c = c_avg_atlas
        else:
            c = c_coregister

        # End of Program
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # Change of tab
        elif event == "tabgrp":
            c.refresh()

        elif event == "Color_Picker":
            if m.tensors["atlas"] is not None:
                m.color_map = set_color_map(np.unique(m.tensors["atlas"]),
                                            [int(c * 255) for c in plt.colors.to_rgb(v.popup_color_chooser())])
                c.refresh()

        elif event == "change-colors":
            if m.tensors["atlas"] is not None:
                m.color_map = get_color_map(np.unique(m.tensors["atlas"]))
                c.refresh()

        else:
            for key in m.keys:

                # DICOM info popup
                if event == "DICOM-Info-"+key:
                    sg.popup_scrolled(m.dcms[key], title=key)

                # DICOM read
                elif event == key+"_name":
                    v.window[key+"_file"].Update(value=v.values[key+"_name"])
                    if key == "patient":
                        cc.read_dcom_folder(key)
                    else:
                        cc.read_dcom_file(key)

                    if key == v.tab or key in v.tab:
                        c.refresh()

            for key in m.tab_keys:

                # Change slice
                if event == key+"-set-front":
                    c.refresh_view(1)
                elif event == key+"-set-end":
                    c.refresh_view(2)
                elif event == key+"-set-top":
                    c.refresh_view(0)

            for key in m.alpha_keys:
                if event == "set-alpha-"+key:
                    c.refresh()

    v.window.close()
