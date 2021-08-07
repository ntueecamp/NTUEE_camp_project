import requests
import json
import re
import youtube_dl

print("Youtube Pocket - youtube music/playlist downloader\n")

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

VID_PATTERN = r"^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(embed\/|v\/|(watch\?([a-zA-Z0-9_=;\-]+&)*v=))?(?P<video_id>[a-zA-Z0-9_\-]{11,})(\?[a-zA-Z0-9_=\-]+)?(?:&[a-zA-Z0-9_=;\-]+)*(?:\#[a-zA-Z0-9_=;\-]+)*$"
LID_PATTERN = r"^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?|playlist\?)([a-zA-Z0-9_=;\-]+&)*list=(?P<playlist_id>[a-zA-Z0-9_\-]{18,})(\?[a-zA-Z0-9_=\-]+)?(?:&[a-zA-Z0-9_=;\-]+)*(?:\#[a-zA-Z0-9_=;\-]+)*$"
YT_DATA_PATTERN = r"var ytInitialData = (?P<JsonData>.*?);<\/script>"

class Video(object):
    def __init__(self, vid = None, title = None, length_text = None):
        self.id = vid
        self.title = title
        self.length_text = length_text

def get_data(url):
    global USER_AGENT, YT_DATA_PATTERN
    response = requests.get(url, headers = {"user-agent" : USER_AGENT})
    if not response.ok:
        return None
    raw_content = response.text
    data = json.loads(re.search(YT_DATA_PATTERN, raw_content).group("JsonData"))
    return data

def get_one_video(lid):
    url = "https://www.youtube.com/playlist?list=" + lid
    data = get_data(url)
    vid = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"][0]["playlistVideoRenderer"]["videoId"]
    return vid

CRAWL_URL = input("URL: ")
# CRAWL_URL = "https://www.youtube.com/watch?v=wvrQU9VCts0&list=PL2mVqrrF_bnn5qt_fqHZNRzWjKp4jqfyF"
# CRAWL_URL = "https://www.youtube.com/playlist?list=PL2mVqrrF_bnn5qt_fqHZNRzWjKp4jqfyF"
# CRAWL_URL = "https://www.youtube.com/watch?v=wvrQU9VCts0"

prog_vid = re.compile(VID_PATTERN)
prog_lid = re.compile(LID_PATTERN)
video_id = None
playlist_id = None
while not prog_vid.match(CRAWL_URL) and not prog_lid.match(CRAWL_URL):
    print("Invalid URL")
    CRAWL_URL = input("URL: ")

video_id = re.match(VID_PATTERN, CRAWL_URL)
if video_id:
    video_id = video_id.group("video_id")
playlist_id = re.match(LID_PATTERN, CRAWL_URL)
if playlist_id:
    playlist_id = playlist_id.group("playlist_id")

if playlist_id:
    if not video_id:
        video_id = get_one_video(playlist_id)
    CRAWL_URL = "https://www.youtube.com/watch?v=" + video_id + "&list=" + playlist_id
elif video_id:
    CRAWL_URL = "https://www.youtube.com/watch?v=" + video_id
else:
    exit()

print("Requsteing: {}".format(CRAWL_URL))
DATA = get_data(CRAWL_URL)

try:
    playlist = DATA["contents"]["twoColumnWatchNextResults"]["playlist"]["playlist"]
except Exception as e:
    print(e)

playlist_title = playlist["title"]
playlist_length = playlist["totalVideos"]
videos = []
for vi in playlist["contents"]:
    video_info = vi["playlistPanelVideoRenderer"]
    videos.append(Video(vid = video_info["videoId"], title = video_info["title"]["simpleText"], length_text = video_info["lengthText"]["simpleText"]))

print("Downloading playlist: {0} with {1} videos\n".format(playlist_title, playlist_length))
i = 1
for vi in videos:
    print("# {0}  [Processing] {1}".format(i, vi.title))
    ydl_opts = {"format": "mp4", "outtmpl": "{0}/{1}-{2}.%(ext)s".format(playlist_title, vi.title, vi.length_text)}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        url = "https://www.youtube.com/watch?v=" + vi.id
        ydl.download([url])
    i += 1
    print("")

print("Download complete!")
