import requests
import json
import re

CRAWL_URL = input("URL: ")
FILE_NAME = input("File name: ").split('.')[0]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

response = requests.get(CRAWL_URL, headers = {"user-agent" : USER_AGENT})

# soup = BeautifulSoup(response.text, "html.parser")

raw_content = response.text

with open(FILE_NAME+"_raw.html", 'w', encoding = "utf-8") as f:
    f.write(raw_content)

with open(FILE_NAME+".html", 'w', encoding = "utf-8") as f:
    f.write(raw_content)

# CONFIG_KEYWORD = "window._sharedData = "
# config_start_pos = raw_content.find(CONFIG_KEYWORD) + len(CONFIG_KEYWORD)
# config_end_pos = raw_content.find("</script>",config_start_pos) - 1

# FEED_KEYWORD = "window.__additionalDataLoaded('feed',"
# feed_start_pos = raw_content.find(FEED_KEYWORD,config_end_pos) + len(FEED_KEYWORD)
# feed_end_pos = raw_content.find("</script>",feed_start_pos) - 2

# data_config = json.loads(raw_content[config_start_pos:config_end_pos])
# data_feed = json.loads(raw_content[feed_start_pos:feed_end_pos])


# fp = codecs.open('data_config.json', 'w', 'utf-8')
# fp.write(json.dumps(data_config,ensure_ascii=False))
# fp.close()

