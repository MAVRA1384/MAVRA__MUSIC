import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    user_id = update.message.from_user.id

    if not await check_membership(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 🎵", url="https://t.me/MAVRA_MUSIC")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"سلام {user_name} عزیز! 👋\n\n❌ برای استفاده از ربات ابتدا در کانال ما عضو شو!",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text(
        f"سلام {user_name} عزیز! 🎵\n\n"
        "به ربات MAVRA MUSIC خوش اومدی! 🎶\n\n"
        "🔹 کافیه لینک یه پست یا ریل اینستاگرام رو برام بفرستی\n"
        "🔹 ویدیو رو برات دانلود میکنم\n\n"
        "یه لینک اینستاگرام بفرست! 👇"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if not await check_membership(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 🎵", url="https://t.me/MAVRA_MUSIC")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ برای استفاده از ربات ابتدا در کانال ما عضو شو!",
            reply_markup=reply_markup
        )
        return

    if "instagram.com" not in text:
        await update.message.reply_text("لطفاً یه لینک اینستاگرام بفرست! 🔗")
        return

    await update.message.reply_text("⏳ در حال پردازش، صبر کن...")
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
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
