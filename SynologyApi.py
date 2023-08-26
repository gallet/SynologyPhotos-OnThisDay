import requests
import json


def api_req(url, api, version, method, syno_token=None, **kwargs):

    params = {
        "api": api,
        "version": version,
        "method": method
    }

    if syno_token is not None:
        params.update({"_sid": syno_token.get_sid(), "SynoToken": syno_token.get_token()})

    params.update(kwargs)

    response = requests.get(url, params=params)
    response.raise_for_status()
    return json.loads(response.text)
