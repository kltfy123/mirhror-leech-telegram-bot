import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# المكتبات الأساسية للموتور
import yt_dlp
from tiktokapipy.async_api import AsyncTikTokAPI # للمهام المتقدمة في تيك توك
from pyrogram import Client # لو حبيت تستخدم ميزات بايروجرام لاحقاً

# إعداد السجلات (Logs)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكن الجديد اللي بعته
TOKEN = '8640929836:AAEV-p30frbxqNSCXWLw9jQLTRsBCBlaYNU'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("الموتور دار! ابعت رابط الفيديو من يوتيوب أو تيك توك وهجهزهولك.")

def download_video(update: Update, context: CallbackContext):
    url = update.message.text
    chat_id = update.effective_chat.id
    
    msg = update.message.reply_text("جاري سحب الفيديو... انتظر ثواني.")

    # إعدادات المحرك yt-dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/{chat_id}_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو للمستخدم
        with open(filename, 'rb') as video:
            context.bot.send_video(chat_id=chat_id, video=video, timeout=1000)
        
        # تنظيف المجلد
        os.remove(filename)
        msg.delete()

    except Exception as e:
        update.message.reply_text(f"عطل في المحرك: {str(e)}")

def main():
    # بناء البوت على إصدار 13.7
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    # استقبال الروابط
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

    print("البوت شغال الآن بالتوكن الجديد...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
