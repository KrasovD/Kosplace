import datetime
import requests
import json

import config


class Zreport():
    def _datetime_format(self, date) -> str:
        timedelta = datetime.timedelta(hours=3)
        return (datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta).strftime('%d.%m %H:%M')

    def _opened(self, data):
        return self._datetime_format(data)
    
    def _closed(self, data, status):
        if status == 'CLOSED':     
            return self._datetime_format(data)
        else:
            return 'открыта'
    
    def _productOutgoing(self, data):
        if data:
            dish = list()
            for check in data:
                try:
                    dish.append((
                        check['product']['name'],
                        round(abs(check['amount'])),
                        round(check['product']['basePriceInList'] * abs(check['amount']))))
                except Exception as e:
                    print(e)
            return dish
        else:
            return None
        
    def _avg_check(self):
        if self.ordersCount != 0:
            return round((self.totalCard + self.totalCash) / self.ordersCount)
        else:
            return 0
    def _terminal(self, kkmTerminal):
        if kkmTerminal['id'] == 3:
            return 'Бородинская 2/86'
        if kkmTerminal['id'] == 5:
            return 'Коменданский 65'

    def __init__(self, id = None, opened = None, closed = None, 
                 totalCash = None, totalCard = None, 
                 ordersCount = None, totalCashIn = None, 
                 totalCashOut = None, productOutgoing = None,
                 shiftNumber = None, status = None,
                 openedEmployee = None, kkmTerminal = None, **kwargs):
        self.id = id
        try:
            self.open = (datetime.datetime.strptime(opened, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3))
            self.opened = self._opened(opened)
            self.closed = self._closed(closed, status)
        except:
            self.open = datetime.datetime.now() - datetime.timedelta(days=300)
        self.totalCard = round(totalCard)
        self.totalCash = round(totalCash)
        self.ordersCount = ordersCount
        self.openedEmployee = openedEmployee
        self.totalCashIn = round(totalCashIn)
        self.totalCashOut = round(totalCashOut)
        self.productOutgoing = self._productOutgoing(productOutgoing)
        self.avg_check = self._avg_check()
        self.shiftNumber = shiftNumber
        self.status = status
        self.total = round(totalCard) + round(totalCash)
        self.terminal = self._terminal(kkmTerminal)

    def __repr__(self) -> str:
        return '%s, %s, %s' % (self.shiftNumber, self.productOutgoing, self.status)
    
class Encashment():  

    def __init__(self, amount = None, shift = None, typeTransaction = None,
                 comment = None, **kwargs):
        self.amount = amount
        self.shift_id = shift['id']
        self.type = typeTransaction
        self.comment = comment
        

class Api():
    '''
    Обьект основной информации выгруженной их API QuickResto
    '''

    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    # url для входа в API QuickResto
    URL = 'https://{login}.quickresto.ru/platform/online/'.format(login=config.login)

    def _json_format(self, data) -> str:
        '''Преобразование словаря в читаемый API QR формат'''
        return str(data).replace('\'', '"').replace(' ', '').encode('utf-8')
    
    def _get(self, url, params) -> requests:
        '''Get запрос в API QuickResto и возврат в json формате'''
        return requests.get(url=url, auth=(config.login, config.password), headers=self.headers, params=params).json()

    def list_zreport(self) -> list:
        ''' выгрузка из API данных о всех сменах без подробностей '''

        url = self.URL + 'api/list'
        params = {
            'moduleName': 'front.zreport',
        }
        return [Zreport(**shift) for shift in self._get(url, params)]
    
    def get_zreport(self, id) -> Zreport:
        ''' Выгрузка из API данных об определенной смене (id смены) с подробностями '''

        url = self.URL + 'api/read'
        params = {
            'moduleName':'front.zreport',
            'objectId': id,
        }
        return Zreport(**self._get(url, params))
    

    def list_encashment(self) -> list:
        ''' выгрузка из API данных об инкассации '''

        url = self.URL + 'api/list'
        params = {
            'moduleName': 'front.encashment',
        }
        #return self._get(url, params)
        return [Encashment(**shift) for shift in self._get(url, params)]


def closed_zreport(z_report: Zreport, z_encas: Encashment = ''):
    # формирование отчета о смене

    if z_encas != '':
        cashOut = ''
        cashIn = ''
        for encas in z_encas:
            if encas.type == 'cashOut':
                cashOut += '<code>{} - {}\n</code>'.format(encas.amount, encas.comment)
            if encas.type == 'cashIn':
                cashIn += '<code>{} - {}\n</code>'.format(encas.amount, encas.comment)
    else:
        cashIn = ''
        cashOut = ''
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
    {}
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
    z_report.terminal,
    'Время открытия:', ' '* space('hh:mm', 'Время открытия:'), z_report.opened,
    'Время закрытия:', ' '*space('hh:mm', 'Время закрытия:'), z_report.closed,
    'Наличные:', ' '*space('Наличные:', z_report.totalCash, ' руб'), z_report.totalCash, ' руб',
    'Карта:', ' '*space('Карта:', z_report.totalCard, ' руб'), z_report.totalCard, ' руб',
    'Чеков:', ' '*space('Чеков:', z_report.ordersCount), z_report.ordersCount,
    'Средний чек:', ' '*space('Средний чек:', z_report.avg_check, ' руб'),  z_report.avg_check, ' руб',
    'Итого:', ' '*space('Итого:', z_report.totalCash + z_report.totalCard, ' руб'), z_report.totalCard + z_report.totalCash, ' руб', 
    'Внесение:', ' '*space('Внесение:', z_report.totalCashIn, ' руб'), z_report.totalCashIn, ' руб',
    cashIn,
    'Изьятие:', ' '*space('Изьятие:', z_report.totalCashOut, ' руб'), z_report.totalCashOut, ' руб',
    cashOut
    )
    return text

def top_dish(terminal, list_dish, sort) -> str:
    text = ''
    try:
        if len(list_dish) < 5:
            result = sorted(list_dish, key=lambda x: x[sort], reverse=True)[:len(list_dish)]
            text += '<code>Кофейня: {}\n</code>'.format(terminal)
            for i in range(len(list_dish)):
                text += '<code>{0}. {1}: {2} руб ({3} шт)\n</code>'.format(i+1, result[i][0], round(result[i][2]), round(result[i][1]))
            return text
        else:
            result = sorted(list_dish, key=lambda x: x[sort], reverse=True)[:5]
            text += '<code>Кофейня: {}\n</code>'.format(terminal)
            for i in range(5):
                text += '<code>{0}. {1}: {2} руб ({3} шт)\n</code>'.format(i+1, result[i][0], round(result[i][2]), round(result[i][1]))
            return text
    except:
        pass

def shift_info(info, place: set):
    ''' Собирает информацию из Апи и 
    выводит отчеты ('z_report'), 
    топ позиции по сумме ('dish_by_sum'), 
    топ позиции по кол-ву('dish_by_count')
    place (Коменданский 65, Бородинская 2/86)'''

    api = Api()
    list_shift = api.list_zreport()
    time_now = datetime.datetime.now()
    for shift in list_shift:
        if shift.open.date() == time_now.date() and shift.terminal in place:
            z_report = api.get_zreport(shift.id)
            if info == 'z_report':
                yield closed_zreport(z_report)
            if info == 'dish_by_sum':
                yield top_dish(z_report.terminal, z_report.productOutgoing, 2)
            if info == 'dish_by_count':
                yield top_dish(z_report.terminal, z_report.productOutgoing, 1)
            

if __name__ == '__main__':
    api = Api()
    l = api.list_encashment()
    with open('encas.json', 'w') as w:
        json.dump(l,w)

