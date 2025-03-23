import os
import tempfile
from flask import Flask, request
from pyrogram import Client, filters
import requests
import json

# Get environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Flask app for webhook
app = Flask(__name__)

# Pyrogram bot instance
bot = Client(
    "PhotoToUrlBot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# Set webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    bot.process_update(update)
    return "OK", 200

# Command: /start
@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("👋 Welcome! Send me:\n"
                       "📷 A photo to get a URL\n"
                       "📜 HTML code to generate a temporary link\n"
                       "🔍 Any text to get information.")

# Feature 1: Photo to URL
@bot.on_message(filters.photo)
def photo_to_url(client, message):
    photo = message.photo.file_id
    file_path = client.download_media(photo)
    
    # Upload to Telegra.ph
    with open(file_path, "rb") as file:
        response = requests.post("https://telegra.ph/upload", files={"file": ("file.jpg", file, "image/jpeg")})
    
    if response.status_code == 200:
        result = response.json()
        image_url = "https://telegra.ph" + result[0]["src"]
        message.reply_text(f"🖼 Your image URL: {image_url}")
    else:
        message.reply_text("❌ Failed to upload image.")
    
    os.remove(file_path)

# Feature 2: Temporary HTML Compiler
@bot.on_message(filters.text & filters.regex(r"<\s*html.*?>.*?</\s*html\s*>", flags=re.DOTALL))
def html_to_url(client, message):
    html_code = message.text
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    temp_file.write(html_code.encode("utf-8"))
    temp_file.close()

    # Upload to 0x0.st (a temporary file hosting service)
    with open(temp_file.name, "rb") as f:
        response = requests.post("https://0x0.st", files={"file": f})

    if response.status_code == 200:
        message.reply_text(f"📝 Your HTML link: {response.text}")
    else:
        message.reply_text("❌ Failed to create link.")

    os.remove(temp_file.name)

# Feature 3: Get Information About Text
@bot.on_message(filters.text & ~filters.command(["start"]))
def text_info(client, message):
    text = message.text
    words = len(text.split())
    chars = len(text)

    message.reply_text(f"📄 Text Info:\n"
                       f"🔢 Characters: {chars}\n"
                       f"🔠 Words: {words}")

# Set webhook function
@bot.on_message(filters.command("setwebhook"))
def set_webhook(client, message):
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.set_webhook(webhook_url)
    message.reply_text(f"✅ Webhook set to: {webhook_url}")

# Run the bot
if __name__ == "__main__":
    bot.start()
    app.run(host="0.0.0.0", port=8080)
