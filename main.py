from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import os
import psycopg2

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('telegram_bot_token')
DB_URI = os.environ.get('DATABASE_URL')
TELASI_URL = 'http://www.telasi.ge/ru/power/'

# TODO:1) To return entire paragraph with time when power-off is, instead of just informing is address in
#      2) Automatic work every morning for example
#      3) Interface for choosing address and time of notification
#      5) Fully functional DB for users

db_connection = psycopg2.connect(DB_URI, sslmode='require')
db_object = db_connection.cursor()


def is_address_in_page(url, address):
    response = requests.get(url)
    if address in response.text:
        print(True)
        return True
    else:
        print(False)
        return False


def check_address(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    db_object.execute(f'SELECT id FROM users WHERE id = {user_id}')
    result = db_object.fetchone()  # fetchone method returns last line of result after execution
    if not result:
        db_object.execute('INSERT INTO users(id, username, messages) VALUES(%s, %s, %s)', (user_id, username, 0))
        db_connection.commit()
    db_object.execute(f'UPDATE users SET messages = messages+1 WHERE id = {user_id}')
    db_object.execute(f"UPDATE users SET address='{update.message.text}' WHERE id = {user_id}")
    db_connection.commit()
    if is_address_in_page(TELASI_URL, update.message.text):
        update.message.reply_text('Есть такое')
    else:
        update.message.reply_text('Нет такого')


def bop(update, context):
    print(update)
    update.message.reply_text('woof')


def easter_egg(update, context):
    print('Easter egg activated', update)
    print('Easter egg activated', context)
    update.message.reply_text('🥚🥚🥚🥚🥚')  # 🥚


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('Easter', easter_egg))
    dp.add_handler(MessageHandler(Filters.text, check_address))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://salty-plains-61736.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
