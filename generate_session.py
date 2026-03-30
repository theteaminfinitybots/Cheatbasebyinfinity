#!/usr/bin/env python3
"""
Session String Generator for Pyrogram

This script helps users generate their Telegram session string
which is required for the userbot scraper.
"""

import asyncio
from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

async def generate_session():
    """Generate Pyrogram session string"""
    print("=" * 50)
    print("📱 Pyrogram Session String Generator")
    print("=" * 50)
    print()

    if not API_ID or not API_HASH:
        print("❌ Error: API_ID and API_HASH not found in .env file")
        print()
        print("Please add the following to your .env file:")
        print("API_ID=your_api_id")
        print("API_HASH=your_api_hash")
        print()
        print("Get these from: https://my.telegram.org/apps")
        return

    print("This will generate a session string for your Telegram account.")
    print("You'll need to:")
    print("1. Enter your phone number")
    print("2. Enter the verification code sent to your Telegram")
    print("3. Enter your 2FA password (if enabled)")
    print()

    async with Client("temp_session", api_id=int(API_ID), api_hash=API_HASH) as app:
        print()
        print("✅ Login successful!")
        print()
        print("=" * 50)
        print("📋 Your Session String:")
        print("=" * 50)
        print()
        print(await app.export_session_string())
        print()
        print("=" * 50)
        print()
        print("⚠️  IMPORTANT:")
        print("• Keep this session string safe and private")
        print("• Never share it with anyone")
        print("• Use it to add session in the bot with /addsession command")
        print()
        print("💡 Usage:")
        print("/addsession <paste_your_session_string_here>")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(generate_session())
    except KeyboardInterrupt:
        print("\n\n❌ Generation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
