# iFunny-AutoPost
A meme stealer and auto uploader for the meme app iFunny


Requirements: Google Chrome, Chromedriver.exe, Python 3.7+ (I use 3.10)
Optional (But recommended): Any python IDE (Visual Studio Code, Pycharm, VIM)

How to install Chromedriver:

	First find your chrome version number by opening chrome, going to Settings, then click "About Chrome"
	
	Download Chromedriver from this website: https://chromedriver.chromium.org/downloads
	Make sure you download the same version your chrome is running

	Extract the .exe out of the zip file, and place it into the libs folder


How to install Python:

	https://www.python.org/downloads/

	download link ^ and install, !!!Make sure to click "Add to PATH"!!!



Instructions:
	
	First we need to install the required modules, to do this we will open the folder, and copy the directory. (E.G: C:\Users\Admin\Desktop\AutoPost )
	
	Open command prompt and type: cd (directory you copied)
	now copy and paste: pip install -r requirements.txt

	Python should start downloading the required modules listed in the text file.

	Once it is finished, edit the config.env file and input your email and password in the appropriate fields.
	Now run the login.py, You should see the login status be documented in the terminal as it runs. Follow any instructions the terminal may give you.
	
	Once you get the "Login Success!", run the run.py file. Posts should start appearing on your profile every 5 miniutes. You can lower this time amount by editing the 
	"TIME" variable in config.env



					(っ・ω・)っ [̲̅$̲̅(̲̅5̲̅)̲̅$̲̅]
					"I can haz dollar?" ~ cash.app/$iFunnyScripts
							      https://iFunny.co/user/Scripts
