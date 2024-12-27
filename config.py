import os

class Config(object):
  API_ID = int(os.getenv("apiid"))
  
  API_HASH = os.getenv("apihash")
  
  BOT_TOKEN = os.getenv("tk")
  
  AUTH = os.getenv("auth")
  
  OWNER = os.getenv("owner")

  DOM = os.getenv("murl")

  MCHAT = os.getenv("mchat")

  DL_FOLDER = os.getenv("dl","./RvxDl")

  DISK_USAGE_THRESHOLD = 0.98
