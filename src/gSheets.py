import os

from googleapiclient.errors import HttpError

from config.config import sheet_id
from src.models.model import requestModel, exist_user, fill_fields
from src.gSheetsSet import get_sheet

SPREADSHEET_ID = sheet_id


class google_sheets:
    @classmethod
    async def check_user(cls, data: requestModel) -> exist_user: #Эта функция отвечает за получение данных из гугл таблицы по введеным в сваггере значениям
        try:
            sheet = get_sheet().spreadsheets() #Тут происходит настройка подключения к таблице
            user_dict = data.model_dump() #здесь мы парсим переданные в функцию данные в словарь
            l = user_dict["group_number"] #Устанавливаем параметры для таблицы, а именно название листа - № группы
            range_ = f"{l}!A:AH" #тут задаем диапозон таблицы, который собираемся получить
            
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range_).execute() #тут выполняем получение данных
            values = result.get("values", []) #парсим данные в массив
            flag = 0
            if not values:
                return {"ok": False, "login": user_dict["login"], "num_in_list": -1} #ну и просто проверки
            else:
                match_found = 0
                for row in values:
                    try:
                        # Номер по списку (первый столбец)
                        num = row[0]
                        # Ник GitHub (последний столбец, 32-й в этом примере)
                        github_nick = row[33]
                        """Если необходима проверка на ФИО, то нужно добавить в model ввод ФИО, а после распарсить тут и вставить сравнение с row[1]"""

                        # Проверка совпадения номера лабораторной и ника GitHub
                        if github_nick == user_dict["login"]:
                            print(f"Совпадение найдено: Номер по списку: {num} GitHub: {github_nick}")
                            match_found = 1
                            return {"ok": True, "login": github_nick, "num_in_list": num}  # Прекращаем поиск после первого совпадения
                    except IndexError:
                        print("Некорректная строка, пропускаем...")

                if not match_found:
                    return {"ok": False, "login": user_dict["login"], "num_in_list": -2} #Никого не нашли, в router.py обработаем эту ошибку по флагу в "num_in_list"
                    
              
            # Добавить проверку наличия идентификатора (тг, дискорд), если нужна
            
        except HttpError as error:
            print(error)
            
    
    @classmethod
    async def exists_list(cls, group_num: str) -> int: # проверка существования нужной таблицы)
        try:
            service = get_sheet()
            
            spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute() #все просходит аналогично, только парсим сразу все листы и ещем нужный
            sheets = spreadsheet.get("sheets", [])                                                                                #сравнивая с помощью ключа
            
            for sheet in sheets:
                if sheet["properties"]["title"] == group_num:
                    return 1
            
        except HttpError as error:
            print(error)

        return 0
    
    @classmethod
    async def write_in_field(cls, data: fill_fields) -> bool: #функция для записи в таблицу (метод put)
        service = get_sheet()
        col_letter = chr(ord('C') + data.num_of_lab) # парсим нужные нам данные
        row_number = data.num_in_list + 2
        cell_range = f'{data.group_number}!{col_letter}{row_number}' # устанавливаем диапозон (ячейку), куда собираемся писать
        if data.flag[1] == 0: #проверка на флаги, думаю тут все понятно, расписывать не надо
            if data.flag[0] == 0:                                  #единственное отмечу, что data.flag представлены массивом интов только для проверки 4-ой лабы
                value = [["v*0.5"]]                                #я сделал это в последний момент, просто, что первое пришло в голову
            elif data.flag[0] > 0:                                 #проверил у себя, ничего не отвалилсоь, но у меня два алгоритма, так что советую проверить это
                value = [[f"v*0.5-{data.flag[0]}"]]                #на своем компе, мало ли, если вдруг будет отваливаться, напиши, я помогу исправить
        elif data.flag[0] == 0:                                      #на скорость это никак не должно влиять
            value = [["v"]]
        elif data.flag[0] > 0:
            value = [[f"v-{data.flag[0]}"]]
        elif data.flag[0] == -2:
            value = [["WRONG TASKID"]]
        elif data.flag[0] == -4:
            value = [["TEST CHANGED"]]
        else:
            return 0
        
        body = {
        'values': value
        }
        result = service.spreadsheets().values().update( #здесь просто заполнение тела функции обновления ячейки
            spreadsheetId=SPREADSHEET_ID,
            range=cell_range,
            valueInputOption="RAW",
            body=body
        ).execute()
        
        print(f'{result.get("updatedCells")} ячеек обновлено.')
        
        return 1
    
    """Этот файл отвечает за работу с апи гугл таблиц, из импортируемых модулей можно увидеть, что присутствует файл gSheetsSet - это настройка соединения с апи,
    в нем я тое опишу, что и как)
    sreadsheetID - написанное капсом, я получаю из файла 'config/config.py - там хранится айди гугл таблицы (в видосе я показывал, откуда его взять, если будет
    непонятно, напиши))"""