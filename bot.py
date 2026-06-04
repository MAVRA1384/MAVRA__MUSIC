import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from shazamio import Shazam
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def download_instagram(url: str) -> str:
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

async def extract_audio(video_path: str) -> str:
    audio_path = "/tmp/audio.mp3"
    os.system(f"ffmpeg -i {video_path} -q:a 0 -map a {audio_path} -y -loglevel quiet")
    return audio_path

async def find_song(audio_path: str) -> str:
    shazam = Shazam()
    result = await shazam.recognize(audio_path)
    if 'track' in result:
        track = result['track']
        title = track.get('title', 'نامشخص')
        artist = track.get('subtitle', 'نامشخص')
        return f"🎵 آهنگ: {title}\n🎤 خواننده: {artist}"
    return "❌ آهنگی پیدا نشد"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com" not in text:
        await update.message.reply_text("لطفاً یه لینک اینستاگرام بفرست!")
        return
    await update.message.reply_text("⏳ در حال پردازش، صبر کن...")
    try:
        video_path = await asyncio.to_thread(download_instagram, text)
        with open(video_path, 'rb') as v:
            await update.message.reply_video(v)
        audio_path = await extract_audio(video_path)
        song_info = await find_song(audio_path)
        await update.message.reply_text(song_info)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")
    finally:
        for f in ['/tmp/video.mp4', '/tmp/video.webm', '/tmp/audio.mp3']:
            if os.path.exists(f):
                os.remove(f)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
