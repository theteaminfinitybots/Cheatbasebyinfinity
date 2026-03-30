# 🤖 Waifu Scraper SaaS System

A scalable Telegram-based automated waifu scraping platform built with Pyrogram and MongoDB. Deploy and manage multiple userbot scrapers through a clean Telegram interface.

## 🎯 Features

- **Multi-User Support**: Each user can deploy their own scraper instance
- **Automated Scraping**: Continuously collect waifu images from inline bots
- **Smart Deduplication**: Skip duplicate cards based on bot name + text
- **Media Management**: Auto-download and store images locally
- **Real-time Logging**: All activities logged to Telegram channel
- **Stats Tracking**: Monitor fetched, saved, and skipped items
- **Graceful Control**: Start/stop scrapers with clean shutdown

## 🏗️ Architecture

### Components

1. **Controller Bot** (Bot API)
   - User interface and control panel
   - Session management
   - Scraper lifecycle control

2. **Userbot Scrapers** (User API)
   - Dynamic instances per user
   - Inline bot querying
   - Media downloading
   - Data persistence

3. **MongoDB Database**
   - User sessions and stats
   - Scraped card data
   - Deduplication indexes

## 📋 Requirements

- Python 3.10+
- MongoDB 4.4+
- Telegram Bot Token
- Telegram API credentials (API_ID, API_HASH)

## 🚀 Installation

### 1. Clone Repository

```bash
git clone <repository_url>
cd waifu-scraper
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file:

```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id
API_HASH=your_api_hash

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=waifu_scraper

# Logging
LOG_GC=-1001234567890

# Scraper Settings
SCRAPER_DELAY=2
INLINE_BOTS=@pic,@anime_waifu_bot
KEYWORDS=waifu,anime,neko,maid
TARGET_CHANNEL=-1001234567890

# Storage
MEDIA_DIR=./downloads
```

### 4. Get Telegram Credentials

1. **Bot Token**: Get from [@BotFather](https://t.me/BotFather)
2. **API Credentials**: Get from [my.telegram.org/apps](https://my.telegram.org/apps)
3. **Log Channel**: Create a private channel and add your bot as admin

### 5. Setup MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

## 🎮 Usage

### Start the System

```bash
python main.py
```

### Generate Session String

```bash
python generate_session.py
```

Follow the prompts to login and copy your session string.

### Bot Commands

- `/start` - Initialize bot and show main menu
- `/addsession <string>` - Add your Pyrogram session
- `/menu` - Show control panel
- `/stats` - View your statistics

### Control Panel

- **➕ Add Session** - Add your session string
- **🚀 Start Scraper** - Launch your scraper instance
- **🛑 Stop Scraper** - Stop your scraper gracefully
- **📊 Status** - View stats and scraper status
- **❌ Stop System** - Admin control (manual)

## 📊 How It Works

### Scraping Flow

1. User adds their Telegram session via `/addsession`
2. User starts scraper from control panel
3. Scraper queries inline bots with configured keywords
4. Results are sent to target channel
5. Media is downloaded and stored
6. Data is saved to MongoDB (with deduplication)
7. Stats are updated in real-time
8. Logs are sent to log channel

### Deduplication

Cards are uniquely identified by:
- `bot_name` + `text` combination
- MongoDB unique index prevents duplicates
- Skipped duplicates are logged

## 🗂️ Project Structure

```
waifu-scraper/
├── bot/
│   ├── controller.py      # Main controller bot
│   └── handlers.py        # Command handlers
├── scraper/
│   ├── userbot.py         # Userbot scraper class
│   └── manager.py         # Scraper lifecycle manager
├── database/
│   ├── db.py              # MongoDB connection
│   └── models.py          # User and Card models
├── utils/
│   ├── media.py           # Media handling
│   └── logger.py          # Logging utilities
├── config.py              # Configuration management
├── main.py                # Entry point
├── generate_session.py    # Session generator
├── requirements.txt       # Dependencies
└── .env.example          # Environment template
```

## 🔒 Security Notes

- **Never commit** `.env` or session files
- **Keep session strings private** - they provide full account access
- **Use separate accounts** for scrapers (not your main account)
- **Monitor rate limits** - Telegram has FloodWait protections
- **Secure MongoDB** - Use authentication in production

## ⚙️ Configuration Options

### Scraper Settings

- `SCRAPER_DELAY`: Delay between bot queries (seconds)
- `INLINE_BOTS`: Comma-separated list of inline bots
- `KEYWORDS`: Comma-separated search keywords
- `TARGET_CHANNEL`: Channel ID for posting results

### Advanced

- `MEDIA_DIR`: Local storage path for downloads
- Future: Add cloud storage (S3, R2)
- Future: Image deduplication via MD5/pHash

## 📈 Statistics

Each scraper tracks:
- **Fetched**: Total inline results processed
- **Saved**: Unique cards saved to database
- **Skipped**: Duplicates detected
- **Last Error**: Recent error message

## 🐛 Troubleshooting

### Session Invalid

```
Error: Invalid session - please add a new one
```

**Solution**: Generate a new session string and re-add it.

### FloodWait Errors

```
FloodWait triggered - waiting X seconds
```

**Solution**: System automatically waits. Reduce `SCRAPER_DELAY` or use fewer keywords.

### MongoDB Connection Failed

```
Failed to connect to MongoDB
```

**Solution**: Ensure MongoDB is running and `MONGO_URI` is correct.

### No Inline Results

```
No results found
```

**Solution**: Check if inline bots are valid and keywords are appropriate.

## 🚀 Advanced Features (Roadmap)

- [ ] Multi-account load balancing
- [ ] Image deduplication (MD5/pHash)
- [ ] Cloud storage integration (S3, R2)
- [ ] Web dashboard (FastAPI)
- [ ] Auto-scaling workers
- [ ] Session rotation
- [ ] Webhook support
- [ ] API endpoints
- [ ] Analytics dashboard

## 📝 License

This project is for educational purposes. Respect Telegram's Terms of Service and rate limits.

## ⚠️ Disclaimer

- Use responsibly and ethically
- Respect bot owners and content creators
- Don't spam or abuse Telegram's API
- Follow all applicable laws and regulations

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation carefully

---

**Built with ❤️ using Pyrogram and MongoDB**
