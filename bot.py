import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

# Your Token has been added here
TOKEN = '8640929836:AAEV-p30frbxqNSCXWLw9jQLTRsBCBlaYNU'

async def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    # Supports Instagram and YouTube
    if "instagram.com" in url or "youtube.com"or"tiktok.com" in url: in url or "youtu.be" in url:
        await update.message.reply_text("Processing your link... ⏳")
        try:
            await download_video(url)
            if os.path.exists('video.mp4'):
                with open('video.mp4', 'rb') as video_file:
                    await update.message.reply_video(video=video_file)
                os.remove('video.mp4')
            else:
                await update.message.reply_text("Failed to find the downloaded video.")
        except Exception as e:
            await update.message.reply_text(f"Error occurred: {e}")
    else:
        await update.message.reply_text("Please send a valid Instagram or YouTube link.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is starting...")
    app.run_polling()
