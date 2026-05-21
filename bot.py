import os
import google.generativeai as genai

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)

# =========================
# ENV
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("Thiếu BOT_TOKEN")

if not GEMINI_API_KEY:
    raise ValueError("Thiếu GEMINI_API_KEY")

# =========================
# GEMINI SETUP
# =========================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="""
Bạn là Vạn Trí AI - trợ lý AI tiếng Việt.

Quy tắc:
- Trả lời tự nhiên
- Ngắn gọn dễ hiểu
- Hữu ích
- Không spam emoji
- Ưu tiên tiếng Việt
"""
)

# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 Xin chào!

Tôi là Vạn Trí AI Bot.
Bạn hãy gửi tin nhắn để bắt đầu chat.
"""

    await update.message.reply_text(text)

# =========================
# CHAT FUNCTION
# =========================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    try:

        # typing...
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        response = model.generate_content(user_text)

        reply = response.text

        if not reply:
            reply = "Tôi chưa có câu trả lời."

        # Telegram giới hạn 4096 ký tự
        MAX_LENGTH = 4000

        for i in range(0, len(reply), MAX_LENGTH):
            chunk = reply[i:i + MAX_LENGTH]

            await update.message.reply_text(chunk)

    except Exception as e:

        error_text = str(e)

        print("ERROR:", error_text)

        # quota
        if "429" in error_text:
            await update.message.reply_text(
                "⚠️ Gemini đang quá tải hoặc bạn đã hết quota free."
            )

        # model lỗi
        elif "not found" in error_text.lower():

            await update.message.reply_text(
                "⚠️ Model Gemini không tồn tại.\n"
                "Hãy kiểm tra model_name."
            )

        # api key
        elif "api key" in error_text.lower():

            await update.message.reply_text(
                "⚠️ API KEY Gemini không hợp lệ."
            )

        else:

            await update.message.reply_text(
                f"⚠️ Có lỗi xảy ra:\n{error_text}"
            )

# =========================
# MAIN
# =========================

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

# =========================

if __name__ == "__main__":
    main()
