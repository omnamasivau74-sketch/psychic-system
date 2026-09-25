import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "/start" in update.message.text:
        await update.message.reply_text("Link bhej, mai download karke dunga!")
    else:
        await update.message.reply_text(f"Link mil gaya: {update.message.text}")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
print("Bot running")
app.run_polling()
