import requests
import datetime 
import keys

WEBHOOK_SSL_CERT = 'webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(keys.WEBHOOK_HOST, keys.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(keys.API_TOKEN)



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
    response = requests.get(url=url, auth=(keys.login, keys.password), headers=headers, params=data)

    return response.json()[0]
    

def closed_zreport():
    # формирование отчета о смене
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
    response = requests.get(url=url, auth=(keys.login, keys.password), headers=headers, params=data).json()

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
        try:
            result = sorted(topPos, key=lambda x: x[3], reverse=True)[:5]
            for i in range(5):
                text += '<code>{0}. {1}: {2} руб ({3} шт)\n</code>'.format(i+1, result[i][0], round(result[i][3]), round(result[i][2]))
        except:
            pass
    if info == 'count':
        try:
            result = sorted(topPos, key=lambda x: x[2], reverse=True)[:5]
            for i in range(5):
                text += '<code>{0}. {1}: {2} руб ({3} шт)\n</code>'.format(i+1, result[i][0], round(result[i][3]), round(result[i][2]))
        except:
            pass
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
    response = requests.get(url=url, auth=(keys.login, keys.password), headers=headers, params=data).json()
    cashIn = ''
    cashOut = ''
    i = 0
    while response[i]['shift']['id'] == id:
        if response[i]['typeTransaction'] == 'cashIn':
            if cashIn != '':
                cashIn += '\n'
            cashIn += ('%d - %s' % (response[i]['amount'],  response[i]['comment']))
        if response[i]['typeTransaction'] == 'cashOut':
            if cashOut != '':
                cashOut += '\n'
            cashOut += ('%d - %s' % (response[i]['amount'],  response[i]['comment']))
        i += 1 

    return cashIn, cashOut
    
