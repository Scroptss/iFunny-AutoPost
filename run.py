import json
import requests
import random
import io
import os
import asyncio
from dotenv import load_dotenv
from libs import fleep
from urllib.request import urlopen
from termcolor import colored
from datetime import datetime
import time

#Subreddit names to get your posts from. You can add or delete some but this is what i personally use
subreddits = ["dankmemes","memes","schizopostingmemes","cursed_images","shitposting","deepfriedmemes",
"surrealmemes", "nukedmemes", "bigbangedmemes", "wackytictacs", "bonehurtingjuice"] 

#edit this to determine how many seconds will pass before another post gets posted. I'd recommend a slow-ish speed as not to get shadow banned if they ever detect this.
load_dotenv("config.env")
seconds_between_posts = int(os.getenv("TIME"))
print(seconds_between_posts)

#Thanks iFunny user Affect for this dope function that prints in pretty colors
def cprint(*args, end_each=" ", end_all=""):
	dt = str(datetime.fromtimestamp(int(time.time())))
	print(colored(dt, "white"), end=end_each)
	for i in args:
		print(colored(str(i[0]), i[1].lower()), end=end_each)
	print(end_all)

try:
    with open("bearer.json","r") as f:
        data = json.load(f)

        bearer = data.get("bearer")
except:
    cprint(("You need to run the Login file first! Read the README!","red"))
    bearer = None

posted = []

#Main loop getting a post from reddit and uploading to profile
async def autopost():

    if not bearer:
        return
    
    while True:
        tag = random.choice(subreddits)
        color = random.choice(["cyan","magenta","green","blue","yellow"])
        r = requests.get("https://meme-api.herokuapp.com/gimme/"+tag).json()
        url = r.get("url")
        if not url:
            continue
        nsfw = r["nsfw"]
        if nsfw:
            continue
        #print(url)
        if url in posted:
            continue
        try:
            r = urlopen(url).read()
        except:
            continue

        image_bytes = io.BytesIO(r)
        mime = fleep.get(image_bytes.getvalue()).mime
        
        if mime:
            datatype = mime[0]
            if datatype.startswith("image/"):
                upload_type = "pic"

                if datatype.endswith("/gif"):
                    upload_type = "gif"

            elif datatype.startswith("video/"):
                upload_type = "video_clip"

        else:
            continue

        if upload_type == "video_clip":
            uppload = "video"
        else:
            uppload = "image"

        headers = {
            "Host": "api.ifunny.mobi",
            "Accept": "video/mp4, image/jpeg",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
            "ApplicationState": "1", 
            "Authorization":"Bearer " + bearer,
            "iFunny-Project-Id": "iFunny",
            "User-Agent": "iFunny/7.14.2(22213) iphone/14.0.1 (Apple; iPhone8,4)",
            "Accept-Language": "en-US;q=1, zh-Hans-US;q=0.9"
            }

        requests.post(url='https://api.ifunny.mobi/v4/content', data={'type':upload_type, 'tags':[], 'description':'', 'visibility':'public'}, headers=headers, files={uppload: ("image.tmp", image_bytes.getvalue(), mime[0])})
        posted.append(url)
        cprint(("Posted a new meme! Refresh your profile.",color))
        await asyncio.sleep(seconds_between_posts) 
        continue

asyncio.run(autopost())