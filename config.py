import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH")

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "waifu_scraper")

    # Logging
    LOG_GC = os.getenv("LOG_GC")

    # Scraper Configuration
    SCRAPER_DELAY = int(os.getenv("SCRAPER_DELAY", "2"))
    INLINE_BOTS = os.getenv("INLINE_BOTS", "@pic").split(",")
    KEYWORDS = os.getenv("KEYWORDS", "waifu,anime").split(",")
    TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

    # Media Storage
    MEDIA_DIR = os.getenv("MEDIA_DIR", "./downloads")

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "API_ID": cls.API_ID,
            "API_HASH": cls.API_HASH,
            "LOG_GC": cls.LOG_GC,
        }

        missing = [key for key, value in required.items() if not value or value == "0"]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

        return True
