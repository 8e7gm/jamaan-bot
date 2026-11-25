import os, asyncio, sys
from pathlib import Path
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.errors import FloodWait, UserAlreadyParticipant

load_dotenv()
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
DIR = Path("downloads")
DIR.mkdir(exist_ok=True)

async def main():
    target = sys.argv[1] if len(sys.argv)>1 else None
    if not target:
        print("Usage: python tg_bot.py <link> [limit]")
        return
    limit = int(sys.argv[2]) if len(sys.argv)>2 else 20
    async with Client("session", api_id=API_ID, api_hash=API_HASH) as app:
        me = await app.get_me()
        print(f"Logged in: {me.first_name}")
        if "+" in target:
            hash_ = target.split("/+")[-1].split("+")[-1]
            try:
                chat = await app.join_chat(hash_)
                channel = chat.id
                print(f"Joined: {chat.title}")
            except UserAlreadyParticipant:
                chat = await app.get_chat(hash_)
                channel = chat.id
        else:
            channel = target
        count = 0
        async for msg in app.get_chat_history(channel, limit=limit):
            if not (msg.video or msg.document):
                continue
            f = DIR / f"vid_{msg.id}.mp4"
            if f.exists():
                continue
            print(f"Downloading #{msg.id}...")
            try:
                await app.download_media(msg, file_name=str(f))
                count += 1
                await asyncio.sleep(1.5)
            except FloodWait as e:
                await asyncio.sleep(e.value+2)
            except Exception as e:
                print(f"Skip: {e}")
        print(f"Done! {count} videos saved.")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
