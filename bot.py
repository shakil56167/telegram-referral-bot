"""
Telegram Bot: Referral System + Admin Auto-Posting
====================================================
Hosted on Render.com
"""

import logging
import sqlite3
import os
from contextlib import contextmanager

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =============================================
# 🔧 CONFIGURATION - ENVIRONMENT VARIABLES
# =============================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
# Get from @BotFather

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))
# Your Telegram numeric user ID (@userinfobot)

BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBotUsername")
# Bot username WITHOUT @ (e.g., MyReferralBot)

MAIN_GROUP_INVITE_LINK = os.getenv("MAIN_GROUP_INVITE_LINK", "https://t.me/+XXXXXXXXXXXXXXXX")
# Private group invite link

TARGET_GROUP_CHAT_ID = int(os.getenv("TARGET_GROUP_CHAT_ID", "-1001234567890"))
# Group chat ID where bot posts videos (AUTO-DETECTED from group message)

# =============================================
# SETTINGS
# =============================================

REQUIRED_INVITES = int(os.getenv("REQUIRED_INVITES", "4"))
DB_PATH = os.getenv("DB_PATH", "/opt/render/project/src/referral_bot.db")

POST_CAPTION = (
    "🔥 BANGLADESHI NEW COLLECTION UNLOCKED 🔐\n\n"
    "এক্ষুনি জয়েন করে ফুল কালেকশন এক্সেস নিন! "
    "Full & lots of more collection available. 👑\n\n"
    "নিচের বাটনে ক্লিক করে শেয়ার করে দিন অথবা অ্যাক্সেস নিন!"
)

# =============================================
# LOGGING
# =============================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# =============================================
# DATABASE HELPERS
# =============================================

def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                referrer_id INTEGER DEFAULT NULL,
                username   TEXT,
                full_name  TEXT,
                joined_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_referrer ON users (referrer_id)
        """)
    logger.info("Database ready at %s", DB_PATH)


@contextmanager
def get_db():
    """Yield a committed-or-rolled-back SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def upsert_user(user_id, referrer_id, username, full_name):
    """Insert new user or ignore if exists. Returns True if new."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (user_id, referrer_id, username, full_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (user_id, referrer_id, username, full_name),
        )
        return cursor.rowcount == 1


def get_invite_count(user_id):
    """Return how many users used this user's referral link."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM users WHERE referrer_id = ?",
            (user_id,),
        ).fetchone()
        return row["cnt"] if row else 0


# =============================================
# KEYBOARD BUILDERS
# =============================================

