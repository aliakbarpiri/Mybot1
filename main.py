import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google import genai 

# ================== تنظیمات اختصاصی لوفی شاپ ==================
# توکن ربات تلگرام خود را اینجا بگذارید
TOKEN = "8719139878:AAELuQ2HpjFPOXjKIsPNkoCwD_-BMZE05-0" 

# اطلاعات کانال و گروه برای قفل عضویت
CHANNEL_ID = "@Luffy_sh_op"
GROUP_ID = -1003499181273
GROUP_LINK = "https://t.me/Gap_Luffy_Shop"

# توکن جدید گوگل (حتماً از یک Project جدید در Google AI Studio بگیرید)
API_KEY = "AIzaSyCm8FwNyAaD60vz269ueP9z_aKFnlnZSUI" 
client = genai.Client(api_key=API_KEY)
# ============================================================

SENS_TEXTS = [
    "𝗦𝗘𝗡𝗦𝗜 ⚡🔥\n𝐆𝐞𝐧𝐞𝐫𝐚𝐥: ⚡ 194\n𝐑𝐞𝐝 𝐝𝐨𝐭: 🎯 179\n𝟐𝐱 𝐒𝐜𝐨𝐩𝐞: ⚙️ 190\n𝟒𝐱 𝐒𝐜𝐨𝐩𝐞: ❄️ 178\n𝐒𝐧𝐢𝐩𝐞𝐫 𝐒𝐜𝐨𝐩𝐞: 👁 104\n\n𝘽𝙪𝙩𝙩𝙤𝙣: 🎮 46\n𝘿𝙋𝙄: 🛠 625",
    "🔵 سنس پیشنهادی جدید لود شد!\n❤️ ممنون که از لوفی شاپ استفاده می‌کنی."
]

main_keyboard = [['🤖 هوش مصنوعی'], ['💀 سنس']]
back_keyboard = [['🔙 بازگشت به منوی اصلی']]

# سرور سلامت برای زنده نگه داشتن ربات در هاستینگ
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Luffy Bot is Active")

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
        update.message.reply_text("✨ به ربات لوفی شاپ خوش آمدی!\nاز منوی زیر استفاده کن:", 
                                  reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    else:
        btn = [[InlineKeyboardButton("📢 کانال لوفی", url=f"https://t.me/{CHANNEL_ID[1:]}")],
               [InlineKeyboardButton("👥 گروه گپ", url=GROUP_LINK)]]
        update.message.reply_text("⚠️ برای استفاده از ربات، ابتدا عضو کانال و گروه شوید:", 
                                  reply_markup=InlineKeyboardMarkup(btn))

def handle_message(update, context):
    text = update.message.text
    user_id = update.effective_user.id

    if text == '💀 سنس':
        update.message.reply_text(random.choice(SENS_TEXTS))
    elif text == '🤖 هوش مصنوعی':
        update.message.reply_text("سوالت رو از لوفی بپرس:", 
                                  reply_markup=ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True))
    elif text == '🔙 بازگشت به منوی اصلی':
        update.message.reply_text("برگشتیم منوی اصلی.", 
                                  reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    else:
        # بررسی عضویت قبل از پاسخ هوش مصنوعی
        if not check_membership(context, user_id):
            update.message.reply_text("❌ شما عضو کانال یا گروه نیستید!")
            return
            
        msg = update.message.reply_text("⏳ لوفی در حال فکر کردن...")
        
        try:
            # ارسال درخواست به مدل 1.5 فلش (سهمیه رایگان بالا)
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=text
            )
            
            if response and response.text:
                msg.edit_text(response.text)
            else:
                msg.edit_text("⚠️ متأسفانه پاسخی تولید نشد. دوباره سوال کنید.")

        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                msg.edit_text("⚠️ ظرفیت پاسخگویی در این دقیقه پر شده. ۳۰ ثانیه صبر کنید و دوباره بپرسید.")
            elif "403" in error_str:
                msg.edit_text("🚫 خطای دسترسی! توکن شما مسدود شده یا محدودیت منطقه دارید.")
            else:
                print(f"Detailed Error: {e}")
                msg.edit_text("❌ خطای غیرمنتظره رخ داد. لطفاً دوباره تلاش کنید.")

def main():
    # اجرای سرور سلامت در ترد جداگانه
    threading.Thread(target=run_health_server, daemon=True).start()
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    print("--- ربات لوفی شاپ با مدل 1.5 Flash آنلاین شد ---")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
