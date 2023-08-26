import os

# CONFIG_FILE = USER = os.getenv('CONFIG_FILE')
CONFIG_FILE = r"./config/config.txt"


class Config:
    def __init__(self, data):
        # (Optional: load cookie from permanent storage)
        self.data = data
        # self.read_config_file()
        self.data['API_URI'] = self.data['SYNO_BASE_URI'] + '/webapi/entry.cgi'

    def get_val(self, var_name):
        return self.data[var_name]

    def read_config_file(self):
        with open(CONFIG_FILE, "r") as config_file:
            for line in config_file:
                key, value = line.partition("=")[::2]
                self.data[key.strip()] = value.strip()
