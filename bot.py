import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import datetime

# دریافت توکن‌ها از محیط
openai.api_key = os.getenv("OPENAI_API_KEY")
TG_TOKEN = os.getenv("TG_TOKEN")

# ذخیره‌ی وضعیت جلسه برای هر کاربر
sessions = {}

# شروع جلسه مشاوره
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sessions[user_id] = {
        "start_time": datetime.datetime.now(),
        "stage": "warmup",
        "history": []
    }
    await update.message.reply_text("سلام، خوش اومدی به جلسه مشاوره CBT. لطفاً بگو امروز چه احساسی داری؟")

# دریافت پیام و پاسخ درمانی از GPT
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in sessions:
        await update.message.reply_text("لطفاً با دستور /start جلسه را آغاز کن.")
        return

    sessions[user_id]["history"].append({"role": "user", "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "تو یک روان‌درمانگر حرفه‌ای با رویکرد CBT هستی. با حفظ مرزهای درمانی، جلسه را هدایت کن."},
            *sessions[user_id]["history"]
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    sessions[user_id]["history"].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

# ساخت اپلیکیشن تلگرام
app = ApplicationBuilder().token(TG_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
