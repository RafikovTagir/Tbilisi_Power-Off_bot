import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
import psycopg2
import myconstants as consts
import main
import datetime


TOKEN = consts.TOKEN
DB_URI = consts.DB_URI


db_connection = psycopg2.connect(DB_URI, sslmode='require')
db_object = db_connection.cursor()
updater = Updater(TOKEN, use_context=True)


db_object.execute(f'SELECT id, notification_time, address, page_url FROM users WHERE enable_notification = true')
for record in db_object:
    print(record)
    answer = main.is_address_in_page(record[3], record[2])
    updater.bot.sendMessage(chat_id=record[0], text=answer)


db_connection.close()
