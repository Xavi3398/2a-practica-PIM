class Model:

    def __init__(self):

        # Files
        self.file = None
        self.dcm = None

        # Tensors
        self.tensor = None
        self.tensor_result = None
        self.tensor_result_copy = None
        self.tensor_mask = None

        # Images
        self.img_dcm = None
        self.img_result_copy = None
        self.img_result = None
        self.img_mask = None

        # Plots
        self.in_img_plot = None
        self.out_img_plot = None
        self.windowing_hist_plot = None
        self.crop_plot = None
        self.seg_plot = None

        # Frame Control
        self.frame = 0
        self.axis = 2

        # Aspect Ratio
        self.dim_x = 0
        self.dim_y = 0
        self.dim_z = 0

        # Segmentation
        self.point = None
        self.color = (255, 0, 0)

    def get_aspect(self):
        if self.tensor is None:
            return self.dim_y / self.dim_x
        else:
            if self.axis == 0:
                return self.dim_z / self.dim_x
            elif self.axis == 1:
                return self.dim_z / self.dim_y
            elif self.axis == 2:
                return self.dim_y / self.dim_x
