import json
import requests
import time
import json
import os
import webbrowser
from dotenv import load_dotenv
from termcolor import colored
from datetime import datetime

#Load the config file and get the email and password
load_dotenv("config.env")
email = os.getenv("EMAIL") # Dont edit this, add your email in the config.env
password = os.getenv("PASSWORD") # Dont edit this, add your email in the config.env

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

#Thanks iFunny user Affect for this dope function that prints in pretty colors
def cprint(*args, end_each=" ", end_all=""):
	dt = str(datetime.fromtimestamp(int(time.time())))
	print(colored(dt, "white"), end=end_each)
	for i in args:
		print(colored(str(i[0]), i[1].lower()), end=end_each)
	print(end_all)



#Where the magic happens :)
def login():
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

                cprint(("Captcha required, Please solve the captcha that appears, then close then window and press the \"enter\" key.","red"))
                
                key = captchasolve(r["data"]["captcha_url"])
                if key == "Chrome":
                    return

                
                cprint(("Logging in...","green"))

                #Logging in a second time after completing captcha
                try:
                    login = requests.post(url,headers=header,data=paramz).json()
                    bearer = login['access_token']
                    
                except:
                    cprint(("Something went wrong, Probably user auth rate exceeded. Try again to confirm.","red"))
                    return

                break

            if r["error"] == "unsupported_grant_type":
                cprint(("Something went wrong. Try again?","red"))
                return
            
            if r["error"] == "too_many_user_auths":
                cprint(("Please wait about 10 minutes for iFunny's dumb user auth ratelimit, and run this again.","red"))
                return
            
            if r["error"] == "forbidden":
                

                #Primes the bearer token that was freshly generated so it can be used 
                requests.get(host+"/v4/counters",headers=userheader)

                
                cprint(("Priming your basic auth token... please wait","green"))
                time.sleep(10)

                index += 1
                if index <= 1:
                    continue

                #If basic token priming fails twice, then its likely a credential problem
                cprint(("Your email and password are not correct! Please check your credentials and try again.", "red"))
                return
            
            if r["error"] == "invalid_grant":
                cprint(("Invalid characters in the Email or Password, or you forgot the '@gmail.com'","red"))
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
    cprint(("Logged in successfully as","green"),(f"{data['data']['original_nick']}!","cyan"),("\nNow run the run.py and you should see posts appearing automatically.","green"))


#A simple Captcha solver that uses YOU to solve it
def captchasolve(captcha_id = str):

    pageurl = captcha_id

    try:
        webbrowser.open_new(pageurl)
        input()
        return
        
    except:
        cprint(("IDK how you messed that one up, chief :/", "red"))
        return "Chrome"

login()
