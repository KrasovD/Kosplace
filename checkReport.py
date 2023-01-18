import logging
import fastapi
import uvicorn
import telebot
import report
from telebot import types
import sqlite3
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(report.API_TOKEN)

app = fastapi.FastAPI(docs=None, redoc_url=None)


def sql_insert(user_id):
    #Запись в таблицу
    base = sqlite3.connect('userid.db')
    cursordb = base.cursor()
    data = cursordb.execute("select count(*) from sqlite_master where type='table' and name='telegram_id'")
    print(data)
    for row in data:
        if row[0] == 0:
            cursordb.execute('CREATE TABLE telegram_id (user_id integer)')
        else:
            try:
                cursordb.execute('INSERT INTO telegram_id (user_id) VALUES (%d)'% user_id)
            except:
                print('ERROR')
    base.commit()

@bot.message_handler(commands=['start'])
def message_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Отчет")
    item2 = types.KeyboardButton("Топ 5 блюд по кол-ву")
    item3 = types.KeyboardButton("Топ 5 блюд по сумме")
    markup.add(item1, item2, item3)
    print(message.chat.id)
    bot.send_message(message.chat.id, text='Привет, %s' %message.from_user.first_name, reply_markup=markup)
    sql_insert(message.chat.id)

@app.post(f'/{report.API_TOKEN}/')
def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return



@bot.message_handler(content_types='text')
def message_reply(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Отчет")
    item2 = types.KeyboardButton("Топ 5 блюд по кол-ву")
    item3 = types.KeyboardButton("Топ 5 блюд по сумме")
    markup.add(item1, item2, item3)
    print(message)
    if message.text==r'/start':
        bot.send_message(message.chat.id, text='Привет', reply_markup=markup)
    if message.text=="Отчет":
        bot.send_message(message.chat.id, text=report.closed_zreport(), reply_markup=markup, parse_mode='HTML')
        print(message.chat.id)
    if message.text=="Топ 5 блюд по кол-ву":
        bot.send_message(message.chat.id, text=report.top_dish('count'), reply_markup=markup, parse_mode='HTML')
    if message.text=="Топ 5 блюд по сумме":
        bot.send_message(message.chat.id, text=report.top_dish('sum'), reply_markup=markup, parse_mode='HTML')

# Set webhook
bot.set_webhook(
    url=report.WEBHOOK_URL_BASE + report.WEBHOOK_URL_PATH,
    certificate=open(report.WEBHOOK_SSL_CERT, 'r')
)

uvicorn.run(
    app,
    host=report.WEBHOOK_LISTEN,
    port=report.WEBHOOK_PORT,
    ssl_certfile=report.WEBHOOK_SSL_CERT,
    ssl_keyfile=report.WEBHOOK_SSL_PRIV
)
