import os
import time
from pyrogram import Client, filters
from config import Config

# Configuration
API_ID = Config.API_ID
API_HASH = Config.API_HASH
BOT_TOKEN = Config.BOT_TOKEN
dom = Config.DOM
PRIVATE_CHANNEL_ID = Config.MCHAT # Replace with your private channel ID
DOWNLOAD_FOLDER = Config.DL_FOLDER # Directory to store files
DISK_USAGE_THRESHOLD = Config.DISK_USAGE_THRESHOLD  # 98% disk usage limit

plugins = dict(root="plugins")
# Initialize bot
app = Client("file_hosting_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, plugins=plugins)

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


if __name__ == "__main__":
    print("Bot is running...")
    app.run()
