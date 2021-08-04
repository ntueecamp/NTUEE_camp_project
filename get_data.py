import requests
import json
import re

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

# CRAWL_URL = input("URL: ")
CRAWL_URL = "https://www.youtube.com/watch?v=wvrQU9VCts0&list=PL2mVqrrF_bnn5qt_fqHZNRzWjKp4jqfyF"
# CRAWL_URL = "https://www.youtube.com/playlist?list=PL2mVqrrF_bnn5qt_fqHZNRzWjKp4jqfyF"
# CRAWL_URL = "https://www.youtube.com/watch?v=wvrQU9VCts0"

response = requests.get(CRAWL_URL, headers = {"user-agent" : USER_AGENT})
raw_content = response.text

pattern = r"var ytInitialData = (?P<JsonData>.*?);<\/script>"
result = re.search(pattern, raw_content).group("JsonData")
data = json.loads(result)

try:
    cur_video = data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]
    cur_video_info = cur_video[0]["videoPrimaryInfoRenderer"]
    owner_info = cur_video[1]["videoSecondaryInfoRenderer"]
    recommend_video = data["contents"]["twoColumnWatchNextResults"]["secondaryResults"]["secondaryResults"]["results"]
    playlist = data["contents"]["twoColumnWatchNextResults"]["playlist"]["playlist"]
except Exception as e:
    print(e)

