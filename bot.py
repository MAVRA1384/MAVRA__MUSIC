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
            spotify = song.get('spotify', {})
            apple = song.get('apple_music', {})
            spotify_link = spotify.get('external_urls', {}).get('spotify', '') if spotify else ''
            apple_link = apple.get('url', '') if apple else ''
            return {
                'title': song.get('title', 'نامشخص'),
                'artist': song.get('artist', 'نامشخص'),
                'spotify': spotify_link,
                'apple': apple_link,
                'found': True
            }
        return {'found': False}
    except:
        return {'found': False}

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
        "🔹 آهنگش رو پیدا میکنم و لینکش رو میدم!\n\n"
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
                msg = f"🎵 آهنگ: {title}\n🎤 خواننده: {artist}\n\n"
                buttons = []
                if song_data.get('spotify'):
                    buttons.append([InlineKeyboardButton("🟢 Spotify", url=song_data['spotify'])])
                if song_data.get('apple'):
                    buttons.append([InlineKeyboardButton("🍎 Apple Music", url=song_data['apple'])])
                if buttons:
                    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
                else:
                    await update.message.reply_text(msg)
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
