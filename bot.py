import asyncio
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def download_instagram(url: str) -> str:
    ydl_opts = {
        'outtmpl': '/tmp/video.%(ext)s',
        'format': 'best',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for f in os.listdir('/tmp'):
        if f.startswith('video.'):
            return f'/tmp/{f}'
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com" not in text:
        await update.message.reply_text("لطفاً یه لینک اینستاگرام بفرست!")
        return
    await update.message.reply_text("⏳ در حال پردازش...")
    try:
        loop = asyncio.get_event_loop()
        video_path = await loop.run_in_executor(None, download_instagram, text)
        if video_path and os.path.exists(video_path):
            with open(video_path, 'rb') as v:
                await update.message.reply_video(v)
            await update.message.reply_text("✅ ویدیو دانلود شد!")
            os.remove(video_path)
        else:
            await update.message.reply_text("❌ نتونستم ویدیو رو دانلود کنم")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
