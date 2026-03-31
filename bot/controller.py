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
            [
                InlineKeyboardButton("ᴄʟσηє ꜱєꜱꜱɪση", callback_data="add_session"),
                InlineKeyboardButton("ꜱᴛᴧʀᴛ ꜱᴄʀᴧᴘᴘєʀ", callback_data="start_scraper")
            ],
            [
                InlineKeyboardButton("ꜱᴛσᴘ ꜱᴄʀᴧᴘᴘєʀ", callback_data="stop_scraper"),
                InlineKeyboardButton("ʀєꜱᴜʟᴛꜱ", callback_data="status")
            ],
            [InlineKeyboardButton("ᴄσᴅєʀ", url="https://t.me/scriptyxx")],
        ])

    async def send_welcome(self, chat_id: int):
        """Send welcome message with image + styled caption"""

        video_url = "https://files.catbox.moe/p9toct.mp4"

        welcome_text = (
            "<blockquote><b>✦ ˹ ɪɴꜰɪɴɪᴛʏ ꭙ ᴡᴧɪꜰᴜ ꜱᴄʀᴧᴘᴘєʀ ˼\n\n"
            " ʜєʟʟσ, — ᴡєʟᴄσϻє ᴛσ ᴘʀєϻɪᴜϻ ꜱᴧᴧꜱ ᴄσηᴛʀσʟ\n"
            " ⊚ ᴧᴜᴛσϻᴧᴛєᴅ ᴡᴧɪꜰᴜ ᴄσʟʟєᴄᴛɪση ꜱʏꜱᴛєϻ\n"
            " ✦ ꜰєᴧᴛᴜʀєꜱ:\n"
            " • ɪηꜱᴛᴧηᴛ ꜱᴄʀᴧᴘᴘєʀ ᴅєᴘʟσʏϻєηᴛ\n"
            " • ɪηʟɪηє ʙσᴛ ᴅᴧᴛᴧ ꜰєᴛᴄʜɪηɢ\n"
            " • ꜱϻᴧʀᴛ ᴅᴜᴘʟɪᴄᴧᴛє ꜰɪʟᴛєʀ\n"
            " • ʟɪᴠє ꜱᴛᴧᴛꜱ + ʟσɢꜱ\n\n"
            " ➻ ᴛᴧᴘ ʙєʟσω ᴛσ ꜱᴛᴧʀᴛ ʏσᴜʀ ɪηꜱᴛᴧηᴄє ✦</b></blockquote>"
        )

        await self.app.send_video(
            chat_id=chat_id,
            video=video_url,
            caption=welcome_text,
            parse_mode="markdown",
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
