from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from config import Config
from database import Database, User
from utils import BotLogger
import logging

logger = logging.getLogger(__name__)

class ControllerBot:
    """Main controller bot for managing scraper instances"""

    def __init__(self):
        self.app = Client(
            "controller_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )

        self.db = Database()
        self.bot_logger = BotLogger()

    async def start(self):
        """Start the controller bot"""
        await self.app.start()
        self.bot_logger.set_client(self.app)
        logger.info("Controller bot started")

    async def stop(self):
        """Stop the controller bot"""
        await self.app.stop()
        logger.info("Controller bot stopped")

    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """Generate main menu keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Session", callback_data="add_session")],
            [InlineKeyboardButton("🚀 Start Scraper", callback_data="start_scraper")],
            [InlineKeyboardButton("🛑 Stop Scraper", callback_data="stop_scraper")],
            [InlineKeyboardButton("📊 Status", callback_data="status")],
            [InlineKeyboardButton("❌ Stop System", callback_data="stop_system")]
        ])

    async def send_welcome(self, chat_id: int):
        """Send welcome message with menu"""
        welcome_text = (
            "🤖 **Waifu Scraper SaaS Controller**\n\n"
            "Welcome to the automated waifu scraping platform!\n\n"
            "**Features:**\n"
            "• Deploy your own scraper instance\n"
            "• Auto-collect waifu images from inline bots\n"
            "• Smart deduplication system\n"
            "• Real-time stats and logging\n\n"
            "Get started by adding your session!"
        )

        await self.app.send_message(
            chat_id=chat_id,
            text=welcome_text,
            reply_markup=self.get_main_menu()
        )

    async def handle_add_session(self, callback_query: CallbackQuery):
        """Handle add session request"""
        await callback_query.message.edit_text(
            "📝 **Add Your Session String**\n\n"
            "Please send your Pyrogram string session.\n\n"
            "To generate a session string:\n"
            "1. Run `python generate_session.py`\n"
            "2. Login with your Telegram account\n"
            "3. Copy the session string\n\n"
            "Send it here with:\n"
            "`/addsession <your_string_session>`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("« Back", callback_data="main_menu")]
            ])
        )

    async def handle_status(self, callback_query: CallbackQuery):
        """Handle status request"""
        user_id = callback_query.from_user.id
        user_data = User.find_by_id(user_id)

        if not user_data:
            await callback_query.answer("❌ No session added yet!", show_alert=True)
            return

        has_session = bool(user_data.get("string_session"))
        scraper_active = user_data.get("scraper_active", False)
        stats = user_data.get("stats", {})

        status_text = (
            f"📊 **Your Status**\n\n"
            f"**Session:** {'✅ Added' if has_session else '❌ Not added'}\n"
            f"**Scraper:** {'🟢 Running' if scraper_active else '🔴 Stopped'}\n\n"
            f"**Statistics:**\n"
            f"• Fetched: {stats.get('fetched', 0)}\n"
            f"• Saved: {stats.get('saved', 0)}\n"
            f"• Skipped: {stats.get('skipped', 0)}\n"
        )

        if stats.get("last_error"):
            status_text += f"\n**Last Error:** {stats['last_error']}"

        await callback_query.message.edit_text(
            status_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="status")],
                [InlineKeyboardButton("« Back", callback_data="main_menu")]
            ])
        )

    async def handle_main_menu(self, callback_query: CallbackQuery):
        """Return to main menu"""
        await callback_query.message.edit_text(
            "🤖 **Waifu Scraper Controller**\n\nChoose an option:",
            reply_markup=self.get_main_menu()
        )

    def run(self):
        """Run the controller bot"""
        self.app.run()
