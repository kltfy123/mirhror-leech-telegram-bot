import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp

# التوكن الخاص بك
TOKEN = "8640929836:AAEV-p30frbxqNSCXWLw9jQLTRsBCBlaYNU"

# إعدادات التحميل - جودة كويسة وبدون وجع دماغ
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'video_%(id)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
}

async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    # رسالة بسيطة عشان تعرف إنه شغال
    status_msg = await update.message.reply_text("جاري التحميل... 🚀")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # لو الملف نزل بصيغة مختلفة (زي mkv) يفضل نبعته كفيديو
            with open(filename, 'rb') as video:
                await context.bot.send_video(chat_id=chat_id, video=video)
            
            # مسح الملف من السيرفر بعد الإرسال عشان الزحمة
            os.remove(filename)
            await status_msg.delete()

    except Exception:
        # هنا "يلمزك" بهدوء لو الرابط بايظ بدل ما يبعت كود خطأ طويل
        await status_msg.edit_text("الرابط ده فيه مشكلة أو غير مدعوم حالياً.")

if __name__ == '__main__':
    # تشغيل البوت
    app = ApplicationBuilder().token(TOKEN).build()
    
    # بيسمع لأي رسالة فيها رابط
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))
    
    print("البوت شغال دلوقتي.. ارسل الرابط مباشرة.")
    app.run_polling()
