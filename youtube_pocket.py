#!/usr/bin/env python

import requests
from urllib import parse
import json
import re
import time
import random
import subprocess
import sys, os

def get_player(url):
    # get "ytInitialPlayerResponse" from html
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    YT_PLAYER_PATTERN = r"var ytInitialPlayerResponse = (?P<JsonData>{.*?}}});"

    response = requests.get(url, headers = {"user-agent" : USER_AGENT})
    if not response.ok:
        return None
    raw_content = response.text

    player = None
    result_player = re.search(YT_PLAYER_PATTERN, raw_content)
    if result_player:
        player = json.loads(result_player.group("JsonData"))

    return player

def get_data(url):
    # get "ytInitialData" from html
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    YT_DATA_PATTERN = r"var ytInitialData = (?P<JsonData>{.*?}}});"

    response = requests.get(url, headers = {"user-agent" : USER_AGENT})
    if not response.ok:
        return None
    raw_content = response.text

    data = None
    result_data = re.search(YT_DATA_PATTERN, raw_content)
    if result_data:
        data = json.loads(result_data.group("JsonData"))

    return data

def get_dl_fmts(PLAYER):
    SIG_URL_PATTERN = r"s=(?P<sig>.*?)(&.*?)*&url=(?P<url>.*)"
    prog_sig_url = re.compile(SIG_URL_PATTERN)

    # itags of potenial formats, from best to worest
    PREF_ITAG = {      "video": [137, 399, 136, 398, 135, 397, 134, 396, 133, 395, 160, 394],
                       "audio": [140, 141, 139],
                 "video/audio": [37, 22, 18]}

    # extract available formats
    available_fmts = []
    try:
        available_fmts = PLAYER["streamingData"]["formats"] + PLAYER["streamingData"]["adaptiveFormats"]
    except:
        print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

    # get the best available video format
    video_dl_fmt = None
    for v_itag in PREF_ITAG["video"]:
        for fmt in available_fmts:
            if "itag" in fmt and ("url" in fmt or "signatureCipher" in fmt) and v_itag == fmt["itag"]:
                # generate download url from "signatureCipher" if needed
                if not "url" in fmt:
                    m = prog_sig_url.match(fmt["signatureCipher"])
                    sig = m.group("sig")
                    url = parse.unquote(m.group("url"))
                    fmt["url"] = "{0}&sig={1}".format(url, sig)
                if not "qualityLabel" in fmt:
                    fmt["qualityLabel"] = "unknown"
                video_dl_fmt = fmt
        if video_dl_fmt is not None:
            break

    # get the best available audio format
    audio_dl_fmt = None
    for a_itag in PREF_ITAG["audio"]:
        for fmt in available_fmts:
            if "itag" in fmt and ("url" in fmt or "signatureCipher" in fmt) and a_itag == fmt["itag"]:
                # generate download url from "signatureCipher" if needed
                if not "url" in fmt:
                    m = prog_sig_url.match(fmt["signatureCipher"])
                    sig = m.group("sig")
                    url = parse.unquote(m.group("url"))
                    fmt["url"] = "{0}&sig={1}".format(url, sig)
                if not "audioQuality" in fmt:
                    fmt["audioQuality"] = "unknown"
                audio_dl_fmt = fmt
        if audio_dl_fmt is not None:
            break

    # get the best available video+audio format
    video_audio_dl_fmt = None
    if not (video_dl_fmt and audio_dl_fmt):
        for va_itag in PREF_ITAG["video/audio"]:
            for fmt in available_fmts:
                if "itag" in fmt and ("url" in fmt or "signatureCipher" in fmt) and va_itag == fmt["itag"]:
                    # generate download url from "signatureCipher" if needed
                    if not "url" in fmt:
                        m = prog_sig_url.match(fmt["signatureCipher"])
                        sig = m.group("sig")
                        url = parse.unquote(m.group("url"))
                        fmt["url"] = "{0}&sig={1}".format(url, sig)
                    if not "qualityLabel" in fmt:
                        fmt["qualityLabel"] = "unknown"
                    video_audio_dl_fmt = fmt
            if video_audio_dl_fmt is not None:
                break

    return {      "video": video_dl_fmt,
                  "audio": audio_dl_fmt,
            "video/audio": video_audio_dl_fmt}

