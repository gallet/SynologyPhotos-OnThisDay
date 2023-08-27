import json

import SynologyApi
from Config import Config
from SynoToken import SynoToken

MAX_PHOTOS_PAGE = 5000
MAX_TAGS_PAGE = MAX_PHOTOS_PAGE


class SynoPhotos:
    def __init__(self, syno_token: SynoToken, config: Config, offset=0, max_photo_count=None):
        self.config = config
        self.uri = self.config.api_uri
        self.syno_token = syno_token
        self.photo_count = self.get_picture_count()
        self.available_tags = self.get_tags()
        if max_photo_count is not None and max_photo_count > 0:
            self.photo_count = min(self.photo_count, max_photo_count)
        self.offset = offset
        self.photo_data = self.get_photos()
        self.photos_to_tag = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_picture_count(self):
        api = "SYNO.FotoTeam.Browse.Item"
        version = 3
        method = "count"
        rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token, verify=self.config.ssl_verify)

        return rsp['data']['count']

    def get_photos(self):
        api = "SYNO.FotoTeam.Browse.Item"
        version = 3
        method = "list"
        pages = []
        for i in range(self.offset, self.offset + self.photo_count, MAX_PHOTOS_PAGE):
            print(f'retrieving photos {i} to {min(i+MAX_PHOTOS_PAGE, self.offset + self.photo_count)}')

            rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token, verify=self.config.ssl_verify,
                                      offset=i,
                                      limit=min(MAX_PHOTOS_PAGE, self.photo_count),
                                      additional=json.dumps(["tag"])
                                      )
            pages += rsp['data']['list']

        return pages

    def get_tags(self):
        api = "SYNO.FotoTeam.Browse.GeneralTag"
        version = 1
        method = "count"

        rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token, verify=self.config.ssl_verify)
        tag_count = rsp['data']['count']

        method = "list"
        pages = []
        for i in range(0, tag_count, MAX_TAGS_PAGE):
            print(f'retrieving tags {i} to {min(i+MAX_TAGS_PAGE, tag_count)}')
            rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token, verify=self.config.ssl_verify,
                                      offset=i,
                                      limit=MAX_TAGS_PAGE
                                      )
            pages += rsp['data']['list']

        return {t['name']: t['id'] for t in pages}

    def add_tag(self, tag_to_be_set):
        print(f'creating/getting new tag ({tag_to_be_set}) in SYNOLOGY PHOTO and adding to self.available_tags')
        api = "SYNO.FotoTeam.Browse.GeneralTag"
        version = 1
        method = "create"
        rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token, verify=self.config.ssl_verify,
                                  name=tag_to_be_set
                                  )
        tag_id = rsp['data']['tag']['id']

        self.available_tags.update({tag_to_be_set: tag_id})

        return tag_id

    def get_tag_id(self, tag):
        if tag in self.available_tags:
            # print('tag found self.available_tags')
            return self.available_tags[tag]
        else:
            return self.add_tag(tag)

    def add_photo_to_tag(self, photo_id, tag_to_be_set):
        tag_id = self.get_tag_id(tag_to_be_set)

        if tag_id in self.photos_to_tag:
            # print('tag_id found in photos_to_tag')
            pass
        else:
            # print(f'creating new entries for tag_id ({tag_to_be_set}:{tag_id}) in self.photos_to_tag')
            self.photos_to_tag[tag_id] = {"tag": tag_to_be_set, "photos": []}

        self.photos_to_tag[tag_id]['photos'].append(photo_id)

    def tag_photos(self, photos, tag_to_be_set):
        tag_id = self.get_tag_id(tag_to_be_set)
        print(f"tagging photo(s) with {tag_to_be_set} (tag_id = {tag_id}): {photos}")

        api = "SYNO.FotoTeam.Browse.Item"
        version = 3
        method = "add_tag"
        for i in range(len(photos)):
            photos_to_tag = photos[i * 100:(i + 1) * 100]
            if len(photos_to_tag) == 0:
                continue

            # photo_id_list = ','.join(str(p) for p in photos_to_tag)
            rsp = SynologyApi.api_req(self.uri, api, version, method, self.syno_token, verify=self.config.ssl_verify,
                                      tag=json.dumps([tag_id]),
                                      id=json.dumps(photos_to_tag)
                                      )
            # print(rsp)
