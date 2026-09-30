import telebot

BOT_TOKEN = "8798146373:AAEb1dOAb3ws948YZRNej6F59tKH-eQfAzU" 
ADMIN_ID = 736783447 # Yaha Apni ID Dal @userinfobot se

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id == ADMIN_ID:
        bot.send_message(m.chat.id, "Tu Admin hai ✅ Bot ON hai.")
    else:
        bot.send_message(m.chat.id, "Hello! Message bhejo, admin reply karega.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'voice', 'sticker'])
def handle_user(m):
    if m.from_user.id == ADMIN_ID: return
    info = f"📩 Naya Msg\nName: {m.from_user.first_name}\nID: {m.from_user.id}\nUsername: @{m.from_user.username}"
    bot.send_message(ADMIN_ID, info)
    fwd = bot.copy_message(ADMIN_ID, m.chat.id, m.message_id)
    user_data[fwd.message_id] = m.chat.id
    bot.send_message(m.chat.id, "✅ Admin tak pahuch gaya.")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def handle_admin(m):
    if m.reply_to_message and m.reply_to_message.message_id in user_data:
        user_id = user_data[m.reply_to_message.message_id]
        bot.copy_message(user_id, m.chat.id, m.message_id)

print("Bot Running...")
bot.infinity_polling()
