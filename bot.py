import os
import requests

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
    raise ValueError("❌ Thiếu BOT_TOKEN")

if not GROQ_API_KEY:
    raise ValueError("❌ Thiếu GROQ_API_KEY")

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

Nhiệm vụ:
- viết bài ngắn gọn nhưng cực cuốn
- văn phong cảm xúc
- truyền cảm hứng
- giống fanpage triệu view
- dễ đăng Facebook

Khi user nhập tên sách:

Viết theo format:

📚 Tên sách

✨ Một câu mở đầu cực cuốn hút.

✍️ Viết đoạn giới thiệu:
- ngắn gọn
- giàu cảm xúc
- có chiều sâu
- văn phong nhẹ nhàng
- tạo động lực

🎯 Chủ đề nổi bật:
• bullet ngắn

🔥 Một quote cực hay.

📌 Kết bằng câu truyền cảm hứng.

Thêm hashtag:
#sach
#reviewsach
#book
#phattrienbanthan

Quy tắc:
- xuống dòng đẹp
- không quá dài
- không viết khô khan
- ngôn ngữ hiện đại
"""

# =========================================
# GET REAL BOOK COVER
# =========================================

def get_book_cover(book_name):

    try:

        url = (
            "https://www.googleapis.com/books/v1/volumes"
            f"?q=intitle:{book_name}"
        )

        response = requests.get(url)

        data = response.json()

        items = data.get("items")

        if not items:
            return None

        book = items[0]

        volume_info = book.get("volumeInfo", {})

        image_links = volume_info.get("imageLinks", {})

        image_url = (
            image_links.get("extraLarge")
            or image_links.get("large")
            or image_links.get("medium")
            or image_links.get("thumbnail")
        )

        return image_url

    except Exception as e:

        print("BOOK COVER ERROR:", e)

        return None

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📚 Bot review sách AI

Dùng:

/sach tên sách

Ví dụ:
/sach Đắc Nhân Tâm
/sach Nhà Giả Kim
/sach Atomic Habits
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

    # lấy tên sách
    book_name = " ".join(context.args)

    try:

        # typing...
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        # AI generate
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

        # lấy ảnh bìa thật
        image_url = get_book_cover(book_name)

        # gửi ảnh + caption
        if image_url:

            await update.message.reply_photo(
                photo=image_url,
                caption=reply[:1024]
            )

            # nếu caption dài
            if len(reply) > 1024:

                await update.message.reply_text(
                    reply[1024:]
                )

        else:

            # fallback text
            MAX_LENGTH = 4000

            for i in range(0, len(reply), MAX_LENGTH):

                chunk = reply[i:i + MAX_LENGTH]

                await update.message.reply_text(chunk)

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

    # commands
    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("sach", sach)
    )

    print("🤖 Bot sách AI đang chạy...")

    app.run_polling()

# =========================================

if __name__ == "__main__":
    main()
