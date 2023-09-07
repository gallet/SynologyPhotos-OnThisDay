import requests
import json

MAX_PHOTOS_PAGE = 5000
MAX_ALBUMS_PAGE = 5000
MAX_TAGS_PAGE = 5000

API_MAP = {
    # python method: (SYNO API, VERSION, METHOD)
    "is_token_valid": ("SYNO.FileStation.Info", 1, "get"),
    "authenticate": ("SYNO.API.Auth", 6, "login"),
    "logout": ("SYNO.API.Auth", 6, "logout"),
    "get_photo_count": ("SYNO.FotoTeam.Browse.Item", 3, "count"),
    "get_photos": ("SYNO.FotoTeam.Browse.Item", 3, "list"),
    "get_album_count": ("SYNO.Foto.Browse.Album", 2, "count"),
    "get_albums": ("SYNO.Foto.Browse.Album", 2, "list"),
    "update_photo_album_conditions": ("SYNO.Foto.Browse.ConditionAlbum", 2, "set_condition"),
    "get_photo_tag_count": ("SYNO.FotoTeam.Browse.GeneralTag", 1, "count"),
    "get_photo_tags": ("SYNO.FotoTeam.Browse.GeneralTag", 1, "list"),
    "new_photo_tag": ("SYNO.FotoTeam.Browse.GeneralTag", 1, "create"),
    "tag_photos": ("SYNO.FotoTeam.Browse.Item", 3, "add_tag"),
}


class Synology:
    def __init__(self, base_url: str, user: str, password: str, ssl_verify: bool = True):
        self.base_url = base_url + '/webapi/entry.cgi'
        self.user = user
        self.password = password
        self.ssl_verify = ssl_verify
        self.sid = None
        self.token = None
        self.authenticate()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def api_req(self, api, version, method, do_validate: bool = True, **kwargs):
        params = {
            "api": api,
            "version": version,
            "method": method
        }

        # if the token and sid are None, then this function is either called in error, called by methods that do nore
        # require authentication, or to obtain the token and sid, regardless, the payload should not be enriched with
        # sid and token.
        if self.token is not None and self.sid is not None:
            if do_validate:
                self.validate_connection()
            params.update({"_sid": self.sid, "SynoToken": self.token})

        params.update(kwargs)

        response = requests.get(self.base_url, params=params, verify=self.ssl_verify)
        response.raise_for_status()
        return json.loads(response.text)

    # Check if the cookie is still valid
    def is_token_valid(self):
        if self.sid is None or self.token is None:
            return False
        else:
            try:
                api, version, method = API_MAP["is_token_valid"]
                rsp = self.api_req(api, version, method, False)

                if "success" in rsp and rsp["success"]:
                    return True
                else:
                    return False
            except Exception as e:
                print("Error:", e)
                return False

    # Function to get a valid cookie
    def validate_connection(self):
        try:
            if self.is_token_valid():
                # print("Using stored token.")
                pass
            else:
                print("Connection validation failed, requesting a new token.")
                self.authenticate()
        except Exception as e:
            print("Error:", e)

    # Authenticate and obtain session ID using cookies
    def authenticate(self):
        self.sid = None
        self.token = None
        try:
            api, version, method = API_MAP["authenticate"]
            rsp = self.api_req(api, version, method, account=self.user, passwd=self.password, enable_syno_token="yes")
            if "success" in rsp and rsp["success"]:
                self.sid = rsp['data']['sid']
                self.token = rsp['data']['synotoken']
                print('Login successful')
            else:
                raise Exception("Authentication failed. Check your credentials.")
        except Exception as e:
            print("Error:", e)
            raise Exception("Error in the authentication request.")

    def logout(self):
        if not self.is_token_valid():
            return
        else:
            api, version, method = API_MAP["logout"]

            try:
                rsp = self.api_req(api, version, method)
                if "success" in rsp and rsp["success"]:
                    self.sid = None
                    self.token = None
                    print("Logout successful")
                else:
                    raise Exception("Logout could not complete")
            except Exception as e:
                print("Error:", e)
                raise Exception("Error in the logging out request.")

    def get_photos(self):
        api, version, method = API_MAP["get_photo_count"]
        photo_count = self.api_req(api, version, method)['data']['count']

        api, version, method = API_MAP["get_photos"]
        pages = []
        for i in range(0, photo_count, MAX_PHOTOS_PAGE):
            print(f'Retrieving photos {i} to {min(i+MAX_PHOTOS_PAGE, photo_count)}')
            rsp = self.api_req(api, version, method, offset=i, limit=MAX_PHOTOS_PAGE, additional=json.dumps(["tag"]))
            pages += rsp['data']['list']

        return pages

    def get_photo_albums(self):
        api, version, method = API_MAP["get_album_count"]
        album_count = self.api_req(api, version, method)['data']['count']

        api, version, method = API_MAP["get_albums"]
        pages = []
        for i in range(0, album_count, MAX_ALBUMS_PAGE):
            print(f'Retrieving albums {i} to {min(i+MAX_ALBUMS_PAGE, album_count)}')
            rsp = self.api_req(api, version, method, offset=i, limit=MAX_ALBUMS_PAGE)
            pages += rsp['data']['list']

        return pages

    def update_photo_album_condition(self, album_id, conditions):
        api, version, method = API_MAP["update_photo_album_conditions"]
        print(f"Modifying condition of album {album_id}: {conditions}")
        self.api_req(api, version, method, id=album_id, condition=json.dumps(conditions))

    def get_photo_tags(self):
        api, version, method = API_MAP["get_photo_tag_count"]
        tag_count = self.api_req(api, version, method)['data']['count']

        api, version, method = API_MAP["get_photo_tags"]
        pages = []
        for i in range(0, tag_count, MAX_TAGS_PAGE):
            print(f'Retrieving photo tags {i} to {min(i+MAX_TAGS_PAGE, tag_count)}')
            rsp = self.api_req(api, version, method, offset=i, limit=MAX_TAGS_PAGE)
            pages += rsp['data']['list']

        return {t['name']: t['id'] for t in pages}

    def new_photo_tag(self, new_photo_tag):
        print(f'Creating a new photo tag ({new_photo_tag})')
        api, version, method = API_MAP["new_photo_tag"]
        rsp = self.api_req(api, version, method, name=new_photo_tag)
        tag_id = rsp['data']['tag']['id']

        return {new_photo_tag: tag_id}

    def tag_photos(self, photos, tag_id):
        print(f"Tagging photo(s) with tag_id = {tag_id}: {photos}")
        api, version, method = API_MAP["tag_photos"]

        for i in range(len(photos)):
            photos_to_tag = photos[i * 100:(i + 1) * 100]
            if len(photos_to_tag) == 0:
                continue

            self.api_req(api, version, method, tag=json.dumps([tag_id]), id=json.dumps(photos_to_tag))
