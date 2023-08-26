import os


class Config:
    def __init__(self, data):
        self.url = data["URL"]
        self.user = data["USER"]
        self.pswd = data["PSWD"]
        self.album_name = data["ALBUM_NAME"]
        self.album_name_unrated = data["ALBUM_NAME_UNRATED"]
        self.api_uri = self.url + '/webapi/entry.cgi'
