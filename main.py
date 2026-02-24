import requests
import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ================== تنظیمات اصلی ==================
TOKEN = "8719139878:AAELuQ2HpjFPOXjKIsPNkoCwD_-BMZE05-0" 
CHANNEL_ID = "@Luffy_sh_op"
GROUP_ID = -1003499181273
GROUP_LINK = "https://t.me/Gap_Luffy_Shop"
GEMINI_API_KEY = "AIzaSyAkApiuYA1pODx4X6DrHstId-hibZSc92A"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
# =================================================

SENS_TEXTS = [
    "𝗦𝗘𝗡𝗦𝗜 ⚡🔥\n𝐆𝐞𝐧𝐞𝐫𝐚𝐥: ⚡ 194\n𝐑𝐞𝐝 𝐝𝐨𝐭: 🎯 179\n𝟐𝐱 𝐒𝐜𝐨𝐩𝐞: ⚙️ 190\n𝟒𝐱 𝐒𝐜𝐨𝐩𝐞: ❄️ 178\n𝐒𝐧𝐢𝐩𝐞𝐫 𝐒𝐜𝐨𝐩𝐞: 👁 104\n𝐅𝐫𝐞𝐞 𝐥𝐨𝐨𝐤: 🌀 170\n\n𝘽𝙪𝙩𝙩𝙤𝙣: 🎮 46\n𝘿𝙋𝙄: 🛠 625",
    "🔵 سنس جدید تنظیم شد!"
]

main_keyboard = [['🤖 هوش مصنوعی'], ['💀 سنس']]
back_keyboard = [['🔙 بازگشت به منوی اصلی']]

# زنده نگه داشتن در Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def check_membership(context, user_id):
    try:
        c_status = context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id).status
        g_status = context.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id).status
        return c_status in ['member', 'administrator', 'creator'] and g_status in ['member', 'administrator', 'creator']
    except: return False

def start(update, context):
    user_id = update.effective_user.id
    if check_membership(context, user_id):
        update.message.reply_text("خوش آمدی!", reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    else:
        keyboard = [[InlineKeyboardButton("📢 کانال", url=f"https://t.me/{CHANNEL_ID[1:]}")],
                    [InlineKeyboardButton("👥 گروه", url=GROUP_LINK)]]
        update.message.reply_text("ابتدا عضو شوید:", reply_markup=InlineKeyboardMarkup(keyboard))

def handle_message(update, context):
    text = update.message.text
    if text == '💀 سنس':
        update.message.reply_text(random.choice(SENS_TEXTS))
    elif text == '🤖 هوش مصنوعی':
        update.message.reply_text("سوالت رو بپرس:")
    elif text == '🔙 بازگشت به منوی اصلی':
        update.message.reply_text("منوی اصلی:", reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    else:
        try:
            res = requests.post(GEMINI_URL, json={"contents": [{"parts": [{"text": text}]}]}, timeout=15)
            ai_reply = res.json()['candidates'][0]['content']['parts'][0]['text']
            update.message.reply_text(ai_reply)
        except:
            update.message.reply_text("❌ خطا در هوش مصنوعی.")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    print("--- ربات فعال شد ---")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
