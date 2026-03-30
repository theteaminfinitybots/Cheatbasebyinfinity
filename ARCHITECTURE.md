# 🏗️ System Architecture

## Overview

The Waifu Scraper SaaS is a multi-tier system designed for scalability, reliability, and ease of use.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         TELEGRAM USERS                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CONTROLLER BOT                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Bot API (Pyrogram)                                  │    │
│  │  • Command Handlers                                    │    │
│  │  • Inline Keyboard UI                                  │    │
│  │  • Session Management                                  │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPER MANAGER                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Lifecycle Control                                   │    │
│  │  • Instance Registry                                   │    │
│  │  • Task Management                                     │    │
│  └────────────────────────────────────────────────────────┘    │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  USERBOT 1  │ │  USERBOT 2  │ │  USERBOT 3  │ │  USERBOT N  │
│             │ │             │ │             │ │             │
│ • Session 1 │ │ • Session 2 │ │ • Session 3 │ │ • Session N │
│ • Scraper   │ │ • Scraper   │ │ • Scraper   │ │ • Scraper   │
│ • Stats     │ │ • Stats     │ │ • Stats     │ │ • Stats     │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │
       └───────────────┴───────────────┴───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INLINE BOTS (Telegram)                       │
│  @pic • @anime_waifu_bot • @image_bot • ...                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                  │
│  ┌───────────────────┐        ┌──────────────────────┐         │
│  │    MONGODB        │        │   LOCAL STORAGE      │         │
│  │                   │        │                      │         │
│  │ • users           │        │ • downloads/         │         │
│  │ • cards           │        │ • media files        │         │
│  │ • indexes         │        │ • user folders       │         │
│  └───────────────────┘        └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOGGING SYSTEM                               │
│  • Console Logs                                                 │
│  • File Logs (waifu_scraper.log)                               │
│  • Telegram Log Channel                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Controller Bot Layer

**Responsibilities:**
- User authentication and onboarding
- Session string collection and storage
- UI presentation via inline keyboards
- Scraper lifecycle commands (start/stop)
- Status reporting

**Tech Stack:**
- Pyrogram (Bot API)
- Async/await pattern
- Callback query handlers

**Key Files:**
- `bot/controller.py` - Main bot class
- `bot/handlers.py` - Command and callback handlers

### 2. Scraper Manager Layer

**Responsibilities:**
- Create and destroy scraper instances
- Manage async tasks
- Track active scrapers
- Resource cleanup

**Tech Stack:**
- Asyncio task management
- Singleton pattern
- Background task orchestration

**Key Files:**
- `scraper/manager.py` - Central manager
- Maintains dictionaries of scrapers and tasks

### 3. Userbot Scraper Layer

**Responsibilities:**
- Connect as user (via session string)
- Query inline bots
- Send results to target channel
- Download media
- Save to database
- Handle rate limits (FloodWait)

**Tech Stack:**
- Pyrogram (User API)
- Async loops
- Error handling and retries

**Key Files:**
- `scraper/userbot.py` - Individual scraper class

### 4. Data Layer

**Responsibilities:**
- Persist user sessions
- Store scraped cards
- Maintain statistics
- Ensure data integrity

**Tech Stack:**
- MongoDB (pymongo)
- Indexed collections
- Unique constraints for deduplication

**Collections:**

#### users
```json
{
  "user_id": 123456789,
  "username": "example_user",
  "string_session": "encrypted_session_string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "scraper_active": true,
  "stats": {
    "fetched": 100,
    "saved": 80,
    "skipped": 20,
    "last_error": null
  }
}
```

#### cards
```json
{
  "user_id": 123456789,
  "bot_name": "@pic",
  "text": "Cute anime waifu #001",
  "media_path": "/downloads/123456789/file.jpg",
  "media_type": "photo",
  "file_id": "AgACAgIAAxkBAAI...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Indexes:**
- `users.user_id` (unique)
- `cards.(bot_name + text)` (unique, for deduplication)
- `cards.user_id`
- `cards.created_at`

### 5. Utilities Layer

**Media Handler** (`utils/media.py`)
- Download photos, documents, videos
- Organize by user_id
- Calculate file hashes
- Storage statistics

**Logger** (`utils/logger.py`)
- Dual logging (console + Telegram)
- Structured log messages
- Event categorization
- Async log sending

## Data Flow

### User Onboarding

```
User → /start → Controller Bot
       ↓
    Create user record in MongoDB
       ↓
    Show main menu
