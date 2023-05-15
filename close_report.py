import telebot
import time, datetime
import pygsheets
from sqlalchemy import create_engine, insert, select

from model import z_report, user_id
import config
from api import Api, closed_zreport

bot = telebot.TeleBot(config.TOKEN)
client = pygsheets.authorize(service_file='creds.json')
engine = create_engine('sqlite:///kos_report.db')
sheet = client.open_by_key('1_Zkm2gAtJl2TeA5r8vtRqF8dYEajmUafRCVo_vTeSIc')
api = Api()

while True:
    time_now = datetime.datetime.now()
    list_shifts = api.list_zreport()
    list_encas = api.list_encashment()
    with engine.connect() as conn:
        db_shift = conn.execute(select(z_report.c.shift_id, z_report.c.terminal)).all()
    for shift in list_shifts:
        if shift.open.date() == time_now.date() and shift.status == 'CLOSED' and \
        shift.terminal in ('Коменданский 65', 'Бородинская 2/86') and \
        (shift.id, shift.terminal) not in db_shift:
            
            data_shift = insert(z_report).values(
                    shift_id=shift.id,
                    terminal=shift.terminal,
                    open_date=shift.open,
                    cash=shift.totalCash,
                    card=shift.totalCard,
                    count=shift.ordersCount,
                    avg_check=shift.avg_check,
                    total=shift.total
                    )
            with engine.connect() as conn:
                result = conn.execute(data_shift)
                conn.commit()

            shift_data = [
                (shift.open.date()).strftime('%d.%m'), 
                shift.totalCash, 
                shift.totalCard, 
                shift.ordersCount, 
                shift.avg_check, 
                shift.totalCash+shift.totalCard
                ]       
            sheet_name = (str(shift.open.month) + '.' + str(shift.open.year))
            try:
                wks = sheet.worksheet_by_title(sheet_name)
            except:
                sheet.add_worksheet(sheet_name)
                wks = sheet.worksheet_by_title(sheet_name)
                wks.update_values('A1:F2', [
                    ['','','Бородинская', '', '', ''],
                    ['Дата', 'Нал', 'Безнал', 'Чеков', 'Ср. чек', 'Итого']])
                wks.update_values('A37:C37', [['Дата', 'Сумма', 'Комментарий']])
                wks.update_values('H1:M2', [
                    ['','','Коменданский', '', '', ''],
                    ['Дата', 'Нал', 'Безнал', 'Чеков', 'Ср. чек', 'Итого']])
                wks.update_values('H37:J37', [['Дата', 'Сумма', 'Комментарий']])
                
            def send_report(range_report, range_encas):
                sheet_values = wks.get_values(range_report[0], range_report[1])  
                sheet_values.append(shift_data)
                wks.update_values(range_report[0]+':'+range_report[1], sheet_values)
                all_encas = list()
                for encas in list_encas:
                    if encas.shift_id == shift.id:
                        all_encas.append(encas)
                    if encas.shift_id == shift.id and encas.type == 'cashOut' and \
                    encas.comment != "\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0438\u043d\u043a\u0430\u0441\u0441\u0430\u0446\u0438\u044f":
                        sheet_values = wks.get_values(range_encas[0], range_encas[1])  
                        sheet_values.append([
                            (shift.open.date()).strftime('%d.%m'), 
                            encas.amount,
                            encas.comment])
                        wks.update_values(range_encas[0]+':'+range_encas[1], sheet_values)   
                with engine.connect() as conn:
                    users = conn.execute(select(user_id.c.user_id)).all()
                for user in users:
                    try:
                        bot.send_message(chat_id=user.user_id, text=closed_zreport(shift, all_encas), parse_mode='HTML')
                    except:
                        pass

            if shift.terminal == 'Коменданский 65':
                send_report(['H2', 'M36'], ['H37', 'J60'])
            if shift.terminal == 'Бородинская 2/86':
                send_report(['A2', 'F36'], ['A37', 'C60'])
    time.sleep(300)

