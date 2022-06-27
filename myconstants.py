import os


PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('telegram_bot_token')
DB_URI = os.environ.get('DATABASE_URL')
TELASI_URL = 'http://www.telasi.ge/ru/power/'
REDIS_URL = os.environ.get('REDIS_URL')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_HOST = os.environ.get('REDIS_HOST')