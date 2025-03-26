import os
import logging
import datetime
import requests
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from docx2pdf import convert
from bs4 import BeautifulSoup
from flask import Flask  # For health check endpoint

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app for health checks (required for Koyeb)
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is running", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Telegram Bot Functions
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🌟 Welcome to Multi-Feature Bot! 🌟\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/time - Current time and date\n"
        "/series - Latest OTT web series releases\n\n"
        "Features:\n"
        "• Send Terabox/Instagram links → Download videos\n"
        "• Send DOCX files → Convert to PDF"
    )

def time_command(update: Update, context: CallbackContext):
    update.message.reply_text(f"⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def series_command(update: Update, context: CallbackContext):
    try:
        url = "https://www.imdb.com/list/ls099530931/"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        series = [f"• {item.text.strip()}" for item in soup.select(".lister-item-header a")[:5]]
        update.message.reply_text("🎬 Latest Web Series:\n\n" + "\n".join(series))
    except Exception as e:
        logger.error(f"Series scrape failed: {e}")
        update.message.reply_text("⚠️ Failed to fetch series. Try again later.")

def handle_document(update: Update, context: CallbackContext):
    if update.message.document.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            file = context.bot.get_file(update.message.document.file_id)
            docx_path = f"temp_{update.message.document.file_name}"
            pdf_path = docx_path.replace(".docx", ".pdf")
            
            file.download(docx_path)
            convert(docx_path, pdf_path)
            
            with open(pdf_path, "rb") as f:
                update.message.reply_document(document=f, caption="✅ Your PDF is ready!")
            
            os.remove(docx_path)
            os.remove(pdf_path)
        except Exception as e:
            logger.error(f"DOCX conversion failed: {e}")
            update.message.reply_text("❌ Conversion failed. Send a valid DOCX file.")
    else:
        update.message.reply_text("⚠️ Please send a .docx file for conversion.")

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if "terabox.com" in text or "tb.ixigua.com" in text:
        update.message.reply_text("📥 Terabox downloader coming soon! For now, try: /series")
    elif "instagram.com" in text:
        update.message.reply_text("📸 Instagram downloader coming soon! Try: /time")
    else:
        update.message.reply_text("🤖 I can:\n• Convert DOCX to PDF\n• Show time (/time)\n• List OTT series (/series)")

def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error: {context.error}")

# Main Execution
if __name__ == '__main__':
    TOKEN = os.getenv("TOKEN")  # Set in Koyeb dashboard
    
    # Start health check server in a thread
    import threading
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Initialize Telegram Bot
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add handlers
    handlers = [
        CommandHandler("start", start),
        CommandHandler("time", time_command),
        CommandHandler("series", series_command),
        MessageHandler(Filters.document, handle_document),
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    ]
    for handler in handlers:
        dispatcher.add_handler(handler)
    
    dispatcher.add_error_handler(error_handler)
    
    logger.info("Bot started in polling mode...")
    updater.start_polling()
    updater.idle()
