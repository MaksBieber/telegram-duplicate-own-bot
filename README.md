🤖 Telegram Duplicate Own Bot

A simple Telegram bot that can save and duplicate media (photos, videos, etc.) with captions using a SQLite database.

This bot is useful for saving media and sending duplicates automatically.

---

✨ Features

- 📥 Save media to database
- 🖼 Duplicate photos and videos
- 📝 Caption support
- 👤 Admin control
- 💾 SQLite database storage
- ⚡ Fast and lightweight

---

📦 Requirements

- Python 3.9+
- Termux / Linux / Windows
- Telegram Bot Token

---

📲 Termux Installation (Step by Step)

1️⃣ Update packages

pkg update -y
pkg upgrade -y

2️⃣ Install dependencies

pkg install git python -y

3️⃣ Clone repository

git clone https://github.com/MaksBieber/telegram-duplicate-own-bot
cd telegram-duplicate-own-bot

4️⃣ Install Python library

pip install python-telegram-bot

5️⃣ Configure bot

Edit "config.py"

Example:

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [123456789]

---

▶️ Run the Bot

python bot.py

---

⚡ One-Line Install (Termux)

pkg update -y && pkg install git python -y && git clone https://github.com/MaksBieber/telegram-duplicate-own-bot && cd telegram-duplicate-own-bot && pip install python-telegram-bot && python bot.py

---

🔑 Get Telegram Bot Token

1. Open Telegram
2. Search @BotFather
3. Type "/newbot"
4. Follow instructions
5. Copy your Bot Token

---

🆔 Get Telegram User ID

Search @userinfobot in Telegram and press "/start".

---

📁 Project Structure

telegram-duplicate-own-bot
│
├── bot.py
├── config.py
├── media.db
└── README.md

---

🟢 Run 24/7 in Termux (Optional)

Install tmux:

pkg install tmux

Start tmux:

tmux
python bot.py

Detach session:

CTRL + B then press D

---

👨‍💻 Author

GitHub: https://github.com/MaksBieber
