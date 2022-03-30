import json
import requests
import time
import json
import os
import webbrowser
import asyncio
import io
import random
from PIL import Image
from libs import fleep
from urllib.request import urlopen
from datetime import datetime
import sys


host = "https://api.ifunny.mobi"



#Getting an existing basic auth token, or creating a basic auth token if one doesnt exist
def get_or_create_basic():
    try:
        with open("./libs/bearer.json","r") as f:
            data = json.load(f)
            return data["basic"]
    except:
        from secrets import token_hex
        from hashlib import sha1
        from base64 import b64encode
        client_id = "JuiUH&3822"
        client_secret = "HuUIC(ZQ918lkl*7"
        device_id = token_hex(32)
        hashed = sha1(f"{device_id}:{client_id}:{client_secret}".encode('utf-8')).hexdigest()
        basic = b64encode(bytes(f"{f'{device_id}_{client_id}'}:{hashed}", 'utf-8')).decode()
        with open("./libs/bearer.json","w") as f:
            json.dump({'basic':basic},f,indent=1)
        return basic



#Where the magic happens :)
def login(email,password):

    index = 0
    data = get_or_create_basic()
    url = host+"/v4/oauth2/token"

    paramz = {'grant_type':'password','username': email,'password': password}
    header = {'Host': 'api.ifunny.mobi','Applicationstate': '1','Accept': 'video/mp4, image/jpeg','Content-Type': 'application/x-www-form-urlencoded','Authorization': 'Basic '+data,'Content-Length':'77','Ifunny-Project-Id': 'iFunny','User-Agent': 'iFunny/7.19.3(22399) iphone/15.1 (Apple; iPhone11,8)','Accept-Language': 'en-US;q=1','Accept-Encoding': 'gzip, deflate'}
    userheader = {'Host': 'api.ifunny.mobi','Accept': 'video/mp4, image/jpeg','Applicationstate': '1','Accept-Encoding': 'gzip, deflate','Ifunny-Project-Id': 'iFunny','User-Agent': 'iFunny/7.14.2(22213) iphone/14.0.1 (Apple; iPhone8,4)','Accept-Language': 'en-US;q=1','Authorization': 'Basic '+data,}
    
    #Main login loop that tries logging in // Bypasses captcha
    while True:

        r = requests.post(url,headers=header,data=paramz).json()

        #Checking for any errors in login
        if "error" in r:
            if r["error"] == "captcha_required":

                print("Captcha required, Please solve the captcha that appears, then close then window and press the \"enter\" key.")
                time.sleep(2)
                key = captchasolve(r["data"]["captcha_url"])
                if key == "Chrome":
                    return

                
                print("Logging in...Again..")

                #Logging in a second time after completing captcha
                try:
                    login = requests.post(url,headers=header,data=paramz).json()
                    bearer = login['access_token']
                    
                except:
                    print("Something went wrong, Probably user auth rate exceeded. Try again to confirm.")
                    return

                break

            if r["error"] == "unsupported_grant_type":
                print("Something went wrong. Try again?")
                return
            
            if r["error"] == "too_many_user_auths":
                print("Please wait about 10 minutes for iFunny's dumb user auth ratelimit, and run this again.")
                return
            
            if r["error"] == "forbidden":
                

                #Primes the bearer token that was freshly generated so it can be used 
                requests.get(host+"/v4/counters",headers=userheader)

                
                print("Priming your basic auth token... please wait")
                time.sleep(10)

                index += 1
                if index <= 1:
                    continue

                #If basic token priming fails twice, then its likely a credential problem
                print("Your email and password are not correct! Please check your credentials and try again.")
                return
            
            if r["error"] == "invalid_grant":
                print("Invalid characters in the Email or Password, or you forgot the '@gmail.com'")
                return
        break
    
    #Saving the user info to the Bearer.json file, so the run.py can work. Also requesting the username of the account you logged into to display in the terminal
    url = host+"/v4/account"
    daheader = {"Authorization":"Bearer "+login["access_token"],'Ifunny-Project-Id': 'iFunny','User-Agent': 'iFunny/7.14.1 (1120087) iphone/14.0.1 (Apple; iPhone8,4)'}
    req = requests.get(url,headers = daheader).json()

    
    data = requests.get(host+"/v4/users/"+req["data"]["id"],headers=userheader).json()

    with open("./libs/bearer.json","r") as bearer_file:
        s = json.load(bearer_file)
        s.update({'bearer':login['access_token'],'user_id':req['data']['id'],'username':req['data']['original_nick']})

    with open("./libs/bearer.json","w") as fi:
        json.dump(s,fi,indent=1)
    print(f"Logged in successfully as {data['data']['original_nick']}!")
    return bearer


#A simple Captcha solver that uses YOU to solve it
def captchasolve(captcha_id = str):

    pageurl = captcha_id

    try:
        webbrowser.open_new(pageurl)
        input()
        return
        
    except:
        print("IDK how you messed that one up, chief :/")
        return "Chrome"





#Autopost Stuff:
async def crop_watermark(url):

    img = Image.open(requests.get(url, stream=True).raw)
    w, h = img.size
    img.crop((0,0,w,h-24))
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format=img.format)

    return imgByteArr


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
async def autopost(bearer,seconds_between_posts):

    if not bearer:
        return
    
    #Loads posts from existing memess.json file, or requests posts from ifunny and caches ~100 of them for later
    try:
        with open("./libs/memes.json","r") as f:
            data = json.load(f)
        
    except:
        data = await get_collective()
        
    print("Autopost has started!")

    while True:

        if data == []:
            data = await get_collective()
        
        meme = random.choice(data)
        url = meme["url"]
        m_type = meme["type"]
        tags = meme["tags"]

        tags.extend(["scriptsautoposter","scripts","scropts","featured","gif","GIFS"])
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
        print(f"Posting a new {uppload.capitalize()}...")

        requests.post(url='https://api.ifunny.mobi/v4/content', data={'type':upload_type, 'tags':json.dumps(tags), 'description':'Posted using an autoposter made by Scripts', 'visibility':'public'}, headers=headers, files={uppload: ("image.tmp", image_bytes.getvalue(), mime[0])})
        print(f"Posted a new {uppload.capitalize()}! Refresh your profile.")
        
        data.remove(meme)
        with open("./libs/memes.json","w") as f:
            json.dump(data,f,indent=1)
        
        await asyncio.sleep(seconds_between_posts) 
        continue


def get_time():
    seconds_between_posts = input("Time in seconds between each post: ")
    if not seconds_between_posts.isdigit():
        print("Seconds needs to be a number, Exiting...")
        time.sleep(3)
        exit()
    return int(seconds_between_posts)


try:
    with open("./libs/bearer.json","r") as f:
        data = json.load(f)
        bearer = data['bearer']
    print("Using bearer token from previous login, if this doesnt work, delete the \"Bearer.json\" file in the libs folder.")
    seconds_between_posts = get_time()
    asyncio.run(autopost(bearer,seconds_between_posts))

except:
    email = input("Email: ")
    password = input("Password: ")
    bearer = login(email,password)
    seconds_between_posts = get_time()
    asyncio.run(autopost(bearer,seconds_between_posts))