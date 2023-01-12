import requests
import telebot
from telebot import types
import datetime
import json



login = 'kosplace'
password = 'e0LDx023'

'''
1. Выгрузка выручка за день(нал безнал), кол-во чеков и средний чек за день, кол-во нал в кассе, топ за день(3-5), 
2. Инфо о бонусном счете клиента (бунусы, фамилия, телефон, день рождения) инфо о тратах, топ блюд, топ напитков
Новинки, наши топы (за месяц)
http://test.quickresto.ru/platform/online/api/get?moduleName=warehouse.providers&amp;objectId=1
'''

'''
Таблица, дата выгрузки (при смене информации вывождить инфу(кофнтейнер, производитель, дата была\стала))
'''



def bot():
    bot = telebot.TeleBot('5880505887:AAE64lOk3XZsZTGqi1ktgX0PeS6DKbUSies')

    @bot.message_handler(content_types='text')
    def message_reply(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Отчет")
        item2 = types.KeyboardButton("Топ 5 блюд по кол-ву")
        item3 = types.KeyboardButton("Топ 5 блюд по сумме")
        markup.add(item1, item2, item3)
        if message.text=="Отчет":
            bot.send_message(message.chat.id, text=closed_zreport(), reply_markup=markup, parse_mode='HTML')
        if message.text=="Топ 5 блюд по кол-ву":
            bot.send_message(message.chat.id, text=top_dish('count'), reply_markup=markup)
        if message.text=="Топ 5 блюд по сумме":
            bot.send_message(message.chat.id, text=top_dish('sum'), reply_markup=markup)

    bot.polling(none_stop=True, interval=0)


def load_data():
    # выгрузка из API данных о последней смене
    url = 'https://kosplace.quickresto.ru/platform/online/api/list'
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    data = dict(
        moduleName='front.zreport',
    )
    response = requests.get(url=url, auth=(login,password), headers=headers, params=data)

    return response.json()[0]
    

def closed_zreport():
    response = load_data()
    incas = load_encas(response['id'])
    timedelta = datetime.timedelta(hours=3)
    open_time = (datetime.datetime.strptime(response['opened'], '%Y-%m-%dT%H:%M:%S.000Z') + timedelta).strftime('%d.%m %H:%M')
    try:
        close_time = (datetime.datetime.strptime(response['closed'], '%Y-%m-%dT%H:%M:%S.000Z') + timedelta).strftime('%d.%m %H:%M')
    except:
        close_time = 'открыта'
    def space(*item):
        sum = 0
        for i in range(len(item)):
            if isinstance(item[i], str):
                sum += len(item[i])
            else:
                sum += len(str(item[i]))
        return 26 - sum

    text = """
<code>
        KOS.PLACE
{}{}{}
{}{}{}
--------------------------
{}{}{}{}
{}{}{}{}
{}{}{}
--------------------------
{}{}{}{}
{}{}{}{}
--------------------------
{}{}{}{}
{}
{}{}{}{}
{}

</code>""".format(
    'Время открытия:', ' '* space('hh:mm', 'Время открытия:'), open_time,
    'Время закрытия:', ' '*space('hh:mm', 'Время закрытия:'), close_time,
    'Наличные:', ' '*space('Наличные:', response['totalCash'], ' руб'), response['totalCash'], ' руб',
    'Карта:', ' '*space('Карта:', response['totalCard'], ' руб'), response['totalCard'], ' руб',
    'Чеков:', ' '*space('Чеков:', response['ordersCount']), response['ordersCount'],
    'Средний чек:', ' '*space('Средний чек:', (round((response['totalCard']+response['totalCash'])/(response['ordersCount']), 1)), ' руб'),  (round((response['totalCard']+response['totalCash'])/(response['ordersCount']), 1)), ' руб',
    'Итого:', ' '*space('Итого:',(response['totalCard']+response['totalCash']), ' руб'), response['totalCard']+response['totalCash'], ' руб', 
    'Внесение:', ' '*space('Внесение:', response['totalCashIn'], ' руб'), response['totalCashIn'], ' руб',
    incas[0],
    'Изьятие:', ' '*space('Изьятие:', response['totalCashOut'], ' руб'), response['totalCashOut'], ' руб',
    incas[1]
    )
    return text


def top_dish(info):
    # Выгружает из базы топ позиций по сумме или количеству
    day_id = load_data()['id']
    url = 'https://kosplace.quickresto.ru/platform/online/api/read'
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    data = dict(
        moduleName='front.zreport',
        objectId = day_id,
    )
    response = requests.get(url=url, auth=(login,password), headers=headers, params=data).json()

    topPos = list()
    i = 0
    while True:
        try:
            topPos.append((
                response['productOutgoing'][i]['product']['name'],
                response['productOutgoing'][i]['product']['price'],
                abs(response['productOutgoing'][i]['amount']),
                response['productOutgoing'][i]['product']['price']*abs(response['productOutgoing'][i]['amount']) 
                ))
        except:
            break
        i += 1

    text = ''
    if info == 'sum':
        result = sorted(topPos, key=lambda x: x[3], reverse=True)[:5]
        for i in range(5):
            text += '{0}. {1}:\n{2} руб, ({3} шт)\n'.format(i+1, result[i][0], round(result[i][3]), round(result[i][2]))
    if info == 'count':
        result = sorted(topPos, key=lambda x: x[2], reverse=True)[:7]
        for i in range(7):
            text += '{0}. {1}:\n{2} руб, ({3} шт)\n'.format(i+1, result[i][0], round(result[i][3]), round(result[i][2]))
    return text


def load_encas(id):
    # выгрузка из API данных об инкассации
    url = 'https://kosplace.quickresto.ru/platform/online/api/list'
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    data = dict(
        moduleName='front.encashment',
    )
    response = requests.get(url=url, auth=(login,password), headers=headers, params=data).json()
    cashIn = ''
    cashOut = ''
    i = 0
    while response[i]['shift']['id'] == id:
        if response[i]['typeTransaction'] == 'cashIn':
            cashIn += ('%d - %s' % (response[i]['amount'],  response[i]['comment']))
        if response[i]['typeTransaction'] == 'cashOut':
            cashOut += ('%d - %s' % (response[i]['amount'],  response[i]['comment']))
        i += 1 

    return cashIn, cashOut
    
bot()