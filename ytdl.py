from bs4 import BeautifulSoup
import requests
import json
import re

HEADER = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
link = "https://www.youtube.com/playlist?list=PL2mVqrrF_bnn5qt_fqHZNRzWjKp4jqfyF"

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
    print(VideoId[j][0]+VideoId[j][1]+VideoId[j][2]+VideoId[j][3]+VideoId[j][4]+VideoId[j][5]+VideoId[j][6]+VideoId[j][7]+VideoId[j][8]+VideoId[j][9]+VideoId[j][10])
print(len(VideoId))

cut_link = link.replace('playlist?', '&')
new_link = cut_link.split("&")

LINK = []
for j in range(0, len(VideoId)):
    LINK.append(new_link[0]+'watch?v='+VideoId[j][0]+VideoId[j][1]+VideoId[j][2]+VideoId[j][3]+VideoId[j][4]+VideoId[j][5]+VideoId[j][6]+VideoId[j][7]+VideoId[j][8]+VideoId[j][9]+VideoId[j][10]+'&'+new_link[1])
    print(LINK[j])