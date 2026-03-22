import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "video-protector",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# Temporary DB (Later MongoDB laga dena)
db = {}

BOT_USERNAME = None

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    if len(message.text.split()) > 1:
        data = message.text.split()[1]

        if data.startswith("vid_"):
            try:
                _, priv_id, msg_id = data.split("_")

                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=int(priv_id),
                    message_id=int(msg_id),
                    protect_content=True
                )
                return

            except Exception as e:
                return await message.reply_text("❌ Video nahi mili ya delete ho gayi hai.")

    await message.reply_text(
        "🛡️ **Video Protector Bot Online!**\n\n"
        "1. Bot ko private & public channel me admin banao\n"
        "2. Connect karo:\n"
        "`/connect -100private -100public`"
    )


@app.on_message(filters.command("connect"))
async def connect_cmd(client, message):
    try:
        priv_id = message.command[1]
        pub_id = message.command[2]

        db[priv_id] = pub_id

        await message.reply_text(
            f"✅ Connected\n\nPrivate: `{priv_id}`\nPublic: `{pub_id}`"
        )

    except:
        await message.reply_text("❌ Use: `/connect private_id public_id`")


@app.on_message(filters.video | filters.document)
async def forward_logic(client, message):
    chat_id = str(message.chat.id)

    if chat_id not in db:
        return

    public_id = db[chat_id]

    try:
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "▶️ Watch Video",
                url=f"https://t.me/{BOT_USERNAME}?start=vid_{chat_id}_{message.id}"
            )
        ]])

        caption = message.caption or "🎥 Nayi Video Aa Gayi Hai!"

        await client.send_message(
            public_id,
            f"📥 **{caption}**\n\n👇 Button dabao aur dekho:",
            reply_markup=btn
        )

    except Exception as e:
        print(f"Error: {e}")


async def main():
    global BOT_USERNAME

    async with app:
        me = await app.get_me()
        BOT_USERNAME = me.username

        print(f"🚀 BOT ONLINE: @{BOT_USERNAME}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
