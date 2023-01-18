from pprint import pprint
from datetime import datetime
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


# Файл, полученный в Google Developer Console
CREDENTIALS_FILE = 'creds.json'
# ID Google Sheets документа (можно взять из его URL)
spreadsheet_id = '1_Zkm2gAtJl2TeA5r8vtRqF8dYEajmUafRCVo_vTeSIc'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

def get_values():
# Пример чтения файла
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='A1:C35',
        majorDimension='COLUMNS'
    ).execute()
    range = 'A{0}:F{0}'.format(len(values['values'][0])+1)
    return range

def post_values(range:str, values:list):
    # Пример записи в файл
    values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": range,
                "majorDimension": "ROWS",
                "values": [values]},
        ]
        }
    ).execute()


def post_to_sheet(date:datetime, card, cash, count, avg, total):
    try:
        range = "'{0}'!{1}".format(date.strftime("%m.%Y"), get_values())
        dt = [
        "{}".format(date.strftime("%d.%m")),
        "{}".format(cash),
        "{}".format(card),
        "{}".format(count),
        "{}".format(avg),
        "{}".format(total)
        ]
        post_values(range, dt)
    except:
        pass
