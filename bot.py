import os
import requests
import urllib.parse

from groq import Groq

from telegram import Update
from telegram.constants import ChatAction

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler
)

# =========================================
# ENV
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN:
    raise ValueError("Thiếu BOT_TOKEN")

if not GROQ_API_KEY:
    raise ValueError("Thiếu GROQ_API_KEY")

# =========================================
# GROQ
# =========================================

client = Groq(
    api_key=GROQ_API_KEY
)

MODEL_NAME = "llama-3.3-70b-versatile"

# =========================================
# SYSTEM PROMPT
# =========================================

SYSTEM_PROMPT = """
Bạn là content creator Facebook chuyên review sách.

Mục tiêu:
- viết cực cuốn
- tạo cảm xúc
- văn phong truyền cảm hứng
- giống bài viết fanpage triệu view

Format:

📚 Tên sách

✨ Hook mở đầu thật thu hút.

✍️ Viết đoạn ngắn:
- giàu cảm xúc
- văn thơ nhẹ nhàng
- dễ viral Facebook

🎯 Chủ đề:
• bullet ngắn

🔥 Một quote cực hay.

📌 Kết bằng câu khiến người đọc muốn tìm sách ngay.

Hashtag:
#sach
#book
#reviewsach
#phattrienbanthan
"""

# =========================================
# AI IMAGE
# =========================================

def generate_ai_image(book_name):

    prompt = f"""
beautiful cinematic book cover style,
facebook post,
reading book,
warm light,
coffee table,
motivational,
aesthetic,
book: {book_name}
"""

    encoded_prompt = urllib.parse.quote(prompt)

    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    )

    return image_url

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📚 Bot review sách AI

Dùng:

/sach tên sách

Ví dụ:
/sach Atomic Habits
/sach Nhà Giả Kim
"""

    await update.message.reply_text(text)

# =========================================
# /SACH
# =========================================

async def sach(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "❌ Ví dụ:\n/sach Atomic Habits"
        )

        return

    book_name = " ".join(context.args)

    try:

        # typing...
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        # AI content
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": book_name
                }
            ],
            temperature=0.95,
            max_tokens=900
        )

        reply = completion.choices[0].message.content

        # AI image
        image_url = generate_ai_image(book_name)

        # send photo
        await update.message.reply_photo(
            photo=image_url,
            caption=reply[:1024]
        )

        # nếu caption dài
        if len(reply) > 1024:

            await update.message.reply_text(
                reply[1024:]
            )

    except Exception as e:

        print("ERROR:", e)

        await update.message.reply_text(
            f"⚠️ Lỗi:\n{str(e)}"
        )

# =========================================
# MAIN
# =========================================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("sach", sach)
    )

    print("🤖 Bot AI sách đang chạy...")

    app.run_polling()

# =========================================

if __name__ == "__main__":
    main()
