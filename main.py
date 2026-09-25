from flask import Flask
from threading import Thread
import os, logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web).start()

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready! Insta/Youtube/Telegram ka link ya video bhejo")

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Forwarded video
    if update.message.video:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=update.message.video.file_id, caption="✅ Ye raha video!")
        return
    if update.message.document:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=update.message.document.file_id)
        return

    url = (update.message.text or "").strip()
    if not url: return
    
    if "t.me/c/" in url:
        await update.message.reply_text("🔒 Private link hai. Video ko Forward karke bhejo ya Download karke bhejo, link se nahi hoga.")
        return

    if "http" in url:
        status = await update.message.reply_text("⏳ Download kar raha hu...")
        try:
            opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                # YE LINE YOUTUBE FIX HAI
                'extractor_args': {'youtube': {'player_client': ['android', 'web'], 'player_skip': ['webpage']}},
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                fname = ydl.prepare_filename(info)
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(fname, 'rb'), caption=f"✅ {info.get('title','')}")
            os.remove(fname)
            await status.delete()
        except Exception as e:
            await status.edit_text(f"❌ Error: {e}")

if __name__ == "__main__":
    app2 = Application.builder().token(TOKEN).build()
    app2.add_handler(CommandHandler("start", start))
    app2.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_all))
    app2.run_polling()
