import logging
import random
import requests
import os
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

logging.basicConfig(level=logging.INFO)

symbols = {
    "XAUUSD": "طلا",
    "EURUSD": "یورو",
    "USDJPY": "ین",
    "GBPUSD": "پوند",
    "BTCUSD": "بیت‌کوین",
    "ETHUSD": "اتریوم"
}

psychology_tips = [
    "صبور باشید؛ بازار همیشه فرصت جدید می‌دهد.",
    "با ضررها کنار بیایید؛ مدیریت احساسات کلید موفقیت است.",
    "هرگز با پولی که توان از دست دادنش را ندارید ترید نکنید.",
    "پلن معاملاتی داشته باشید و به آن وفادار بمانید."
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    if member.status in ['member', 'administrator', 'creator']:
        await update.message.reply_text(
            f"سلام {update.effective_user.first_name} 🌟\nبه ربات مدیریت سرمایه خوش آمدید.",
        )
        buttons = [
            [InlineKeyboardButton(symbols[sym], callback_data=sym)] for sym in symbols
        ]
        await update.message.reply_text(
            "لطفاً یکی از جفت ارزها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.message.reply_text(
            f"لطفاً ابتدا در کانال زیر عضو شوید:\n{CHANNEL_ID}"
        )

async def pair_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pair = query.data
    context.user_data['pair'] = pair
    await query.edit_message_text(f"جفت ارز انتخاب شده: {symbols[pair]}")
    await query.message.reply_text("لطفاً مقدار سرمایه خود را به دلار وارد کنید:")

async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("مقدار باید عددی باشد.")
        return

    balance = float(text)
    context.user_data['balance'] = balance
    lot_size = round(balance * 0.01 / 1000, 2)  # ریسک ۱٪ و SL 100 پیپ
    pair = context.user_data.get('pair')

    await update.message.reply_text(
        f"💰 سرمایه شما: {balance}$\n"
        f"📊 لات سایز پیشنهادی: {lot_size} لات برای {symbols.get(pair, '')}"
    )

    price = get_price(pair)
    await update.message.reply_text(
        f"📈 قیمت لحظه‌ای {symbols.get(pair, pair)}:\n{price}"
    )

    await update.message.reply_text(f"🧠 نکته روانشناسی:\n{random.choice(psychology_tips)}")

def get_price(symbol):
    try:
        url = f"https://api.forexrateapi.com/latest?base={symbol[:3]}&symbols={symbol[3:]}"
        res = requests.get(url)
        data = res.json()
        return data["rates"][symbol[3:]]
    except:
        return "در دسترس نیست"

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pair_selection))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_balance))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
