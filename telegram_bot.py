import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ============================================================
# ⚙️ YAHAN APNI DETAILS BHARO — SIRF 3 JAGAH
# ============================================================

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
PASSWORD = os.environ.get("PASSWORD")
# ============================================================

logging.basicConfig(level=logging.INFO)

# /start command — user bot open kare toh yeh message aayega
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔐 Channel Join Karo", callback_data="join")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Welcome!*\n\n"
        "🔑 Private Channel join karne ke liye\n"
        "Neeche button dabao aur *Password* enter karo.",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

# Button click hone par password maango
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "join":
        await query.message.reply_text(
            "🔑 *Apna Password Type Karo:*",
            parse_mode="Markdown"
        )

# User jo bhi type kare — password check karo
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if user_input == PASSWORD:
        try:
            # Single-use invite link banao
            invite = await context.bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
                name=f"User-{update.effective_user.id}"
            )
            keyboard = [[InlineKeyboardButton("✅ Channel Join Karo", url=invite.invite_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "✅ *Sahi Password!*\n\n"
                "👇 Neeche button dabao aur channel join karo.\n"
                "⚠️ Yeh link sirf *1 baar* kaam karega.",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        except Exception as e:
            await update.message.reply_text(
                "❌ Link generate nahi hua.\n"
                "Bot ko channel ka Admin banao aur dobara try karo."
            )
            logging.error(f"Invite link error: {e}")
    else:
        keyboard = [[InlineKeyboardButton("🔄 Dobara Try Karo", callback_data="join")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ *Wrong Password!*\n\nDobara try karo.",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_password))
    print("✅ Bot chal raha hai...")
    app.run_polling()

if __name__ == "__main__":
    main()