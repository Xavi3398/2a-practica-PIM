class Model:

    def __init__(self):

        self.keys = ["patient", "atlas", "avg", "patient->avg", "atlas->patient"]
        self.tab_keys = ["patient", "atlas_atlas", "avg", "avg_atlas", "patient->avg", "atlas->patient"]
        self.coregister_keys = ["patient_points", "avg_points"]
        self.alpha_keys = ["avg_atlas", "atlas_atlas", "atlas->patient"]

        self.dcms = {key: None for key in self.keys}

        self.files = {key: None for key in self.keys}

        self.tensors = {key: None for key in self.keys}

        self.aspects = {key: [1.0, 1.0, 1.0] for key in self.keys}
        self.ratio_pat_avg = [0.95, 1.89, 1.95]

        self.color = (255, 0, 0)
        self.color_map = None

        self.region_names = None
        self.region_ids = None

        self.points = {"patient": [[243, 41, 37],
                                 [245, 41, 410],
                                 [103, 41, 325],
                                 [420, 41, 290],
                                 [267, 193,302],
                                 [274, 46,302],
                                 [381, 77,302],
                                 [130, 75,302]],
                       "avg": [[88 , 0, 214],
                             [88, 0, 20],
                             [173 , 0, 80],
                             [3, 0, 80],
                             [94 , 154, 80],
                             [96, 9, 80],
                             [36 , 39, 80],
                             [148, 38, 80]]}
        self.transform_params = None
