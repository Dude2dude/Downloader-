import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize bot
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Set webhook
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    response = bot.set_webhook(webhook_url)
    if response:
        logger.info("Webhook set successfully!")
    else:
        logger.error("Failed to set webhook!")

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    logger.info("Received /start command")
    update.message.reply_text("Send me a video link from Instagram, Facebook, YouTube, or Terabox.")

# Video download handler
def download_video(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    logger.info(f"Received message: {message_text}")

    if "youtube.com" in message_text or "youtu.be" in message_text:
        update.message.reply_text("Downloading YouTube video...")

        # Example API usage (Replace this with a real API)
        response = requests.get(f"https://some-api.com/download?url={message_text}")
        
        if response.status_code == 200:
            update.message.reply_text("✅ Video downloaded! Sending...")
            update.message.reply_video(video=response.json()["video_url"])
        else:
            update.message.reply_text("❌ Failed to download video. Try another link.")

    elif "instagram.com" in message_text:
        update.message.reply_text("Instagram downloading is not yet supported.")
    
    else:
        update.message.reply_text("❌ Unsupported link. Please send a valid video URL.")

# Flask webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    logger.info(f"Received update: {update}")
    dispatcher.process_update(update)
    return "OK", 200

# Initialize dispatcher
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

# Set webhook on startup
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=8080)
