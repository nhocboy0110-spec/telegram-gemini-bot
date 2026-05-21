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
Bạn là AI chuyên viết content Facebook về sách.

Khi người dùng nhập tên sách:

Hãy viết:
- văn phong cảm xúc
- truyền cảm hứng
- có chiều sâu
- câu mở đầu thu hút
- kiểu viral Facebook
- ngắn gọn nhưng cuốn hút

Format:

📚 Tên sách

✨ Một câu hook mở đầu cực cuốn.

✍️ Viết 1 đoạn ngắn:
- giàu cảm xúc
- có chất văn thơ
- tạo động lực
- dễ đăng Facebook

🎯 Chủ đề chính:
• bullet ngắn

🔥 Một quote thật hay.

📌 Kết bằng câu truyền cảm hứng.

Thêm hashtag cuối bài:
#sach
#reviewsach
#book
#phattrienbanthan

Quy tắc:
- xuống dòng đẹp
- không quá dài
- giọng văn hiện đại
- giống content creator Facebook
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

        return image_links.get("thumbnail")

    except Exception as e:

        print("BOOK COVER ERROR:", e)

        return None

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📚 Xin chào!

Dùng lệnh:

/sach tên sách

Ví dụ:
/sach Đắc Nhân Tâm
/sach Nhà Giả Kim
/sach Atomic Habits
"""

    await update.message.reply_text(text)

# =========================================
# SACH COMMAND
# =========================================

async def sach(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "❌ Vui lòng nhập tên sách.\n\nVí dụ:\n/sach Atomic Habits"
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
            temperature=0.9,
            max_tokens=900
        )

        reply = completion.choices[0].message.content

        # image
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

    print("🤖 Bot sách đang chạy...")

    app.run_polling()

# =========================================

if __name__ == "__main__":
    main()
