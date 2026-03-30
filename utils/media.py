import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from pyrogram.types import Message
from config import Config
import logging

logger = logging.getLogger(__name__)

class MediaHandler:
    """Handle media download and storage"""

    def __init__(self):
        self.media_dir = Path(Config.MEDIA_DIR)
        self.media_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_media_type(message: Message) -> Optional[str]:
        """Determine media type from message"""
        if message.photo:
            return "photo"
        elif message.document:
            return "document"
        elif message.video:
            return "video"
        elif message.animation:
            return "animation"
        return None

    @staticmethod
    def get_file_id(message: Message) -> Optional[str]:
        """Extract file_id from message"""
        if message.photo:
            return message.photo.file_id
        elif message.document:
            return message.document.file_id
        elif message.video:
            return message.video.file_id
        elif message.animation:
            return message.animation.file_id
        return None

    async def download_media(self, message: Message, user_id: int) -> Optional[Tuple[str, str]]:
        """
        Download media from message
        Returns: (file_path, media_type) or None
        """
        media_type = self.get_media_type(message)
        if not media_type:
            return None

        try:
            # Create user-specific directory
            user_dir = self.media_dir / str(user_id)
            user_dir.mkdir(exist_ok=True)

            # Download file
            file_path = await message.download(file_name=str(user_dir / ""))

            if file_path:
                logger.info(f"Downloaded {media_type} to {file_path}")
                return (file_path, media_type)

            return None

        except Exception as e:
            logger.error(f"Error downloading media: {e}")
            return None

    @staticmethod
    def calculate_md5(file_path: str) -> Optional[str]:
        """Calculate MD5 hash of file for deduplication"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating MD5: {e}")
            return None

    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        total_size = 0
        file_count = 0

        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1

        return {
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count
        }
