import json

CONFIG_FILE = "config.json"


class ConfigurationHandler(object):
    class __ConfigurationHandler:
        def __init__(self):
            with open(CONFIG_FILE) as config_file:
                self.config_data = json.load(config_file)
                locals().update(self.config_data)

        def get(self, key):
            locals().update(self.config_data)
            return self.config_data[key]

    instance = None

    def __new__(cls):  # __new__ always a classmethod
        if not ConfigurationHandler.instance:
            ConfigurationHandler.instance = ConfigurationHandler.__ConfigurationHandler()
        return ConfigurationHandler.instance


def loadConfigData():
    obj = ConfigurationHandler()
    config = obj
    return config
