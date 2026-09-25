from flask import Flask
from threading import Thread
import logging, os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web).start()

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Super Downloader Ready!**\n\n"
        "✅ Insta / YouTube link bhejo\n"
        "✅ Public Channel ka link: `t.me/channelname/123`\n"
        "✅ Private Channel: Mujhe us channel me Admin banao, fir link bhejo\n"
        "✅ Ya Private ka video Forward kar do mujhe\n\n"
        "Sab download kar dunga!",
        parse_mode='Markdown'
    )

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip() if update.message.text else ""

    # CASE 1: User forwarded a video/file from private channel
    if update.message.video or update.message.document or update.message.photo:
        msg = await update.message.reply_text("⏳ Forwarded video download kar raha hu...")
        try:
            file_id = None
            if update.message.video: file_id = update.message.video.file_id
            elif update.message.document: file_id = update.message.document.file_id
            elif update.message.photo: file_id = update.message.photo[-1].file_id
            
            file = await context.bot.get_file(file_id)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=file.file_id, caption="✅ Ye raha aapka private channel ka video!")
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"Error: {e}")
        return

    # CASE 2: Link handling
    if "http" not in url: return

    status = await update.message.reply_text("⏳ Downloading...")

    # Special handling for t.me links
    if "t.me/" in url:
        await status.edit_text(
            "🔗 Telegram ka link detect kiya!\n"
            "⚠️ Private channel hai toh:\n"
            "1. Mujhe us channel me Admin banao\n"
            "2. Ya video ko yaha Forward kar do\n\n"
            "Public channel ka video try kar raha hu..."
        )

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['android']}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Try as video, fallback to document
        try:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(filename, 'rb'), caption=f"✅ {info.get('title','')}")
        except:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(filename, 'rb'))
        
        os.remove(filename)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}\n\nPrivate channel hai toh bot ko channel me Add karke Admin banao, fir link bhejo.")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # Text + Video + Document sab handle karega
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, download_handler))
    application.run_polling()
