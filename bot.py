# ==============================
# IMPORT
# ==============================

import asyncio
import sqlite3

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes,
)

from config import TOKEN, ADMIN_IDS

# ==============================
# DATABASE
# ==============================

db = sqlite3.connect("guard.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS groups(
chat_id INTEGER PRIMARY KEY,
active INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS hashes(
chat_id INTEGER,
hash TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
chat_id INTEGER,
user_id INTEGER,
duplicates INTEGER,
warns INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS allowed_groups(
chat_id INTEGER PRIMARY KEY
)
""")

db.commit()

# ==============================
# HASH CACHE
# ==============================

hash_cache = set()

cur.execute("SELECT hash FROM hashes")
for row in cur.fetchall():
    hash_cache.add(row[0])

# ==============================
# AUTO DELETE
# ==============================

async def delete_later(msg, sec=30):

    await asyncio.sleep(sec)

    try:
        await msg.delete()
    except:
        pass

# ==============================
# GROUP ACTIVE CHECK
# ==============================

def group_active(chat_id):

    cur.execute(
        "SELECT active FROM groups WHERE chat_id=?",
        (chat_id,)
    )

    r = cur.fetchone()

    if r:
        return r[0] == 1

    return False

# ==============================
# SETUP
# ==============================

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    chat = update.effective_chat.id

    cur.execute(
        "INSERT OR REPLACE INTO groups VALUES (?,1)",
        (chat,)
    )

    cur.execute(
        "INSERT OR IGNORE INTO allowed_groups VALUES (?)",
        (chat,)
    )

    db.commit()

    msg = await update.message.reply_text("✅ Guard Bot Activated")

    asyncio.create_task(delete_later(msg))

# ==============================
# ENDUP
# ==============================

async def endup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    chat = update.effective_chat.id

    cur.execute(
        "DELETE FROM groups WHERE chat_id=?",
        (chat,)
    )

    cur.execute(
        "DELETE FROM hashes WHERE chat_id=?",
        (chat,)
    )

    db.commit()

    msg = await update.message.reply_text("❌ Guard Bot Disabled")

    asyncio.create_task(delete_later(msg))

# ==============================
# HELP
# ==============================

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 Duplicate Guard Bot

/setup - Activate bot
/endup - Disable bot
/help - Show commands

Protection:
• Duplicate media auto delete
• 10 duplicates → warn
• 3 warns → mute
"""

    msg = await update.message.reply_text(text)

    asyncio.create_task(delete_later(msg,60))

# ==============================
# MEDIA HANDLER
# ==============================

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat.id
    user = update.effective_user.id
    name = update.effective_user.full_name

    # security check
    cur.execute(
        "SELECT chat_id FROM allowed_groups WHERE chat_id=?",
        (chat,)
    )

    if not cur.fetchone():
        await context.bot.leave_chat(chat)
        return

    if not group_active(chat):
        return

    message = update.message

# ==============================
# DETECT MEDIA
# ==============================

    if message.photo:
        h = message.photo[-1].file_unique_id

    elif message.video:
        h = message.video.file_unique_id

    elif message.document:
        h = message.document.file_unique_id

    else:
        return

# ==============================
# DUPLICATE CHECK
# ==============================

    if h in hash_cache:

        await message.delete()

        dupmsg = await context.bot.send_message(
            chat,
            f"⚠️ [{name}](tg://user?id={user}) duplicate media removed",
            parse_mode="Markdown"
        )

        asyncio.create_task(delete_later(dupmsg))

        cur.execute(
            "INSERT OR IGNORE INTO users VALUES (?,?,0,0)",
            (chat, user)
        )

        cur.execute(
            """
            UPDATE users
            SET duplicates = duplicates + 1
            WHERE chat_id=? AND user_id=?
            """,
            (chat, user)
        )

        db.commit()

        cur.execute(
            "SELECT duplicates,warns FROM users WHERE chat_id=? AND user_id=?",
            (chat, user)
        )

        dup, warn = cur.fetchone()

        if dup >= 10:

            warn += 1

            cur.execute(
                """
                UPDATE users
                SET duplicates=0, warns=?
                WHERE chat_id=? AND user_id=?
                """,
                (warn, chat, user)
            )

            db.commit()

            await context.bot.send_message(
                chat,
                f"⚠️ [{name}](tg://user?id={user}) warned ({warn}/3)",
                parse_mode="Markdown"
            )

        return

# ==============================
# SAVE HASH
# ==============================

    hash_cache.add(h)

    cur.execute(
        "INSERT INTO hashes VALUES (?,?)",
        (chat, h)
    )

    db.commit()

# ==============================
# BOT START
# ==============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("setup", setup))
app.add_handler(CommandHandler("endup", endup))
app.add_handler(CommandHandler("help", help_cmd))

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Document.ALL,
        media
    )
)

print("Guard Bot Running...")

app.run_polling()
