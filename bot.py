import os
import requests

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
Bạn là AI chuyên viết nội dung Facebook về sách.

Khi người dùng nhập tên sách:

Hãy viết theo format:

📚 Tên sách

✍️ Giới thiệu ngắn:
- 2 đến 4 câu
- dễ đọc
- súc tích
- truyền cảm hứng

🎯 Chủ đề chính:
- bullet ngắn gọn

🔥 Một câu quote nổi bật.

#sach #book #phattrienbanthan

Quy tắc:
- Viết tiếng Việt
- Ngắn gọn
- Xuống dòng đẹp
- Hợp đăng Facebook
- Không quá dài
"""

# =========================================
# GET BOOK COVER
# =========================================

def get_book_cover(book_name):

    try:

        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}"

        response = requests.get(url)

        data = response.json()

        items = data.get("items")

        if not items:
            return None

        volume_info = items[0]["volumeInfo"]

        image_links = volume_info.get("imageLinks")

        if not image_links:
            return None

        thumbnail = image_links.get("thumbnail")

        return thumbnail

    except Exception as e:

        print("BOOK COVER ERROR:", e)

        return None

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📚 Xin chào!

Hãy gửi tên một quyển sách.

Ví dụ:
- Đắc Nhân Tâm
- Nhà Giả Kim
- Atomic Habits
"""

    await update.message.reply_text(text)

# =========================================
# CHAT
# =========================================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    if not user_text:
        return

    try:

        # typing...
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        # AI response
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=700
        )

        reply = completion.choices[0].message.content

        # get image
        image_url = get_book_cover(user_text)

        # send image + caption
        if image_url:

            await update.message.reply_photo(
                photo=image_url,
                caption=reply[:1024]
            )

        else:

            await update.message.reply_text(reply)

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
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("🤖 Bot sách đang chạy...")

    app.run_polling()

# =========================================

if __name__ == "__main__":
    main()
