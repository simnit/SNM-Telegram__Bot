import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

WELCOME = (
    "👋 Welcome to the SNM Asstes Bot This Bot will help you to complete your purchases\n\n"
    "Use these commands:\n"
    "/start - open menu\n"
    "/help - how to use me\n"
    "/about - what I do\n"
)

HELP = (
    "📌 How to use this bot:\n"
    "1) Tap a command or type it.\n"
    "2) Send a message if you’re not sure.\n\n"
    "Commands:\n"
    "/start\n"
    "/help\n"
    "/about\n"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I’m a Telegram bot running on Railway 🤖🚄")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"You said: {text}\n\nType /help to see options.")

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN missing in Railway Variables")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))

    # catches normal messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()

if __name__ == "__main__":
    main()

