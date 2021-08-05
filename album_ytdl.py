from bs4 import BeautifulSoup
import requests
import json
import re
import youtube_dl
import os

HEADER = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
link = "https://www.youtube.com/playlist?list=PLR88DX42WbRomH5g0MrM1zaTOa5rNgUgC"

response = requests.get(link, headers=HEADER)
soup = BeautifulSoup(response.text, "html.parser")

with open('youtube_content2.json', 'w', encoding = 'utf-8') as f:
    json.dump(response.text, f, ensure_ascii = False)


pattern = r'"watchEndpoint":\{"videoId":"[a-zA-Z0-9_.+-]+","playlistId":"[a-zA-Z0-9_.+-]+","index":[0-9]+,"params"'
m = re.findall(pattern, response.text)

VideoId = []
for i in range(0, len(m)):
    if not m[i] in VideoId:
        VideoId.append(m[i].replace('"watchEndpoint":{"videoId":"', ''))

for j in range(0,len(VideoId)):
    print(VideoId[j][0:11])
print(len(VideoId))

cut_link = link.replace('playlist?', '&')
new_link = cut_link.split("&")

LINK = []
for j in range(0, len(VideoId)):
    LINK.append(new_link[0]+'watch?v='+VideoId[j][0:11]+'&'+new_link[1])
    print(LINK[j])

ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

print("LINK_len=", len(LINK))

for i in range(0,len(LINK)):
    with ydl:
        result = ydl.extract_info(LINK[i][0:43], download=True)
        video_info = result.get('title')
        print("video_info" + video_info)

    Video_name = LINK[i].replace('https://www.youtube.com/watch?v=', '')[0:11]
    Video_name += '.mp4'
    Dirname = os.path.dirname(Video_name)
    new_name = Dirname + video_info.replace('/', '') + '.mp4'
    filename = os.path.abspath(Video_name)
    print("filename = " + filename)
    print("new_name = " + new_name)
    os.rename(filename, new_name)
