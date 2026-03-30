# 🚀 Quick Setup Guide

## Step-by-Step Setup

### 1. Prerequisites

Before starting, ensure you have:
- Python 3.10 or higher installed
- MongoDB running (locally or remote)
- A Telegram account

### 2. Get Telegram Credentials

#### A. Create a Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the **Bot Token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### B. Get API Credentials

1. Visit [my.telegram.org/apps](https://my.telegram.org/apps)
2. Login with your Telegram phone number
3. Create a new application
4. Copy **API_ID** (numeric) and **API_HASH** (alphanumeric)

#### C. Create Log Channel

1. Create a new private channel in Telegram
2. Add your bot as an admin
3. Forward any message from the channel to [@RawDataBot](https://t.me/RawDataBot)
4. Copy the **channel ID** (negative number, like: `-1001234567890`)

#### D. Create Target Channel

1. Create another private channel for scraped content
2. Add your bot as an admin
3. Get the channel ID using [@RawDataBot](https://t.me/RawDataBot)

### 3. Install MongoDB

#### Option 1: Docker (Recommended)

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

#### Option 2: Local Installation

**Ubuntu/Debian:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Windows:**
Download and install from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)

### 4. Configure the Project

#### A. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### B. Create .env File

Copy the example and fill in your credentials:

```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

Fill in:

```env
# Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=waifu_scraper

# Logging
LOG_GC=-1001234567890

# Scraper Settings
SCRAPER_DELAY=2
INLINE_BOTS=@pic,@anime_waifu_bot,@image_bot
KEYWORDS=waifu,anime,neko,maid,kawaii
TARGET_CHANNEL=-1001234567890

# Storage
MEDIA_DIR=./downloads
```

### 5. Generate Your Session String

Run the session generator:

```bash
python generate_session.py
```

Follow the prompts:
1. Enter your phone number (with country code, e.g., +1234567890)
2. Enter the verification code sent to Telegram
3. Enter your 2FA password (if enabled)
4. Copy the session string that appears

**⚠️ IMPORTANT:** Keep this session string private!

### 6. Start the System

```bash
python main.py
```

You should see:

```
🤖 Waifu Scraper SaaS System is running!
```

### 7. Setup Your Scraper

1. Open Telegram and find your bot
2. Send `/start`
3. Click **"➕ Add Session"**
4. Send `/addsession <your_session_string>`
5. Click **"🚀 Start Scraper"**
6. Your scraper is now running!

### 8. Monitor Activity

- Check your **log channel** for real-time activity
- Check your **target channel** for scraped content
- Use `/stats` in the bot to see statistics

## 📊 Configuration Explained

### INLINE_BOTS

These are the Telegram inline bots your scraper will query.

Examples:
- `@pic` - General image bot
- `@anime_waifu_bot` - Anime images
- `@image_bot` - Image search bot

**Format:** Comma-separated, with @ symbol

### KEYWORDS

Search terms used to query inline bots.

Examples:
- `waifu,anime,neko,maid,kawaii`
- `pokemon,pikachu,charizard`
- `nature,landscape,mountains`

**Format:** Comma-separated, no spaces around commas

### SCRAPER_DELAY

Time in seconds between queries to prevent rate limiting.

- **Recommended:** 2-5 seconds
- **Faster:** 1 second (higher risk of FloodWait)
- **Safer:** 10+ seconds (slower but more stable)

### TARGET_CHANNEL

Where scraped content will be posted.

- Must be a channel (not a group)
- Bot must be admin
- Can be private or public
- Format: `-1001234567890` (negative number)

## 🔧 Troubleshooting

### "Failed to connect to MongoDB"

**Check if MongoDB is running:**
```bash
# Linux/Mac
sudo systemctl status mongodb
# or
brew services list

# Windows
services.msc  # Look for MongoDB service
```

**Test connection:**
```bash
mongo  # or mongosh for newer versions
```

### "Invalid session - please add a new one"

- Generate a fresh session string
- Make sure you're using the correct API_ID and API_HASH
- Try logging out from the device and regenerating

### "FloodWait triggered"

This is normal! Telegram limits API usage. The system will automatically wait.

**To reduce FloodWait:**
- Increase `SCRAPER_DELAY`
- Use fewer keywords
- Query fewer bots

### "No results found"

- Check if inline bots are working (try them manually in Telegram)
- Verify keywords are appropriate for the bot
- Some bots may be offline or restricted

### Bot doesn't respond

- Check `BOT_TOKEN` is correct
- Verify bot is not blocked
- Check system logs: `tail -f waifu_scraper.log`

## 🎯 Best Practices

### 1. Use a Separate Account

Don't use your main Telegram account for scraping. Create a new account to avoid potential restrictions.

### 2. Start Small

Begin with:
- 1-2 inline bots
- 2-3 keywords
- Higher delay (5+ seconds)

Gradually optimize based on results.

### 3. Monitor Logs

Regularly check your log channel to:
- Detect errors early
- Understand scraping patterns
- Optimize configuration

### 4. Backup Data

Regularly backup your MongoDB database:

```bash
mongodump --db waifu_scraper --out backup/
```

### 5. Secure Your Environment

- Never commit `.env` file
- Keep session strings private
- Use strong MongoDB authentication in production
- Restrict access to log and target channels

## 📈 Scaling Tips

### Multiple Users

The system supports unlimited users. Each user:
- Adds their own session
- Runs independent scraper
- Has separate stats

### Performance Optimization

- Use MongoDB indexes (auto-created)
- Increase server resources for many users
- Consider horizontal scaling with multiple instances

### Storage Management

Large media collections can consume disk space:

```bash
# Check storage usage
du -sh downloads/

# Clean old files (example: >30 days)
find downloads/ -type f -mtime +30 -delete
```

## 🆘 Getting Help

1. **Check logs:** `tail -f waifu_scraper.log`
2. **Read error messages** - they usually indicate the issue
3. **Search existing issues** on GitHub
4. **Create a new issue** with:
   - Error message
   - Configuration (without sensitive data)
   - Steps to reproduce

## ✅ Quick Verification Checklist

- [ ] Python 3.10+ installed
- [ ] MongoDB running
- [ ] Bot created via @BotFather
- [ ] API credentials from my.telegram.org
- [ ] Log channel created with bot as admin
- [ ] Target channel created with bot as admin
- [ ] .env file configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Session string generated
- [ ] System started (`python main.py`)
- [ ] Session added via bot
- [ ] Scraper started
- [ ] Activity visible in log channel

---

**You're all set! Happy scraping! 🎉**
