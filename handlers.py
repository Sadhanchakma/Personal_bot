from telegram import ReplyKeyboardMarkup
from database import load_data, save_data
from config import ADMIN_ID

users = load_data()
user_steps = {}

services = {
    "Netflix": {
        "1 Month (Share) Price 400": 400,
        "1 Month (Private) Price 1500": 1500
    },
    "Spotify": {
        "1 Month (Share) Price 230": 230,
        "1 Month (Private)Price 700": 700
    }
}

# ---------------- MAIN MENU ----------------
async def main_menu(update):
    keyboard = [
        ["💰 Balance", "➕ Add Balance"],
        ["🛒 Buy Service"]
    ]
    await update.message.reply_text(
        "🏠 Main Menu",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------------- START ----------------
async def start(update, context):
    user = update.message.from_user
    user_id = str(user.id)
    username = user.username

    if username:
        username_text = username.replace("_", "\\_")
        username_text = f"@{username_text}"
    else:
        username_text = "No Username"

    if user_id not in users:
        users[user_id] = {"balance": 0}
        save_data(users)

    keyboard = [
        ["💰 Balance", "➕ Add Balance"],
        ["🛒 Buy Service"]
    ]

    await update.message.reply_text(
        f"""👋 স্বাগতম! {username_text}

👤 Username: {username_text}
🆔 User ID: `{user_id}`

💰 Balance: {users[user_id]['balance']} Tk
━━━━━━━━━━━━━━━━━━━━
✨ আপনার অ্যাকাউন্ট সফলভাবে লোড হয়েছে  
━━━━━━━━━━━━━━━━━━━━""",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )

# ---------------- HANDLE TEXT ----------------
async def handle(update, context):
    user_id = update.message.from_user.id
    text = update.message.text
    uid = str(user_id)

    # 🔙 BACK
    if text == "🔙 Back":
        user_steps.pop(user_id, None)
        return await main_menu(update)

    # ❌ CANCEL
    if text == "❌ Cancel":
        user_steps.pop(user_id, None)
        return await update.message.reply_text("❌ Process cancelled")

    # 💰 BALANCE
    if text == "💰 Balance":
        user_steps.pop(user_id, None)
        bal = users[uid]["balance"]
        return await update.message.reply_text(f"💰 Balance: {bal} Tk")

    # ➕ ADD BALANCE
    if text == "➕ Add Balance":
        user_steps[user_id] = {"step": "method"}

        keyboard = [
            ["bKash", "Nagad"],
            ["Rocket", "Binance"],
            ["🔙 Back", "❌ Cancel"]
        ]

        return await update.message.reply_text(
            "💳 পেমেন্ট মেথড নির্বাচন করুন:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # 🛒 BUY SERVICE
    if text == "🛒 Buy Service":
        user_steps[user_id] = {"step": "service"}

        keyboard = [[s] for s in services.keys()]
        keyboard.append(["🔙 Back"])

        return await update.message.reply_text(
            "🛒 Service select korun:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # ---------------- STEP SYSTEM ----------------
    if user_id in user_steps:
        step = user_steps[user_id]["step"]

        # METHOD
        if step == "method":
            numbers = {
                "bKash": "01537310053",
                "Nagad": "01533833020",
                "Rocket": "01537310053",
                "Binance": "989885533"
            }

            if text not in numbers:
                return await update.message.reply_text("❌ Valid method select korun")

            user_steps[user_id]["method"] = text
            user_steps[user_id]["step"] = "amount"

            return await update.message.reply_text(
                f"""📲 {text} Number:

`{numbers[text]}`

💰 Minimum Amount : 100 Tk
👉আপনার টাকার পরিমাণ দেন :""",
                parse_mode="Markdown"
            )

        # AMOUNT
        elif step == "amount":
            if not text.isdigit():
                return await update.message.reply_text(
                    "❌ অনুগ্রহ করে শুধুমাত্র সংখ্যায় পরিমাণ লিখুন"
                )

            amount = int(text)

            if amount < 100:
                return await update.message.reply_text(
                    "❌ সর্বনিম্ন ১০০ টাকা যোগ করতে হবে"
                )

            user_steps[user_id]["amount"] = amount
            user_steps[user_id]["step"] = "trx"

            return await update.message.reply_text(
                """🔑 অনুগ্রহ করে আপনার ট্রানজ্যাকশন আইডি প্রদান করুন:

━━━━━━━━━━━━━━━━━━━━
⚠️ সঠিক TRX ID দিন, ভুল হলে ব্যালেন্স যোগ করা হবে না
━━━━━━━━━━━━━━━━━━━━"""
            )

        # TRX
        elif step == "trx":
            user_steps[user_id]["trx"] = text
            user_steps[user_id]["step"] = "ss"

            return await update.message.reply_text(
                """📸 অনুগ্রহ করে আপনার পেমেন্টের স্ক্রিনশটটি পাঠান:

━━━━━━━━━━━━━━━━━━━━
⚠️ নিশ্চিত করুন স্ক্রিনশটটি পরিষ্কার ও সম্পূর্ণ দেখা যায়
━━━━━━━━━━━━━━━━━━━━"""
            )

        # SERVICE SELECT
        elif step == "service":
            if text not in services:
                return await update.message.reply_text("❌ Valid service select korun")

            user_steps[user_id]["service"] = text
            user_steps[user_id]["step"] = "plan"

            plans = services[text]

            keyboard = [[p] for p in plans.keys()]
            keyboard.append(["🔙 Back"])

            return await update.message.reply_text(
                f"📦 {text} plan select korun:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )

        # PLAN SELECT
        elif step == "plan":
            service = user_steps[user_id]["service"]
            plans = services[service]

            if text not in plans:
                return await update.message.reply_text("❌ Valid plan select korun")

            price = plans[text]

            if users[uid]["balance"] >= price:
                users[uid]["balance"] -= price
                save_data(users)

                user_steps.pop(user_id)

                return await update.message.reply_text(
                    f"""✅ Order Successful!

📦 Service: {service}
💎 Plan: {text}
💰 Price: {price} Tk
⬆️  Forward it our admin @Sadhan_chakma"""
                )
            else:
                return await update.message.reply_text("❌ Balance nai!")

# ---------------- HANDLE PHOTO ----------------
async def handle_photo(update, context):
    user_id = update.message.from_user.id

    if user_id in user_steps and user_steps[user_id]["step"] == "ss":
        data = user_steps[user_id]

        caption = f"""
💰 New Balance Request

👤 User ID: {user_id}
💳 Method: {data['method']}
💵 Amount: {data['amount']} Tk
🔑 TRX ID: {data['trx']}
"""

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption
        )

        await update.message.reply_text(
            """✅ আপনার রিকুয়েস্ট সফলভাবে অ্যাডমিনের কাছে পাঠানো হয়েছে।

🔍 যাচাই শেষে আপনার ব্যালেন্সে টাকা যোগ করা হবে।

━━━━━━━━━━━━━━━━━━━━
⏳ অনুগ্রহ করে কিছুক্ষণ অপেক্ষা করুন
━━━━━━━━━━━━━━━━━━━━

❗ কোনো ধরনের সমস্যা হলে অনুগ্রহ করে অ্যাডমিনের সাথে যোগাযোগ করুন:
👤 @Sadhan_chakma"""
        )

        user_steps.pop(user_id)

# ---------------- ADMIN ADD BALANCE ----------------
async def addbalance(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = context.args[0]
        amount = int(context.args[1])

        if user_id not in users:
            users[user_id] = {"balance": 0}

        users[user_id]["balance"] += amount
        save_data(users)

        await update.message.reply_text("✅ Balance Added!")

        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ {amount} Tk added to your balance!"
        )

    except:
        await update.message.reply_text("❌ Use: /addbalance user_id amount")
