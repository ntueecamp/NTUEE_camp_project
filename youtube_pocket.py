import requests
from urllib import parse
import json
import re
import time
import random
import subprocess
import sys, os

print("Youtube Pocket - youtube music/playlist downloader\n")

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

VID_PATTERN = r"^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(embed\/|v\/|(watch\?([a-zA-Z0-9_=;\-]+&)*v=))?(?P<video_id>[a-zA-Z0-9_\-]{11,})(\?[a-zA-Z0-9_=\-]+)?(?:&[a-zA-Z0-9_=;\-]+)*(?:\#[a-zA-Z0-9_=;\-]+)*$"
LID_PATTERN = r"^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?|playlist\?)([a-zA-Z0-9_=;\-]+&)*list=(?P<playlist_id>[a-zA-Z0-9_\-]{18,})(\?[a-zA-Z0-9_=\-]+)?(?:&[a-zA-Z0-9_=;\-]+)*(?:\#[a-zA-Z0-9_=;\-]+)*$"
YT_PLAYER_PATTERN = r"var ytInitialPlayerResponse = (?P<JsonData>{.*?}}});"
YT_DATA_PATTERN = r"var ytInitialData = (?P<JsonData>{.*?}}});"

PREF_ITAG= {      "video": [137, 399, 136, 398, 135, 397, 134, 396, 133, 395, 160, 394],
                  "audio": [140, 141, 139],
            "video/audio": [37, 22, 18]}

def get_player_and_data(url):
    global USER_AGENT, YT_PLAYER_PATTERN, YT_DATA_PATTERN
    response = requests.get(url, headers = {"user-agent" : USER_AGENT})
    if not response.ok:
        return None, None
    raw_content = response.text

    player = None
    data = None
    result_player = re.search(YT_PLAYER_PATTERN, raw_content)
    if result_player:
        player = json.loads(result_player.group("JsonData"))
    result_data = re.search(YT_DATA_PATTERN, raw_content)
    if result_data:
        data = json.loads(result_data.group("JsonData"))

    return player, data

def get_one_video(lid):
    url = "https://www.youtube.com/playlist?list=" + lid
    _, data = get_player_and_data(url)
    vid = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"][0]["playlistVideoRenderer"]["videoId"]
    return vid

def get_dl_fmts(PLAYER):
    global PREF_ITAG
    SIG_URL_PATTERN = r"s=(?P<sig>.*?)(&.*?)*&url=(?P<url>.*)"
    prog_sig_url = re.compile(SIG_URL_PATTERN)
    try:
        available_fmts = PLAYER["streamingData"]["formats"] + PLAYER["streamingData"]["adaptiveFormats"]
    except:
        print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

    video_dl_fmt = None
    for v_itag in PREF_ITAG["video"]:
        for fmt in available_fmts:
            if "itag" in fmt and ("url" in fmt or "signatureCipher" in fmt) and v_itag == fmt["itag"]:
                if not "url" in fmt:
                    m = prog_sig_url.match(fmt["signatureCipher"])
                    sig = m.group("sig")
                    url = parse.unquote(m.group("url"))
                    fmt["url"] = "{0}&sig={1}".format(url, sig)
                video_dl_fmt = fmt
        if video_dl_fmt is not None:
            break

    audio_dl_fmt = None
    for a_itag in PREF_ITAG["audio"]:
        for fmt in available_fmts:
            if "itag" in fmt and ("url" in fmt or "signatureCipher" in fmt) and a_itag == fmt["itag"]:
                if not "url" in fmt:
                    m = prog_sig_url.match(fmt["signatureCipher"])
                    sig = m.group("sig")
                    url = parse.unquote(m.group("url"))
                    fmt["url"] = "{0}&sig={1}".format(url, sig)
                audio_dl_fmt = fmt
        if audio_dl_fmt is not None:
            break

    video_audio_dl_fmt = None
    if not (video_dl_fmt and audio_dl_fmt):
        for va_itag in PREF_ITAG["video/audio"]:
            for fmt in available_fmts:
                if "itag" in fmt and ("url" in fmt or "signatureCipher" in fmt) and va_itag == fmt["itag"]:
                    if not "url" in fmt:
                        m = prog_sig_url.match(fmt["signatureCipher"])
                        sig = m.group("sig")
                        url = parse.unquote(m.group("url"))
                        fmt["url"] = "{0}&sig={1}".format(url, sig)
                    video_audio_dl_fmt = fmt
            if video_audio_dl_fmt is not None:
                break

    return {      "video": video_dl_fmt,
                  "audio": audio_dl_fmt,
            "video/audio": video_audio_dl_fmt}

def validate_filename(name):
    def replace(m):
        if m.group(0) == "\"" or m.group(0) == "*" or m.group(0) == "<" or m.group(0) == ">":
            return "\'"
        else:
            return "_"
    new_name = re.sub(r"[<>:?\.\"\*\/\|\\]", replace, name)
    new_name = re.sub(r"\s+", " ", new_name)
    new_name = re.sub(r"_+", "_", new_name)
    return new_name

