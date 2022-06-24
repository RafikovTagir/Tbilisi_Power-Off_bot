from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import redis
import requests
import os
import psycopg2

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('telegram_bot_token')
DB_URI = os.environ.get('DATABASE_URL')
TELASI_URL = 'http://www.telasi.ge/ru/power/'
REDIS_URL = os.environ.get('REDIS_URL')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_HOST = os.environ.get('REDIS_HOST')

# TODO:
#      2) Automatic start every morning and put request page into db
#      3) Interface for choosing web-site and time of notification
#      6) Make it works for user-defined sites


db_connection = psycopg2.connect(DB_URI, sslmode='require')
db_object = db_connection.cursor()


def is_address_in_page(url, address):
    response = requests.get(url)
    print(address)
    print(response.text)
    index = response.text.find(address)
    if index == -1:
        print(False)
        return 'There are no such address on page'
    else:
        print(True)
        left_p = response.text.rfind('<p>', 1, index)
        right_p = response.text.find('</p>', index)
        if left_p == -1:
            left_p = index-20
        if right_p == -1:
            right_p = index+20  # todo remake as exception

        print(left_p, right_p)
        print(response.text[left_p + 3:right_p])
        return response.text[left_p + 3:right_p]


def address_choose(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    db_object.execute(f'SELECT id FROM users WHERE id = {user_id}')
    result = db_object.fetchone()  # fetchone method returns last line of result after execution
    if not result:
        db_object.execute('INSERT INTO users(id, username, messages, address) VALUES(%s, %s, %s, %s)', (user_id, username, 0, update.message.text))
        db_connection.commit()
    db_object.execute(f'UPDATE users SET messages = messages+1 WHERE id = {user_id}')
    db_object.execute(f"UPDATE users SET address='{update.message.text}' WHERE id = {user_id}")
    db_connection.commit()

    update.message.reply_text(f'You are chose address: {update.message.text}')
    update.message.reply_text('If you want to check it, use /check command')


def start(update, context):
    update.message.reply_text('Hello)🖐\nDo you want to customize your settings?')


def check(update, context):
    user_id = update.message.from_user.id
    db_object.execute(f'SELECT address FROM users Where id = {user_id}')
    result = db_object.fetchone()
    print(result)
    if not result:
        update.message.reply_text('first we need to know site and word for search')
        start(update, context)
    else:
        update.message.reply_text(is_address_in_page(TELASI_URL, result[0]))


def easter_egg(update, context):
    print('Easter egg activated', update)
    print('Easter egg activated', context)
    update.message.reply_text('🥚🥚🥚🥚🥚')  # 🥚


def redis_up(update, context):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)
    print(r.ping())


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('Easter', easter_egg))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('check', check))
    dp.add_handler(CommandHandler('redis', redis_up))
    dp.add_handler(MessageHandler(Filters.text, address_choose))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://salty-plains-61736.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
