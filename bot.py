import os

from groq import Groq

from telegram import Update
from telegram.constants import ChatAction

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# ======================
# ENV
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ======================
# GROQ
# ======================

client = Groq(
    api_key=GROQ_API_KEY
)

MODEL_NAME = "llama-3.3-70b-versatile"

# ======================
# START
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Xin chào!\nTôi là AI Bot."
    )

# ======================
# CHAT
# ======================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    try:

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là trợ lý AI tiếng Việt thân thiện."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )

        reply = completion.choices[0].message.content

        if not reply:
            reply = "Không có phản hồi."

        MAX_LENGTH = 4000

        for i in range(0, len(reply), MAX_LENGTH):

            chunk = reply[i:i + MAX_LENGTH]

            await update.message.reply_text(chunk)

    except Exception as e:

        print(e)

        await update.message.reply_text(
            f"⚠️ Lỗi:\n{str(e)}"
        )

# ======================
# MAIN
# ======================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("🤖 Bot đang chạy...")

    app.run_polling()

# ======================

if __name__ == "__main__":
    main()
