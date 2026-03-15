import asyncio
import logging
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

# Logging for debugging
logging.basicConfig(level=logging.INFO)

app = Client("SecureForwarder", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# Database Setup
db_client = AsyncIOMotorClient(Config.MONGO_DB_URI)
db = db_client["VideoProtectDB"]
connections = db["links"]
analytics = db["user_stats"]

# --- 1. CHANNEL CONNECT COMMAND ---
@app.on_message(filters.command("connect") & filters.user(Config.OWNER_IDS))
async def connect_cmd(client, message):
    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.reply_text("❌ Format: `/connect -100SourceID -100DestID` ")
        
        src, dst = int(args[1]), int(args[2])
        await connections.update_one({"source": src}, {"$set": {"dest": dst}}, upsert=True)
        await message.reply_text(f"✅ **Linked Successfully!**\n📥 Source: `{src}`\n📤 Display: `{dst}`")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# --- 2. THE PROTECTOR LOGIC (No Video Loss) ---
@app.on_message((filters.video | filters.document) & ~filters.forwarded)
async def protector(client, message):
    # Check if this channel is connected
    conn = await connections.find_one({"source": message.chat.id})
    if not conn: return

    dest_id = conn["dest"]
    title = message.caption or "Secure Video Content"
    
    # Anti-Flood Delay: Thoda wait taaki Telegram block na kare
    await asyncio.sleep(2) 

    bot_info = await client.get_me()
    # Deep link: bot?start=SourceID_MessageID
    watch_link = f"https://t.me/{bot_info.username}?start={message.chat.id}_{message.id}"
    
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Video Securely", url=watch_link)]])
    
    try:
        await client.send_message(
            chat_id=dest_id,
            text=f"💎 **Title:** `{title}`\n\n🛡️ *Content Protected. Watch in bot.*",
            reply_markup=markup
        )
    except errors.FloodWait as e:
        await asyncio.sleep(e.value) # Agar speed zyada hui toh bot khud rukk jayega
        await client.send_message(chat_id=dest_id, text=f"💎 **Title:** `{title}`", reply_markup=markup)
    except Exception as e:
        logging.error(f"Error sending to Display Channel: {e}")

# --- 3. SECURE PLAYBACK & TRACKER ---
@app.on_message(filters.command("start") & filters.private)
async def secure_start(client, message):
    if len(message.command) > 1:
        try:
            data = message.command[1].split("_")
            src_id, msg_id = int(data[0]), int(data[1])
            
            # User Analytics
            await analytics.update_one(
                {"user_id": message.from_user.id},
                {"$inc": {"count": 1}, "$set": {"name": message.from_user.first_name}},
                upsert=True
            )

            # Sending protected message
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=src_id,
                message_id=msg_id,
                protect_content=True # Screenshot/Forwarding Blocked
            )
        except Exception:
            await message.reply_text("❌ Video not found. Please use the link from channel.")
    else:
        await message.reply_text("👑 **Loser's Video Protection Bot**\n\nMain admin menu active.")

# --- 4. ANALYTICS COMMAND ---
@app.on_message(filters.command("videoaccess") & filters.user(Config.OWNER_IDS))
async def access_report(client, message):
    stats = analytics.find().sort("count", -1).limit(30)
    report = "📊 **Recent Video Access Report:**\n\n"
    async for user in stats:
        report += f"👤 {user['name']} | ID: `{user['user_id']}` | 📺 `{user['count']}` videos\n"
    
    if report == "📊 **Recent Video Access Report:**\n\n":
        report = "❌ No data yet."
    await message.reply_text(report)

print("🛡️ Protection Bot Started Successfully!")
app.run()
