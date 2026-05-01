"""
بوت تيليغرام لتحميل الفيديوهات
يدعم: يوتيوب، تيك توك
المكتبات: python-telegram-bot, yt-dlp, tiktokapipy, pyrogram
"""

import os
import asyncio
import logging
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp
from tiktokapipy.async_api import AsyncTikTokAPI

# ─────────────────────────────────────────────
# الإعدادات
# ─────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # ← ضع توكن البوت هنا
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# أدوات مساعدة
# ─────────────────────────────────────────────
def detect_platform(url: str) -> str:
    url = url.lower()
    if "tiktok.com" in url:
        return "tiktok"
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "other"


def cleanup(file_path: Path):
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"تعذّر حذف الملف: {e}")


# ─────────────────────────────────────────────
# تحميل يوتيوب عبر yt-dlp
# ─────────────────────────────────────────────
async def download_youtube(url: str, quality: str = "best") -> Path:
    format_map = {
        "best":  "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "720":   "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
        "480":   "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
        "audio": "bestaudio[ext=m4a]/bestaudio",
    }

    ydl_opts = {
        "format":           format_map.get(quality, format_map["best"]),
        "outtmpl":          str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "quiet":            True,
        "no_warnings":      True,
        "merge_output_format": "mp4",
    }

    loop = asyncio.get_event_loop()

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = Path(ydl.prepare_filename(info))
            if not path.exists():
                path = path.with_suffix(".mp4")
            return path

    return await loop.run_in_executor(None, _download)


# ─────────────────────────────────────────────
# تحميل تيك توك
# ─────────────────────────────────────────────
async def download_tiktok_api(url: str):
    try:
        async with AsyncTikTokAPI() as api:
            video = await api.video(url)
            download_url = video.video.download_addr
            ydl_opts = {
                "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
                "quiet": True,
            }
            loop = asyncio.get_event_loop()
            def _dl():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(download_url, download=True)
                    return Path(ydl.prepare_filename(info))
            return await loop.run_in_executor(None, _dl)
    except Exception as e:
        logger.warning(f"tiktokapipy فشل: {e} — سيُستخدم yt-dlp كاحتياطي")
        return None


async def download_tiktok(url: str) -> Path:
    result = await download_tiktok_api(url)
    if result:
        return result

    # احتياطي: yt-dlp مباشرةً
    ydl_opts = {
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "quiet": True,
        "format": "best[ext=mp4]/best",
    }
    loop = asyncio.get_event_loop()
    def _dl():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return Path(ydl.prepare_filename(info))
    return await loop.run_in_executor(None, _dl)


# ─────────────────────────────────────────────
# معالجات البوت
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً! أنا بوت تحميل الفيديوهات.\n\n"
        "📥 أرسل رابط من:\n"
        "• يوتيوب 🎬\n"
        "• تيك توك 🎵"
    )


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    platform = detect_platform(url)

    if platform == "youtube":
        keyboard = [
            [
                InlineKeyboardButton("🎬 أفضل جودة", callback_data=f"yt|best|{url}"),
                InlineKeyboardButton("📺 720p",       callback_data=f"yt|720|{url}"),
            ],
            [
                InlineKeyboardButton("📱 480p",       callback_data=f"yt|480|{url}"),
                InlineKeyboardButton("🎵 صوت فقط",   callback_data=f"yt|audio|{url}"),
            ],
        ]
        await update.message.reply_text(
            "اختر جودة التحميل:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif platform == "tiktok":
        msg = await update.message.reply_text("⏳ جاري التحميل من تيك توك...")
        try:
            file_path = await download_tiktok(url)
            await update.message.reply_video(
                video=open(file_path, "rb"),
                caption="✅ تم التحميل من تيك توك 🎵",
            )
        except Exception as e:
            await msg.edit_text(f"❌ فشل التحميل: {e}")
        finally:
            await msg.delete()
            if "file_path" in locals():
                cleanup(file_path)

    else:
        await update.message.reply_text("❌ الرابط غير مدعوم. أرسل روابط يوتيوب أو تيك توك فقط.")


async def youtube_quality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, quality, url = query.data.split("|", 2)
    await query.edit_message_text(f"⏳ جاري التحميل بجودة {quality}...")

    try:
        file_path = await download_youtube(url, quality)
        if quality == "audio":
            await query.message.reply_audio(
                audio=open(file_path, "rb"),
                caption="✅ تم تحميل الصوت من يوتيوب 🎵",
            )
        else:
            await query.message.reply_video(
                video=open(file_path, "rb"),
                caption=f"✅ تم التحميل من يوتيوب ({quality}) 🎬",
                supports_streaming=True,
            )
    except Exception as e:
        await query.message.reply_text(f"❌ فشل التحميل: {e}")
    finally:
        await query.message.delete()
        if "file_path" in locals():
            cleanup(file_path)


# ─────────────────────────────────────────────
# تشغيل البوت
# ─────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(youtube_quality_callback, pattern=r"^yt\|"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    logger.info("✅ البوت يعمل...")
    app.run_polling()


if __name__ == "__main__":
    main()
