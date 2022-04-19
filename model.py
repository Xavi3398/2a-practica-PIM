class Model:

    def __init__(self):

        self.keys = ["patient", "atlas", "avg"]

        self.dcms = {key: None for key in self.keys}

        self.files = {key: None for key in self.keys}

        self.tensors = {key: None for key in self.keys}

        self.aspects = {key: [1.0, 1.0, 1.0] for key in self.keys}
