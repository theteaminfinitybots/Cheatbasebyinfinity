import asyncio
import logging
from config import Config
from database import Database
from bot import ControllerBot, setup_handlers
from scraper.manager import ScraperManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('waifu_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point"""
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Config.validate()

        # Connect to database
        logger.info("Connecting to MongoDB...")
        db = Database()
        if not db.connect():
            logger.error("Failed to connect to MongoDB. Exiting...")
            return

        # Initialize controller bot
        logger.info("Initializing controller bot...")
        controller = ControllerBot()

        # Setup handlers
        setup_handlers(controller)

        # Initialize scraper manager
        scraper_manager = ScraperManager.get_instance()
        scraper_manager.set_logger_client(controller.app)

        # Start controller bot
        logger.info("Starting controller bot...")
        await controller.start()

        logger.info("=" * 50)
        logger.info("🤖 Waifu Scraper SaaS System is running!")
        logger.info("=" * 50)

        # Keep running
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal...")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)

    finally:
        # Cleanup
        logger.info("Shutting down...")

        # Stop all scrapers
        if 'scraper_manager' in locals():
            await scraper_manager.stop_all_scrapers()

        # Stop controller bot
        if 'controller' in locals():
            await controller.stop()

        # Close database
        if 'db' in locals():
            db.close()

        logger.info("Shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
