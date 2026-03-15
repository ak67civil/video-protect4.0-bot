import os
import asyncio
from pyrogram import Client, filters

# Configs - Heroku se lega
API_ID = int(os.environ.get("API_ID", "33401543"))
API_HASH = os.environ.get("API_HASH", "7cdea5bbc8bd991b4a49807ce86")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("SimpleBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_msg(client, message):
    await message.reply_text("💪 Dekh Bhai! Bot Ekdam Perfect Chal Raha Hai!")

# Modern Start Logic (Python 3.14 Safe)
async def main():
    async with app:
        print("🚀 BOT IS ONLINE!")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
    
