import requests
import random
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ================== تنظیمات اصلی ==================
# توکن ربات تلگرام شما
TOKEN = "8719139878:AAELuQ2HpjFPOXjKIsPNkoCwD_-BMZE05-0" 

# آیدی کانال و گروه شما
CHANNEL_ID = "@Luffy_sh_op"
GROUP_ID = -1003499181273
GROUP_LINK = "https://t.me/Gap_Luffy_Shop"

# کلید هوش مصنوعی گوگل (Gemini) که فرستادی
GEMINI_API_KEY = "AIzaSyAkApiuYA1pODx4X6DrHstId-hibZSc92A"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
# =================================================

# لیست سنس‌های کامل شما
SENS_TEXTS = [
    "𝗦𝗘𝗡𝗦𝗜 ⚡🔥\n𝐆𝐞𝐧𝐞𝐫𝐚𝐥: ⚡ 194\n𝐑𝐞𝐝 𝐝𝐨𝐭: 🎯 179\n𝟐𝐱 𝐒𝐜𝐨𝐩𝐞: ⚙️ 190\n𝟒𝐱 𝐒𝐜𝐨𝐩𝐞: ❄️ 178\n𝐒𝐧𝐢𝐩𝐞𝐫 𝐒𝐜𝐨𝐩𝐞: 👁 104\n𝐅𝐫𝐞𝐞 𝐥𝐨𝐨𝐤: 🌀 170\n\n𝘽𝙪𝙩𝙩𝙤𝙣: 🎮 46\n𝘿𝙋𝙄: 🛠 625",
    "🔵 سنس\n\n182\n140\n151\n132\n130\n131\n\n(سایز دکمه تیر : 39)\n\n( ممنون میشم اگه سنس بالا خوب بود برای رفیقت هم بفرستی که اونم بتونه استفاده کنه )❤️"
]

# کیبوردهای اصلی
main_keyboard = [['🤖 هوش مصنوعی'], ['💀 سنس']]
back_keyboard = [['🔙 بازگشت به منوی اصلی']]

def check_membership(context: CallbackContext, user_id: int) -> bool:
    """بررسی عضویت اجباری در کانال و گروه"""
    allowed = ['member', 'administrator', 'creator']
    try:
        c_status = context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id).status
        g_status = context.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id).status
        return c_status in allowed and g_status in allowed
    except:
        return False

def start(update: Update, context: CallbackContext) -> None:
    """دستور شروع ربات"""
    user_id = update.effective_user.id
    if check_membership(context, user_id):
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        update.message.reply_text(
            f"سلام {update.effective_user.first_name} عزیز! خوش آمدی.\nیک گزینه را انتخاب کن:",
            reply_markup=reply_markup
        )
    else:
        # دکمه‌های شیشه‌ای برای عضویت
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")],
            [InlineKeyboardButton("👥 عضویت در گروه", url=GROUP_LINK)]
        ]
        update.message.reply_text(
            "⚠️ برای استفاده از ربات، ابتدا باید در کانال و گروه ما عضو شوید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def handle_message(update: Update, context: CallbackContext) -> None:
    """مدیریت پیام‌های ارسالی"""
    if not update.message: return
    
    text = update.message.text
    user_id = update.effective_user.id

    # چک کردن عضویت قبل از هر پاسخ
    if not check_membership(context, user_id):
        update.message.reply_text("❌ شما هنوز عضو کانال یا گروه نیستید!")
        return

    if text == '💀 سنس':
        update.message.reply_text(random.choice(SENS_TEXTS), reply_markup=ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True))

    elif text == '🤖 هوش مصنوعی':
        update.message.reply_text("هر سوالی داری بپرس! (برای خروج دکمه بازگشت را بزن)", reply_markup=ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True))

    elif text == '🔙 بازگشت به منوی اصلی':
        update.message.reply_text("به منوی اصلی برگشتیم.", reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))

    else:
        # بخش هوش مصنوعی گوگل Gemini
        processing_msg = update.message.reply_text("⏳ در حال پردازش...")
        try:
            payload = {
                "contents": [{"parts": [{"text": text}]}]
            }
            res = requests.post(GEMINI_URL, json=payload, timeout=20)
            res.raise_for_status()
            
            data = res.json()
            # استخراج پاسخ متن از ساختار گوگل
            ai_reply = data['candidates'][0]['content']['parts'][0]['text']
            processing_msg.edit_text(ai_reply)
        except Exception as e:
            print(f"AI Error: {e}")
            processing_msg.edit_text("❌ خطا در اتصال به هوش مصنوعی. لطفا دوباره تلاش کنید یا وضعیت هاست را چک کنید.")

def main():
    # تنظیم ربات
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # هندلرها
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("--- ربات با موفقیت فعال شد ---")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
                     
