import json

import SynologyApi

from Config import Config
from SynoToken import SynoToken


MAX_ALBUMS_PAGE = 5000


class SynoAlbums:
    def __init__(self, syno_token: SynoToken, config: Config):
        self.config = config
        self.uri = self.config.api_uri
        self.syno_token = syno_token
        self.album_counts = self.get_album_counts()
        self.albums = self.get_albums()
        # self.album_data = self.get_albums()

    def get_album_counts(self):
        api = "SYNO.Foto.Browse.Album"
        version = 2
        method = "count"
        rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token)

        return rsp['data']['count']

    def get_album(self, album_name):
        for a in self.albums:
            if a['name'] == album_name:
                return a

    def get_albums(self):
        api = "SYNO.Foto.Browse.Album"
        version = 2
        method = "list"
        pages = []
        for i in range(0, self.album_counts, MAX_ALBUMS_PAGE):
            print(f'retrieving albums {i} to {min(i+MAX_ALBUMS_PAGE, self.album_counts)}')

            rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token,
                                      offset=i,
                                      limit=min(MAX_ALBUMS_PAGE, self.album_counts)
                                      )
            pages += rsp['data']['list']

        return pages

    def update_conditions(self, album, conditions):
        if 'id' in album:
            album_id = album['id']
        else:
            return

        # print(f"{album['name']} ({album['id']}): {conditions}")

        if album_id is not None:
            api = "SYNO.Foto.Browse.ConditionAlbum"
            version = 2
            method = "set_condition"
            rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token,
                                      id=album_id,
                                      condition=json.dumps(conditions)
                                      )
            return rsp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
