import sys
from urllib.parse import parse_qsl
from urllib.parse import urlencode
import json

import xbmc
import xbmcgui
import xbmcplugin
from lib import util

BASE_URL = "http://www.api.v3.tvp.pl/shared/listing.php?parent_id=%d&count=%d&page=%d&dump=json"
VIDEO_SERVICE_URL = "http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id=%d"

BASE_COUNT = 100
BASE_CATEGORY_ID = 1785454

HANDLE = int(sys.argv[1])
PLUGIN_URL = sys.argv[0]
ARGS = dict(parse_qsl(sys.argv[2][1:]))


def list_shows(self):
    xbmc.log("[info] shows" + str(sys.argv), level=xbmc.LOGINFO)


def list_episodes(self):
    xbmc.log("[info] episodes" + str(sys.argv), level=xbmc.LOGINFO)


def open_video(video_id, quality):
    xbmc.log("[info] play" + str(sys.argv), level=xbmc.LOGINFO)
    url = VIDEO_SERVICE_URL % (int(video_id))
    content = util.get_url_content(url)
    video_url = get_video_url(content, quality)
    xbmc.log("[info] video url: " + video_url, level=xbmc.LOGINFO)

    # xbmc.executebuiltin('XBMC.PlayMedia('+video_url+')')
    list_item = xbmcgui.ListItem(path='')
    list_item.setInfo(type="Video", infoLabels=get_video_labels(content))

    xbmc.Player().play(video_url, list_item)


def get_video_url(content,quality):
    video_url = None
    max_bitrate = 0
    if "formats" in content:

        for video_format in content["formats"]:
            # xbmc.log("[info] formats" + str(video_format), level=xbmc.LOGINFO)

            if video_format["mimeType"] == quality and video_format["totalBitrate"] > max_bitrate:
                video_url = video_format["url"]
                max_bitrate = video_format["totalBitrate"]

    # xbmc.log("[info] best format" + str(max_bitrate) + ", " + video_url, level=xbmc.LOGINFO)

    return video_url


def get_video_labels(content):
    return {}


def open_folder(folder_id, page=1):
    folder_url = BASE_URL % (folder_id, BASE_COUNT, page)
    content = util.get_url_content(folder_url)

    if "items" in content:
        for item in content["items"]:

            # TODO: jeśli "object_type": "video" ustawić link na video
            # TODO: sprawdzić czy to coś zmienia "paymethod": 0
            # TODO: jeśli ojekt nie ma "title" nie wywalać błędu

            title = "None"
            if "title" in item:
                title = item["title"]

            is_folder = True
            action = "openFolder"
            if "object_type" in item and item["object_type"] == "video":
                is_folder = False
                action = "openVideo"

            xbmc.log("[info] categories, items: " + title, level=xbmc.LOGINFO)
            url_params = {
                "action": action,
                "id": item["_id"]
            }

            add_dir(title, url_params, None, None, is_folder)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)


def add_dir(name, url_params, icon_image=None, thumbnail=None, folder=False):
    item = xbmcgui.ListItem(name)
    url = PLUGIN_URL + '?' + urlencode(url_params)
    dit = xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=item, isFolder=folder)
    return dir


def route(self):
    xbmc.log("[info] ARGS: " + str(ARGS), level=xbmc.LOGINFO)
    if "action" in ARGS:
        action = ARGS["action"]
    else:
        action = None

    if action is None:
        # start base action
        xbmc.log("[info] no action", level=xbmc.LOGINFO)
        open_folder(BASE_CATEGORY_ID, 1)

    elif action == "openFolder" and "id" in ARGS:
        xbmc.log("[info] opening folder with id: " + ARGS["id"], level=xbmc.LOGINFO)

        page = 1
        if "page" in ARGS:
            page = int(ARGS["page"])

        open_folder(int(ARGS["id"]), page)

    elif action == "openVideo" and "id" in ARGS:
        xbmc.log("[info] opening video with id: " + ARGS["id"], level=xbmc.LOGINFO)
        open_video(int(ARGS["id"]), "video/mp4")

    else:
        # start action
        xbmc.log("[info] no known action: " + str(ARGS), level=xbmc.LOGINFO)
