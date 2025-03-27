from flask import Flask, request
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

app = Flask(__name__)

# Replace 'YOUR_TOKEN_HERE' with your bot's token
TOKEN = '7318650217:AAEXr17lLVfhXGBKgnMLgmtYjV1kJ_pAdmQ'

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hello')

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True))
    dispatcher.process_update(update)
    return 'ok'

def main() -> None:
    """Start the bot."""
    global dispatcher
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Register the /start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Start the Bot
    updater.start_polling()

    # Set webhook
    updater.bot.setWebhook('https://your-koyeb-app-url/webhook')

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
