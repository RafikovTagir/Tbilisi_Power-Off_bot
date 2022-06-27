from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import redis
import requests
import os
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

# TODO:
#      2) Automatic start every morning and put request page into db
#      3) Use logging instead of print
#      4) Validate user input


updater = Updater(TOKEN, use_context=True)


db_connection = psycopg2.connect(DB_URI, sslmode='require')
db_object = db_connection.cursor()


r = redis.from_url(REDIS_URL)


def is_address_in_page(url, address):
    response = requests.get(url)
    print(address)
    print(response.text)
    index = response.text.find(address)
    if index == -1:
        print(False)
        return 'There are no such word on page'
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


def start(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    db_object.execute(f'SELECT id FROM users WHERE id = {user_id}')
    result = db_object.fetchone()
    if not result:
        db_object.execute('INSERT INTO users(id, username, messages) VALUES(%s, %s, %s)', (user_id, username, 0))
        db_connection.commit()
    update.message.reply_text('Hello)🖐\nDo you want to customize your settings?')


def check(update, context):
    user_id = update.message.from_user.id
    db_object.execute(f'SELECT address FROM users Where id = {user_id}')
    result = db_object.fetchone()
    print(result)
    if not result:
        update.message.reply_text('We cant find you in our database, please use /start command')
        return
    else:
        update.message.reply_text(is_address_in_page(TELASI_URL, result[0]))


def easter_egg(update, context):
    print('Easter egg activated', update)
    print('Easter egg activated', context)
    update.message.reply_text('🥚🥚🥚🥚🥚')  # 🥚


def redis_up(update, context):
    print(r.ping())
    r.set('user_id', 'current_state_session')
    print(r.get('foo'))


def settings(update, context):
    keyboard = [InlineKeyboardButton("URL 🌐", callback_data='page_url'),
                InlineKeyboardButton("Search word 🔍", callback_data='address'),
                InlineKeyboardButton("Notification time ⌚", callback_data='notification_time')]

    reply_markup = InlineKeyboardMarkup([keyboard], one_time_keyboard=True)
    update.message.reply_text('What you wanna change?', reply_markup=reply_markup)


def button(update, context):
    print(update)
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    print(query.data)
    query.answer()
    context.user_data['settings_state'] = query.data

    db_object.execute(f'SELECT {query.data} FROM users WHERE id = {user_id}')
    result = db_object.fetchone()
    if not result:
        update.message.reply_text('We cant find you in our database, please use /start command')
        return

    query.edit_message_text(text=f'current {query.data} is {result[0]} please type new one')


def user_input(update, context):
    if 'settings_state' not in context.user_data:
        update.message.reply_text("I don't understand you, please use buttons")
        return
    db_column = context.user_data['settings_state']
    user_id = update.message.from_user.id
    db_object.execute(f"UPDATE users SET {db_column} = '{update.message.text}' WHERE id = {user_id}")
    db_connection.commit()
    update.message.reply_text(f'Now your {db_column} is: {update.message.text}')
    del context.user_data['settings_state']


def all_users_notification(update, context):
    db_object.execute(f'SELECT id FROM users')
    for record in db_object:
        updater.bot.sendMessage(chat_id=record, text=update.message.text)


def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('Easter', easter_egg))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('check', check))
    dp.add_handler(CommandHandler('redis', redis_up))
    dp.add_handler(CommandHandler('settings', settings))
    dp.add_handler(CommandHandler('all', all_users_notification))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text, user_input))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://salty-plains-61736.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
