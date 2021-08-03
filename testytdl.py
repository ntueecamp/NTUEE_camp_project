import youtube_dl
import os

ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
link = 'https://www.youtube.com/watch?v=Z1eiALxC_9I'

with ydl:
    result = ydl.extract_info(link, download=True)
    video_info = result.get('title')

print(video_info)

Video_name = link.replace('https://www.youtube.com/watch?v=', '')
Video_name += '.mp4'

filename = os.path.abspath(Video_name)
Dirname = os.path.dirname(Video_name)

new_name = Dirname + video_info + '.mp4'

if os.path.exists(filename):
    print("完整路徑名稱: "+filename)

os.rename(filename, new_name)
