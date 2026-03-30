from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from database import User
from bot.controller import ControllerBot
import logging

logger = logging.getLogger(__name__)

def setup_handlers(controller: ControllerBot):
    """Setup all command and callback handlers"""

    @controller.app.on_message(filters.command("start") & filters.private)
    async def start_command(client, message: Message):
        """Handle /start command"""
        user_id = message.from_user.id
        username = message.from_user.username

        # Create user record if doesn't exist
        User.create_or_update(user_id, username)

        await controller.send_welcome(message.chat.id)

    @controller.app.on_message(filters.command("addsession") & filters.private)
    async def add_session_command(client, message: Message):
        """Handle /addsession command"""
        user_id = message.from_user.id
        username = message.from_user.username

        # Extract session string
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **Invalid format!**\n\n"
                "Usage: `/addsession <your_session_string>`\n\n"
                "Example:\n"
                "`/addsession 1BVtsOJwBu7...`"
            )
            return

        session_string = message.text.split(maxsplit=1)[1].strip()

        # Validate session string (basic check)
        if len(session_string) < 100:
            await message.reply_text(
                "❌ **Invalid session string!**\n\n"
                "The session string seems too short. Please check and try again."
            )
            return

        # Save session
        success = User.create_or_update(user_id, username, session_string)

        if success:
            await message.reply_text(
                "✅ **Session added successfully!**\n\n"
                "You can now start your scraper.\n\n"
                "Use the menu to start scraping.",
                reply_markup=controller.get_main_menu()
            )
            await controller.bot_logger.log(f"✅ Session added for User {user_id} (@{username})")
        else:
            await message.reply_text("❌ Failed to save session. Please try again.")

    @controller.app.on_message(filters.command("menu") & filters.private)
    async def menu_command(client, message: Message):
        """Handle /menu command"""
        await controller.send_welcome(message.chat.id)

    @controller.app.on_message(filters.command("stats") & filters.private)
    async def stats_command(client, message: Message):
        """Handle /stats command"""
        user_id = message.from_user.id
        user_data = User.find_by_id(user_id)

        if not user_data:
            await message.reply_text("❌ No data found. Use /start to begin.")
            return

        stats = user_data.get("stats", {})
        scraper_active = user_data.get("scraper_active", False)

        stats_text = (
            f"📊 **Your Statistics**\n\n"
            f"**Status:** {'🟢 Running' if scraper_active else '🔴 Stopped'}\n\n"
            f"**Totals:**\n"
            f"• Fetched: {stats.get('fetched', 0)}\n"
            f"• Saved: {stats.get('saved', 0)}\n"
            f"• Skipped: {stats.get('skipped', 0)}\n"
        )

        await message.reply_text(stats_text)

    @controller.app.on_callback_query(filters.regex("^main_menu$"))
    async def callback_main_menu(client, callback_query: CallbackQuery):
        """Handle main menu callback"""
        await controller.handle_main_menu(callback_query)
        await callback_query.answer()

    @controller.app.on_callback_query(filters.regex("^add_session$"))
    async def callback_add_session(client, callback_query: CallbackQuery):
        """Handle add session callback"""
        await controller.handle_add_session(callback_query)
        await callback_query.answer()

    @controller.app.on_callback_query(filters.regex("^status$"))
    async def callback_status(client, callback_query: CallbackQuery):
        """Handle status callback"""
        await controller.handle_status(callback_query)
        await callback_query.answer()

    @controller.app.on_callback_query(filters.regex("^start_scraper$"))
    async def callback_start_scraper(client, callback_query: CallbackQuery):
        """Handle start scraper callback"""
        from scraper.manager import ScraperManager

        user_id = callback_query.from_user.id
        manager = ScraperManager.get_instance()

        result = await manager.start_scraper(user_id)

        if result["success"]:
            await callback_query.answer("✅ Scraper started!", show_alert=True)
            await controller.handle_status(callback_query)
        else:
            await callback_query.answer(f"❌ {result['message']}", show_alert=True)

    @controller.app.on_callback_query(filters.regex("^stop_scraper$"))
    async def callback_stop_scraper(client, callback_query: CallbackQuery):
        """Handle stop scraper callback"""
        from scraper.manager import ScraperManager

        user_id = callback_query.from_user.id
        manager = ScraperManager.get_instance()

        result = await manager.stop_scraper(user_id)

        if result["success"]:
            await callback_query.answer("✅ Scraper stopped!", show_alert=True)
            await controller.handle_status(callback_query)
        else:
            await callback_query.answer(f"❌ {result['message']}", show_alert=True)

    @controller.app.on_callback_query(filters.regex("^stop_system$"))
    async def callback_stop_system(client, callback_query: CallbackQuery):
        """Handle stop system callback"""
        await callback_query.answer(
            "⚠️ System stop must be done manually via server control",
            show_alert=True
        )

    logger.info("All handlers registered")