def build_main_keyboard(user_id):
    """Keyboard for /start message."""
    referral_url = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    share_text = (
        "🔥 এই বটে জয়েন করুন এবং এক্সক্লুসিভ কন্টেন্ট আনলক করুন! "
        "আমার রেফারেল লিংক ব্যবহার করুন:"
    )
    share_url = f"https://t.me/share/url?url={referral_url}&text={share_text}"

    keyboard = [
        [
            InlineKeyboardButton("🔓 Get Access", callback_data=f"access:{user_id}"),
            InlineKeyboardButton("⭕ SHARE NOW", url=share_url),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_post_keyboard():
    """Keyboard attached to auto-posted videos."""
    bot_url = f"https://t.me/{BOT_USERNAME}"
    share_text = "🔥 এক্সক্লুসিভ কন্টেন্ট আনলক করুন! এই বটে জয়েন করুন:"
    share_url = f"https://t.me/share/url?url={bot_url}&text={share_text}"

    keyboard = [
        [
            InlineKeyboardButton("🔓 Get Access", url=bot_url),
            InlineKeyboardButton("⭕ SHARE NOW", url=share_url),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =============================================
# HANDLERS
# =============================================

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with optional referral tracking."""
    user = update.effective_user
    args = context.args
    
    # 🆕 AUTO-DETECT CHAT ID IF CALLED FROM GROUP
    global TARGET_GROUP_CHAT_ID
    if update.effective_chat.type == "supergroup":
        chat_id = update.effective_chat.id
        if chat_id != TARGET_GROUP_CHAT_ID:
            TARGET_GROUP_CHAT_ID = chat_id
            logger.info("✅ Auto-detected group Chat ID: %s", chat_id)

    referrer_id = None
    if args:
        try:
            candidate = int(args[0])
            if candidate != user.id:
                referrer_id = candidate
        except ValueError:
            pass

    is_new = upsert_user(
        user_id=user.id,
        referrer_id=referrer_id,
        username=user.username,
        full_name=user.full_name,
    )

    if is_new and referrer_id:
        logger.info("New user %s referred by %s", user.id, referrer_id)

    invite_count = get_invite_count(user.id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start={user.id}"

    text = (
        f"👋 স্বাগতম, {user.first_name}!\n\n"
        f"📊 আপনার ইনভাইট: *{invite_count} / {REQUIRED_INVITES}*\n\n"
        f"🔗 আপনার রেফারেল লিংক:\n`{referral_link}`\n\n"
        f"নিচের বাটন থেকে শেয়ার করুন অথবা অ্যাক্সেস নিন।"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=build_main_keyboard(user.id),
    )


async def access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Get Access' button click."""
    query = update.callback_query
    await query.answer()

    try:
        target_user_id = int(query.data.split(":")[1])
    except (IndexError, ValueError):
        await query.answer("Invalid request.", show_alert=True)
        return

    if query.from_user.id != target_user_id:
        await query.answer("❌ এই বাটনটি আপনার জন্য নয়।", show_alert=True)
        return

    invite_count = get_invite_count(target_user_id)

    if invite_count >= REQUIRED_INVITES:
        await query.message.reply_text(
            f"✅ অভিনন্দন! আপনার {invite_count}টি সফল রেফারেল আছে।\n\n"
            f"🎉 গ্রুপে জয়েন করুন:\n{MAIN_GROUP_INVITE_LINK}",
            disable_web_page_preview=True,
        )
    else:
        remaining = REQUIRED_INVITES - invite_count
        await query.message.reply_text(
            f"⛔ আপনার এখনো *{remaining}টি* ইনভাইট দরকার।\n\n"
            f"📊 বর্তমান ইনভাইট: *{invite_count} / {REQUIRED_INVITES}*\n\n"
            f"আরো বন্ধুকে আপনার রেফারেল লিংক শেয়ার করুন!",
            parse_mode="Markdown",
        )


async def post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /post command - ADMIN ONLY video posting."""
    user = update.effective_user

    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return

    message = update.message
    video = None

    if message.video:
        video = message.video
    elif message.reply_to_message and message.reply_to_message.video:
        video = message.reply_to_message.video
    else:
        await message.reply_text(
            "📹 একটি ভিডিও ফাইল পাঠান এবং ক্যাপশনে /post লিখুন,\n"
            "অথবা একটি ভিডিও মেসেজ রিপ্লাই করে /post লিখুন।"
        )
        return

    try:
        await context.bot.send_video(
            chat_id=TARGET_GROUP_CHAT_ID,
            video=video.file_id,
            caption=POST_CAPTION,
            reply_markup=build_post_keyboard(),
        )
        await message.reply_text("✅ ভিডিও সফলভাবে গ্রুপে পোস্ট হয়েছে!")
        logger.info("Admin %s posted video to group %s", user.id, TARGET_GROUP_CHAT_ID)
    except Exception as exc:
        logger.error("Failed to post video: %s", exc)
        await message.reply_text(
            f"❌ পোস্ট করতে ব্যর্থ হয়েছে।\n\nError: {exc}\n\n"
            "নিশ্চিত করুন বটটি গ্রুপের অ্যাডমিন।"
        )


async def get_chat_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chatid command - Show current chat ID."""
    if update.effective_user.id != ADMIN_USER_ID:
        return

    current_chat_id = update.effective_chat.id
    
    text = (
        f"📊 *Chat Information*\n\n"
        f"💬 Current Chat ID: `{current_chat_id}`\n"
        f"📍 Saved TARGET_GROUP_CHAT_ID: `{TARGET_GROUP_CHAT_ID}`\n\n"
        f"ℹ️ এটি আপনার `TARGET_GROUP_CHAT_ID` এর জন্য:\n"
        f"`TARGET_GROUP_CHAT_ID={current_chat_id}`"
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - ADMIN ONLY."""
    if update.effective_user.id != ADMIN_USER_ID:
        return

    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        top = conn.execute(
            """
            SELECT referrer_id, COUNT(*) AS cnt
            FROM users
            WHERE referrer_id IS NOT NULL
            GROUP BY referrer_id
            ORDER BY cnt DESC
            LIMIT 10
            """
        ).fetchall()

    lines = [f"📊 *Bot Statistics*\n\nTotal users: *{total}*\n\n🏆 *Top Referrers:*"]
    for i, row in enumerate(top, 1):
        lines.append(f"{i}. User `{row['referrer_id']}` — {row['cnt']} referrals")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# =============================================
# ENTRY POINT
# =============================================

def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("post", post_handler))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("chatid", get_chat_id_handler))
    app.add_handler(CallbackQueryHandler(access_callback, pattern=r"^access:\d+$"))
    app.add_handler(
        MessageHandler(filters.VIDEO & filters.User(ADMIN_USER_ID), post_handler)
    )

    logger.info("Bot is running on Render.com...")
    logger.info("✅ Auto-detect Chat ID enabled!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
