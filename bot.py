import os, asyncio, signal
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION = os.environ["SESSION"]

userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, msg: Message):
    await msg.reply("👋 هلا! أنا جماان سحب 🎬\nأرسل رابط أي منشور حتى المقيد 🔥")

@bot.on_message(filters.text & filters.private & ~filters.command(["start"]))
async def handle_link(client, msg: Message):
    link = msg.text.strip()
    if "t.me" not in link:
        await msg.reply("❌ أرسل رابط تلقرام صحيح")
        return
    wait_msg = await msg.reply("⏳ جاري السحب...")
    try:
        async with userbot:
            if "/c/" in link:
                parts = link.split("/c/")[1].split("/")
                chat_id = int("-100" + parts[0])
                msg_id = int(parts[1])
            else:
                parts = link.rstrip("/").split("/")
                chat_id = parts[-2]
                msg_id = int(parts[-1])
            tg_msg = await userbot.get_messages(chat_id, msg_id)
            if not tg_msg or not tg_msg.media:
                await wait_msg.edit("❌ المنشور ما فيه ميديا")
                return
            file = await userbot.download_media(tg_msg, in_memory=True)
            await wait_msg.edit("📤 جاري الإرسال...")
            if tg_msg.video:
                await bot.send_video(msg.chat.id, file, caption="✅ تم السحب")
            elif tg_msg.document:
                await bot.send_document(msg.chat.id, file, caption="✅ تم السحب")
            elif tg_msg.audio:
                await bot.send_audio(msg.chat.id, file, caption="✅ تم السحب")
            elif tg_msg.photo:
                await bot.send_photo(msg.chat.id, file, caption="✅ تم السحب")
            await wait_msg.delete()
    except FloodWait as e:
        await wait_msg.edit(f"⚠️ انتظر {e.value} ثانية")
    except Exception as e:
        await wait_msg.edit(f"❌ خطأ: {str(e)[:200]}")

async def main():
    await bot.start()
    print("Bot started ✅")
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, stop_event.set)
    loop.add_signal_handler(signal.SIGINT, stop_event.set)
    await stop_event.wait()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
