import asyncio
from datetime import datetime
from typing import Optional
from pyrogram import Client
from pyrogram.errors import FloodWait, SessionPasswordNeeded, AuthKeyUnregistered
from pyrogram.raw.functions.messages import GetInlineBotResults
from pyrogram.raw.types import InputBotInlineMessageMediaAuto
from config import Config
from database import User, Card
from utils import MediaHandler, BotLogger
import logging

logger = logging.getLogger(__name__)

class UserbotScraper:
    """Individual userbot scraper instance for each user"""

    def __init__(self, user_id: int, string_session: str, bot_logger: BotLogger):
        self.user_id = user_id
        self.string_session = string_session
        self.running = False
        self.bot_logger = bot_logger
        self.media_handler = MediaHandler()

        # Statistics
        self.stats = {
            "fetched": 0,
            "saved": 0,
            "skipped": 0,
            "last_error": None
        }

        # Create userbot client
        self.client = Client(
            name=f"scraper_{user_id}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=string_session
        )

    async def start(self) -> bool:
        """Start the userbot scraper"""
        try:
            await self.client.start()
            self.running = True
            logger.info(f"Userbot scraper started for user {self.user_id}")

            # Get user info
            me = await self.client.get_me()
            username = me.username if me.username else "Unknown"

            await self.bot_logger.log_scraper_start(self.user_id, username)
            User.set_scraper_status(self.user_id, True)

            return True

        except AuthKeyUnregistered:
            logger.error(f"Invalid session for user {self.user_id}")
            self.stats["last_error"] = "Invalid session - please add a new one"
            await self.bot_logger.log_error(self.user_id, "Invalid session")
            return False

        except Exception as e:
            logger.error(f"Error starting scraper for user {self.user_id}: {e}")
            self.stats["last_error"] = str(e)
            await self.bot_logger.log_error(self.user_id, str(e))
            return False

    async def stop(self):
        """Stop the userbot scraper gracefully"""
        self.running = False
        logger.info(f"Stopping scraper for user {self.user_id}")

        try:
            if self.client.is_connected:
                await self.client.stop()

            User.set_scraper_status(self.user_id, False)

            me = await self.client.get_me() if self.client.is_connected else None
            username = me.username if me and me.username else None

            await self.bot_logger.log_scraper_stop(self.user_id, username)

        except Exception as e:
            logger.error(f"Error stopping scraper: {e}")

    async def fetch_inline_results(self, bot_username: str, query: str, offset: str = "") -> list:
        """Fetch results from inline bot"""
        try:
            # Resolve bot
            bot = await self.client.resolve_peer(bot_username)

            # Get inline results
            results = await self.client.invoke(
                GetInlineBotResults(
                    bot=bot,
                    peer=await self.client.resolve_peer("me"),
                    query=query,
                    offset=offset
                )
            )

            return results.results if results else []

        except FloodWait as e:
            await self.bot_logger.log_flood_wait(self.user_id, e.value)
            await asyncio.sleep(e.value)
            return []

        except Exception as e:
            logger.error(f"Error fetching inline results: {e}")
            return []

    async def send_inline_result(self, bot_username: str, query_id: int, result_id: str):
        """Send inline bot result to target channel"""
        try:
            if not Config.TARGET_CHANNEL:
                logger.warning("No target channel configured")
                return None

            # Send inline result
            message = await self.client.send_inline_bot_result(
                chat_id=Config.TARGET_CHANNEL,
                query_id=query_id,
                result_id=result_id
            )

            return message

        except FloodWait as e:
            await self.bot_logger.log_flood_wait(self.user_id, e.value)
            await asyncio.sleep(e.value)
            return None

        except Exception as e:
            logger.error(f"Error sending inline result: {e}")
            return None

    async def process_result(self, bot_username: str, result, query_id: int) -> bool:
        """Process a single inline result"""
        try:
            # Extract text/caption
            text = ""
            if hasattr(result, 'send_message'):
                if isinstance(result.send_message, InputBotInlineMessageMediaAuto):
                    text = result.send_message.message

            if not text:
                text = result.id

            # Check if already exists (deduplication)
            if Card.exists(bot_username, text):
                self.stats["skipped"] += 1
                await self.bot_logger.log_duplicate_skip(bot_username, text)
                return False

            # Send to channel and get message
            message = await self.send_inline_result(bot_username, query_id, result.id)

            if not message:
                return False

            # Download media if present
            media_path = None
            media_type = None

            media_result = await self.media_handler.download_media(message, self.user_id)
            if media_result:
                media_path, media_type = media_result

            # Get file_id
            file_id = self.media_handler.get_file_id(message)

            # Save to database
            card = Card(
                user_id=self.user_id,
                bot_name=bot_username,
                text=text,
                media_path=media_path,
                media_type=media_type,
                file_id=file_id
            )

            saved_id = Card.save(card)

            if saved_id:
                self.stats["saved"] += 1
                await self.bot_logger.log_card_saved(self.user_id, bot_username, text)
                return True
            else:
                self.stats["skipped"] += 1
                return False

        except Exception as e:
            logger.error(f"Error processing result: {e}")
            self.stats["last_error"] = str(e)
            return False

    async def scrape_bot(self, bot_username: str, keywords: list):
        """Scrape a specific inline bot with multiple keywords"""
        for keyword in keywords:
            if not self.running:
                break

            logger.info(f"Scraping {bot_username} with keyword '{keyword}'")

            results = await self.fetch_inline_results(bot_username, keyword)

            if not results:
                continue

            # Get query_id for sending results
            query_id = None
            try:
                bot = await self.client.resolve_peer(bot_username)
                inline_results = await self.client.invoke(
                    GetInlineBotResults(
                        bot=bot,
                        peer=await self.client.resolve_peer("me"),
                        query=keyword,
                        offset=""
                    )
                )
                query_id = inline_results.query_id
            except Exception as e:
                logger.error(f"Error getting query_id: {e}")
                continue

            # Process each result
            for result in results[:10]:  # Limit to 10 results per keyword
                if not self.running:
                    break

                self.stats["fetched"] += 1
                await self.process_result(bot_username, result, query_id)

                # Small delay between results
                await asyncio.sleep(1)

            # Delay between keywords
            await asyncio.sleep(Config.SCRAPER_DELAY)

    async def run(self):
        """Main scraping loop"""
        logger.info(f"Starting scraping loop for user {self.user_id}")

        while self.running:
            try:
                # Scrape each configured bot
                for bot_username in Config.INLINE_BOTS:
                    if not self.running:
                        break

                    await self.scrape_bot(bot_username, Config.KEYWORDS)

                    # Update stats in database
                    User.update_stats(self.user_id, self.stats)

                    # Log stats periodically
                    if self.stats["fetched"] % 50 == 0:
                        await self.bot_logger.log_stats(self.user_id, self.stats)

                    # Delay between bots
                    await asyncio.sleep(Config.SCRAPER_DELAY)

                # Delay before next full cycle
                if self.running:
                    logger.info(f"Cycle complete for user {self.user_id}. Waiting before next cycle...")
                    await asyncio.sleep(60)  # 1 minute between cycles

            except Exception as e:
                logger.error(f"Error in scraping loop: {e}")
                self.stats["last_error"] = str(e)
                await self.bot_logger.log_error(self.user_id, str(e))
                await asyncio.sleep(30)  # Wait 30 seconds on error

        logger.info(f"Scraping loop stopped for user {self.user_id}")
