import os
import asyncio
from pyrogram import Client, filters

# Configs - Heroku Config Vars se uthayega
API_ID = int(os.environ.get("API_ID", "33401543"))
API_HASH = os.environ.get("API_HASH", "7cdea5bbc8bd991b4a49807ce86")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Bot Client Initialize
app = Client("ProtectorBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text("✅ Bot is now ALIVE and Running!")

# --- THE REAL FIX FOR RUNTIME ERROR ---
async def start_bot():
    try:
        await app.start()
        print("🚀 BOT STARTED SUCCESSFULLY!")
        # Keep the bot running without crashing the loop
        while True:
            await asyncio.sleep(1000)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Python 3.10+ loop handling
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())
    
