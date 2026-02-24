import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai  # کتابخانه جدید گوگل
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ================== تنظیمات اصلی ==================
TOKEN = "8719139878:AAELuQ2HpjFPOXjKIsPNkoCwD_-BMZE05-0" 
CHANNEL_ID = "@Luffy_sh_op"
GROUP_ID = -1003499181273
GROUP_LINK = "https://t.me/Gap_Luffy_Shop"
GEMINI_API_KEY = "AIzaSyAkApiuYA1pODx4X6DrHstId-hibZSc92A"

# راه اندازی کلاینت جدید گوگل
client = genai.Client(api_key=GEMINI_API_KEY)
# =================================================

SENS_TEXTS = [
    "𝗦𝗘𝗡𝗦𝗜 ⚡🔥\n𝐆𝐞𝐧𝐞𝐫𝐚𝐥: ⚡ 194\n...\n𝘽𝙪𝙩𝙩𝙤𝙣: 🎮 46\n𝘿𝙋𝙄: 🛠 625",
    "🔵 سنس پیشنهادی لوفی شاپ با موفقیت بارگذاری شد!"
]

main_keyboard = [['🤖 هوش مصنوعی'], ['💀 سنس']]
back_keyboard = [['🔙 بازگشت به منوی اصلی']]

# سرور سلامت برای زنده نگه داشتن هاست
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive with Google GenAI!")

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
    if check_membership(context, update.effective_user.id):
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
        update.message.reply_text("سوالت رو بپرس:", reply_markup=ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True))
    elif text == '🔙 بازگشت به منوی اصلی':
        update.message.reply_text("منوی اصلی:", reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    else:
        if not check_membership(context, update.effective_user.id):
            update.message.reply_text("لطفاً ابتدا عضو کانال و گروه شوید.")
            return

        processing_msg = update.message.reply_text("⏳ در حال پردازش...")
        try:
            # استفاده از متد جدید کتابخانه google-genai
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=text
            )
            
            if response.text:
                processing_msg.edit_text(response.text)
            else:
                processing_msg.edit_text("❌ پاسخی دریافت نشد.")
        except Exception as e:
            print(f"GenAI Error: {e}")
            processing_msg.edit_text("❌ خطا در لایه هوش مصنوعی. ممکن است به دلیل محدودیت منطقه باشد.")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    print("--- ربات با Gemini 2.0 فعال شد ---")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
