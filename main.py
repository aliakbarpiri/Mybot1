import requests
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.error import BadRequest

# ================== تنظیمات اصلی (حتماً پر شود) ==================
TOKEN = "8719139878:AAELuQ2HpjFPOXjKIsPNkoCwD_-BMZE05-0" 
CHANNEL_ID = "@Luffy_sh_op"       # آیدی کانال شما
GROUP_ID = -1003499181273          # آیدی عددی گروه (با -100 شروع شود)
GROUP_LINK = "https://t.me/Gap_Luffy_Shop" # لینک واقعی گروه شما
AI_API_URL = "https://shython-apis.liara.run/ai"
# ==========================================================

# لیست سنس‌ها
SENS_TEXTS = [
    "𝗦𝗘𝗡𝗦𝗜 ⚡🔥\n𝐆𝐞𝐧𝐞𝐫𝐚𝐥: ⚡ 194\n𝐑𝐞𝐝 𝐝𝐨𝐭: 🎯 179\n𝟐𝐱 𝐒𝐜𝐨𝐩𝐞: ⚙️ 190\n𝟒𝐱 𝐒𝐜𝐨𝐩𝐞: ❄️ 178\n𝐒𝐧𝐢𝐩𝐞𝐫 𝐒𝐜𝐨𝐩𝐞: 👁 104\n𝐅𝐫𝐞𝐞 𝐥𝐨𝐨𝐤: 🌀 170\n\n𝘽𝙪𝙩𝙩𝙤𝙣: 🎮 46\n𝘿𝙋𝙄: 🛠 625",
    "🔵 سنس\n\n182\n140\n151\n132\n130\n131\n\n(سایز دکمه تیر : 39)\n\n( ممنون میشم اگه سنس بالا خوب بود برای رفیقت هم بفرستی که اونم بتونه استفاده کنه )❤️"
]

# کیبوردها
main_keyboard = [['🤖 هوش مصنوعی'], ['💀 سنس']]
back_keyboard = [['🔙 بازگشت به منوی اصلی']]

def check_membership(context: CallbackContext, user_id: int) -> bool:
    """بررسی عضویت در کانال و گروه"""
    allowed = ['member', 'administrator', 'creator']
    try:
        # بررسی کانال
        c_status = context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id).status
        # بررسی گروه
        g_status = context.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id).status
        
        return c_status in allowed and g_status in allowed
    except Exception as e:
        print(f"Membership Check Error: {e}")
        return False

def get_join_markup():
    """ایجاد دکمه‌های شیشه‌ای برای جوین اجباری"""
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")],
        [InlineKeyboardButton("👥 عضویت در گروه", url=GROUP_LINK)],
        [InlineKeyboardButton("✅ عضو شدم / بررسی مجدد", callback_data='check_again')]
    ]
    return InlineKeyboardMarkup(keyboard)

def start(update: Update, context: CallbackContext) -> None:
    if not update.effective_user: return
    
    user_id = update.effective_user.id
    if check_membership(context, user_id):
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        update.message.reply_text(
            f"سلام {update.effective_user.first_name} عزیز! خوش آمدی.\nیک گزینه را انتخاب کن:",
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            "⚠️ برای استفاده از ربات، ابتدا باید در **کانال** و **گروه** ما عضو شوید:",
            reply_markup=get_join_markup(),
            parse_mode='Markdown'
        )

def button_callback(update: Update, context: CallbackContext) -> None:
    """مدیریت کلیک روی دکمه عضو شدم"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == 'check_again':
        if check_membership(context, user_id):
            query.answer("✅ تایید شد! منوی اصلی باز شد.")
            query.edit_message_text("عضویت شما تایید شد. خوش آمدید!")
            reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
            context.bot.send_message(chat_id=user_id, text="چه کاری می‌توانم برایت انجام دهم؟", reply_markup=reply_markup)
        else:
            query.answer("❌ هنوز در هر دو مورد عضو نشده‌اید!", show_alert=True)

def handle_message(update: Update, context: CallbackContext) -> None:
    if not update.effective_user or not update.message: return
    
    user_id = update.effective_user.id
    text = update.message.text

    # چک کردن عضویت قبل از هر دستور
    if not check_membership(context, user_id):
        update.message.reply_text("❌ شما هنوز عضو کانال یا گروه نیستید!", reply_markup=get_join_markup())
        return

    if text == '🔙 بازگشت به منوی اصلی':
        update.message.reply_text("به منوی اصلی برگشتیم.", reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))

    elif text == '💀 سنس':
        update.message.reply_text(random.choice(SENS_TEXTS), reply_markup=ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True))

    elif text == '🤖 هوش مصنوعی':
        update.message.reply_text("هر سوالی داری بپرس! (برای خروج دکمه بازگشت را بزن)", reply_markup=ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True))

    elif text:
        # پردازش هوش مصنوعی برای متن‌های متفرقه
        processing_msg = update.message.reply_text("⏳ در حال پردازش...")
        try:
            res = requests.get(AI_API_URL, params={'prompt': text}, timeout=25).json()
            ai_reply = res.get("data", "متأسفانه پاسخی دریافت نشد.")
            processing_msg.edit_text(ai_reply)
        except Exception:
            processing_msg.edit_text("❌ خطایی در اتصال به هوش مصنوعی رخ داد.")

def main():
    # ساخت اوبجکت Updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # ثبت هندلرها
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("--- ربات با موفقیت فعال شد و آماده استفاده است ---")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
