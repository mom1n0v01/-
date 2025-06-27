import hashlib
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === НАСТРОЙКИ ===
TOKEN = "7849789306:AAHE4tGKrSCOcziCQLZOIkM_TTVcAPmSMaQ"
PASSWORD = "1234"
OWNER_ID = 123456789  # ← Замени на свой Telegram user ID

# === СОСТОЯНИЯ ===
authorized_users = set()
password_attempts = {}

# === КНОПКИ ===
main_keyboard = ReplyKeyboardMarkup(
    [["/start", "Ввести хэш"]],
    resize_keyboard=True
)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Этот бот не для тебя.")
        return

    await update.message.reply_text(
        "Привет! Введи пароль, чтобы получить доступ.",
        reply_markup=main_keyboard
    )

# === Обработка текстов ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    if user_id not in authorized_users:
        password_attempts[user_id] = password_attempts.get(user_id, 0) + 1
        if text == PASSWORD:
            authorized_users.add(user_id)
            await update.message.reply_text("✅ Пароль принят. Отправь хэш.")
        else:
            if password_attempts[user_id] >= 3:
                await update.message.reply_text("❌ Слишком много попыток. Доступ закрыт.")
            else:
                await update.message.reply_text("❗ Неверный пароль. Попробуй ещё.")
        return

    # Расчёт X из хэша
    hash_bytes = hashlib.sha256(text.encode()).digest()
    num = int.from_bytes(hash_bytes, 'big')
    position = (num % 10) + 1

    await update.message.reply_text(f"🎯 X = {position}")

    # Лог в консоль
    print(f"[{user_id}] Хэш: {text} → X = {position}")

# === Запуск ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("✅ Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
