import datetime

def log(text: str):
	dt = datetime.datetime.now()
	print("[{}] {}".format(dt.strftime('%H:%M:%S'),text))