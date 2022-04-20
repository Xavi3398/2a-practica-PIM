from utils import *
import glob
import pydicom
import numpy as np
from matplotlib import pyplot as plt


class Controls:

    def __init__(self, model, view):
        self.m = model
        self.v = view

    #  --------------------------------- View functions ----------------------------------

    def read_dcom_file(self, key):

        # Read file
        self.m.files[key] = self.v.values[key+"_name"]
        self.m.dcms[key] = pydicom.dcmread(self.m.files[key])
        self.m.tensors[key] = self.m.dcms[key].pixel_array

        # Get dcom aspect ratio
        # self.m.aspect_atlas[0] = float(self.m.dcm_atlas["PixelSpacing"][0])
        # self.m.aspect_atlas[1] = float(self.m.dcm_atlas["PixelSpacing"][1])

        # Set cropping slider values
        self.v.reset_sliders(key)

        if key == "avg":
            self.m.tensors[key] = self.m.tensors[key][6:-6, 6:-6, 6:-6]
        elif key == "atlas":
            self.v.window['avg_atlas-frame-top'].Update(range=(0, self.m.tensors[key].shape[0] - 1), value=0)
            self.v.window['avg_atlas-frame-front'].Update(range=(0, self.m.tensors[key].shape[1] - 1), value=0)
            self.v.window['avg_atlas-frame-end'].Update(range=(0, self.m.tensors[key].shape[2] - 1), value=0)
            self.m.color_map = get_color_map(np.unique(self.m.tensors[key]))

        print(self.m.tensors[key].shape)

    def read_dcom_folder(self, key):

        self.m.file_patient = self.v.values[key+"_name"]
        imgs = []

        files = glob.glob(self.m.file_patient + "/*.dcm")

        # Read files in folder
        for file in files:
            dcm = pydicom.dcmread(file)
            imgs.append([dcm.pixel_array, dcm["SliceLocation"].value])

        # Order slices by instance number and get the ordered list of images
        imgs = sorted(imgs, key=lambda t: t[1], reverse=True)
        self.m.aspects[key][0] = float(abs(imgs[0][1] - imgs[1][1]))
        imgs = [img[0] for img in imgs]

        # Change order of axis (Y, X, Z) instead of (Z, Y, X)
        self.m.tensors[key] = np.array(imgs)

        # Load first frame
        self.m.dcms[key] = pydicom.dcmread(files[0])

        # Get aspect ratio
        self.m.aspects[key][1] = float(self.m.dcms[key]["PixelSpacing"][0])
        self.m.aspects[key][2] = float(self.m.dcms[key]["PixelSpacing"][1])

        # Set slider values
        self.v.reset_sliders(key)
