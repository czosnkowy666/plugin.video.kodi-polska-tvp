import json
import urllib.parse
import urllib.request

import xbmc


def parse_params(query_string):
    params = {}
    if len(query_string) > 1:
        params = dict(urllib.parse.parse_qsl(query_string.replace('?','')))

    return params


def get_url_content(url):
    xbmc.log("[info] get_url, url: " + url, level=xbmc.LOGINFO)

    response_json = None

    request = urllib.request.Request(url=url)
    request.add_header("Content-type", "application/json; charset=UTF-8")
    request.add_header("User-Agent", "Apache-HttpClient/UNAVAILABLE (java 1.4)")

    with urllib.request.urlopen(request) as response:
        response_content = response.read().decode("utf-8")
        response_code = response.code

    xbmc.log("[info] get_url code: " + str(response_code), level=xbmc.LOGINFO)
#    xbmc.log("[info] get_url data: " + str(response_content), level=xbmc.LOGINFO)

    try:
        response_json = json.loads(response_content)
    except Exception as e:
        xbmc.log("[error] get_url: " + str(url), level=xbmc.LOGERROR)
        xbmc.log("[error] exception: " + str(e), level=xbmc.LOGERROR)

    return response_json

