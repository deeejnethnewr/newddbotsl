import os
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import asyncio
import subprocess
import time
import re

load_dotenv()

API_ID = int(os.getenv("15647296"))
API_HASH = os.getenv("0cb3f4a573026b56ea80e1c8f039ad6a")
BOT_TOKEN = os.getenv("7695562666:AAEo8E_GUw30Nki3wTveRjx7wsIEvkdRMAY")

bot = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def extract_file_id(gdrive_url):
    patterns = [
        r"https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, gdrive_url)
        if match:
            return match.group(1)
    return None

async def download_gdrive_file(file_id, output_path):
    command = f"gdown https://drive.google.com/uc?id={file_id} -O \"{output_path}\""
    process = await asyncio.create_subprocess_shell(command)
    await process.communicate()

@bot.on_message(filters.private & filters.text)
async def handle_gdrive(client, message: Message):
    url = message.text.strip()
    file_id = extract_file_id(url)

    if not file_id:
        await message.reply_text("❌ Valid Google Drive link එකක් නෙමෙයි.")
        return

    temp_filename = f"{file_id}.mp4"
    status_msg = await message.reply_text("⏬ Downloading video...")

    start_time = time.time()
    await download_gdrive_file(file_id, temp_filename)
    elapsed = time.time() - start_time

    if not os.path.exists(temp_filename):
        await status_msg.edit("❌ Download failed.")
        return

    await status_msg.edit(f"✅ Download complete in {int(elapsed)}s. Uploading...")

    await client.send_document(chat_id=message.chat.id, document=temp_filename, caption="📤 Uploaded from Google Drive")

    await status_msg.delete()
    os.remove(temp_filename)

bot.run()
