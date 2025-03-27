from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pytube import YouTube
import os
import requests

app = Flask(__name__)

# Replace 'YOUR_TOKEN_HERE' with your bot's token
TOKEN = '7318650217:AAEXr17lLVfhXGBKgnMLgmtYjV1kJ_pAdmQ'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Welcome! Send me a YouTube video link or a Terabox file link to download.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Here are the commands you can use:\n"
        "/start - Start the bot\n"
        "/help - Get help information\n"
        "/download_youtube <YouTube URL> - Download the YouTube video\n"
        "/download_terabox <Terabox URL> - Download the Terabox file\n"
    )
    await update.message.reply_text(help_text)

async def download_youtube_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download a YouTube video from the provided URL."""
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a YouTube URL. Usage: /download_youtube <YouTube URL>")
        return

    video_url = context.args[0]  # Get the URL from user input
    try:
        yt = YouTube(video_url)
        video = yt.streams.get_highest_resolution()
        download_path = 'downloads/'
        
        # Create downloads directory if it doesn't exist
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        video.download(output_path=download_path)  # Specify download directory
        await update.message.reply_text(f"Downloaded: {yt.title}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def download_terabox_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download a file from Terabox using the provided link."""
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a Terabox file link. Usage: /download_terabox <Terabox URL>")
        return

    terabox_url = context.args[0]  # Get the URL from user input
    try:
        # Placeholder for Terabox download logic
        # You would need to implement the actual download logic here
        # For demonstration, we will just send a placeholder message
        await update.message.reply_text(f"Initiating download for: {terabox_url}")
        
        # Example: response = requests.get(terabox_url)
        # Save the file and send a confirmation message

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True))
    application.process_update(update)
    return 'ok'

def main() -> None:
    """Start the bot."""
    global application
    application = ApplicationBuilder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("download_youtube", download_youtube_video))
    application.add_handler(CommandHandler("download_terabox", download_terabox_file))

    # Set webhook
    application.bot.set_webhook('https://<your-koyeb-app-name>.koyeb.app/webhook')

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
