from aiogram import Dispatcher, Bot, executor, types
import logging
from sqlalchemy import create_engine, insert, select

import config
import api
from model import user_id
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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    