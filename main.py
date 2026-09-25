from flask import Flask
from threading import Thread
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Alive ✅"
def run_flask(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_flask).start()

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready ✅ Link bhejo")

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=update.message.video.file_id)
        return
    if update.message.document:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=update.message.document.file_id)
        return

    url = (update.message.text or "").strip()
    if not url or "http" not in url:
        return

    if "t.me/c/" in url:
        await update.message.reply_text("Private hai, forward karke bhejo")
        return

    status = await update.message.reply_text("⏳ Downloading...")
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'vid.%(ext)s',
            'noplaylist': True
