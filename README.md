Installation (Termux)

pkg update -y
pkg upgrade -y
pkg install git -y
pkg install python -y

git clone https://github.com/yourname/telegram-media-bot
cd telegram-media-bot

pip install -r requirements.txt

python bot.py
