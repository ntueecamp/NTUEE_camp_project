import requests
import json
import urllib.parse
import csv
import matplotlib.dates as md
import matplotlib.pyplot as plt
import datetime
from pylab import figure, show

# apply for API key on https://console.cloud.google.com/flows/enableapi?apiid=youtube&pli=1
# can apply multiple keys since google restricts the times you request(50000 requests per day per project)
API_KEY = "YOUR_OWN_API_KEY"
# some constants, lists and dictionaries
YOUTUBER = ""
PLAYLIST_ID = ""
VIDEO = ""
VIDEO_IDS = []
VIDEO_DATES = []
VIDEO_TITLES = []
NEXTPAGE_TOKEN = ["FIRST"]
URL = "https://www.googleapis.com/youtube/v3/"
INFO_TYPE = ["search", "channels", "playlistItems"]
PART_PARA = ["snippet", "contentDetails", ]
SEARCH_TYPE = ["channel", "playlist", "video"]
PAGE = 0
contents = {}
search_results = []
snippets = []
MAX_RESULT = 10
RESULT = -2

# sample request url and parameters
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

def crawl(url):
    # request website contents
    req = requests.get(url)
    global contents
    contents.clear()
    contents = json.loads(req.text) # contents is a dictionary
    # check if we get our desired contents
    with open("check.json", 'w', encoding = 'utf-8') as f:
        json.dump(contents, f, ensure_ascii = False)
    global search_results
    search_results.clear()
    search_results = contents["items"] # search_results is a list

def get_search_list(url, type): 
    crawl(url)
    global snippets # snippets is a list
    snippets = []
    for s in search_results:
        # s are dictionaries
        snippets.append(s["snippet"])
    # print out 10 search resluts' title and description
    for i in range(len(snippets)):
        print("%2d. %s\n%s" %  (i + 1, snippets[i]["title"], snippets[i]["description"]))
        if snippets[i]["description"] != '':
            print()
    # if there are more than 10 results according to the keyword
    # results will be recorded in different pages, and each page has its own token
    # save nth page's token at list[n - 1]
    global PAGE
    NEXTPAGE_TOKEN.insert(PAGE + 1, contents["nextPageToken"])
    # get the first page's token on the second page's "prevPageToken"
    if PAGE == 1:
        NEXTPAGE_TOKEN[0] = contents["prevPageToken"]
    choose_result(url, type)

def choose_result(url, type):
    global PAGE
    # ask users to choose the youtuber/playlist/video they are looking for
    question = "Which "
    if int(type) == 0:
        question += "youtuber"
    else:
        question += SEARCH_TYPE[int(type)]
    question += " are you looking for?\nPlease enter a number. Looking for more results, enter 0.\nGoing back to the previous page, enter -1\n"
    result = int(input(question))
    '''
    check_value = False
    while(check_value == False):
        try:
            result = int(input(question))
            check_value = True
        except ValueError:
            check_value = False
    '''
    global MAX_RESULT
    global RESULT
    if (result <= MAX_RESULT) and (result >= 1):
        # if they find their desired result on the current page
        # they will enter a number from 1 to 10
        RESULT = result
    elif result == 0:
        # go to next page
        url = next_page(url)
        get_search_list(url, type)
    elif (result == -1) and PAGE != 0:
        # go to previous page
        url = prev_page(url)
        get_search_list(url, type)
    elif (result == -1) and PAGE == 0:
        print("You are already on the first page")
        choose_result(url, type)
    else:
        print("invalid input")
        choose_result(url, type)

def prev_page(url):
    # add the previous page token to the url
    index = int(url.find("&pageToken"))
    if index != -1:
        token = url[index:len(url)]
        url = url.replace(token, '')
    url += "&pageToken="
    global PAGE
    url += NEXTPAGE_TOKEN[PAGE - 1]
    PAGE -= 1
    return url

def next_page(url):
    # add the next page token to the url
    index = int(url.find("&pageToken"))
    if index != -1:
        token = url[index:len(url)]
        url = url.replace(token, '')
    url += "&pageToken="
    global PAGE
    url += NEXTPAGE_TOKEN[PAGE + 1]
    PAGE += 1
    return url

def get_videos_list(url):
    # save videos' information of a youtuber to lists
    crawl(url)
    global VIDEO_IDS
    global VIDEO_DATES
    for s in search_results:
        VIDEO_IDS.append(s["snippet"]["resourceId"]["videoId"])
        VIDEO_TITLES.append(s["snippet"]["title"])
        VIDEO_DATES.append(s["snippet"]["publishedAt"])
    global PAGE
    global NEXTPAGE_TOKEN
    try:
        NEXTPAGE_TOKEN.insert(PAGE + 1, contents["nextPageToken"])
        END = False
    except KeyError:
        END = True
    if PAGE == 1:
        NEXTPAGE_TOKEN[0] = contents["prevPageToken"]
    # keep looking for the next page and save all datas
    if END == False:
        url = next_page(url)
        get_videos_list(url)

def get_videos_statistics(url):
    with open("youtube_statistics.csv", 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'title', 'publishDate','viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount'])
    get_videos_list(url)
    # get information of a video by its ID
    for i in range(len(VIDEO_IDS)):
        if(VIDEO_TITLES[i] != "Private video") and (VIDEO_TITLES[i] != "Deleted video"):
            get_video_info(VIDEO_IDS[i], VIDEO_TITLES[i], VIDEO_DATES[i])

