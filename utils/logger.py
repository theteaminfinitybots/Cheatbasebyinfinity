import logging
from datetime import datetime
from typing import Optional
from pyrogram import Client
from config import Config

class BotLogger:
    """Centralized logging to Telegram channel"""

    def __init__(self, client: Optional[Client] = None):
        self.client = client
        self.log_channel = Config.LOG_GC
        self.logger = logging.getLogger(__name__)

    def set_client(self, client: Client):
        """Set Pyrogram client for sending logs"""
        self.client = client

    async def log(self, message: str, level: str = "INFO"):
        """Send log message to Telegram channel"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{level}] {timestamp}\n{message}"

        # Log to console
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)

        # Send to Telegram if client is available
        if self.client and self.log_channel:
            try:
                await self.client.send_message(
                    chat_id=self.log_channel,
                    text=formatted_message
                )
            except Exception as e:
                self.logger.error(f"Failed to send log to Telegram: {e}")

    async def log_scraper_start(self, user_id: int, username: Optional[str] = None):
        """Log scraper start event"""
        user_info = f"@{username}" if username else f"User {user_id}"
        await self.log(f"🚀 Scraper started for {user_info}")

    async def log_scraper_stop(self, user_id: int, username: Optional[str] = None):
        """Log scraper stop event"""
        user_info = f"@{username}" if username else f"User {user_id}"
        await self.log(f"🛑 Scraper stopped for {user_info}")

    async def log_card_saved(self, user_id: int, bot_name: str, text: str):
        """Log new card saved"""
        preview = text[:50] + "..." if len(text) > 50 else text
        await self.log(f"💾 New card saved\nUser: {user_id}\nBot: {bot_name}\nText: {preview}")

    async def log_duplicate_skip(self, bot_name: str, text: str):
        """Log duplicate card skip"""
        preview = text[:50] + "..." if len(text) > 50 else text
        await self.log(f"⏭️ Duplicate skipped\nBot: {bot_name}\nText: {preview}")

    async def log_flood_wait(self, user_id: int, wait_time: int):
        """Log FloodWait event"""
        await self.log(
            f"⏰ FloodWait triggered for User {user_id}\nWaiting {wait_time} seconds",
            level="WARNING"
        )

    async def log_error(self, user_id: int, error: str):
        """Log error event"""
        await self.log(f"❌ Error for User {user_id}\n{error}", level="ERROR")

    async def log_stats(self, user_id: int, stats: dict):
        """Log scraper statistics"""
        message = (
            f"📊 Stats Update - User {user_id}\n"
            f"Fetched: {stats.get('fetched', 0)}\n"
            f"Saved: {stats.get('saved', 0)}\n"
            f"Skipped: {stats.get('skipped', 0)}"
        )
        await self.log(message)
