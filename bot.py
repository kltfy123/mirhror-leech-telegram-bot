import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# --- إعدادات البوت ---
API_ID = "YOUR_API_ID"        # احصل عليه من my.telegram.org
API_HASH = "YOUR_API_HASH"    # احصل عليه من my.telegram.org
BOT_TOKEN = "8640929836:AAEV-p30frbxqNSCXWLw9jQLTRsBCBlaYNU"

app = Client("tiktok_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# فلتر للتأكد أن الرابط يخص تيك توك فقط
tiktok_filter = filters.regex(r"(?i)(?:tiktok\.com|vt\.tiktok\.com)")

@app.on_message(filters.private & tiktok_filter)
async def tiktok_downloader(client, message):
    url = message.text
    status = await message.reply("⏳ جاري معالجة فيديو تيك توك...")

    # إعدادات yt-dlp لتحميل الفيديو بدون علامة مائية (إن أمكن)
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        loop = asyncio.get_event_loop()
        
        with YoutubeDL(ydl_opts) as ydl:
            # استخراج البيانات والتحميل
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            file_path = ydl.prepare_filename(info)
            description = info.get('title', 'TikTok Video')

        await status.edit("📤 جاري رفع الفيديو...")

        # إرسال الفيديو للبوت
        await message.reply_video(
            video=file_path,
            caption=f"✅ تم التحميل من تيك توك\n\n📝: {description[:100]}..."
        )

        # حذف الملف من السيرفر بعد الإرسال
        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ حدث خطأ:\n`{str(e)}`")

@app.on_message(filters.private & ~tiktok_filter & filters.text)
async def not_tiktok(client, message):
    await message.reply("⚠️ من فضلك أرسل رابط تيك توك صحيح فقط.")

print("🚀 بوت تحميل تيك توك يعمل الآن...")
app.run()
