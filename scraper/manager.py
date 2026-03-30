import asyncio
from typing import Dict, Optional
from database import User
from scraper.userbot import UserbotScraper
from utils import BotLogger
import logging

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages lifecycle of all scraper instances"""

    _instance = None
    _scrapers: Dict[int, UserbotScraper] = {}
    _tasks: Dict[int, asyncio.Task] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScraperManager, cls).__new__(cls)
            cls._scrapers = {}
            cls._tasks = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.bot_logger = BotLogger()

    def set_logger_client(self, client):
        """Set Pyrogram client for logging"""
        self.bot_logger.set_client(client)

    async def start_scraper(self, user_id: int) -> dict:
        """Start a scraper instance for a user"""
        # Check if already running
        if user_id in self._scrapers and self._scrapers[user_id].running:
            return {
                "success": False,
                "message": "Scraper is already running"
            }

        # Get user data
        user_data = User.find_by_id(user_id)

        if not user_data:
            return {
                "success": False,
                "message": "User not found. Use /start first."
            }

        string_session = user_data.get("string_session")

        if not string_session:
            return {
                "success": False,
                "message": "No session found. Add your session first."
            }

        # Create scraper instance
        try:
            scraper = UserbotScraper(user_id, string_session, self.bot_logger)

            # Start the scraper
            started = await scraper.start()

            if not started:
                return {
                    "success": False,
                    "message": "Failed to start scraper. Check session validity."
                }

            # Store scraper
            self._scrapers[user_id] = scraper

            # Create and store background task
            task = asyncio.create_task(scraper.run())
            self._tasks[user_id] = task

            logger.info(f"Scraper started for user {user_id}")

            return {
                "success": True,
                "message": "Scraper started successfully"
            }

        except Exception as e:
            logger.error(f"Error starting scraper for user {user_id}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def stop_scraper(self, user_id: int) -> dict:
        """Stop a scraper instance for a user"""
        # Check if scraper exists
        if user_id not in self._scrapers:
            return {
                "success": False,
                "message": "No scraper instance found"
            }

        scraper = self._scrapers[user_id]

        # Stop the scraper gracefully
        try:
            await scraper.stop()

            # Cancel the background task
            if user_id in self._tasks:
                task = self._tasks[user_id]
                task.cancel()

                try:
                    await task
                except asyncio.CancelledError:
                    pass

                del self._tasks[user_id]

            # Remove scraper
            del self._scrapers[user_id]

            logger.info(f"Scraper stopped for user {user_id}")

            return {
                "success": True,
                "message": "Scraper stopped successfully"
            }

        except Exception as e:
            logger.error(f"Error stopping scraper for user {user_id}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def stop_all_scrapers(self):
        """Stop all running scrapers"""
        logger.info("Stopping all scrapers...")

        user_ids = list(self._scrapers.keys())

        for user_id in user_ids:
            await self.stop_scraper(user_id)

        logger.info("All scrapers stopped")

    def get_active_scrapers(self) -> list:
        """Get list of active scraper user IDs"""
        return [user_id for user_id, scraper in self._scrapers.items() if scraper.running]

    def get_scraper_stats(self, user_id: int) -> Optional[dict]:
        """Get statistics for a specific scraper"""
        if user_id in self._scrapers:
            return self._scrapers[user_id].stats
        return None

    def is_running(self, user_id: int) -> bool:
        """Check if scraper is running for a user"""
        return user_id in self._scrapers and self._scrapers[user_id].running
