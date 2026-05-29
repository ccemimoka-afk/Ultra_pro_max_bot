import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
BACKUP_CHANNEL_ID = int(os.environ.get("BACKUP_CHANNEL_ID"))
PASSWORD = os.environ.get("PASSWORD")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔐 Join Channel", callback_data="join")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Welcome!*\n\n"
        "🔑 To join the Private Channel,\n"
        "click the button below and enter the *Password*.",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "join":
        await query.message.reply_text(
            "🔑 *Please enter your Password:*",
            parse_mode="Markdown"
        )

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    if user_input == PASSWORD:
        try:
            invite = await context.bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
                name=f"User-{update.effective_user.id}"
            )
            keyboard = [[InlineKeyboardButton("✅ Join Channel", url=invite.invite_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "✅ *Correct Password!*\n\n"
                "👇 Click the button below to join the channel.\n"
                "⚠️ This link can only be used *once*.",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        except Exception as e:
            await update.message.reply_text(
                "❌ Could not generate invite link.\n"
                "Please make sure the bot is an Admin in the channel and try again."
            )
            logging.error(f"Invite link error: {e}")
    else:
        keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data="join")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ *Wrong Password!*\n\nPlease try again.",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

async def auto_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.channel_post and update.channel_post.chat.id == CHANNEL_ID:
            await context.bot.forward_message(
                chat_id=BACKUP_CHANNEL_ID,
                from_chat_id=update.channel_post.chat_id,
                message_id=update.channel_post.message_id
            )
            logging.info("Backup successful!")
    except Exception as e:
        logging.error(f"Backup error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_password))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.CHANNEL, auto_backup))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
