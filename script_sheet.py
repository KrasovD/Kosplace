from googlesheet import post_to_sheet
import datetime
import requests
import keys


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
    response = requests.get(url=url, auth=(keys.login,keys.password), headers=headers, params=data)

    return response.json()[1:18]
response = load_data()
for s in response:
    post_to_sheet(
            datetime.datetime.strptime(s['opened'], '%Y-%m-%dT%H:%M:%S.000Z'),
            s['totalCard'], 
            s['totalCash'],
            s['ordersCount'],
            round((s['totalCard']+s['totalCash'])/(s['ordersCount']), 1),
            s['totalCard']+s['totalCash']
            )