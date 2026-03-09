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
# ADD ADMIN
# ==============================

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        msg = await update.message.reply_text("Usage: /addadmin USER_ID")
        asyncio.create_task(delete_later(msg))
        return

    uid = int(context.args[0])

    if uid not in ADMIN_IDS:
        ADMIN_IDS.append(uid)

        msg = await update.message.reply_text(f"✅ Admin added: {uid}")
    else:
        msg = await update.message.reply_text("Already admin")

    asyncio.create_task(delete_later(msg))


# ==============================
# REMOVE ADMIN
# ==============================

async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        msg = await update.message.reply_text("Usage: /removeadmin USER_ID")
        asyncio.create_task(delete_later(msg))
        return

    uid = int(context.args[0])

    if uid in ADMIN_IDS:
        ADMIN_IDS.remove(uid)

        msg = await update.message.reply_text(f"❌ Admin removed: {uid}")
    else:
        msg = await update.message.reply_text("User not admin")

    asyncio.create_task(delete_later(msg))


# ==============================
# DATABASE
# ==============================

db = sqlite3.connect("guard.db")
cur = db.cursor()

# groups table
cur.execute("""
CREATE TABLE IF NOT EXISTS groups(
chat_id INTEGER PRIMARY KEY,
active INTEGER
)
""")

# ==============================
# ALLOWED GROUPS (BOT SECURITY)
# ==============================

cur.execute("""
CREATE TABLE IF NOT EXISTS allowed_groups(
chat_id INTEGER PRIMARY KEY
)
""")

db.commit()

# media hashes
cur.execute("""
CREATE TABLE IF NOT EXISTS hashes(
chat_id INTEGER,
hash TEXT
)
""")

db.commit()

# ==============================
# USERS TABLE (WARN + DUPLICATE)
# ==============================

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
chat_id INTEGER,
user_id INTEGER,
duplicates INTEGER,
warns INTEGER
)
""")

db.commit()

# ==============================
# AUTO DELETE MESSAGE
# ==============================

async def delete_later(msg, sec=30):

    await asyncio.sleep(sec)

    try:
        await msg.delete()
    except:
        pass


# ==============================
# CHECK GROUP ACTIVE
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
# SETUP COMMAND
# ==============================

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    chat = update.effective_chat.id

    cur.execute(
        "INSERT OR REPLACE INTO groups VALUES (?,1)",
        (chat,)
    )

    # add group to allowed list
    cur.execute(
    "INSERT OR IGNORE INTO allowed_groups VALUES (?)",
    (chat,)
    )

    db.commit()

    msg = await update.message.reply_text(
        "✅ Guard Bot Activated"
    )

    asyncio.create_task(delete_later(msg))


# ==============================
# ENDUP COMMAND
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

    msg = await update.message.reply_text(
        "❌ Guard Bot Disabled"
    )

    asyncio.create_task(delete_later(msg))


# ==============================
# STATS COMMAND
# ==============================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    chat = update.effective_chat.id

    cur.execute(
        "SELECT COUNT(*) FROM hashes WHERE chat_id=?",
        (chat,)
    )

    media = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE chat_id=? AND warns>0",
        (chat,)
    )

    warned = cur.fetchone()[0]

    msg = await update.message.reply_text(
        f"""
📊 Guard Stats

Stored Media: {media}
Warned Users: {warned}
"""
    )

    asyncio.create_task(delete_later(msg))

# ==============================
# HELP COMMAND
# ==============================

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 Duplicate Guard Bot Help

📌 Setup
/setup - Activate bot in group [Admin only]
/endup - Disable bot [Admin only]

📊 Stats
/stats - Show guard statistics [Admin only]

🧹 Moderation
/purge <number> - Delete last messages 
/clearall - Clear messages

⚠️ Warn Control
/removewarn - Remove warn (reply user)

👑 Admin Control
/addadmin <user_id> - Add admin
/removeadmin <user_id> - Remove admin

🛡 Protection
• Duplicate media auto delete
• 10 duplicates → warn
• 3 warns → mute 1 hour
• Admin cannot be muted
"""

    msg = await update.message.reply_text(text)

    asyncio.create_task(delete_later(msg, 60))

# ==============================
# CLEAR ALL MESSAGES
# ==============================

