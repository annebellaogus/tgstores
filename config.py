# ============================================
# TELEGRAM SESSION STORE BOT - CONFIGURATION
# ============================================
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@AnneBellaSessionBot")
BOT_NAME = os.getenv("BOT_NAME", "AnneBella Session Store")

# Admin Settings
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

# Payment Settings
PAYMENT_METHODS = {
    "crypto": {
        "enabled": True,
        "name": "Crypto (BTC/USDT)",
        "wallet": os.getenv("CRYPTO_WALLET", "YOUR_CRYPTO_WALLET")
    },
    "upi": {
        "enabled": True,
        "name": "UPI",
        "id": os.getenv("UPI_ID", "yourupi@upi")
    }
}

# Prices (in USD for crypto, INR for UPI)
PRICES = {
    "fresh_session": {"usd": 2, "inr": 150},
    "aged_6m": {"usd": 5, "inr": 400},
    "aged_1y": {"usd": 8, "inr": 650},
    "aged_2y": {"usd": 15, "inr": 1200},
    "premium_aged": {"usd": 25, "inr": 2000}
}

# Stock Categories
CATEGORIES = {
    "fresh_session": "🆕 Fresh Sessions",
    "aged_6m": "📅 6+ Months Aged",
    "aged_1y": "📅 1+ Year Aged",
    "aged_2y": "📅 2+ Years Aged",
    "premium_aged": "👑 Premium Aged (3Y+)"
}

# Channel Settings (for force join)
FORCE_JOIN_CHANNEL = os.getenv("FORCE_JOIN_CHANNEL", "@AnneBellaUpdates")
FORCE_JOIN_GROUP = os.getenv("FORCE_JOIN_GROUP", "@AnneBellaSupport")

# Support
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@AnneBellaSupport")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///session_store.db")

# Messages
WELCOME_MESSAGE = f"""
✨ <b>Welcome to {BOT_NAME}</b> ✨

🔹 <b>What we offer:</b>
   • Fresh Telegram Sessions
   • Aged Accounts (6M | 1Y | 2Y | 3Y+)
   • Session + JSON Format
   • Instant Auto-Delivery
   • 24/7 Support

💰 <b>Starting from just $2 / ₹150</b>

🛡️ <b>All accounts are:</b>
   ✓ Phone Verified (PVA)
   ✓ Real SIM Numbers
   ✓ Ready to Use
   ✓ Replacement Guarantee

👇 <b>Use the buttons below to browse our store!</b>
"""

ABOUT_MESSAGE = f"""
📌 <b>About {BOT_NAME}</b>

🤖 <b>Bot Features:</b>
   • Instant Auto-Delivery
   • Multiple Payment Options
   • Stock Updates in Real-time
   • Secure & Private
   • Replacement Policy

💼 <b>Account Types:</b>
   • Fresh Sessions - New accounts
   • Aged 6M+ - 6+ months old
   • Aged 1Y+ - 1+ year old
   • Aged 2Y+ - 2+ years old
   • Premium 3Y+ - Elite accounts

📞 <b>Support:</b> {SUPPORT_USERNAME}
"""

REPLACEMENT_POLICY = """
🔄 <b>Replacement Policy</b>

✅ <b>Eligible for replacement if:</b>
   • Account banned within 24 hours
   • Wrong credentials provided
   • Account already in use

❌ <b>Not eligible if:</b>
   • Used for spam/illegal activities
   • Modified account settings
   • Reported by user after 24 hours

📌 <b>Contact support with your Order ID for replacement.</b>
"""
