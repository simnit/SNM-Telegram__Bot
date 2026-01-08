import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # e.g. "123456789"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")  # e.g. "snmassets" (no @)

# --- Product catalog (edit this) ---
PRODUCTS = {
    "netflix_premium": {
        "name": "Netflix Premium",
        "desc": "Netflix Premium (Ultra HD, multiple screens)",
        "rules": (
            "📌 Rules & Guidelines (Netflix Premium)\n"
            "• Do not change email/password.\n"
            "• Do not share outside your device(s).\n"
            "• No profile lock / no extra members.\n"
            "• If login issues happen, message support with screenshot.\n"
        ),
    },
    "canva_pro": {
        "name": "Canva Pro",
        "desc": "Canva Pro access (premium features)",
        "rules": (
            "📌 Rules & Guidelines (Canva Pro)\n"
            "• Do not remove admin/owner.\n"
            "• Do not change account email.\n"
            "• Use responsibly (no policy violations).\n"
            "• If anything breaks, contact support immediately.\n"
        ),
    },
    "capcut_pro": {
        "name": "CapCut Pro",
        "desc": "CapCut Pro (4K export, premium templates, no watermark)",
        "rules": (
            "📌 Rules & Guidelines (CapCut Pro)\n"
            "• Do not change email/password.\n"
            "• Don’t log in on too many devices.\n"
            "• Avoid suspicious VPN switching.\n"
            "• For issues, message support with your error screenshot.\n"
        ),
    },
}

WELCOME = (
    "Welcome to your one-stop account store 🚀\n"
    "Browse trusted premium accounts, instant delivery, and smooth deals.\n"
    "Tap the menu, explore the offers, and upgrade your digital life today 🔐✨\n\n"
    "Choose a product from the menu below 👇"
)


def build_products_menu() -> InlineKeyboardMarkup:
    keyboard = []
    for key, item in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(item["name"], callback_data=f"prod:{key}")])
    keyboard.append([InlineKeyboardButton("📌 Help", callback_data="help")])
    return InlineKeyboardMarkup(keyboard)


def build_confirm_menu(product_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm:{product_key}")],
        [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
    ])


def build_contact_admin_button(product_key: str) -> InlineKeyboardMarkup:
    # Opens your personal chat (best UX). Needs ADMIN_USERNAME.
    if ADMIN_USERNAME:
        url = f"https://t.me/{ADMIN_USERNAME}?start=buy_{product_key}"
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Message Admin to Buy", url=url)],
            [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
        ])

    # Fallback: no username set
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=build_products_menu())


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu":
        await query.edit_message_text(WELCOME, reply_markup=build_products_menu())
        return

    if data == "help":
        help_text = (
            "📌 How to use:\n"
            "1) Pick a product.\n"
            "2) Read rules.\n"
            "3) Tap Confirm.\n"
            "4) You’ll get a button to message the admin.\n"
        )
        await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Back to Products", callback_data="menu")]
        ]))
        return

    # Product selected
    if data.startswith("prod:"):
        product_key = data.split("prod:")[1]
        product = PRODUCTS.get(product_key)

        if not product:
            await query.edit_message_text("Product not found. Try again.", reply_markup=build_products_menu())
            return

        # store selection
        context.user_data["selected_product"] = product_key

        text = (
            f"🛍️ *{product['name']}*\n"
            f"{product['rules']}\n"
            "If you agree to the rules, tap *Confirm* ✅"
        )
        await query.edit_message_text(
            text,
            reply_markup=build_confirm_menu(product_key),
            parse_mode="Markdown",
        )
        return

    # Confirm clicked
    if data.startswith("confirm:"):
        product_key = data.split("confirm:")[1]
        product = PRODUCTS.get(product_key)

        if not product:
            await query.edit_message_text("Product not found. Try again.", reply_markup=build_products_menu())
            return

        user = query.from_user
        username = f"@{user.username}" if user.username else "(no username)"
        user_link = f"tg://user?id={user.id}"

        # 1) Notify admin (YOU)
        if ADMIN_CHAT_ID:
            admin_msg = (
                "🧾 *New Purchase Request*\n\n"
                f"👤 Buyer: {user.full_name}\n"
                f"🔗 Username: {username}\n"
                f"🆔 User ID: `{user.id}`\n"
                f"📎 Link: {user_link}\n\n"
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
                # If admin chat_id wrong or bot can't message admin
                print("Admin notify error:", e)

        # 2) Show user a button to message you (personal chat)
        user_text = (
            "✅ Confirmed!\n\n"
            "Tap the button below to message the admin to complete your order.\n"
            "Your selected product will be sent to the admin automatically 💬"
        )

        await query.edit_message_text(
            user_text,
            reply_markup=build_contact_admin_button(product_key),
        )
        return


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN missing in Railway Variables")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))

    app.run_polling()


if __name__ == "__main__":
    main()
