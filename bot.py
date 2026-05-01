import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# إعدادات البوت
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("أهلاً بك! أرسل لي رابط فيديو من يوتيوب، تيك توك، أو انستجرام وسأقوم بتحميله لك.")

@app.on_message(filters.text & ~filters.command("start"))
async def download_video(client, message):
    url = message.text
    msg = await message.reply_text("جاري المعالجة... انتظر قليلاً ⏳")
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'quiet': True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video')
            
        await message.reply_video(video="video.mp4", caption=f"<b>تم التحميل بنجاح ✅</b>\n\n<b>العنوان:</b> {title}", parse_mode="html")
        await msg.delete()
        
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")
            
    except Exception as e:
        await msg.edit_text(f"حدث خطأ أثناء التحميل: {str(e)}")

app.run()
