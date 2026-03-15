import asyncio
import logging
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

logging.basicConfig(level=logging.INFO)

app = Client("VideoProtectBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# Database Setup
db_client = AsyncIOMotorClient(Config.MONGO_DB_URI)
db = db_client["VideoProtectDB"]
connections = db["links"]
analytics = db["user_stats"]

# --- COMMANDS ---

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    if len(message.command) > 1:
        try:
            data = message.command[1].split("_")
            src_id, msg_id = int(data[0]), int(data[1])
            
            # Update Analytics
            await analytics.update_one(
                {"user_id": message.from_user.id},
                {"$inc": {"count": 1}, "$set": {"name": message.from_user.first_name}},
                upsert=True
            )

            # Log to Channel
            if Config.LOG_CHANNEL:
                await client.send_message(Config.LOG_CHANNEL, f"👤 `{message.from_user.first_name}` is watching video `{msg_id}`")

            # COPY with PROTECTION (Screenshot/Forward Blocked)
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=src_id,
                message_id=msg_id,
                protect_content=True
            )
        except Exception:
            await message.reply_text("❌ Video link expired or Bot not admin in source.")
    else:
        await message.reply_text("🛡️ **Loser Video Protector Active**\n\nCommands: /connect, /videoaccess")

@app.on_message(filters.command("connect") & filters.user(Config.OWNER_IDS))
async def connect_handler(client, message):
    try:
        args = message.text.split()
        src, dst = int(args[1]), int(args[2])
        await connections.update_one({"source": src}, {"$set": {"dest": dst}}, upsert=True)
        await message.reply_text(f"✅ **Linked!**\nSource: `{src}`\nDisplay: `{dst}`")
    except:
        await message.reply_text("❌ `/connect -100SourceID -100DestID` ")

@app.on_message(filters.command("videoaccess") & filters.user(Config.OWNER_IDS))
async def access_handler(client, message):
    stats = analytics.find().sort("count", -1).limit(20)
    res = "📊 **Watch Stats:**\n\n"
    async for u in stats:
        res += f"👤 {u['name']} - 📺 `{u['count']}`\n"
    await message.reply_text(res)

# --- AUTO FORWARD LOGIC ---

@app.on_message((filters.video | filters.document) & ~filters.forwarded)
async def auto_post(client, message):
    conn = await connections.find_one({"source": message.chat.id})
    if not conn: return

    dest_id = conn["dest"]
    title = message.caption or "Secure Video"
    bot_me = await client.get_me()
    
    # Secure deep link
    watch_url = f"https://t.me/{bot_me.username}?start={message.chat.id}_{message.id}"
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Play Video", url=watch_url)]])
    
    try:
        await client.send_message(dest_id, f"💎 **Title:** `{title}`", reply_markup=markup)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(dest_id, f"💎 **Title:** `{title}`", reply_markup=markup)

# --- CRASH-PROOF STARTING ---

async def start_bot():
    await app.start()
    print("🚀 Bot is Online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_bot())
    except RuntimeError:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(start_bot())
        
