import json
from selenium import webdriver
import requests
import time
import json
import os
from dotenv import load_dotenv
from termcolor import colored
from datetime import datetime

#Load the config file and get the email and password
load_dotenv("config.env")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

host = "https://api.ifunny.mobi"



#Getting an existing basic auth token, or creating a basic auth token if one doesnt exist
def get_or_create_basic():
    try:
        with open("bearer.json","r") as f:
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
        with open("bearer.json","w") as f:
            json.dump({'basic':basic,'bearer':'','user_id':''},f,indent=1)
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
    paramz = {'grant_type':'password',
               'username': email,
               'password': password}
    header = {'Host': 'api.ifunny.mobi','Applicationstate': '1','Accept': 'video/mp4, image/jpeg','Content-Type': 'application/x-www-form-urlencoded','Authorization': 'Basic '+data,'Content-Length':'77','Ifunny-Project-Id': 'iFunny','User-Agent': 'iFunny/7.19.3(22399) iphone/15.1 (Apple; iPhone11,8)','Accept-Language': 'en-US;q=1','Accept-Encoding': 'gzip, deflate'}
    
    #Main login loop that tries logging in // Bypasses captcha
    while True:
        r = requests.post(url,headers=header,data=paramz).json()
        #Checking for any errors in login
        if "error" in r:
            if r["error"] == "captcha_required":

                cprint(("Captcha required, Bypassing...\nPlease do not close or interact with the chrome tab that will pop up! It will close automatically when the bypass is finished.","red"))
                
                key = captchasolve(r["data"]["captcha_url"])
                if key == "Chrome":
                    return

                payload = f'g-recaptcha-response={key}'
                paramz1 = {'Host': 'api.ifunny.mobi','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Content-Type': 'application/x-www-form-urlencoded','Origin': 'https://api.ifunny.mobi','Content-Length': f'{len(payload)}','Accept-Language': 'en-us','User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148','Referer': f'{r["data"]["captcha_url"]}','Accept-Encoding': 'gzip, deflate'}
                
                re = requests.post(url=r["data"]["captcha_url"],headers=paramz1,data=payload,allow_redirects=False)
                
                cprint(("Logging in...","green"))

                #Logging in a second time after completing captcha
                try:
                    login = requests.post(url,headers=header,data=paramz).json()
                    
                except:
                    cprint(("Something went wrong. Try again?","red"))
                    return

                break

            if r["error"] == "unsupported_grant_type":
                cprint(("Something went wrong. Try again?","red"))
                return
            
            if r["error"] == "too_many_user_auths":
                cprint(("Please wait about 10 minutes for iFunny's dumb user auth ratelimit, and run this again.","red"))
                return
            
            if r["error"] == "forbidden":
                
                index += 1

                #Primes the bearer token that was freshly generated so it can be used 
                header = {'Host': 'api.ifunny.mobi','Accept': 'video/mp4, image/jpeg','Applicationstate': '1','Accept-Encoding': 'gzip, deflate','Ifunny-Project-Id': 'iFunny','User-Agent': 'iFunny/7.14.2(22213) iphone/14.0.1 (Apple; iPhone8,4)','Accept-Language': 'en-US;q=1','Authorization': 'Basic '+data,}
                counter = requests.get(host+"/v4/counters",headers=header)
                
                cprint(("Priming your basic auth token... please wait","green"))
                time.sleep(10)

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
    
    data = requests.get(host+"/v4/users/"+req["data"]["id"],headers=header).json()

    with open("bearer.json","r") as bearer_file:
        s = json.load(bearer_file)
        s["bearer"] = login["access_token"]
        s["user_id"] = req["data"]["id"]
        with open("bearer.json","w") as fi:
            json.dump(s,fi,indent=1)
        cprint(("Logged in successfully as","green"),(f"{data['data']['original_nick']}!","cyan"),("\nNow run the run.py and you should see posts appearing automatically","green"))


#A lazy captcha solver using 2captcha.com API and Selenium to get the captcha key
def captchasolve(captcha_id = str):

    pageurl = captcha_id

    try:
        driver = webdriver.Chrome(executable_path='./libs/chromedriver.exe')
        driver.get(pageurl)

        site_key = "6LflIwgTAAAAAElWMFEVgr9zs2UpH0eiFsVN_KfF"

        api_key = "30d30d74a342bf77179d89bb26a952d9"

        form = {"method": "userrecaptcha",
                "googlekey": site_key,
                "key": api_key, 
                "pageurl": pageurl, 
                "json": 1}

        response = requests.post('http://2captcha.com/in.php', data=form)

        url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={response.json()['request']}&json=1"

        status = 0
        while not status:
            res = requests.get(url).json()
            if res['status']==0:
                time.sleep(3)
                cprint(("Not ready yet, please dont exit chrome or click the verify box. This may take a minute.","red"))
            else:
                requ = res['request']
                js = f'document.getElementById("g-recaptcha-response").innerHTML="{requ}";'
                driver.execute_script(js)

                status = 1
                gen = json.loads(res.text)
                key = gen["request"]
                cprint(("Captcha Successful","green"))
                driver.close()
                return key
    except:
        cprint(("Unable to open chromedriver! Make sure you downloaded the right version and put the .exe in the libs folder!", "red"))
        return "Chrome"

login()
