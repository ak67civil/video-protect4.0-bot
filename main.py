import os
import asyncio
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIGS ---
API_ID = int(os.environ.get("API_ID", "33401543"))
API_HASH = os.environ.get("API_HASH", "7cdea5bbc8bd991b4a49807ce86")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
OWNER_IDS = [int(i.strip()) for i in os.environ.get("OWNER_ID", "").split(",") if i.strip()]

# Database Initialize
db_client = AsyncIOMotorClient(MONGO_DB_URI)
db = db_client["ProtectionBotDB"]
connections = db["links"]
analytics = db["stats"]

app = Client("SecureBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- START / SECURE PLAY ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.command) > 1:
        try:
            data = message.command[1].split("_")
            src_id, msg_id = int(data[0]), int(data[1])
            
            # Analytics Update
            await analytics.update_one(
                {"user_id": message.from_user.id},
                {"$inc": {"count": 1}, "$set": {"name": message.from_user.first_name}},
                upsert=True
            )

            # Log Activity
            if LOG_CHANNEL:
                await client.send_message(LOG_CHANNEL, f"👤 `{message.from_user.first_name}` watched video `{msg_id}` from `{src_id}`")

            # COPY with PROTECTION (Forward/Save OFF)
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=src_id,
                message_id=msg_id,
                protect_content=True
            )
        except:
            await message.reply_text("❌ Link Expired or Bot not Admin in Source.")
    else:
        await message.reply_text("👋 **Bot Online!**\nUse /connect to link channels.")

# --- CONNECT CHANNELS ---
@app.on_message(filters.command("connect") & filters.user(OWNER_IDS))
async def connect(client, message):
    try:
        args = message.text.split()
        src, dst = int(args[1]), int(args[2])
        await connections.update_one({"source": src}, {"$set": {"dest": dst}}, upsert=True)
        await message.reply_text(f"✅ **Connected!**\nSrc: `{src}`\nDst: `{dst}`")
    except:
        await message.reply_text("❌ `/connect -100SourceID -100DestID` ")

# --- VIDEO ACCESS STATS ---
@app.on_message(filters.command("videoaccess") & filters.user(OWNER_IDS))
async def stats(client, message):
    cursor = analytics.find().sort("count", -1).limit(20)
    res = "📊 **Top Watchers:**\n\n"
    async for u in cursor:
        res += f"👤 {u['name']} - {u['count']} videos\n"
    await message.reply_text(res)

# --- AUTO FORWARD ENGINE ---
@app.on_message((filters.video | filters.document) & ~filters.forwarded)
async def protector(client, message):
    conn = await connections.find_one({"source": message.chat.id})
    if not conn: return
    
    dest_id = conn["dest"]
    bot = await client.get_me()
    watch_url = f"https://t.me/{bot.username}?start={message.chat.id}_{message.id}"
    
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Video", url=watch_url)]])
    
    try:
        await client.send_message(dest_id, f"💎 **Title:** `{message.caption or 'Secure Content'}`", reply_markup=markup)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(dest_id, f"💎 **Title:** `{message.caption}`", reply_markup=markup)

# --- FINAL FIX FOR RUNTIME ERROR ---
if __name__ == "__main__":
    print("🚀 Starting Bot...")
    app.run()
    
