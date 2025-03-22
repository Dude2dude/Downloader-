import os
import yt_dlp
import instaloader
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from spotdl import Spotdl

# Telegram Bot Token (Set in Koyeb Environment Variables)
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Set this as your Koyeb app URL

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dispatcher
dispatcher = Dispatcher(bot, None, workers=4, use_context=True)

# Initialize Spotify downloader
spotdl = Spotdl()

# Command: /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me a video link from Instagram, Facebook, YouTube, Spotify, or Terabox.")

# Handle URLs
def download_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text

    if "youtube.com" in url or "youtu.be" in url:
        download_youtube(update, url)
    elif "instagram.com" in url:
        download_instagram(update, url)
    elif "facebook.com" in url:
        download_facebook(update, url)
    elif "spotify.com" in url:
        download_spotify(update, url)
    elif "terabox.com" in url:
        download_terabox(update, url)
    else:
        update.message.reply_text("Unsupported URL. Please send a valid link.")

# Download YouTube Videos
def download_youtube(update: Update, url: str):
    ydl_opts = {"format": "best", "outtmpl": "downloads/%(title)s.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        send_video(update, filename)

# Download Instagram Videos
def download_instagram(update: Update, url: str):
    loader = instaloader.Instaloader()
    post_id = url.split("/")[-2]
    try:
        loader.download_post(instaloader.Post.from_shortcode(loader.context, post_id), target="downloads")
        send_video(update, f"downloads/{post_id}.mp4")
    except Exception as e:
        update.message.reply_text(f"Error downloading Instagram video: {e}")

# Download Facebook Videos
def download_facebook(update: Update, url: str):
    try:
        ydl_opts = {"format": "best", "outtmpl": "downloads/%(title)s.%(ext)s"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            send_video(update, filename)
    except Exception as e:
        update.message.reply_text(f"Error downloading Facebook video: {e}")

# Download Spotify Music
def download_spotify(update: Update, url: str):
    try:
        spotdl.download([url])
        send_video(update, f"{os.path.basename(url)}.mp3")
    except Exception as e:
        update.message.reply_text(f"Error downloading Spotify track: {e}")

# Terabox Download (Not Implemented Yet)
def download_terabox(update: Update, url: str):
    update.message.reply_text("Terabox download is currently not supported.")

# Send Video to Telegram
def send_video(update: Update, file_path: str):
    try:
        update.message.reply_text("Uploading...")
        update.message.reply_video(video=open(file_path, "rb"))
        os.remove(file_path)
    except Exception as e:
        update.message.reply_text(f"Error sending video: {e}")

# Handle Webhook Updates
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Set Webhook
def set_webhook():
    bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info("Webhook set!")

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=5000)
