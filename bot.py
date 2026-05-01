import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# إعدادات البوت (ضع بياناتك هنا)
API_ID = "YOUR_API_ID"        # احصل عليه من my.telegram.org
API_HASH = "YOUR_API_HASH"    # احصل عليه من my.telegram.org
BOT_TOKEN = "8640929836:AAEV-p30frbxqNSCXWLw9jQLTRsBCBlaYNU"

app = Client("my_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.regex(r"(http|https)://"))
async def download_video(client, message):
    url = message.text
    sent_msg = await message.reply("⏳ جاري معالجة الرابط وتحميل الفيديو...")

    # إعدادات التحميل عبر yt-dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        # تشغيل التحميل في خلفية البرنامج لعدم تجميد البوت
        info = await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = YoutubeDL(ydl_opts).prepare_filename(info)

        # إرسال الفيديو إلى المستخدم
        await message.reply_video(video=filename, caption=f"✅ تم التحميل: {info.get('title', 'Video')}")
        
        # حذف الفيديو من الخادم بعد الإرسال لتوفير المساحة
        if os.path.exists(filename):
            os.remove(filename)
            
        await sent_msg.delete()

    except Exception as e:
        await sent_msg.edit(f"❌ حدث خطأ أثناء التحميل: {str(e)}")

print("البوت يعمل الآن...")
app.run()
