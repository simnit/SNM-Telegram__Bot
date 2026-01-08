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

# Railway Variables (recommended)
# ADMIN_USERNAME = your Telegram username WITHOUT @ (example: snmassets)
# ADMIN_CHAT_ID = your numeric Telegram ID (example: 123456789) - used for admin notifications
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

# Optional hard fallback (ONLY if you want):
# If Railway variable ADMIN_USERNAME is empty, this will be used.
# Put your username here WITHOUT @ or keep it empty.
ADMIN_USERNAME_FALLBACK = ""  # e.g. "snmassets"

ADMIN_USERNAME_EFFECTIVE = (ADMIN_USERNAME or ADMIN_USERNAME_FALLBACK).strip()


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
    "3) Pick a plan (1 Month / 1 Year).\n"
    "4) Copy the code and message admin.\n\n"
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

# Plans (same for all products)
PLANS = {
    "year": {"label": "1 Year Access - Price $11", "plan_name": "1 Year"},
    "month": {"label": "1 Month Access - Price $5", "plan_name": "1 Month"},
}

# Your requested suffix
CODE_SUFFIX = "85689098726"


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


def build_plan_menu(product_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(PLANS["year"]["label"], callback_data=f"plan:{product_key}:year")],
        [InlineKeyboardButton(PLANS["month"]["label"], callback_data=f"plan:{product_key}:month")],
        [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
    ])


def make_deal_code(product_key: str, plan_key: str) -> str:
    # vt_dis_*product*_*plan*85689098726
    return f"vt_dis_{product_key}_{plan_key}{CODE_SUFFIX}"


def build_after_code_keyboard(product_key: str, plan_key: str) -> InlineKeyboardMarkup:
    """
    Always show something:
    - If username exists: URL button to message admin
    - Else: a callback button that reveals admin contact info
    """
    if ADMIN_USERNAME_EFFECTIVE:
        safe_key = quote(f"{product_key}_{plan_key}")
        url = f"https://t.me/{ADMIN_USERNAME_EFFECTIVE}?start=buy_{safe_key}"
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Message Admin", url=url)],
            [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
        ])

    # Username not set -> still show a button that gives contact info
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Get Admin Contact", callback_data=f"contact:{product_key}:{plan_key}")],
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

    # Product selected -> show plan buttons
    if data.startswith("prod:"):
        product_key = data.split("prod:", 1)[1]
        product = PRODUCTS.get(product_key)

        if not product:
            await query.edit_message_text("Product not found. Try again.", reply_markup=build_products_menu())
            return

        text = (
            f"🛍️ *{product['name']}*\n\n"
            f"{product['rules']}\n"
            "Now choose your plan 👇"
        )
        await query.edit_message_text(
            text,
            reply_markup=build_plan_menu(product_key),
            parse_mode="Markdown",
        )
        return

    # Plan selected -> generate code + notify admin + show message-admin button
    if data.startswith("plan:"):
        _, product_key, plan_key = data.split(":", 2)
        product = PRODUCTS.get(product_key)
        plan = PLANS.get(plan_key)

        if not product or not plan:
            await query.edit_message_text("Plan/product not found. Try again.", reply_markup=build_products_menu())
            return

        user = query.from_user
        username = f"@{user.username}" if user.username else "(no username)"
        deal_code = make_deal_code(product_key, plan_key)

        # Notify admin (monitor orders)
        if ADMIN_CHAT_ID:
            admin_msg = (
                "🧾 *New Order Selected*\n\n"
                f"👤 Buyer: {user.full_name}\n"
                f"🔗 Username: {username}\n"
                f"🆔 User ID: `{user.id}`\n\n"
                f"🛒 Product: *{product['name']}*\n"
                f"📦 Plan: *{plan['plan_name']}* ({plan['label']})\n"
                f"🔑 Code: `{deal_code}`\n"
            )
            try:
                await context.bot.send_message(
                    chat_id=int(ADMIN_CHAT_ID),
                    text=admin_msg,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print("Admin notify error:", e)

        user_text = (
            "✅ Done!\n\n"
            f"Your deal code is:\n`{deal_code}`\n\n"
            "📩 Please message the admin and send this code to complete the deal."
        )

        await query.edit_message_text(
            user_text,
            reply_markup=build_after_code_keyboard(product_key, plan_key),
            parse_mode="Markdown",
        )
        return

    # If username is missing, this button will show the contact details
    if data.startswith("contact:"):
        _, product_key, plan_key = data.split(":", 2)
        product = PRODUCTS.get(product_key)
        plan = PLANS.get(plan_key)
        deal_code = make_deal_code(product_key, plan_key)

        # This is what user sees when admin username wasn't configured
        contact_text = (
            "📩 Admin Contact\n\n"
            "Admin username is not configured in the bot right now.\n"
            "Please contact the admin manually and send this code:\n\n"
            f"`{deal_code}`\n\n"
            "Then the admin will finish your deal ✅"
        )

        await query.edit_message_text(
            contact_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")]
            ]),
            parse_mode="Markdown",
        )
        return


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type /start to open the menu 🛍️")


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
