import time
import report
import telebot
import sqlite3
import keys
import datetime
from googlesheet import post_to_sheet

mydb = sqlite3.connect('userid.db')
bot = telebot.TeleBot(keys.API_TOKEN)

def sql_select(mydb):
    #Данные об клиентах
    cursordb = mydb.cursor()
    try:
        data = cursordb.execute('SELECT user_id FROM telegram_id')
        return data
    except sqlite3.Error:
        pass


while True:
    time.sleep(300)
    with open('shift_info.txt', 'r') as shift:
        shift_id = shift.read()
    response = report.load_data()
    if response['status'] == 'CLOSED' and response['id'] != int(shift_id):   
        data = sql_select(mydb)
        for row in data:
            for id in row:
                bot.send_message(chat_id=id, text=report.closed_zreport(), parse_mode='HTML')
        with open('shift_info.txt', 'w') as shift:
            shift.write(str(response['id']))
            post_to_sheet(
                datetime.datetime.strptime(response['opened'], '%Y-%m-%dT%H:%M:%S.000Z'),
                response['totalCard'], 
                response['totalCash'],
                response['ordersCount'],
                round((response['totalCard']+response['totalCash'])/(response['ordersCount']), 1),
                response['totalCard']+response['totalCash']
                )
