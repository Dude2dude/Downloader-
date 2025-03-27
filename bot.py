from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

# Replace 'YOUR_TOKEN_HERE' with your bot's token
TOKEN = '7318650217:AAEXr17lLVfhXGBKgnMLgmtYjV1kJ_pAdmQ'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hello')

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True))
    application.process_update(update)
    return 'ok'

def main() -> None:
    """Start the bot."""
    global application
    application = ApplicationBuilder().token(TOKEN).build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Set webhook
    application.bot.set_webhook('https://<your-koyeb-app-name>.koyeb.app/webhook')

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