async def clearall(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    chat = update.effective_chat.id

    msg = await update.message.reply_text("🧹 Clearing messages...")

    # delete last 100 messages
    for i in range(1,101):

        try:
            await context.bot.delete_message(chat, update.message.message_id - i)
        except:
            pass

    asyncio.create_task(delete_later(msg))

# ==============================
# PURGE MESSAGES
# ==============================

async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    chat = update.effective_chat.id

    msg = await update.message.reply_text("🧹 Purging messages...")

    if context.args:
        count = int(context.args[0])

        for i in range(1, count + 1):
            try:
                await context.bot.delete_message(
                    chat,
                    update.message.message_id - i
                )
            except:
                pass

    done = await context.bot.send_message(chat, "✅ Purge complete")

    asyncio.create_task(delete_later(msg, 30))
    asyncio.create_task(delete_later(done, 30))

# ==============================
# MEDIA HANDLER
# ==============================

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat.id

# ==============================
# BOT SECURITY CHECK
# ==============================
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
# DETECT MEDIA TYPE
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

       user = update.effective_user.id
       name = update.effective_user.full_name

      # delete duplicate media
       await message.delete()

       dupmsg = await context.bot.send_message(
        chat,
        f"⚠️ [{name}](tg://user?id={user}) duplicate media removed",
        parse_mode="Markdown"
    )

    asyncio.create_task(delete_later(dupmsg))

    # create user row if not exist
    cur.execute(
        "INSERT OR IGNORE INTO users VALUES (?,?,0,0)",
        (chat, user)
    )

    # increase duplicate counter
    cur.execute(
        """
        UPDATE users
        SET duplicates = duplicates + 1
        WHERE chat_id=? AND user_id=?
        """,
        (chat, user)
    )

    db.commit()

    # get duplicate + warn count
    cur.execute(
        "SELECT duplicates,warns FROM users WHERE chat_id=? AND user_id=?",
        (chat, user)
    )

    dup, warn = cur.fetchone()

    # ==============================
    # WARN SYSTEM
    # ==============================
    if dup >= 10:

        warn = warn + 1

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

        # ==============================
        # MUTE SYSTEM
        # ==============================
        if warn >= 3:

            member = await context.bot.get_chat_member(chat, user)

            # admin mute হবে না
            if member.status in ["administrator", "creator"]:
                return

            await context.bot.restrict_chat_member(
                chat,
                user,
                permissions={}
            )

            await context.bot.send_message(
                chat,
                f"🚫 [{name}](tg://user?id={user}) muted for 1 hour",
                parse_mode="Markdown"
            )

            await asyncio.sleep(3600)

            await context.bot.restrict_chat_member(
                chat,
                user,
                permissions={"can_send_messages": True}
            )

            # reset duplicates and warns
            cur.execute(
                """
                UPDATE users
                SET duplicates=0, warns=0
                WHERE chat_id=? AND user_id=?
                """,
                (chat, user)
            )

            db.commit()

    else:

    # ==============================
    # SAVE NEW HASH
    # ==============================
     hash_cache.add(h)

    cur.execute(
        "INSERT INTO hashes VALUES (?,?)",
        (chat, h)
    )

    db.commit()

# ==============================
# HASH CACHE (FAST MEMORY CHECK)
# ==============================

hash_cache = set()

cur.execute("SELECT hash FROM hashes")

for row in cur.fetchall():
    hash_cache.add(row[0])

# ==============================
# REMOVE WARN COMMAND
# ==============================

async def removewarn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id
    chat = update.effective_chat.id

    cur.execute(
        """
        UPDATE users
        SET warns=0, duplicates=0
        WHERE chat_id=? AND user_id=?
        """,
        (chat, user)
    )

    db.commit()

    msg = await update.message.reply_text(
        "✅ User warns removed"
    )

    asyncio.create_task(delete_later(msg))


# ==============================
# BOT START
# ==============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("setup", setup))
app.add_handler(CommandHandler("endup", endup))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("addadmin", addadmin))
app.add_handler(CommandHandler("removeadmin", removeadmin))
app.add_handler(CommandHandler("clearall", clearall))
app.add_handler(CommandHandler("purge", purge))
app.add_handler(CommandHandler("removewarn", removewarn))
app.add_handler(CommandHandler("help", help_cmd))

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Document.ALL,
        media
    )
)

print("Guard Bot Running...")


app.run_polling()



