import google.generativeai as genai

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""
    Bạn là trợ lý Vạn Trí AI tiếng Việt thân thiện.
    Trả lời ngắn gọn, tự nhiên và hữu ích.
    """
)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào 👋\nTôi là Vạn Trí AI Bot."
    )

# CHAT
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    try:

        response = model.generate_content(
            user_text
        )

        reply = response.text

        # Telegram limit
        if len(reply) > 4000:
            reply = reply[:4000]

        await update.message.reply_text(reply)

    except Exception as e:

        error_text = str(e)

        if "429" in error_text:
            await update.message.reply_text(
                "Gemini đang quá tải hoặc hết quota free."
            )
        else:
            await update.message.reply_text(
                f"Lỗi:\n{error_text}"
            )

# MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)

print("Bot đang chạy...")

app.run_polling()