import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
import psycopg2
import myconstants as consts


PORT = consts.PORT
TOKEN = consts.TOKEN
DB_URI = consts.DB_URI
TELASI_URL = consts.TELASI_URL
REDIS_URL = consts.REDIS_URL
REDIS_PORT = consts.REDIS_PORT
REDIS_PASSWORD = consts.REDIS_PASSWORD
REDIS_HOST = consts.REDIS_HOST


db_connection = psycopg2.connect(DB_URI, sslmode='require')
db_object = db_connection.cursor()


updater = Updater(TOKEN, use_context=True)


db_object.execute(f'SELECT id FROM users WHERE enable_notification = true')
for record in db_object:
    print(record)
    updater.bot.sendMessage(chat_id=record[0], text='Good Morning from file!')


db_connection.close()
