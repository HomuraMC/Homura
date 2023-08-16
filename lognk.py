import datetime
from colorama import Fore, Back, Style

def log(text: str,level: str = None):
	dt = datetime.datetime.now()
	if level == None:
		print("[{}] {}".format(dt.strftime('%H:%M:%S'),text))
	else:
		print("[{}]{} {}".format(dt.strftime('%H:%M:%S'),level.lower(),text))