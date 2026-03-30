from datetime import datetime
from typing import Optional, Dict, Any
from database.db import Database

class User:
    """User model for managing user sessions and stats"""

    def __init__(self, user_id: int, username: Optional[str] = None,
                 string_session: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        self.string_session = string_session
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.scraper_active = False
        self.stats = {
            "fetched": 0,
            "saved": 0,
            "skipped": 0,
            "last_error": None
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "string_session": self.string_session,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "scraper_active": self.scraper_active,
            "stats": self.stats
        }

    @staticmethod
    def find_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        db = Database().db
        return db.users.find_one({"user_id": user_id})

    @staticmethod
    def create_or_update(user_id: int, username: Optional[str] = None,
                        string_session: Optional[str] = None) -> bool:
        """Create or update user"""
        db = Database().db
        user = User(user_id, username, string_session)

        result = db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "username": username,
                    "string_session": string_session,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.utcnow(),
                    "scraper_active": False,
                    "stats": user.stats
                }
            },
            upsert=True
        )
        return result.acknowledged

    @staticmethod
    def update_stats(user_id: int, stats_update: Dict[str, Any]) -> bool:
        """Update user statistics"""
        db = Database().db
        result = db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"stats.{key}": value for key, value in stats_update.items()
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.acknowledged

    @staticmethod
    def set_scraper_status(user_id: int, active: bool) -> bool:
        """Set scraper active status"""
        db = Database().db
        result = db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "scraper_active": active,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.acknowledged


class Card:
    """Card model for scraped waifu data"""

    def __init__(self, user_id: int, bot_name: str, text: str,
                 media_path: Optional[str] = None, media_type: Optional[str] = None,
                 file_id: Optional[str] = None):
        self.user_id = user_id
        self.bot_name = bot_name
        self.text = text
        self.media_path = media_path
        self.media_type = media_type
        self.file_id = file_id
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary"""
        return {
            "user_id": self.user_id,
            "bot_name": self.bot_name,
            "text": self.text,
            "media_path": self.media_path,
            "media_type": self.media_type,
            "file_id": self.file_id,
            "created_at": self.created_at
        }

    @staticmethod
    def save(card: 'Card') -> Optional[str]:
        """Save card to database (with deduplication)"""
        db = Database().db
        try:
            result = db.cards.insert_one(card.to_dict())
            return str(result.inserted_id)
        except Exception:
            # Duplicate key error - card already exists
            return None

    @staticmethod
    def exists(bot_name: str, text: str) -> bool:
        """Check if card already exists"""
        db = Database().db
        return db.cards.find_one({"bot_name": bot_name, "text": text}) is not None

    @staticmethod
    def count_by_user(user_id: int) -> int:
        """Count cards for a user"""
        db = Database().db
        return db.cards.count_documents({"user_id": user_id})

    @staticmethod
    def get_user_cards(user_id: int, limit: int = 10) -> list:
        """Get recent cards for a user"""
        db = Database().db
        return list(db.cards.find({"user_id": user_id})
                   .sort("created_at", -1)
                   .limit(limit))
