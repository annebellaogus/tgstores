# ============================================
# TELEGRAM SESSION STORE BOT
# @AnneBellaSessionBot
# ============================================
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import *
from database import *
from handlers.user import *
from handlers.admin import *

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot Client
app = Client(
    "session_store_bot",
    api_id=int(os.getenv("API_ID", "2040")),
    api_hash=os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627"),
    bot_token=BOT_TOKEN,
    workers=100
)

# ============== USER COMMANDS ==============

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await start_handler(client, message)

@app.on_message(filters.command("prices"))
async def prices_cmd(client, message):
    class FakeCallback:
        def __init__(self, msg):
            self.message = msg
        async def answer(self, *args, **kwargs):
            pass
    await show_prices(FakeCallback(message))

@app.on_message(filters.command("orders"))
async def orders_cmd(client, message):
    class FakeCallback:
        def __init__(self, msg):
            self.message = msg
        async def answer(self, *args, **kwargs):
            pass
    await show_my_orders(client, FakeCallback(message))

@app.on_message(filters.command("support"))
async def support_cmd(client, message):
    await message.reply_text(
        f"📞 <b>Support</b>\n\nContact: {SUPPORT_USERNAME}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")]
        ])
    )

# ============== ADMIN COMMANDS ==============

@app.on_message(filters.command("admin"))
async def admin_cmd(client, message):
    await admin_panel(client, message)

@app.on_message(filters.command("addstock"))
async def addstock_cmd(client, message):
    await add_stock_cmd(client, message)

@app.on_message(filters.command("stats"))
async def stats_cmd(client, message):
    if not is_admin(message.from_user.id):
        return
    update_stats()
    stats = get_stats()
    total_users = get_user_count()
    total_orders = len(get_all_orders())
    delivered = len([o for o in get_all_orders() if o['status'] == 'delivered'])
    revenue = sum([o['amount'] for o in get_all_orders() if o['status'] == 'delivered'])
    
    await message.reply_text(f"""
📊 <b>Bot Statistics</b>

👥 <b>Users:</b> {total_users}
📦 <b>Orders:</b> {total_orders}
✅ <b>Delivered:</b> {delivered}
💰 <b>Revenue:</b> ${revenue:.2f}
""")

@app.on_message(filters.command("ban"))
async def ban_cmd(client, message):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.split()[1])
        ban_user(user_id)
        await message.reply_text(f"🚫 <b>User {user_id} banned!</b>")
    except:
        await message.reply_text("❌ Usage: /ban user_id")

@app.on_message(filters.command("unban"))
async def unban_cmd(client, message):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.split()[1])
        unban_user(user_id)
        await message.reply_text(f"✅ <b>User {user_id} unbanned!</b>")
    except:
        await message.reply_text("❌ Usage: /unban user_id")

# ============== CALLBACK HANDLERS ==============

@app.on_callback_query()
async def callback_query_handler(client, callback):
    data = callback.data
    
    if data.startswith("admin_") or data.startswith("verify_") or data.startswith("deliver_") or data == "back_to_admin":
        await admin_callback_handler(client, callback)
    else:
        await callback_handler(client, callback)

# ============== BROADCAST ==============

broadcast_state = {}

@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(client, message):
    if not is_admin(message.from_user.id):
        return
    
    broadcast_state[message.from_user.id] = True
    await message.reply_text(
        "📢 <b>Broadcast Mode</b>\n\n"
        "Send the message you want to broadcast to ALL users.\n"
        "Send /cancel to cancel."
    )

@app.on_message(filters.private & filters.text)
async def broadcast_handler(client, message):
    user_id = message.from_user.id
    
    if user_id in broadcast_state and broadcast_state[user_id]:
        if message.text == "/cancel":
            broadcast_state[user_id] = False
            await message.reply_text("❌ Broadcast cancelled.")
            return
        
        broadcast_state[user_id] = False
        
        users = get_all_users()
        sent = 0
        failed = 0
        
        status_msg = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
        
        for user in users:
            try:
                await client.send_message(user['user_id'], message.text)
                sent += 1
            except:
                failed += 1
        
        await status_msg.edit_text(
            f"✅ <b>Broadcast Complete!</b>\n\n"
            f"📤 <b>Sent:</b> {sent}\n"
            f"❌ <b>Failed:</b> {failed}\n"
            f"📊 <b>Total:</b> {len(users)}"
        )

# ============== RUN ==============

if __name__ == "__main__":
    logger.info("Starting Session Store Bot...")
    app.run()
