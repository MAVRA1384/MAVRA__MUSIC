import asyncio
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")
AUDD_TOKEN = os.environ.get("AUDD_TOKEN")
CHANNEL_ID = "@MAVRA_MUSIC"

async def check_membership(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

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

def find_song(video_path: str) -> dict:
    try:
        with open(video_path, 'rb') as f:
            response = requests.post(
                'https://api.audd.io/',
                data={'api_token': AUDD_TOKEN, 'return': 'apple_music,spotify'},
                files={'file': f}
            )
        result = response.json()
        if result.get('status') == 'success' and result.get('result'):
            song = result['result']
            return {
                'title': song.get('title', 'نامشخص'),
                'artist': song.get('artist', 'نامشخص'),
                'found': True
            }
        return {'found': False}
    except:
        return {'found': False}

def download_song(title: str, artist: str) -> str:
    try:
        query = f"{artist} {title}"
        ydl_opts = {
            'outtmpl': '/tmp/song.%(ext)s',
            'format': 'bestaudio',
            'quiet': True,
            'default_search': 'ytsearch1',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        for f in os.listdir('/tmp'):
            if f.startswith('song.'):
                return f'/tmp/{f}'
        return None
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    user_id = update.message.from_user.id
    if not await check_membership(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 🎵", url="https://t.me/MAVRA_MUSIC")]]
        await update.message.reply_text(
            f"سلام {user_name} عزیز! 👋\n\n❌ برای استفاده از ربات ابتدا در کانال ما عضو شو!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    await update.message.reply_text(
        f"سلام {user_name} عزیز! 🎵\n\n"
        "به ربات MAVRA MUSIC خوش اومدی! 🎶\n\n"
        "🔹 لینک پست یا ریل اینستاگرام رو بفرست\n"
        "🔹 ویدیو رو دانلود میکنم\n"
        "🔹 آهنگش رو پیدا و دانلود میکنم!\n\n"
        "یه لینک اینستاگرام بفرست! 👇"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    if not await check_membership(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 🎵", url="https://t.me/MAVRA_MUSIC")]]
        await update.message.reply_text(
            "❌ برای استفاده از ربات ابتدا در کانال ما عضو شو!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    if "instagram.com" not in text:
        await update.message.reply_text("لطفاً یه لینک اینستاگرام بفرست! 🔗")
        return
    await update.message.reply_text("⏳ در حال پردازش، صبر کن...")
    loop = asyncio.get_event_loop()
    try:
        video_path = await loop.run_in_executor(None, download_instagram, text)
        if video_path and os.path.exists(video_path):
            with open(video_path, 'rb') as v:
                await update.message.reply_video(v)
            song_data = await loop.run_in_executor(None, find_song, video_path)
            os.remove(video_path)
            if song_data['found']:
                title = song_data['title']
                artist = song_data['artist']
                await update.message.reply_text(
                    f"🎵 آهنگ: {title}\n🎤 خواننده: {artist}\n\n⏳ در حال دانلود آهنگ..."
                )
                song_path = await loop.run_in_executor(None, download_song, title, artist)
                if song_path and os.path.exists(song_path):
                    with open(song_path, 'rb') as s:
                        await update.message.reply_audio(s, title=title, performer=artist)
                    os.remove(song_path)
                else:
                    await update.message.reply_text("❌ نتونستم فایل آهنگ رو دانلود کنم")
            else:
                await update.message.reply_text("❌ آهنگی پیدا نشد")
        else:
            await update.message.reply_text("❌ نتونستم ویدیو رو دانلود کنم")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()        if video_path and os.path.exists(video_path):
            with open(video_path, 'rb') as v:
                await update.message.reply_video(v)
            song_data = await loop.run_in_executor(None, find_song, video_path)
            os.remove(video_path)
            if song_data['found']:
                title = song_data['title']
                artist = song_data['artist']
                await update.message.reply_text(f"🎵 آهنگ: {title}\n🎤 خواننده: {artist}\n\n⏳ در حال دانلود آهنگ...")
                song_path = await loop.run_in_executor(None, download_song, title, artist)
                if song_path and os.path.exists(song_path):
                    with open(song_path, 'rb') as s:
                        await update.message.reply_audio(s, title=title, performer=artist)
                    os.remove(song_path)
                else:
                    await update.message.reply_text("❌ نتونستم فایل آهنگ رو دانلود کنم")
            else:
                await update.message.reply_text("❌ آهنگی پیدا نشد")
        else:
            await update.message.reply_text("❌ نتونستم ویدیو رو دانلود کنم")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
