# 🔥 Telegram Referral Bot

**🇧🇩 Telegram Referral & Auto-Posting Bot** | Python + SQLite | Render.com Ready

A powerful Telegram bot that manages referral systems and allows admins to auto-post content to groups with interactive share buttons.

## ✨ Features

- ✅ **Referral System** - Track user referrals with SQLite database
- ✅ **Automatic Video Posting** - Admin can post videos to a group
- ✅ **Share Buttons** - Built-in share functionality
- ✅ **Admin Statistics** - View top referrers and total user count
- ✅ **Render.com Ready** - Deploy instantly to Render
- ✅ **Bengali Support** - Full Bangla language support

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/shakil56167/telegram-referral-bot.git
cd telegram-referral-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Bot
Edit `bot.py` and update these 5 values (lines 25-37):

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
ADMIN_USER_ID = 123456789           # Your numeric ID (@userinfobot)
BOT_USERNAME = "YourBotUsername"    # Bot username WITHOUT @
MAIN_GROUP_INVITE_LINK = "https://t.me/+XXXXXXX"  # Private group link
TARGET_GROUP_CHAT_ID = -1001234567890  # Group ID (@getidsbot)
```

### 4. Run Locally
```bash
python bot.py
```

## 🌐 Deploy to Render.com

1. **Fork/Push to GitHub** - Make sure your repo is on GitHub
2. **Create Render Account** - Go to [render.com](https://render.com)
3. **Connect GitHub** - Connect your GitHub account
4. **Create Service** - Select "New" → "Web Service"
5. **Configure** - Render will auto-detect `render.yaml`
6. **Deploy** - It will auto-deploy!

Or use the Deploy button (if configured):
```
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
```

## 📱 Bot Commands

### User Commands
- `/start` - Start bot, view referral link & stats
- Click **🔓 Get Access** - Check if you've completed referrals
- Click **⭕ SHARE NOW** - Share referral link

### Admin Commands (Replace `YOUR_ADMIN_ID`)
- `/stats` - View top referrers and total users
- `/post` - Send video with referral buttons to group
  - Send video + caption with `/post`
  - Or reply to a video with `/post`

## 🗄️ Database Structure

**Table: `users`**
```sql
CREATE TABLE users (
    user_id     INTEGER PRIMARY KEY,    -- Telegram user ID
    referrer_id INTEGER,                 -- Who referred this user
    username    TEXT,                    -- @username
    full_name   TEXT,                    -- First + Last name
    joined_at   TIMESTAMP                -- Registration time
);
```

## 🔐 Referral Flow

1. User clicks bot link: `https://t.me/BOT_USERNAME?start=ADMIN_ID`
2. User data stored in database
3. Each share creates a new user entry with referrer_id
4. After 4 referrals → User gets access to private group
5. Admin can verify stats with `/stats`

## 📋 Requirements

- Python 3.9+
- `python-telegram-bot` 20.7+
- SQLite3 (built-in)

## 🛠️ Customization

Edit these in `bot.py`:

```python
REQUIRED_INVITES = 4                    # Line 44 - Referrals needed
POST_CAPTION = "..."                   # Line 47-52 - Video caption
DB_PATH = "/opt/render/project/..."    # Line 45 - Database location
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check BOT_TOKEN is correct |
| Videos not posting | Verify bot is admin in group, TARGET_GROUP_CHAT_ID is correct |
| Database errors | Ensure `/opt/render/project/src/` directory exists |
| Referral not tracking | Make sure user clicks referral link in DM |

## 📞 Support

- **Telegram**: Find `@BotFather` for token issues
- **GitHub**: Open an issue in this repository
- **Render**: Check render.com logs for deployment errors

## 📜 License

This project is open source and available under MIT License.

## 👨‍💻 Author

Created by [@shakil56167](https://github.com/shakil56167)

---

**Made with ❤️ for Bangladesh**
