import os
import shutil
import psutil
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from datetime import datetime, timedelta

# Configuration
API_ID = os.getenv("apiid")
API_HASH = os.getenv("apihash")
BOT_TOKEN = os.getenv("tk")
dom = os.getenv("murl")
PRIVATE_CHANNEL_ID = os.getenv("mchat") # Replace with your private channel ID
DOWNLOAD_FOLDER = os.getenv("dl","./RvxDl") # Directory to store files
DISK_USAGE_THRESHOLD = 0.98  # 98% disk usage limit

# Initialize bot
app = Client("file_hosting_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def get_disk_usage():
    """Check the current disk usage."""
    disk = shutil.disk_usage("/")
    return disk.used / disk.total  # Return usage as a fraction


def free_up_space(required_space):
    """Delete oldest files until enough space is available."""
    files = [
        os.path.join(DOWNLOAD_FOLDER, f)
        for f in os.listdir(DOWNLOAD_FOLDER)
        if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))
    ]
    files.sort(key=lambda x: os.path.getctime(x))  # Sort files by creation time (oldest first)

    freed_space = 0
    for file in files:
        file_size = os.path.getsize(file)
        os.remove(file)
        freed_space += file_size
        print(f"Deleted file: {file} ({file_size / (1024 * 1024):.2f} MB)")

        if freed_space >= required_space:
            break

last_m=""
async def progress_callback(current, total, message: Message, start_time):
    global last_m
    """Callback to update progress messages."""
    elapsed_time = time.time() - start_time
    percentage = (current / total) * 100
    speed = current / elapsed_time  # Bytes per second
    eta = (total - current) / speed if speed > 0 else 0

    # Create progress bar
    progress_bar_length = 20  # Length of the progress bar
    filled_length = int(progress_bar_length * current / total)
    progress_bar = "✅️" * filled_length + "❌️" * (progress_bar_length - filled_length)

    # Format the progress message
    progress_message = (
        f"**Downloading File:**\n"
        f"`[{progress_bar}]`\n\n**Done:** {percentage:.2f}%\n"
        f"**Speed:** {speed / 1024:.2f} KB/s\n"
        f"**ETA:** {str(timedelta(seconds=int(eta)))}\n"
        f"**Downloaded:** {current / (1024 * 1024):.2f} MB / {total / (1024 * 1024):.2f} MB"
    )

    # Update the message every 10 seconds
    if elapsed_time % 10 == 0:
        try:
            if progress_message != last_m:
              last_m = progress_message
              await message.edit_text(progress_message)
        except FloodWait as e:
            time.sleep(e.value)


@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file(client, message: Message):
    """Handle incoming files, forward them to a private channel, and host them."""
    file = message.document or message.video or message.audio or message.photo

    if not file:
        await message.reply_text("No file found.")
        return

    # Forward the file to the private channel
    try:
        forwarded_message = await message.forward(chat_id=PRIVATE_CHANNEL_ID)
        print(f"File forwarded to private channel: {forwarded_message.id}")
    except Exception as e:
        print(f"Error forwarding file: {e}")
        await message.reply_text("Failed to forward the file to the private channel.")
        return

    # Check if there's enough disk space
    disk_usage = get_disk_usage()
    file_size = file.file_size if hasattr(file, "file_size") else 0
    print(f"Current Disk Usage: {disk_usage * 100:.2f}%")
    print(f"Incoming File Size: {file_size / (1024 * 1024):.2f} MB")

    # If disk space is insufficient, free up space
    while disk_usage >= DISK_USAGE_THRESHOLD or psutil.disk_usage("/").free < file_size:
        required_space = file_size - psutil.disk_usage("/").free
        await message.reply_text("Disk space is low. Freeing up space...")
        free_up_space(required_space)
        disk_usage = get_disk_usage()

    # Download the file with progress tracking
    fexname= file.file_name if hasattr(file, "file_name") else f"{message.id}.rvx"
    file_path = os.path.join(DOWNLOAD_FOLDER, fexname)
    progress_message = await message.reply_text("Starting download...")
    downloadL=f"{dom}/download/{fexname}"
    streamL=f"{dom}/stream/{fexname}"
    start_time = time.time()
    try:
        await message.download(
            file_path,
            progress=progress_callback,
            progress_args=(progress_message, start_time),
        )
        print(f"File downloaded: {file_path}")
        await progress_message.edit_text(
            f"**File hosted successfully!**\n\n**Download Link:** {downloadL}\n\n**Watch/stream Link:** {streamL}\n\n💝💝💝💝💝💝💝💝"
        )
    except Exception as e:
        print(f"Error downloading file: {e}")
        await progress_message.edit_text("Error occurred while downloading the file.")


@app.on_message(filters.command("status"))
async def check_status(client, message: Message):
    """Check the current bot status (disk usage)."""
    disk = shutil.disk_usage("/")
    disk_used = disk.used / (1024 * 1024 * 1024)
    disk_total = disk.total / (1024 * 1024 * 1024)
    disk_free = disk.free / (1024 * 1024 * 1024)
    usage_percent = disk.used / disk.total * 100

    await message.reply_text(
        f"**Disk Status:**\n"
        f"Total: {disk_total:.2f} GB\n"
        f"Used: {disk_used:.2f} GB\n"
        f"Free: {disk_free:.2f} GB\n"
        f"Usage: {usage_percent:.2f}%"
    )


@app.on_message(filters.command("hosted_files"))
async def list_files(client, message: Message):
    """List all hosted files."""
    files = os.listdir(DOWNLOAD_FOLDER)
    if not files:
        await message.reply_text("No files are currently hosted.")
        return

    file_list = "\n".join(files)
    await message.reply_text(f"**Hosted Files:**\n\n{file_list}")


if __name__ == "__main__":
    print("Bot is running...")
    app.run()