def download_file(url, content_len = -1, filename = "_"):
    # download file through streaming

    units = ["  B", "KiB", "MiB", "GiB", "TiB"]
    if content_len <= 0:
        print("[Error] invalid content length")
        return False
    chunk_size = random.randint(9375936, 9999999)
    byte_count = 0
    progess = byte_count / content_len
    print("|{0:30}| {1:6.2%}".format("*" * int(30*progess), progess), end = "")

    file = open(filename, "wb")
    while byte_count < content_len:
        start_t = time.time()
        start = byte_count
        end = start + chunk_size
        if end >= content_len:
            end = content_len - 1
        response = requests.get(url + "&range={0}-{1}".format(start, end))

        raw_content = response.content
        try:
            file.write(raw_content)
        except:
            print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
            file.close()
            return False

        end_t = time.time()
        byte_count += len(raw_content)
        speed = len(raw_content) / (end_t - start_t)

        # dynamically adjust chunk size
        if speed > chunk_size:
            chunk_size = int(1.5 * chunk_size)
        elif speed < chunk_size:
            chunk_size = int(0.75 * chunk_size)

        # progress bar
        progess = byte_count / content_len
        unit_index = 0
        while speed >= 1024.0 and unit_index < len(units)-1:
            speed /= 1024.0
            unit_index += 1
        print("\r|{0:30}| {1:6.2%} {2:6.1f} {3}/s    ".format("*" * int(30*progess), progess, speed, units[unit_index]), end = "")
    print("")

    return byte_count == content_len

def validate_filename(name):
    def replace(m):
        if m.group(0) == "\"" or m.group(0) == "*" or m.group(0) == "<" or m.group(0) == ">":
            return "\'"
        else:
            return "_"
    new_name = re.sub(r"[<>:?\.\"\*\/\|\\]", replace, name)
    new_name = re.sub(r"\s+", " ", new_name)
    new_name = re.sub(r"_+", "_", new_name)
    if new_name.isspace():
        new_name = "_"
    return new_name

def download(v_id, filename = None, path = ""):
    print("[Preparing] getting info of: {0}".format(v_id))

    # get json-formatted info about the video
    PLAYER = get_player("https://www.youtube.com/watch?v=" + v_id)
    try:
        if PLAYER["playabilityStatus"]["status"] != "OK":
            return False
    except:
        return False

    # extract and sanitize info about the streaming format
    dl_fmts = get_dl_fmts(PLAYER)
    if not (dl_fmts["video"] or dl_fmts["audio"] or dl_fmts["video/audio"]):
        print("[Error] no available formats")
        return False

    v_title = ""
    try:
        v_title = PLAYER["videoDetails"]["title"]
    except:
        print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

    # helper function to handle videos of playlists, which should be downloaded to one directory
    def add_path(name):
        if path:
            return "{0}\\{1}".format(path, name)
        else:
            return name

    # validate and create directory if needed
    if path:
        path = validate_filename(path)
        if not os.path.exists(path):
            os.makedirs(path)

    # validate output filename
    if filename is not None:
        filename = validate_filename(os.path.splitext(filename)[0])
    if not filename:
        if v_title:
            filename = validate_filename(v_title)
        else:
            filename = "ytVideo_{0}".format(int(time.time()))
    filename = add_path(filename)
    output_fn = "{0}.mp4".format(filename)

    if os.path.exists(output_fn):
        print("[Done] file already exists: {0}".format(output_fn))
        return True

    if dl_fmts["video"] and dl_fmts["audio"]:
        # download video
        video_fmt = dl_fmts["video"]
        video_fn = add_path("{0}_v.mp4".format(validate_filename(v_id)))
        video_len = int(video_fmt["contentLength"])
        video_quality = video_fmt["qualityLabel"]
        video_url = video_fmt["url"]
        print("[Downloading] video part: {0} @ {1}".format(video_fn, video_quality))
        if not download_file(url = video_url, content_len = video_len, filename = video_fn):
            print("[Error] failed to download the video part")
            return False

        # download audio
        audio_fmt = dl_fmts["audio"]
        audio_fn = add_path("{0}_a.m4a".format(validate_filename(v_id)))
        audio_len = int(audio_fmt["contentLength"])
        audio_quality = audio_fmt["audioQuality"]
        audio_url = audio_fmt["url"]
        print("[Downloading] audio part: {0} @ {1}".format(audio_fn, audio_quality))
        if not download_file(url = audio_url, content_len = audio_len, filename = audio_fn):
            print("[Error] failed to download the audio part")
            return False

        # merge video and audio
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", video_fn, "-i", audio_fn, "-c", "copy", "-map", "0:v:0", "-map", "1:a:0", output_fn]
        print("[ffmpeg] merging the video and the audio parts")
        if subprocess.call(cmd) != 0:
            print("[Error] failed to merge the video and the audio parts")
            os.remove(video_fn)
            os.remove(audio_fn)
            return False
        os.remove(video_fn)
        os.remove(audio_fn)

    elif dl_fmts["video/audio"]:
        # download video/audio
        va_fmt = dl_fmts["video/audio"]
        va_fn = output_fn
        va_len = int(va_fmt["contentLength"])
        va_quality = va_fmt["qualityLabel"]
        va_url = va_fmt["url"]
        print("[Downloading] whole video: {0} @ {1}".format(va_fn, va_quality))
        if not download_file(url = va_url, content_len = va_len, filename = va_fn):
            print("[Error] failed to download the whole video")
            return False

    print("[Done] downloaded file: {0}".format(output_fn))
    return True

def get_one_video_id(l_id):
    DATA = get_data("https://www.youtube.com/playlist?list=" + l_id)
    v_id = None
    try:
        v_id = DATA["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"][0]["playlistVideoRenderer"]["videoId"]
    except:
        print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))    
    return v_id