def get_video_info(Id ,title, date):
    with open("youtube_statistics.csv", 'a', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        url = "https://www.googleapis.com/youtube/v3/videos?key=AIzaSyD2J2lqnjE5V0fHviEICHMtc2PSKqY7ISk&part=snippet,statistics"
        url += "&id="
        url += Id
        crawl(url)
        # get information of a video and write them into youtube_statistics.csv
        try:
            viewCount = search_results[0]["statistics"]["viewCount"]
        except KeyError:
            viewCount = "No statistic"
        try:
            likeCount = search_results[0]["statistics"]["likeCount"]
        except KeyError:
            likeCount = "No statistic"
        try:
            dislikeCount = search_results[0]["statistics"]["dislikeCount"]
        except KeyError:
            dislikeCount = "No statistic"
        try:
            favoriteCount = search_results[0]["statistics"]["favoriteCount"]
        except KeyError:
            favoriteCount = "No statistic"
        try:
            commentCount = search_results[0]["statistics"]["commentCount"]
        except KeyError:
            commentCount = "No statistic"
        writer.writerow([Id, title, date, viewCount,likeCount, dislikeCount, favoriteCount, commentCount])
        

def generate_playlist_url(playlist_id):
    # add parameters to the URL to get song from a playlist
    url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails,status"
    url += "&playlistId="
    url += PLAYLIST_ID
    url += API_KEY
    url += "&maxResults=50"
    return url

def change_date(time):
    # date is a string but we can't use string to compare
    # we change its type from string to datetime
    date = time.split('T')
    item = date[0].split('-')
    year = int(item[0])
    month = int(item[1])
    day = int(item[2])
    dt = md.date2num(datetime.datetime(year, month, day))
    return dt

def plot_graph(csv_file):
    with open(csv_file, 'r', newline = '') as csvfile:
        # read information from csv file
        rows = list(csv.reader(csvfile))
        list_x = []
        for row in rows:
            if row[0] != 'ID':
                dt = change_date(row[2])
                list_x.append(dt)
        for i in range(3,8):
            # plot graph of statistics-time
            list_y = []
            for row in rows:
                if row[0] != 'ID': 
                    list_y.append(int(row[i]))
            '''
            # another way to plot graph, but not that pretty
            fig = figure()
            ax = fig.add_subplot(1,1,1)
            ax.plot_date(list_x, list_y, '-')
            fig.autofmt_xdate()
            show()
            '''
            plt.plot(list_x, list_y)
            plt.show()

# ask the user which type of information are they looking for
search_type = int(input("Youtubers(0)/Playlists(1)/Videos(2)"))
if search_type != 3:
    URL += "search?" # use the search function of the API
    URL += "part=snippet"
    # actually I don't know what it is but it contains almost everything I need
    # the API will tell you what information you should add to get the source code you want
    URL += "&maxResults=10" # number of results show on every page
    URL += "&type="
    URL += SEARCH_TYPE[search_type]
    # input keywords and encode the keywords to url 
    keywords = urllib.parse.quote(input("What are you looking for?"))
    URL += "&q="
    URL += keywords
    # add API key in your url to access the API
    URL += API_KEY

if search_type == 0:
    get_search_list(URL, search_type)
    index = RESULT - 1
    YOUTUBER = snippets[index]["channelId"]
    # get the channel ID first
    PAGE = 0
    URL = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails"
    URL += "&id="
    URL += YOUTUBER
    URL += API_KEY
    crawl(URL)
    # then get the channel's playlist ID
    PLAYLIST_ID = search_results[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    URL = generate_playlist_url(PLAYLIST_ID)
    NEXTPAGE_TOKEN = ["FIRST"]
    get_videos_statistics(URL)
    plot_graph("youtube_statistics.csv")

if search_type == 1:
    get_search_list(URL, search_type)
    index = RESULT - 1
    # get the playlist ID
    PLAYLIST_ID = search_results[index]["id"]["playlistId"]
    URL = generate_playlist_url(PLAYLIST_ID)
    NEXTPAGE_TOKEN = ["FIRST"]
    get_videos_statistics(URL)
    plot_graph("youtube_statistics.csv")

if search_type == 2:
    get_search_list(URL, search_type)
    index = RESULT - 1
    # get the video ID
    VIDEO = search_results[index]["id"]["videoId"]
    with open("youtube_statistics.csv", 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'title', 'publishDate','viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount'])
    get_video_info(VIDEO, search_results[0]["snippet"]["title"], search_results[0]["snippet"]["publishedAt"])
    # since there are only one video's information so I just print it out
    with open("youtube_statistics.csv", 'r', newline = '') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            if row[0] != 'ID':
                print("Title: ", row[1], "\npublishTime: ", row[2], "\nViewCount: ", row[3], "\nLikeCount: ", row[4],
                "\ndislikeCount: ", row[5], "\nfavoriteCount: ", row[6], "\ncommentCount: ", row[7]) 

if search_type == 3:
    # for plot test because there are limits on request QQ
    plot_graph("youtube_statistics.csv")