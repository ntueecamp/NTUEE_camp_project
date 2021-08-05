from tkinter import *
from tk_func import display_logo
from PIL import Image, ImageTk      # pip install Pillow
import requests
import json
import re
import youtube_dl                   # pip install youtube_dl
import os
import time

root = Tk()

HEADER = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
pattern = r'"watchEndpoint":\{"videoId":"[a-zA-Z0-9_.+-]+","playlistId":"[a-zA-Z0-9_.+-]+","index":[0-9]+,"params"'

def clicked_l():
    lab_input_album_url.grid_forget()
    input_album_url.grid_forget()
    r_ok_btn.grid_forget()
    wrong_input.grid_forget()
    album_not_found_input.grid_forget()
    not_album_input.grid_forget()
    lab_input_video_url.grid(columnspan=3, column=0, row=6)
    input_video_url.grid(columnspan=5, column=2, row=6)
    l_ok_btn.grid(columnspan=2, column=6, row=6)

def clicked_r():
    lab_input_video_url.grid_forget()
    input_video_url.grid_forget()
    l_ok_btn.grid_forget()
    not_video_input.grid_forget()
    wrong_input.grid_forget()
    video_not_found_input.grid_forget()
    video_progress.grid_forget()
    lab_input_album_url.grid(columnspan=3, column=0, row=6)
    input_album_url.grid(columnspan=5, column=2, row=6)
    r_ok_btn.grid(columnspan=2, column=6, row=6)

def clicked_ok_l():
    not_video_input.grid_forget()
    wrong_input.grid_forget()
    video_not_found_input.grid_forget()
    video_progress.grid_forget()
    if (video_url.get().startswith('https://')==False):
        wrong_input.grid(columnspan=2, column=8, row=6)
    else:
        # print("video:" + video_url.get())
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
        if video_url.get().find('playlist?list=') != -1:
            not_video_input.grid(columnspan=2, column=4, row=9)
            return
        video_progress_text.set("Downloading : 0/1")
        video_progress.grid(columnspan=2, column=8, row=6)
        video_title.grid(columnspan=10, column=2, row=9)
        with ydl:
            try:
                result = ydl.extract_info(video_url.get(), download=True)   # download or not
            except:
                video_not_found_input.grid(columnspan=2, column=4, row=9)
                return
            video_progress_text.set("Downloading : 1/1")
            video_info = result.get('title')
            print("video_info" + video_info)
            video_title_text.set(video_info)

        Video_name = video_url.get().replace('https://www.youtube.com/watch?v=', '')
        Video_name += '.mp4'
        Dirname = os.path.dirname(Video_name)
        new_name = Dirname + video_info.replace('/', '') + '.mp4'
        filename = os.path.abspath(Video_name)
        print("filename = " + filename)
        print("new_name = " + new_name)
        os.rename(filename, new_name)


