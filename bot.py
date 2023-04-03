from aiogram import Bot, types,executor, Dispatcher
#from aiogram.contrib.middlewares.logging import LoggingMiddleware
#from aiogram.dispatcher import Dispatcher
#from aiogram.dispatcher.webhook import SendMessage
#from aiogram.utils.executor import start_webhook

import logging
from sqlalchemy import create_engine, insert, select

import config
import api
from model import user_id

# webhook settings
#WEBHOOK_HOST = 'https://1191015-co09919.tw1.ru'
#WEBHOOK_PATH = ''
#WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
#WEBAPP_HOST = 'localhost'  # or ip
#WEBAPP_PORT = 3001

logging.basicConfig(level=logging.INFO)
engine = create_engine('sqlite:///kos_report.db')
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
#dp.middleware.setup(LoggingMiddleware())

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


'''async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    

async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Bye!')
'''
if __name__ == '__main__':
    executor.start_polling(dp)
    '''start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )'''
    
