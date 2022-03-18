import json
import requests
import random
import io
import os
import asyncio
from PIL import Image
from dotenv import load_dotenv
from libs import fleep
from urllib.request import urlopen
from termcolor import colored
from datetime import datetime
import time


load_dotenv("config.env")
seconds_between_posts = int(os.getenv("TIME"))


#Thanks iFunny user Affect for this dope function that prints in pretty colors
def cprint(*args, end_each=" ", end_all=""):
	dt = str(datetime.fromtimestamp(int(time.time())))
	print(colored(dt, "white"), end=end_each)
	for i in args:
		print(colored(str(i[0]), i[1].lower()), end=end_each)
	print(end_all)


try:
    with open("./libs/bearer.json","r") as f:
        data = json.load(f)

        bearer = data.get("bearer")
except:
    cprint(("You need to run the Login file first! Read the README!","red"))
    bearer = None

async def crop_watermark(url):

    img = Image.open(requests.get(url, stream=True).raw)
    w, h = img.size

    return img.crop((0,0,w,h-24)).tobytes()


async def get_collective():

    headers = {
    'Host': 'api.ifunny.mobi',
    'Accept': 'video/mp4, image/jpeg',
    'Applicationstate': '1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Bearer '+bearer,
    'Content-Length': '8',
    'Ifunny-Project-Id': 'iFunny',
    'User-Agent': 'iFunny/7.14.2(22213) iphone/14.0.1 (Apple; iPhone8,4)',
    'Accept-Language': 'en-US;q=1',
    'Accept-Encoding': 'gzip, deflate',}

    data = 'limit=100'

    r = requests.post('https://api.ifunny.mobi/v4/feeds/collective', headers=headers, data=data).json()

    memes = []

    for i in r['data']['content']['items']:
        data = {'type':i['type'],'url':i['url'],'tags':i['tags'],'approval':i['shot_status']}
        memes.append(data)
        
    with open("./libs/memes.json","w") as f:
        json.dump(memes,f,indent=1)
    return memes



#Main loop getting a random post and uploading to profile
async def autopost():

    if not bearer:
        return
    
    #Loads posts from existing memess.json file, or requests posts from ifunny and caches ~100 of them for later
    try:
        with open("./libs/memes.json","r") as f:
            data = json.load(f)
        
    except:
        data = await get_collective()
        
    

    while True:

        if data == []:
            data = await get_collective()
        
        color = random.choice(["cyan","magenta","green","blue","yellow"])
        
        meme = random.choice(data)
        url = meme["url"]
        m_type = meme["type"]
        tags = meme["tags"]


        if meme["approval"] != "approved":
            data.remove(meme)
            continue

        try:
            if m_type == "pic":
                image_bytes = await crop_watermark(url)
                
            else:
                r = urlopen(url).read()
                image_bytes = io.BytesIO(r)
        except:
            data.remove(meme)
            continue

        
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

        requests.post(url='https://api.ifunny.mobi/v4/content', data={'type':upload_type, 'tags':tags, 'description':'Posted using an autoposter made by Scripts', 'visibility':'public'}, headers=headers, files={uppload: ("image.tmp", image_bytes.getvalue(), mime[0])})

        cprint(("Posted a new meme! Refresh your profile.",color))
        
        data.remove(meme)
        with open("./libs/memes.json","w") as f:
            json.dump(data,f,indent=1)
        
        await asyncio.sleep(seconds_between_posts) 
        continue

asyncio.run(autopost())
