import json

class ConfigParser:

    @staticmethod
    def parse_config(path):
        """

        :param path:
        :return:
        """
        with open(path, 'r') as f:
            config = json.load(f)
        return config
