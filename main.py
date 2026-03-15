import os
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIGS ---
API_ID = int(os.environ.get("API_ID", "33401543"))
API_HASH = os.environ.get("API_HASH", "7cdea5bbc8bd991b4a49807ce86")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# Database
db_client = AsyncIOMotorClient(MONGO_DB_URI)
db = db_client["SimpleBotDB"]
connections = db["links"]

# Simple Client
app = Client("MyBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("✅ Bot is Running Perfect!")

@app.on_message(filters.command("connect") & filters.user(OWNER_ID))
async def connect(client, message):
    try:
        args = message.text.split()
        await connections.update_one({"source": int(args[1])}, {"$set": {"dest": int(args[2])}}, upsert=True)
        await message.reply_text("✅ Linked Successfully!")
    except:
        await message.reply_text("Use: `/connect -100Source -100Dest` ")

# Simple Post Logic
@app.on_message((filters.video | filters.document) & ~filters.forwarded)
async def post(client, message):
    conn = await connections.find_one({"source": message.chat.id})
    if conn:
        bot = await client.get_me()
        link = f"https://t.me/{bot.username}?start={message.chat.id}_{message.id}"
        await client.send_message(conn["dest"], f"🎬 Video Link: {link}")

# Purest way to run (Python 3.14 Safe)
if __name__ == "__main__":
    print("🚀 BOT STARTING...")
    app.run()
    
