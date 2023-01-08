import requests
import json

'''
1. Выгрузка выручка за день(нал безнал), кол-во чеков и средний чек за день, кол-во нал в кассе, топ за день(3-5)
2. Инфо о бонусном счете клиента (бунусы, фамилия, телефон, день рождения) инфо о тратах, топ блюд, топ напитков
Новинки, наши топы (за месяц)
http://test.quickresto.ru/platform/online/api/get?moduleName=warehouse.providers&amp;objectId=1
'''

'''
Таблица, дата выгрузки (при смене информации вывождить инфу(кофнтейнер, производитель, дата была\стала))
'''

login = 'kosplace'
password = 'e0LDx023'
url = 'https://kosplace.quickresto.ru/platform/online/api/get'
headers = {
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
}
data = dict(
    moduleName='front.zreport',
    objectRId='closed',
    objectId='1'
)
response = requests.get(url=url, auth=(login,password), headers=headers, params=data)
print(response.url)
print(response)
print(response.headers)
with open('text.json', 'w') as t:
    json.dump(response.json(), t)