import telebot

BOT_TOKEN = "8798146373:AAHzO55I_C8gSagy-3sdLkAXXt8zklmdu8o"
ADMIN_ID = 736783447  # @userinfobot se apni ID leke dal

bot = telebot.TeleBot(BOT_TOKEN)
reply_map = {} # admin reply ko track karne ke liye

# 1. Group se koi bhi msg aayega to tere private bot me aayega
@bot.message_handler(content_types=['text','photo','video','document','sticker','voice'])
def from_group(m):
    if m.chat.type in ['group', 'supergroup']:
        # Tere paas forward hoga
        info = f"📩 Group: {m.chat.title}\nID: {m.chat.id}\nFrom: {m.from_user.first_name}"
        bot.send_message(ADMIN_ID, info)
        fwd = bot.copy_message(ADMIN_ID, m.chat.id, m.message_id)
        reply_map[fwd.message_id] = {'chat_id': m.chat.id, 'msg_id': m.message_id}

# 2. Tu bot me us msg ka Reply karega, to bot group me bhej dega
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.chat.type == 'private')
def admin_reply(m):
    if m.reply_to_message and m.reply_to_message.message_id in reply_map:
        data = reply_map[m.reply_to_message.message_id]
        bot.copy_message(data['chat_id'], m.chat.id, m.message_id)
        bot.send_message(ADMIN_ID, "✅ Group me bhej diya")
    else:
        bot.send_message(ADMIN_ID, "Reply karke bhejo. Kisi msg pe REPLY dabake likho, tabhi group me jayega.")

print("Any-Group Bot Running...")
bot.infinity_polling()
