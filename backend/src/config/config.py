import yaml


class Config:
    def __init__(self, file):
        self.FILE_NAME = file
        self.data = self.load_data(file)

    def load_data(self, file):
        with open(file, mode="r") as config:
            return yaml.load(config, Loader=yaml.FullLoader)

    # the following overloads the index operator [] so we can do:
    # upload_dir = config["UPLOAD_DIR"] etc

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
