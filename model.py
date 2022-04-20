class Model:

    def __init__(self):

        self.keys = ["patient", "atlas", "avg"]
        self.tab_keys = ["patient", "atlas", "avg", "avg_atlas"]
        self.alpha_keys = ["avg_atlas"]

        self.dcms = {key: None for key in self.keys}

        self.files = {key: None for key in self.keys}

        self.tensors = {key: None for key in self.keys}

        self.aspects = {key: [1.0, 1.0, 1.0] for key in self.keys}

        self.color = (255, 0, 0)
        self.color_map = None

        self.region_names = None
        self.region_ids = None
