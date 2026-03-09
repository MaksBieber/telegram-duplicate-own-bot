Installation (Termux)

pkg update -y
pkg upgrade -y
pkg install git python -y

git clone https://github.com/MaksBieber/telegram-duplicate-own-bot
cd telegram-duplicate-own-bot

pip install -r requirements.txt
python bot.py