def download(v_id, filename = None):
    print("Preparing: {0}".format(v_id))
    PLAYER, DATA = get_player_and_data("https://www.youtube.com/watch?v=" + v_id)
    
    dl_fmts = get_dl_fmts(PLAYER)     #dict
    if not (dl_fmts["video"] or dl_fmts["audio"] or dl_fmts["video/audio"]):
        print("No available formats.")
        return False

    try:
        v_title = DATA["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["title"]["runs"][0]["text"]
        v_length = int(PLAYER["videoDetails"]["lengthSeconds"])
    except:
        print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

    if filename is not None:
        filename = validate_filename(os.path.splitext(filename)[0])
    if not filename:
        if v_title:
            filename = validate_filename(v_title)
        else:
            filename = "ytVideo_{0}".format(int(time.time()))
    # filename without ext

    if dl_fmts["video"] and dl_fmts["audio"]:
        # download video
        video_fn = "{0}_v.mp4".format(validate_filename(v_id))
        video_len = int(dl_fmts["video"]["contentLength"])
        video_url = dl_fmts["video"]["url"]
        print("Downloading: {0}".format(video_fn))
        if not download_file(url = video_url, content_len = video_len, filename = video_fn):
            print("Failed to download the video part.")
            return False

        # download audio
        audio_fn = "{0}_a.m4a".format(validate_filename(v_id))
        audio_len = int(dl_fmts["audio"]["contentLength"])
        audio_url = dl_fmts["audio"]["url"]
        print("Downloading: {0}".format(audio_fn))
        if not download_file(url = audio_url, content_len = audio_len, filename = audio_fn):
            print("Failed to download the audio part.")
            return False

        # merge
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", video_fn, "-i", audio_fn, "-c", "copy", "-map", "0:v:0", "-map", "1:a:0", "{0}.mp4".format(filename)]
        print("Merging the video and the audio parts.")
        if subprocess.call(cmd) != 0:
            print("Failed to merge the video and the audio parts.")
            return False
        os.remove(video_fn)
        os.remove(audio_fn)

        return True

    elif dl_fmts["video/audio"]:
        # download video/audio
        va_fn = "{0}.mp4".format(filename)
        va_len = int(dl_fmts["video/audio"]["contentLength"])
        va_url = dl_fmts["video/audio"]["url"]
        print("Downloading: {0}".format(va_fn))
        if not download_file(url = va_url, content_len = va_len, filename = va_fn):
            print("Failed to download the whole video.")

        return True

def download_file(url, content_len = -1, filename = "_"):
    if content_len <= 0:
        print("Invalid content length.")
        return False
    chunk_size = random.randint(9375936, 10485760)
    byte_count = 0

    file = open(filename, "wb")
    while byte_count < content_len:
        start = byte_count
        end = start + chunk_size
        if end >= content_len:
            end = content_len - 1
        response = requests.get(url + "&range={0}-{1}".format(start, end))

        raw_content = response.content
        try:
            file.write(raw_content)
        except Exception as e:
            print("{0}: {1}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
            file.close()
            return False
        byte_count += len(raw_content)

    return byte_count == content_len

####################

CRAWL_URL = input("URL: ")
# CRAWL_URL = "https://www.youtube.com/watch?v=wvrQU9VCts0&list=PL2mVqrrF_bnn5qt_fqHZNRzWjKp4jqfyF"
# CRAWL_URL = "https://www.youtube.com/playlist?list=PL2mVqrrF_bnn5qt_fqHZNRzWjKp4jqfyF"
# CRAWL_URL = "https://www.youtube.com/watch?v=wvrQU9VCts0"

prog_vid = re.compile(VID_PATTERN)
prog_lid = re.compile(LID_PATTERN)
while not prog_vid.match(CRAWL_URL) and not prog_lid.match(CRAWL_URL):
    print("Invalid URL")
    CRAWL_URL = input("URL: ")

video_id = None
playlist_id = None
video_id = re.match(VID_PATTERN, CRAWL_URL)
if video_id:
    video_id = video_id.group("video_id")
playlist_id = re.match(LID_PATTERN, CRAWL_URL)
if playlist_id:
    playlist_id = playlist_id.group("playlist_id")

if playlist_id and video_id:
    tmp = input("(a)only the current vidoe or (b)the whole playlist :")
    while tmp != 'a' and tmp != 'b':
        tmp = input("(a)only the current vidoe or (b)the whole playlist :")
    if tmp == 'a':
        playlist_id = None

if playlist_id:
    # download whole playlist
    if not video_id:
        video_id = get_one_video(playlist_id)
    CRAWL_URL = "https://www.youtube.com/watch?v=" + video_id + "&list=" + playlist_id
elif video_id:
    # download one video
    if not download(video_id):
        print("Something went wrong. Skipping video {0}".format(video_id))
else:
    exit()

print("Download complete!")


################################################

# print("Requsteing: {0}".format(CRAWL_URL))
# PLAYER, DATA = get_player_and_data(CRAWL_URL)

# try:
#     playlist = DATA["contents"]["twoColumnWatchNextResults"]["playlist"]["playlist"]
# except Exception as e:
#     print(e)

# playlist_title = playlist["title"]
# playlist_length = playlist["totalVideos"]
# videos = []
# for vi in playlist["contents"]:
#     video_info = vi["playlistPanelVideoRenderer"]
#     videos.append(Video(vid = video_info["videoId"], title = video_info["title"]["simpleText"], length_text = video_info["lengthText"]["simpleText"]))

# print("Downloading playlist: {0} with {1} videos\n".format(playlist_title, playlist_length))
# i = 1
# for vi in videos:
#     print("# {0}  [Processing] {1}".format(i, vi.title))
#     ydl_opts = {"format": "mp4", "outtmpl": "{0}/{1}-{2}.%(ext)s".format(playlist_title, vi.title, vi.length_text)}
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         url = "https://www.youtube.com/watch?v=" + vi.id
#         ydl.download([url])
#     i += 1
#     print("")

# print("Download complete!")
