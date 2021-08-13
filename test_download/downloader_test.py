import requests
import time
import random
import subprocess

url = "https://r1---sn-3cgv-un5ee.googlevideo.com/videoplayback?expire=1628870426&ei=ukIWYYPjFZaE2roP8-ivqAM&ip=118.233.118.15&id=o-AD2hEo5Ygl2Fa8wxLvliKW5-M5Ilv9mZZYAGFneA08if&itag=140&source=youtube&requiressl=yes&mh=Tf&mm=31%2C29&mn=sn-3cgv-un5ee%2Csn-u4o-u2xd&ms=au%2Crdu&mv=m&mvi=1&pl=24&initcwndbps=1013750&vprv=1&mime=audio%2Fmp4&ns=E3c9nomVOOqFner7QPx8ywoG&gir=yes&clen=2102336&dur=129.822&lmt=1577727852102406&mt=1628848600&fvip=3&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=3531432&n=oTMNBAX19BQN72J8AjG&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAIxezHAEdhaZnaNy2fSLmcve8jrqOqzPwJVBXPYrDlbxAiEAnGn8iobVVRdbKNVRlmraMxW71MKKYNvaD4dFbj0MLkM%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIhAJDSxuT7DOowCUseTam2kMT6C2ajFAy5MD9tUd5lChxYAiBRGBT-r3GJnzNw3ZpiU92Sl07ouZ5qGLER3YYSqHZfMA%3D%3D"

chunk_size = random.randint(9375936, 10485760)
content_len = 2102336
byte_count = 0

file = open("test1.mp4", "wb")

start_t = time.time()
while byte_count < content_len - 1:
    start = byte_count
    end = start + chunk_size
    if end >= content_len:
        end = content_len - 1
    response = requests.get(url + "&range={0}-{1}".format(start, end))
    raw_content = response.content

    try:
        file.write(raw_content)
    except Exception as e:
        file.close()
        raise e
    byte_count += len(raw_content)
    print(time.time()-start_t, byte_count)

file.close()

# video_fn = "後宮生活】貓遇地震的反應？-o9_lKOnRJXs.mp4"
# audio_fn = "後宮生活】貓遇地震的反應？-o9_lKOnRJXs.m4a"
# output_fn = "貓遇地震的反應？.mp4"

# cmd = ["ffmpeg", "-y", "-i", video_fn, "-i", audio_fn, "-c", "copy", "-map", "0:v:0", "-map", "1:a:0", output_fn]
# subprocess.call(cmd)

