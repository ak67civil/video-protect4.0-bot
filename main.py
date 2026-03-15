import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# Configs
API_ID = int(os.environ.get("API_ID", "33401543"))
API_HASH = os.environ.get("API_HASH", "7cdea5bbc8bd991b4a49807ce86")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# Database
db_client = AsyncIOMotorClient(MONGO_DB_URI)
db = db_client["VideoProtectDB"]
connections = db["links"]

app = Client("Protector", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    if len(message.command) > 1:
        data = message.command[1].split("_")
        try:
            await client.copy_message(chat_id=message.chat.id, from_chat_id=int(data[0]), message_id=int(data[1]), protect_content=True)
        except:
            await message.reply_text("❌ Link Expired!")
    else:
        await message.reply_text("🛡️ Bot Online!")

@app.on_message(filters.command("connect") & filters.user(OWNER_ID))
async def connect_cmd(client, message):
    try:
        args = message.text.split()
        await connections.update_one({"source": int(args[1])}, {"$set": {"dest": int(args[2])}}, upsert=True)
        await message.reply_text(f"✅ Connected!")
    except:
        await message.reply_text("Usage: `/connect -100Source -100Dest` ")

@app.on_message((filters.video | filters.document) & ~filters.forwarded)
async def auto_post(client, message):
    conn = await connections.find_one({"source": message.chat.id})
    if not conn: return
    bot_info = await client.get_me()
    watch_link = f"https://t.me/{bot_info.username}?start={message.chat.id}_{message.id}"
    await client.send_message(conn["dest"], f"🎬 **Title:** `{message.caption or 'New Video'}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Watch Video", url=watch_link)]]))

# --- THE FIX FOR PYTHON 3.14 ---
if __name__ == "__main__":
    app.run()
    
