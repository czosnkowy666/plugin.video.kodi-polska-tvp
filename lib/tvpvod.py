import sys
from urllib.parse import parse_qsl
from urllib.parse import urlencode

import xbmc
import xbmcgui
import xbmcplugin

from lib import util

BASE_URL = "http://www.api.v3.tvp.pl/shared/listing.php?parent_id=%d&count=%d&page=%d&dump=json"
VIDEO_SERVICE_URL = "http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id=%d"
IMAGE_URL = 'http://s.v3.tvp.pl/images/%s/%s/%s/uid_%s_width_%d_gs_0.%s'

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


def get_image_idx(images):
    i = 0
    for image in images:
        if image["title"] == "zaślepka 16x9":
            return i
        i = i + 1

#        xbmc.log("[info] images " + str(image['title']), level=xbmc.LOGINFO)

    return 0


def get_image_url(content):
    image = None
    image_url = None

    if "image" in content:
        image = content["image"]
    if "image_vod" in content:
        image = content["image_vod"]

    if image is not None:
        image_count = len(image)
        xbmc.log("[info] images " + str(image_count), level=xbmc.LOGINFO)
        image_idx = 0
        if image_count > 1:
            image_idx = get_image_idx(image)

        image_file = image[image_idx]['file_name']
        if "width" in image[image_idx]:
            image_width = image[image_idx]['width']
        else:
            image_width = 800

        if image_width > 0:
            image_url = IMAGE_URL %(image_file[0],image_file[1],image_file[2],image_file[:-4],image_width,image_file[-3:])

    return image_url


def open_folder(folder_id, page=1):
    folder_url = BASE_URL % (folder_id, BASE_COUNT, page)
    content = util.get_url_content(folder_url)

    xbmcplugin.setContent(handle=HANDLE, content="files")

    if "items" in content:
        for item in content["items"]:

            # TODO: jeśli "object_type": "video" ustawić link na video
            # TODO: sprawdzić czy to coś zmienia "paymethod": 0
            # TODO: jeśli objekt nie ma "title" nie wywalać błędu

            title = "None"
            if "title_root" in item:
                title = item["title_root"]
            elif "title" in item:
                title = item["title"]

            is_folder = True
            action = "openFolder"

            object_type = None
            if "object_type" in item:
                object_type = item["object_type"]

            # xbmc.log("[info] categories, items: " + title + ', type: ' + str(object_type), level=xbmc.LOGINFO)

            if object_type == "directory_standard" or object_type == "directory_recommended":
                continue

            if "object_type" in item and item["object_type"] == "video":
                is_folder = False
                action = "openVideo"

            url_params = {
                "action": action,
                "id": item["_id"]
            }


            image_url = get_image_url(item)

            meta_data = {
                "Title": 				title,
            }

            if "description_root" in item:
                meta_data["Plot"] = item["description_root"]
            elif "lead_root" in item and item["lead_root"] != "!!! pusty LEAD !!!":
                meta_data["Plot"] = item["lead_root"]
            elif "website_title" in item:
                meta_data["Plot"] = item["website_title"]

            if "duration" in item:
                meta_data["Duration"] = item["duration"]

            if "release_date_dt" in item:
                meta_data["premiered"] = item["release_date_dt"] + ' ' + item["release_date_hour"]

            if "episode_number" in item:
                meta_data["episode"] = item["episode_number"]

            add_dir(title, url_params, meta_data, image_url, None, is_folder)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)


def add_dir(name, url_params, meta_data, icon_image=None, thumbnail=None, folder=False):
    item = xbmcgui.ListItem(name)
    if icon_image is not None:
        # xbmc.log("[info] image: " + icon_image, level=xbmc.LOGINFO)
        item.setArt({'poster': icon_image, 'banner': icon_image})

    item.setInfo(type="Video", infoLabels=meta_data)

    url = PLUGIN_URL + '?' + urlencode(url_params)
    dir_item = xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=item, isFolder=folder)
    return dir_item


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
