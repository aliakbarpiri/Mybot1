import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# نصب این کتابخانه الزامی است: pip install google-genai
from google import genai 

# ================== تنظیمات لوفی شاپ ==================
TOKEN = "8719139878:AAELuQ2HpjFPOXjKIsPNkoCwD_-BMZE05-0" 
CHANNEL_ID = "@Luffy_sh_op"
GROUP_ID = -1003499181273
GROUP_LINK = "https://t.me/Gap_Luffy_Shop"

# تنظیمات کلاینت گوگل
API_KEY = "AIzaSyAkApiuYA1pODx4X6DrHstId-hibZSc92A"
client = genai.Client(api_key=API_KEY)
# ====================================================

SENS_TEXTS = [
    "𝗦𝗘𝗡𝗦𝗜 ⚡🔥\n𝐆𝐞𝐧𝐞𝐫𝐚𝐥: ⚡ 194\n𝐁𝐮𝐭𝐭𝐨𝐧: 🎮 46",
    "🔵 سنس جدید بارگذاری شد!"
]

main_keyboard = [['🤖 هوش مصنوعی'], ['💀 سنس']]
back_keyboard = [['🔙 بازگشت به منوی اصلی']]

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def check_membership(context, user_id):
    try:
        c = context.bot.get_chat_member(CHANNEL_ID, user_id).status
        g = context.bot.get_chat_member(GROUP_ID, user_id).status
        return c in ['member', 'administrator', 'creator'] and g in ['member', 'administrator', 'creator']
    except: return False

def start(update, context):
    if check_membership(context, update.effective_user.id):
        update.message.reply_text("خوش آمدی! از منو انتخاب کن:", 
                                  reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    else:
        btn = [[InlineKeyboardButton("📢 کانال", url=f"https://t.me/{CHANNEL_ID[1:]}")],
               [InlineKeyboardButton("👥 گروه", url=GROUP_LINK)]]
        update.message.reply_text("⚠️ ابتدا عضو شوید:", reply_markup=InlineKeyboardMarkup(btn))

def handle_message(update, context):
    text = update.message.text
    user_id = update.effective_user.id

    if text == '💀 سنس':
        update.message.reply_text(random.choice(SENS_TEXTS))
    elif text == '🤖 هوش مصنوعی':
        update.message.reply_text("سوالت رو بپرس:")
    elif text == '🔙 بازگشت به منوی اصلی':
        update.message.reply_text("منوی اصلی:", reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    else:
        if not check_membership(context, user_id):
            update.message.reply_text("❌ عضو نیستی!")
            return
            
        msg = update.message.reply_text("⏳ در حال پردازش توسط Gemini 3...")
        
        try:
            # استفاده از متد جدید که فرستادی
            response = client.models.generate_content(
                model="gemini-2.0-flash", # یا gemini-3-flash-preview اگر در ریجن شما فعال باشد
                contents=text
            )
            
            ai_reply = response.text
            msg.edit_text(ai_reply)
            
        except Exception as e:
            print(f"Error: {e}")
            msg.edit_text("❌ مشکلی در اتصال به مدل جدید پیش آمد.")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    print("Bot is LIVE with Gemini SDK!")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
