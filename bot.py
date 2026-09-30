import telebot

BOT_TOKEN = "8798146373:AAEb1dOAb3ws948YZRNej6F59tKH-eQfAzU"
# Yaha apni ID daal - @userinfobot se le le
ADMIN_ID = 1234567890

bot = telebot.TeleBot(BOT_TOKEN)

# User ka ID save karne ke liye
user_data = {}

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id == ADMIN_ID:
        bot.send_message(m.chat.id, "Admin Panel On ✅\nAb koi bhi user msg karega to tere pass ayega.")
    else:
        bot.send_message(m.chat.id, "Hello! Apna message bhejo, Admin jaldi reply karega.")

# Jab koi User msg karega
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_user(m):
    # Agar Admin khud msg kar raha hai to ignore
    if m.from_user.id == ADMIN_ID:
        return

    # Admin ke pass forward karo
    try:
        # User ki info ke saath
        info = f"📩 New Msg From: {m.from_user.first_name}\nUsername: @{m.from_user.username}\nID: {m.from_user.id}\n\n"
        bot.send_message(ADMIN_ID, info)
        forwarded = bot.copy_message(ADMIN_ID, m.chat.id, m.message_id)
        
        # Save kar lo ki ye msg kis user ka tha
        user_data[forwarded.message_id] = m.chat.id
        bot.send_message(m.chat.id, "✅ Message Admin tak pahuch gaya, reply ka wait karo.")
    except Exception as e:
        print(e)

# Jab tu (Admin) us msg ka Reply karega
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def handle_admin_reply(m):
    # Agar tune kisi forwarded msg ka reply kiya hai
    if m.reply_to_message:
        original_msg_id = m.reply_to_message.message_id
        if original_msg_id in user_data:
            user_id = user_data[original_msg_id]
            try:
                # User ko tera reply bhej do
                bot.copy_message(user_id, m.chat.id, m.message_id)
            except Exception as e:
                bot.send_message(ADMIN_ID, f"Send nahi hua: {e}")

print("Live Reply Bot Running...")
bot.infinity_polling()
