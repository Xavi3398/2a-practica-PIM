class Model:

    def __init__(self):

        self.keys = ["patient", "atlas", "avg", "patient->avg", "atlas->patient"]
        self.tab_keys = ["patient", "atlas_atlas", "avg", "avg_atlas", "patient->avg", "atlas->patient"]
        self.coregister_keys = ["patient_points", "avg_points"]
        self.alpha_keys = ["avg_atlas", "atlas_atlas", "atlas->patient", "patient->avg"]

        self.dcms = {key: None for key in self.keys}

        self.files = {key: None for key in self.keys}

        self.tensors = {key: None for key in self.keys}
        self.tensors["patient_small"] = None

        self.aspects = {key: [1.0, 1.0, 1.0] for key in self.keys}
        self.scale_mm = [1.0, 1.0, 1.0]

        self.color = (255, 0, 0)
        self.color_map = None

        self.region_names = None
        self.region_ids = None

        self.transform_params = None
        self.points = {"patient": [
                                   [260, 120, 434],
                                   [243, 120, 79],
                                   [223, 120, 297],
                                   [258, 182, 262],
                                   [130,  72, 262],
                                   [395,  82, 262],
                                   [260,  93, 262],
                                   [320,  98, 111],
                                   [320,  44, 322],
                                   [320, 100, 351],

                                   [243,  41, 37],
                                   [245,  41, 410],
                                   [103,  41, 325],
                                   [420,  41, 290],
                                   [267, 193, 302],
                                   [274,  46, 302],
                                   [381,  77, 302],
                                   [130,  75, 302]
                                  ],

                       "avg": [
                               [89,  89, 16],
                               [90,  89, 207],
                               [111, 89, 83],
                               [92, 149, 116],
                               [148, 26, 116],
                               [36,  27, 116],
                               [91,  66, 116],
                               [60,  29, 183],
                               [60,  10, 58],
                               [60,  77, 67],

                               [ 88,   0, 214],
                               [ 88,   0,  20],
                               [173,   0,  80],
                               [  3,   0,  80],
                               [ 94, 154,  80],
                               [ 96,   9,  80],
                               [ 36,  39,  80],
                               [148,  38,  80]
                              ]}

