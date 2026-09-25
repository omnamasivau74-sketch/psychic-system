from flask import Flask
from threading import Thread
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

app = Flask(__name__)
@app.route('/')
def home(): return "Alive"
def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web).start()

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready ✅ Link bhejo")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agar video forward kiya hai toh direct bhej dega
    if update.message.video:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=update.message.video.file_id)
        return
    if update.message.document:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=update.message.document.file_id)
        return

    url = (update.message.text or "").strip()
    if "http" not in url:
        return

    msg = await update.message.reply_text("⏳ Downloading...")
    
    try:
        opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'video.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['android']}},
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fname = ydl.prepare_filename(info)
        
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(fname, 'rb'))
        os.remove(fname)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ {e}\n\nTip: Render pe Manual Deploy > Clear cache & deploy karo")

if __name__ == "__main__":
    app2 = Application.builder().token(TOKEN).build()
    app2.add_handler(CommandHandler("start", start))
    app2.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle))
    app2.run_polling()