def clicked_ok_r():
    wrong_input.grid_forget()
    album_not_found_input.grid_forget()
    not_album_input.grid_forget()

    if (album_url.get().startswith('https://')==False):
        wrong_input.grid(columnspan=2, column=8, row=6)
    else:
        # print("album:" + album_url.get())
        try:
            response = requests.get(album_url.get(), headers=HEADER)
        except:
            not_album_input.grid(columnspan=2, column=4, row=9)
            return
        m = re.findall(pattern, response.text)
        if len(m) == 0:
            if album_url.get().find('playlist?list=') != -1:
                album_not_found_input.grid(columnspan=2, column=4, row=9)
            else:
                not_album_input.grid(columnspan=2, column=4, row=9)
            return

        video_progress_text.set("Downloading : "+str(len(m))+"//"+str(len(m)))
        video_progress.grid(columnspan=2, column=8, row=6)
        video_title.grid(columnspan=5, column=1, row=9)

        VideoId = []
        for i in range(0, len(m)):
            if not m[i] in VideoId:
                VideoId.append(m[i].replace('"watchEndpoint":{"videoId":"', ''))

        for j in range(0,len(VideoId)):
            print(VideoId[j][0:11])
        print(len(VideoId))

        cut_link = album_url.get().replace('playlist?', '&')
        new_link = cut_link.split("&")

        LINK = []
        for j in range(0, len(VideoId)):
            LINK.append(new_link[0]+'watch?v='+VideoId[j][0:11]+'&'+new_link[1])
            print(LINK[j])
        
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

        print("LINK_len=", len(LINK))

        for i in range(0,len(LINK)):
            with ydl:
                result = ydl.extract_info(LINK[i][0:43], download=True)   # download or not
                video_info = result.get('title')
                print("video_info" + video_info)
            video_progress_text.set("Downloading : "+str(i+1)+"/"+str(len(m)))
            video_title_text.set(video_info)   

            
            Video_name = LINK[i].replace('https://www.youtube.com/watch?v=', '')[0:11]
            Video_name += '.mp4'
            Dirname = os.path.dirname(Video_name)
            new_name = Dirname + video_info.replace('/', '') + '.mp4'
            filename = os.path.abspath(Video_name)
            print("filename = " + filename)
            print("new_name = " + new_name)
            os.rename(filename, new_name)



root.title('youtube downloader')
root.geometry('+%d+%d'%(250,20))

header = Frame(root, width=800, height=175, bg="white")
header.grid(columnspan=10, rowspan=5, row=0)

url_in = Frame(root, width=800, height=60, bg="#c8c8c8")
url_in.grid(columnspan=10, rowspan=1, row=6)

main_content = Frame(root, width=800, height=250, bg="#20bebe")
main_content.grid(columnspan=10, rowspan=3, row=9)

display_logo('ytdl_logo.png', 0, 0)

choose_l_btn = Button(root, text="Download video", font=("Arial",10), command=clicked_l, borderwidth = 0, bg="#20bebe", fg="white", width=15, height=1)
choose_l_btn.grid(columnspan=2, column=7,row=1)

choose_r_btn = Button(root, text="Download album", font=("Arial",10), command=clicked_r, borderwidth=0, bg="#20bebe", fg="white", width=15, height=1)
choose_r_btn.grid(columnspan=2, column=7,row=3)

lab_input_video_url = Label(root, text="video url :", font=("Arial",10), bg="#c8c8c8")
lab_input_album_url = Label(root, text="album url :", font=("Arial",10), bg="#c8c8c8")

video_url = StringVar()
album_url = StringVar()
video_progress_text = StringVar()
video_title_text = StringVar()

input_video_url = Entry(root, textvariable=video_url, width=45)
input_album_url = Entry(root, textvariable=album_url, width=45)

l_ok_btn = Button(root, text="OK", font=("Arial",10), command=clicked_ok_l, borderwidth=0, bg="#20bebe", fg="white", width=3, height=1)
r_ok_btn = Button(root, text="OK", font=("Arial",10), command=clicked_ok_r, borderwidth=0, bg="#20bebe", fg="white", width=3, height=1)

wrong_input = Label(root, text="NOT URL !", font=("Arial",12), bg="#c8c8c8", fg="#E62117")
not_album_input = Label(root, text="NOT AN ALBUM !", font=("Arial",12), bg="#20bebe", fg="#E62117")
album_not_found_input = Label(root, text="ALBUM NOT FOUND !", font=("Arial",12), bg="#20bebe", fg="#E62117")
not_video_input = Label(root, text="NOT A VIDEO !", font=("Arial",12), bg="#20bebe", fg="#E62117")
video_not_found_input = Label(root, text="VIDEO NOT FOUND !", font=("Arial",12), bg="#20bebe", fg="#E62117")

video_progress = Label(root, textvariable=video_progress_text, font=("Arial",12), fg="black")
video_title = Label(root, textvariable=video_title_text, font=("Arial",10), bg="#20bebe", fg="black")








root.mainloop()