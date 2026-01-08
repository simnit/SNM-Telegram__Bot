import os
from urllib.parse import quote

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

# Railway Variables:
# ADMIN_CHAT_ID = your numeric Telegram ID (example: 123456789)
# ADMIN_USERNAME = your username without @ (example: snmassets)
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

WELCOME = (
    "Welcome to your one-stop account store 🚀\n"
    "Browse trusted premium accounts, instant delivery, and smooth deals.\n"
    "Tap the menu, explore the offers, and upgrade your digital life today 🔐✨\n\n"
    "Tap *View Products* to continue 👇"
)

HELP = (
    "📌 How to use this bot:\n"
    "1) View Products.\n"
    "2) Pick a product.\n"
    "3) Read rules.\n"
    "4) Tap Confirm.\n"
    "5) Message admin to finish the deal.\n\n"
    "Commands:\n"
    "/start\n"
    "/help\n"
    "/about\n"
)

ABOUT = (
    "This bot is built to make buying premium accounts easy and secure.\n"
    "✔ Verified accounts\n"
    "✔ Fair pricing\n"
    "✔ Fast support\n"
    "✔ No unnecessary steps\n\n"
    "Everything you need, delivered smart and simple 💡"
)

# IMPORTANT: Use SAFE product IDs as keys (no spaces)
PRODUCTS = {
    "chatgpt_plus": {
        "name": "ChatGPT Plus",
        "desc": "ChatGPT is your AI chatbot for everyday use",
        "rules": (
            "📌 Rules & Guidelines (ChatGPT Plus)\n"
            "• Upload proof screenshot of your payment.\n"
            "• Do not change email/password before paying.\n"
            "• Do not share outside your device(s).\n"
            "• No extra members.\n"
            "• If login issues happen, message support with screenshot.\n"
        ),
    },
    "canva_pro": {
        "name": "Canva Pro",
        "desc": "Canva Pro access (premium features)",
        "rules": (
            "📌 Rules & Guidelines (Canva Pro)\n"
            "• Do not share your email with others.\n"
            "• Do not resell it.\n"
            "• Use responsibly.\n"
            "• For issues, contact support immediately.\n"
        ),
    },
    "capcut_pro": {
        "name": "CapCut Pro",
        "desc": "CapCut Pro (4K export, templates, no watermark)",
        "rules": (
            "📌 Rules & Guidelines (CapCut Pro)\n"
            "• Do not change email/password.\n"
            "• Don’t log in on too many devices.\n"
            "• Avoid suspicious VPN switching.\n"
            "• For issues, send an error screenshot.\n"
        ),
    },
}


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 View Products", callback_data="menu")],
        [InlineKeyboardButton("📌 Help", callback_data="help")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
    ])


def back_to_products_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")]
    ])


def build_products_menu() -> InlineKeyboardMarkup:
    keyboard = []
    for key, item in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(f"🛍 {item['name']}", callback_data=f"prod:{key}")])
    keyboard.append([InlineKeyboardButton("📌 Help", callback_data="help")])
    keyboard.append([InlineKeyboardButton("ℹ️ About", callback_data="about")])
    return InlineKeyboardMarkup(keyboard)


def build_confirm_menu(product_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm:{product_key}")],
        [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
    ])


def build_contact_admin_button(product_key: str) -> InlineKeyboardMarkup:
    # Always show a "Message Admin" button.
    # 1) Best: open username chat
    # 2) Fallback: open admin by numeric user id (tg://user?id=...)

    safe_key = quote(product_key)

    if ADMIN_USERNAME:
        url = f"https://t.me/{ADMIN_USERNAME}?start=buy_{safe_key}"
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Message Admin", url=url)],
            [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
        ])

    # Fallback: open chat by user id (works in Telegram desktop/mobile)
    if ADMIN_CHAT_ID:
        url = f"tg://user?id={ADMIN_CHAT_ID}"
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Message Admin", url=url)],
            [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
        ])

    # If neither is set, at least show back button + warning text elsewhere
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=start_keyboard(), parse_mode="Markdown")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, reply_markup=start_keyboard())


async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ABOUT, reply_markup=start_keyboard())


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        await query.edit_message_text("🛍 Select a product:", reply_markup=build_products_menu())
        return

    if data == "help":
        await query.edit_message_text(HELP, reply_markup=back_to_products_keyboard())
        return

    if data == "about":
        await query.edit_message_text(ABOUT, reply_markup=back_to_products_keyboard())
        return

    if data.startswith("prod:"):
        product_key = data.split("prod:", 1)[1]
        product = PRODUCTS.get(product_key)

        if not product:
            await query.edit_message_text("Product not found. Try again.", reply_markup=build_products_menu())
            return

        text = (
            f"🛍️ *{product['name']}*\n\n"
            f"{product['rules']}\n"
            "If you agree to the rules, tap *Confirm* ✅"
        )

        await query.edit_message_text(
            text,
            reply_markup=build_confirm_menu(product_key),
            parse_mode="Markdown",
        )
        return

    if data.startswith("confirm:"):
        product_key = data.split("confirm:", 1)[1]
        product = PRODUCTS.get(product_key)

        if not product:
            await query.edit_message_text("Product not found. Try again.", reply_markup=build_products_menu())
            return

        user = query.from_user
        username = f"@{user.username}" if user.username else "(no username)"

        # Notify admin (you)
        if ADMIN_CHAT_ID:
            admin_msg = (
                "🧾 *New Purchase Request*\n\n"
                f"👤 Buyer: {user.full_name}\n"
                f"🔗 Username: {username}\n"
                f"🆔 User ID: `{user.id}`\n\n"
                f"🛒 Product: *{product['name']}*\n"
                f"📝 Details: {product['desc']}\n"
            )
            try:
                await context.bot.send_message(
                    chat_id=int(ADMIN_CHAT_ID),
                    text=admin_msg,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print("Admin notify error:", e)

        # User message + admin button
        user_text = (
            "✅ Order Confirmed!\n\n"
            "Your request has been sent to the admin 📩\n"
            "Tap the button below to message the admin and complete your order 💬"
        )

        await query.edit_message_text(
            user_text,
            reply_markup=build_contact_admin_button(product_key),
        )
        return


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type /start to open the menu 🛍️")


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Your Telegram ID is: {user.id}\n"
        f"Username: @{user.username}" if user.username else f"Your Telegram ID is: {user.id}"
    )

async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_CHAT_ID:
        await update.message.reply_text("ADMIN_CHAT_ID is not set in Railway Variables.")
        return
    try:
        await context.bot.send_message(chat_id=int(ADMIN_CHAT_ID), text="✅ Admin notify test message works!")
        await update.message.reply_text("Test sent to admin ✅ Check your Telegram.")
    except Exception as e:
        await update.message.reply_text(f"Failed to message admin: {e}")



def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN missing in Railway Variables")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about_cmd))

    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()


if __name__ == "__main__":
    main()

