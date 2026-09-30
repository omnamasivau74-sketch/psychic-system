from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
import zipfile, os, asyncio

# --- CONFIG ---
API_ID = 1234567 # my.telegram.org se
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 1234567890 # Teri ID @userinfobot se
DB_CHANNEL = -1001111111111 # Jaha files store hongi

# Settings
FORWARD_SOURCE = -1002222222222
FORWARD_TARGETS = [-1003333333333]
CUSTOM_CAPTION = None
JOIN_ACCEPT = True
DELETE_JOIN_MSG = True
TOPIC_MAP = {2: 5} # Source Topic : Target Topic

app = Client("MEGA_BOT", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 1. START & HELP ---
@app.on_message(filters.command("start") & filters.private)
async def start(c, m):
    if len(m.text.split()) > 1:
        # File Store ka link se file dena
        file_id = m.text.split()[1]
        try:
            await c.copy_message(m.chat.id, DB_CHANNEL, int(file_id))
            return
        except: pass
    await m.reply_text(
        "🔥 **MEGA BOT ON** 🔥\n\n"
        "🤖 /src <link> - Restricted Save\n"
        "🔄 Auto Forward - ON hai\n"
        "📂 Topic to Topic - ON hai\n"
        "✅ Join Request - Auto Accept ON\n"
        "🗑️ Join Msg Delete - ON\n"
        "✏️ /setcaption <text> - Caption set\n"
        "🔎 Movie naam likho - Search karega\n"
        "💾 File bhejo - Store Link dunga\n"
        "📦 ZIP bhejo - Extract karke dunga"
    )

# --- 2. SRC BOT (Restricted Save) ---
@app.on_message(filters.command("src"))
async def src_bot(c, m):
    if len(m.command) < 2: return await m.reply("Link bhejo: /src https://t.me/xxx/123")
    link = m.command[1]
    try:
        parts = link.split("/")
        msg_id = int(parts[-1])
        chat = parts[-2]
        if chat == "c": chat = int(f"-100{parts[-2]}") # private channel
        msg = await c.get_messages(chat, msg_id)
        await msg.copy(m.chat.id, caption=CUSTOM_CAPTION or msg.caption)
        await m.reply("✅ Saved!")
    except Exception as e: await m.reply(f"Error: {e}")

# --- 3. FORWARD & TOPIC FORWARD ---
@app.on_message(filters.channel & filters.chat(FORWARD_SOURCE))
async def auto_forward(c, m):
    for target in FORWARD_TARGETS:
        try: await m.copy(target, caption=CUSTOM_CAPTION or m.caption)
        except: pass

@app.on_message(filters.group)
async def topic_forward(c, m):
    if not m.message_thread_id: return
    if m.message_thread_id in TOPIC_MAP:
        target_topic = TOPIC_MAP[m.message_thread_id]
        try: await m.copy(m.chat.id, message_thread_id=target_topic)
        except: pass

# --- 4. JOIN REQUEST ACCEPT ---
@app.on_chat_join_request()
async def accept_req(c, req: ChatJoinRequest):
    if JOIN_ACCEPT: await c.approve_chat_join_request(req.chat.id, req.from_user.id)

# --- 5. JOIN MESSAGE DELETE ---
@app.on_message(filters.new_chat_members)
async def del_join(c, m):
    if DELETE_JOIN_MSG: await m.delete()

# --- 6. CAPTION EDITOR ---
@app.on_message(filters.command("setcaption") & filters.user(ADMIN_ID))
async def set_cap(c, m):
    global CUSTOM_CAPTION
    CUSTOM_CAPTION = m.text.replace("/setcaption ", "")
    await m.reply(f"Caption Set: {CUSTOM_CAPTION}")

@app.on_message(filters.command("delcaption") & filters.user(ADMIN_ID))
async def del_cap(c, m):
    global CUSTOM_CAPTION
    CUSTOM_CAPTION = None
    await m.reply("Caption Deleted")

# --- 7. MOVIE SEARCH BOT ---
@app.on_message(filters.text & filters.private & ~filters.command(["start","src","setcaption","delcaption"]))
async def movie_search(c, m):
    if "t.me" in m.text: return # src ke liye ignore
    # DB_CHANNEL me search karega
    try:
        async for msg in c.search_messages(DB_CHANNEL, query=m.text, limit=10):
            if msg.caption and m.text.lower() in (msg.caption or "").lower():
                await msg.copy(m.chat.id)
        # Agar na mile
        # await m.reply(f"'{m.text}' nahi mila, sahi naam likho")
    except: pass

# --- 8. PERMANENT FILE STORE + FILE SHARING ---
@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def file_store(c, m):
    # ZIP hai to extract wale me bhej do
    if m.document and ".zip" in (m.document.file_name or ""):
        return await zip_extract(c, m)

    saved = await m.copy(DB_CHANNEL)
    share_link = f"https://t.me/{(await c.get_me()).username}?start={saved.id}"
    await m.reply(f"💾 **File Stored!**\n\n🔗 Share Link: {share_link}\n✏️ Caption: {CUSTOM_CAPTION or 'Original'}", disable_web_page_preview=True)

# --- 9. ZIP EXTRACTOR ---
async def zip_extract(c, m):
    await m.reply("📦 ZIP Extract kar raha hu...")
    path = await c.download_media(m)
    try:
        with zipfile.ZipFile(path) as z:
            z.extractall(f"./{m.id}")
            for file in os.listdir(f"./{m.id}"):
                await c.send_document(m.chat.id, f"./{m.id}/{file}")
        await m.reply("✅ Extract Done!")
    except Exception as e: await m.reply(f"Error: {e}")

print("MEGA BOT RUNNING...")
app.run()