def get_playlist_info(l_id, v_id):
    playlist_info = {}

    # request to one song of the playlist to get the full playlist content
    if not v_id:
        v_id = get_one_video_id(l_id)
        if not v_id:
            return None

    # get json-formatted info about playlist
    DATA = get_data("https://www.youtube.com/watch?v=" + v_id + "&list=" + l_id)

    # extract wanted info
    playlist_info = {}
    try:
        playlist = DATA["contents"]["twoColumnWatchNextResults"]["playlist"]["playlist"]
        playlist_info["title"] = playlist["title"]
        playlist_info["totalVideos"] = playlist["totalVideos"]
        playlist_contents = playlist["contents"]
    except:
        print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

    # extract videos of the playlist
    videos = []
    video_count = 0
    for vi in playlist_contents:
        video = {}
        try:
            video_info = vi["playlistPanelVideoRenderer"]
            video["id"] = video_info["videoId"]
            if "unplayableText" in video_info:
                # handle unplayable videos, which has no "title"
                print("[Warning] unplayable video: {0}\n".format(video["id"], video_info["unplayableText"]["simpleText"]))
                playlist_info["totalVideos"] -= 1
                continue
            video["title"] = video_info["title"]["simpleText"]
        except:
            print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
            continue
        videos.append(video)
        video_count += 1

    if not "totalVideos" in playlist_info or video_count != playlist_info["totalVideos"]:
        print("[Warning] incorrect number of videos")
    if not videos:
        print("[Error] unable to extract videos from playlist")
        return None
    playlist_info["videos"] = videos

    return playlist_info
    # {
    #     "title": str,
    #     "totalVideos": int,
    #     "videos": [
    #         {
    #             "id": str,
    #             "title": str
    #         },...
    #     ]
    # }

def youtube_pocket(args = sys.argv):
    # url pattern
    VID_PATTERN = r"^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(embed\/|v\/|(watch\?([a-zA-Z0-9_=;\-]+&)*v=))?(?P<video_id>[a-zA-Z0-9_\-]{11,})(\?[a-zA-Z0-9_=\-]+)?(?:&[a-zA-Z0-9_=;\-]+)*(?:\#[a-zA-Z0-9_=;\-]+)*$"
    LID_PATTERN = r"^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?|playlist\?)([a-zA-Z0-9_=;\-]+&)*list=(?P<playlist_id>[a-zA-Z0-9_\-]{18,})(\?[a-zA-Z0-9_=\-]+)?(?:&[a-zA-Z0-9_=;\-]+)*(?:\#[a-zA-Z0-9_=;\-]+)*$"

    print("Youtube Pocket - youtube music/playlist downloader\n")

    # can be executed as python script or cmd tool
    if len(args) > 1:
        CRAWL_URL = args[1]
        print("URL: {0}".format(CRAWL_URL))
    else:
        CRAWL_URL = input("URL: ")

    # check input url
    prog_vid = re.compile(VID_PATTERN)
    prog_lid = re.compile(LID_PATTERN)
    while not (prog_vid.match(CRAWL_URL) or prog_lid.match(CRAWL_URL)):
        print("[Error] invalid URL: \"{0}\"".format(CRAWL_URL))
        CRAWL_URL = input("URL: ")
    print("")

    # prase input url
    video_id = None
    playlist_id = None
    v_m = prog_vid.match(CRAWL_URL)
    if v_m:
        video_id = v_m.group("video_id")
    l_m = prog_lid.match(CRAWL_URL)
    if l_m:
        playlist_id = l_m.group("playlist_id")

    # handle video/playlist ambiguity
    if playlist_id and video_id:
        choice = input("(a)only the current vidoe or (b)the whole playlist: ")
        while choice != 'a' and choice != 'b':
            choice = input("(a)only the current vidoe or (b)the whole playlist: ")
        if choice == 'a':
            playlist_id = None
        print("")

    # download
    dl_count = 0
    if playlist_id:
        # download the whole playlist

        playlist_info = get_playlist_info(playlist_id, video_id)
        if not playlist_info:
            return

        # download videos to one directory
        dir_name = ""
        try:
            dir_name = playlist_info["title"]
            print("[Playlist] download playlist: {0} with {1} videos\n".format(playlist_info["title"], playlist_info["totalVideos"]))
        except:
            print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

        # download videos
        for vi in playlist_info["videos"]:
            if download(vi["id"], None, dir_name):
                dl_count += 1
            else:
                print("Something went wrong. Skipping video {0}".format(v_id))

    elif video_id:
        # download one video

        if download(video_id):
            dl_count += 1
        else:
            print("Something went wrong. Skipping video {0}".format(video_id))

    else:
        # should not happen
        return

    print("\n[Complete] downloaded {0} video(s)".format(dl_count))
    return

if __name__ == "__main__":
    try:
        youtube_pocket()
    except:
        print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))


