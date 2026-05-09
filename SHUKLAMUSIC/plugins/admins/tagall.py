from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
import asyncio
import random

SPAM_CHATS = []
EMOJI = [
    "🦋", "🌸", "❤️", "💖", "🎉", "🐦", "🍭", "🍀", "🌹", "🔥"
]

async def tag_members(chat_id, members, text, replied=None):
    batch, count = [], 0
    emoji = random.choice(EMOJI)

    for member in members:
        if chat_id not in SPAM_CHATS:
            break
        if member.user.is_deleted or member.user.is_bot:
            continue

        batch.append(f"[{emoji}](tg://user?id={member.user.id})")
        count += 1

        if len(batch) == 5:
            try:
                msg = " ".join(batch)
                if replied:
                    await replied.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                else:
                    await app.send_message(chat_id, f"{text}\n{msg}", parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(2)
                batch.clear()
                emoji = random.choice(EMOJI)
            except FloodWait as e:
                await asyncio.sleep(e.value + 2)

    # बचे हुए members
    if batch and chat_id in SPAM_CHATS:
        msg = " ".join(batch)
        if replied:
            await replied.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        else:
            await app.send_message(chat_id, f"{text}\n{msg}", parse_mode=ParseMode.MARKDOWN)

    return count

@app.on_message(filters.command("tagall", prefixes=["/", "@"]))
async def tagall_handler(_, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("⚠️ केवल admins ही इस command का इस्तेमाल कर सकते हैं!")

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text("⏳ Tagging already running. Use /cancel to stop.")

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text("Usage: `/tagall Hello guys!`")

    members = [m async for m in app.get_chat_members(message.chat.id)]
    SPAM_CHATS.append(message.chat.id)

    text = None
    if not replied:
        text = message.text.split(None, 1)[1]

    tagged = await tag_members(message.chat.id, members, text, replied)

    await app.send_message(message.chat.id, f"✅ Tagging completed!\nTotal tagged: {tagged}")
    try:
        SPAM_CHATS.remove(message.chat.id)
    except:
        pass
