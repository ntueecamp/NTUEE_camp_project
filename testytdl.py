import youtube_dl

ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

with ydl:
    result = ydl.extract_info(
        'https://www.youtube.com/watch?v=Z1eiALxC_9I',
        download=True
    )