from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_web).start()
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Link bhej, download kar dunga 👇")

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        return
    msg = await update.message.reply_text("Downloading... ⏳")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': '%(title)s.%(ext)s', 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(filename, 'rb'))
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"Error: {e}")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))
    app.run_polling()