```

### Adding Session

```
User → /addsession <string> → Controller Bot
       ↓
    Validate session string
       ↓
    Store in MongoDB (encrypted)
       ↓
    Confirm success
```

### Starting Scraper

```
User → Click "Start Scraper" → Controller Bot
       ↓
    ScraperManager.start_scraper(user_id)
       ↓
    Create UserbotScraper instance
       ↓
    Connect userbot with session
       ↓
    Start async scraping task
       ↓
    Update user status in DB
```

### Scraping Loop

```
UserbotScraper (async loop)
       ↓
    For each inline bot:
       ↓
       For each keyword:
          ↓
          Fetch inline results
          ↓
          For each result:
             ↓
             Check if duplicate (DB query)
             ↓
             If unique:
                ↓
                Send to target channel
                ↓
                Download media
                ↓
                Save to MongoDB
                ↓
                Update stats
                ↓
                Log to channel
             ↓
          Sleep (SCRAPER_DELAY)
       ↓
    Sleep (60 seconds)
    ↓
    Repeat
```

### Stopping Scraper

```
User → Click "Stop Scraper" → Controller Bot
       ↓
    ScraperManager.stop_scraper(user_id)
       ↓
    Set scraper.running = False
       ↓
    Wait for loop to exit gracefully
       ↓
    Disconnect userbot
       ↓
    Cancel async task
       ↓
    Update user status in DB
       ↓
    Log stop event
```

## Scalability Considerations

### Current Design
- **Single Server:** All components run on one machine
- **Multi-User:** Supports unlimited users concurrently
- **Resource-Bound:** Limited by MongoDB and Telegram API

### Scaling Options

#### Horizontal Scaling
```
Load Balancer
    ├── Instance 1 (Users 1-1000)
    ├── Instance 2 (Users 1001-2000)
    └── Instance N (Users N...)
         ↓
    Shared MongoDB Cluster
```

#### Vertical Scaling
- Increase server RAM for more concurrent scrapers
- Faster CPU for quicker processing
- More storage for media files

#### Database Sharding
- Shard by user_id
- Separate read replicas
- Optimize indexes

## Security Architecture

### Session Protection
- Sessions stored encrypted in MongoDB
- Never logged or exposed
- Separate from bot token

### Access Control
- Private bot (no public access)
- User-specific scrapers (isolated)
- Channel-based logging (restricted)

### Rate Limiting
- Built-in FloodWait handling
- Configurable delays
- Automatic backoff

## Fault Tolerance

### Error Handling
- Try-catch at every async operation
- Graceful degradation
- Error logging to channel

### Recovery Mechanisms
- Auto-reconnect on disconnect
- Session validation before start
- Task cleanup on failure

### Data Integrity
- Unique indexes prevent duplicates
- Atomic operations in MongoDB
- Transaction-like behavior

## Performance Optimizations

### Database
- Indexed queries (O(log n) lookups)
- Batch inserts where possible
- Connection pooling

### Network
- Async I/O throughout
- Parallel scraper instances
- Non-blocking operations

### Storage
- Lazy media downloads (optional)
- Compression for logs
- Regular cleanup scripts

## Monitoring & Observability

### Logs
- **Console:** Development debugging
- **File:** Persistent audit trail
- **Telegram:** Real-time monitoring

### Metrics
- Per-user statistics
- System-wide aggregates
- Error rates

### Alerts
- FloodWait warnings
- Session failures
- Database errors

## Technology Choices

### Why Pyrogram?
- Modern async/await API
- Clean pythonic interface
- Both Bot and User API support
- Active development

### Why MongoDB?
- Flexible schema (JSON-like documents)
- Easy deduplication (unique indexes)
- Horizontal scalability
- Rich query language

### Why Asyncio?
- Non-blocking I/O
- Efficient resource usage
- Natural fit for Telegram API
- Concurrent user handling

## Future Enhancements

### Phase 2
- Web dashboard (FastAPI + React)
- OAuth-based session generation
- Cloud storage integration (S3)
- Advanced deduplication (image hashing)

### Phase 3
- Multi-bot orchestration
- ML-based content filtering
- API endpoints for external access
- Webhook-based notifications

### Phase 4
- Auto-scaling infrastructure
- Kubernetes deployment
- GraphQL API
- Real-time analytics

---

**This architecture provides a solid foundation for a scalable, maintainable, and feature-rich scraping platform.**
