import SynologyApi
from Config import Config


class SynoToken:
    def __init__(self, config: Config):
        # (Optional: load cookie from permanent storage)
        self.config = config
        self.uri = self.config.api_uri
        self.auth_data = {}
        self.auth_data = self.get_auth_data()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def get_sid(self):
        try:
            return self.get_auth_data()["_sid"]
        except Exception as e:
            print("Error:", e)
            return None

    def get_token(self):
        try:
            return self.get_auth_data()["SynoToken"]
        except Exception as e:
            print("Error:", e)
            return None

    # Function to get a valid cookie
    def get_auth_data(self):
        try:
            if self.is_token_valid():
                # print("Using stored token.")
                pass
            else:
                print("get_auth_data: Requesting a new token.")
                self.auth_data = self.authenticate()

            return self.auth_data
        except Exception as e:
            print("Error:", e)
            return None

    # Check if the cookie is still valid
    def is_token_valid(self):
        if self.auth_data == {} or "_sid" not in self.auth_data or "SynoToken" not in self.auth_data:
            return False
        else:

            try:
                api = "SYNO.FileStation.Info"
                version = 1
                method = "get"
                rsp = SynologyApi.api_req(self.uri, api, version, method, None,
                                          _sid=self.auth_data["_sid"],
                                          SynoToken=self.auth_data["SynoToken"]
                                          )

                if "success" in rsp and rsp["success"]:
                    return True
                else:
                    return False
            except Exception as e:
                print("Error:", e)
                return False

    # Authenticate and obtain session ID using cookies
    def authenticate(self):

        try:
            api = "SYNO.API.Auth"
            version = 6
            method = "login"
            rsp = SynologyApi.api_req(self.uri, api, version, method, None,
                                      account=self.config.user,
                                      passwd=self.config.pswd,
                                      enable_syno_token="yes"
                                      )
            if "success" in rsp and rsp["success"]:
                return {'_sid': rsp['data']['sid'], 'SynoToken': rsp['data']['synotoken']}
            else:
                raise Exception("Authentication failed. Check your credentials.")
        except Exception as e:
            print("Error:", e)
            raise Exception("Error in the authentication request.")

    def logout(self):
        if self.auth_data == {}:
            return
        else:
            api = "SYNO.API.Auth"
            version = 6
            method = "logout"

            try:
                rsp = SynologyApi.api_req(self.uri, api, version, method,  self)
                if "success" in rsp and rsp["success"]:
                    self.auth_data = {}
                    print("Logout successful")
                else:
                    raise Exception("Logout could not complete")
            except Exception as e:
                print("Error:", e)
                raise Exception("Error in the logging out request.")
