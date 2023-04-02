from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.webhook import get_new_configured_app
import logging
from sqlalchemy import create_engine, insert, select
import ssl
from aiohttp import web

import config
import api
from model import user_id

WEBHOOK_HOST = '90.156.229.64'  # Domain name or IP addres which your bot is located.
WEBHOOK_PORT = 443  # Telegram Bot API allows only for usage next ports: 443, 80, 88 or 8443
WEBHOOK_URL_PATH = '/kosplace_report'  # Part of URL

WEBHOOK_SSL_CERT = 'YOURPUBLIC.pem' 
WEBHOOK_SSL_PRIV = 'YOURPRIVATE.pem' 

WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_URL_PATH}"

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 3001

 
logging.basicConfig(level=logging.INFO)
engine = create_engine('sqlite:///kos_report.db')
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    try: 
        with engine.connect() as conn:
            conn.execute(insert(user_id).values(user_id=message.chat.id))
            conn.commit()
    except:
        pass
    await message.answer(
        text='Здравтвуйте, %s! Для отчетов воспользуйтесь меню в левом нижнем углу экрана' % message.chat.first_name
        )

@dp.message_handler(commands=['report'])
async def send_report(message: types.Message):
    key1 = types.InlineKeyboardButton(text='Бородинская', callback_data='z_borod')
    key2 = types.InlineKeyboardButton(text='Коменданский', callback_data='z_komend')
    keyboard = types.InlineKeyboardMarkup().add(key1, key2)
    await message.answer(text='Отчет по кофейне:', reply_markup=keyboard, parse_mode='HTML')

@dp.message_handler(commands=['top_dish'])
async def send_top_dish(message: types.Message):
    key1 = types.InlineKeyboardButton(text='По сумме', callback_data='by_sum')
    key2 = types.InlineKeyboardButton(text='По кол-ву', callback_data='by_count')
    keyboard = types.InlineKeyboardMarkup().add(key1, key2)
    await message.answer(text='Топ позиций по:', reply_markup=keyboard, parse_mode='HTML')
    

@dp.callback_query_handler(lambda call: call.data)
async def call_top_dish(call: types.CallbackQuery):
    if call.data == 'z_borod':
        await bot.send_message(
            call.from_user.id, 
            text=api.shift_info('z_report', ('Бородинская 2/86',)).__next__(), 
            parse_mode='HTML'
            )
        await bot.answer_callback_query(call.id)
    if call.data == 'z_komend':
        await bot.send_message(
            call.from_user.id, 
            text=api.shift_info('z_report', ('Коменданский 65',)).__next__(), 
            parse_mode='HTML'
            )
        await bot.answer_callback_query(call.id)
    
    if call.data == 'by_sum':
        for shift in api.shift_info('dish_by_sum',('Коменданский 65', 'Бородинская 2/86')):
            await bot.send_message(
                call.from_user.id, 
                text=shift, 
                parse_mode='HTML'
                )
        await bot.answer_callback_query(call.id)
    if call.data == 'by_count':
        for shift in api.shift_info('dish_by_count',('Коменданский 65', 'Бородинская 2/86')):
            await bot.send_message(
                call.from_user.id, 
                text=shift, 
                parse_mode='HTML')
        await bot.answer_callback_query(call.id)


async def on_startup(app):
    webhook = await bot.get_webhook_info()
    if webhook.url != WEBHOOK_URL:
        if not webhook.url:
            await bot.delete_webhook()

        await bot.set_webhook(WEBHOOK_URL, certificate=open(WEBHOOK_SSL_CERT, 'rb'))

async def on_shutdown(app):
    await bot.delete_webhook()


if __name__ == '__main__':

    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=context)
