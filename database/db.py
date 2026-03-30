from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Establish MongoDB connection"""
        try:
            self._client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[Config.MONGO_DB_NAME]
            logger.info(f"Connected to MongoDB: {Config.MONGO_DB_NAME}")
            self._create_indexes()
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def _create_indexes(self):
        """Create necessary indexes for performance"""
        # Users collection indexes
        self._db.users.create_index("user_id", unique=True)

        # Cards collection indexes
        self._db.cards.create_index([("bot_name", ASCENDING), ("text", ASCENDING)], unique=True)
        self._db.cards.create_index("user_id")
        self._db.cards.create_index("created_at")

        logger.info("Database indexes created")

    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")
