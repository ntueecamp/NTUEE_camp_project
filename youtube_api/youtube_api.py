import requests
import json
import os
import urllib.parse
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

API_KEY = "&key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk"
YOUTUBER = ""
PLAYLIST_ID = ""
VIDEO_IDS = []
NEXTPAGE_TOKEN = ["FIRST"]
URL = "https://www.googleapis.com/youtube/v3/"
INFO_TYPE = ["search", "channels", "playlistItems"]
PART_PARA = ["snippet", "contentDetails", ]
SEARCH_TYPE = ["channel", "playlist", "video"]
PAGE = 0
contents = {}
search_results = []
snippets = []

url_1 = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=UCMUnInmOkrWN4gof9KlhNmQ&key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk"
# get playlist ID from "uploads"
url_2 = "https://www.googleapis.com/youtube/v3/videos?id=agpAxwxeIk4&key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk&part=snippet"
# get title and discription of a video
url_3 = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails,status&playlistId=UUw2W7GIqJNB-UMUxncnMuiw&key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk&maxResults=10"
# get the videos of a channel's playlist(or any playlist with its ID), set the number of videos it returns
# if you want to get more results, add the "next page token" in the json to see the result of next page
url_4 = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails,status&playlistId=UUw2W7GIqJNB-UMUxncnMuiw&key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk&maxResults=10&pageToken=CAoQAA"
# can get the first page's token from "prev page token"
url_5 = "https://www.googleapis.com/youtube/v3/videos?id=agpAxwxeIk4&key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk&part=snippet,statistics"
# add parameters "statistics" at part to get like/dislike/view count/comment count of the video
url_6 = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=25&q=%A4%A4%A4%E5&key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk"
# add the keywords you want to search at q

def get_youtubers_list(url):
    print(url)
    req = requests.get(url)
    global contents
    contents.clear()
    contents = json.loads(req.text) # contents is a dictionary
    search_results = contents["items"] # search_results is a list
    snippets = [] # snippets is a list
    for s in search_results:
        # s are dictionaries
        snippets.append(s["snippet"])
    for i in range(len(snippets)):
        print("%2d. %s" %  (i + 1, snippets[i]["title"]))
    global PAGE
    NEXTPAGE_TOKEN.insert(PAGE + 1, contents["nextPageToken"])
    if PAGE == 1:
        NEXTPAGE_TOKEN[0] = contents["prevPageToken"]
    youtuber = choose_youtuber(url, contents, search)
    return contents, search_results, snippets, youtuber

def choose_youtuber(url):
    global PAGE
    youtuber = int(input("Which Youtuber are you looking for?\nPlease enter a number. Looking for more results, enter 0.\nGoing back to the previous page, enter -1\n"))
    if (youtuber <= 50) and (youtuber >= 1):
        return youtuber
    elif youtuber == 0:
        next_page(url, contents)
    elif (youtuber == -1) and PAGE != 0:
        url = prev_page(url)
        get_youtubers_list(url)
    elif (youtuber == -1) and PAGE == 0:
        print("You are already on the first page")
        choose_youtuber(url)
    else:
        print("invalid input")

def prev_page(url):
    url += "&pageToken="
    global PAGE
    url += NEXTPAGE_TOKEN[PAGE - 1]
    PAGE -= 1
    return url

def next_page(url, contents):
    url += "&pageToken="
    global PAGE
    url += NEXTPAGE_TOKEN[PAGE + 1]
    PAGE += 1
    get_youtubers_list(url)
    NEXTPAGE_TOKEN.insert(PAGE + 1, contents["nextPageToken"])
    with open("youtube_info.json", 'w', encoding = 'utf-8') as f:
        json.dump(contents, f, ensure_ascii = False)
    # if PAGE == 1:
        # NEXTPAGE_TOKEN[0] = contents["prevPageToken"]
    # choose_youtuber()
    
search_type = int(input("Youtubers(0)/Playlists(1)/Videos(2)"))
URL += "search?"
URL += "part=snippet"
URL += "&maxResults=10"
URL += "&type="
URL += SEARCH_TYPE[search_type]
keywords = urllib.parse.quote(input("What are you looking for?"))
URL += "&q="
URL += keywords
URL += API_KEY
print(URL)

if search_type == 0:
    CONTENTS, SEARCH_RESULTS, SNIPPETS, YOUTUBER = get_youtubers_list(URL)
    
        
with open("youtube_info.json", 'w', encoding = 'utf-8') as f:
   json.dump(contents, f, ensure_ascii = False)

