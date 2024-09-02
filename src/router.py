from fastapi import APIRouter, Depends
from typing import Annotated

from src.models.model import requestModel, check_tests, exist_user, return_info_lab, fill_fields
from src.gSheets import google_sheets
from src.githubapi import GitHub

router = APIRouter( #создание рутера с тегами и префиксами
    prefix="/methods",
    tags=["Эндпоинты"]
)


@router.get("/get") #рутер для гет запроса на проверку наличия стунда с введенным логином гита в таблице
async def check_user_exists(request: Annotated[requestModel, Depends()]) -> exist_user:
    list_ = await google_sheets.exists_list(request.group_number)
    if (list_):
        data = await google_sheets.check_user(request)
        print()
        if list_ == "График":            #обычный набор проверок))))
            return {"ok": False, "login": request.login, "num_in_list": 0, "group_number": request.group_number, "status": "В графике нет студентов!"}
        if int(data["num_in_list"]) > 0:
            return {"ok": True, "login": request.login, "num_in_list": int(data["num_in_list"]), "group_number": request.group_number, "status": "Пользователь найден!"}
        elif int(data["num_in_list"]) == -1:
            return {"ok": False, "login": request.login, "num_in_list": 0, "group_number": request.group_number, "status": "Таблица пуста!"}
        elif int(data["num_in_list"]) == -2:
            return {"ok": False, "login": request.login, "num_in_list": 0, "group_number":  request.group_number, "status": "Нет студента с таким аккаунтом GitHub!"}
        
    else:
        return {"ok": False, "login": request.login, "num_in_list": 0, "group_number": request.group_number, "status": "Такой группы нет!"}
    
    
@router.put("/put") #рутер для пост запрос, осуществляется проверка из запроса гет, в дальнейшем происходи проверка репозитория на успешный коммит
async def check_commit(request: Annotated[check_tests, Depends()]) -> return_info_lab:
    login = request.login
    
    list_ = await google_sheets.exists_list(request.group_number)
    if (list_):
        data = await google_sheets.check_user(request)
        if data["ok"]:
            num_of_user = int(data["num_in_list"])
        else:
            return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Не могу найти студента с таким логином!"}
    else:
        return {"ok": False, "login": request.login, "num_in_list": 0, "group_number": request.group_number, "status": "Такой группы нет!"}
    
    number_of_lab = request.number_of_lab
    
    res = GitHub.check_commit(number_of_lab, login, num_of_user) #тут сразу проверятся успешность коммита, изменение тестов, наличие taskid, результат функции - флаг об ошибке или количество снятых за просрок баллов
    data_for_fields = fill_fields(flag=res, num_in_list=num_of_user, num_of_lab=number_of_lab, group_number=request.group_number) #заполнение структуры для передачи в функцию заполнения гугл таблицы
    flag = await google_sheets.write_in_field(data_for_fields)
    if (res[0] == -5):
        return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Успешных коммитов не найдено!"}
    elif res[0] == -4:
        if flag:
            return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Найдены изменения в файлах с тестами!"}
        else:
             return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Найдены изменения в файлах с тестами! Данные не были записаны"}
    elif res[0] == -3:
        return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Файл с вариантом не найден!"}
    elif res[0] == -2:
        if flag:
            return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Неверный TASKID!"}
        else:
            return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Неверный TASKID! Данные не были записаны"}
    elif res[0] == -1:
        return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": "Шо-то с датой!"}
    elif res[0] == 0:
        if res[1] == 1:
            if (flag):
                return {"ok": True, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены, все в срок!"}
            else:
                return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены, все в срок! Данные не были записаны!"}
        else:
            if (flag):
                return {"ok": True, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены, все в срок, половина баллов за один алгоритм снята!!!"}
            else:
                return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены, все в срок, половина баллов за один алгоритм снята!!! Данные не были записаны!"}
    else:
        if res[1] == 1:
            if (flag):
                return {"ok": True, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены. Результат из-за просроченного дедлайна меньше на {res[0]}!"}

            else:
                return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены. результат из-за просроченного дедлайна меньше на {res[0]}! Данные не были записаны"}
        else:
            if (flag):
                return {"ok": True, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены, половина баллов за один алгоритм снята!!! Результат из-за просроченного дедлайна меньше на {res[0]}!"}

            else:
                return {"ok": False, "number_of_lab": number_of_lab, "login": login, "group_number": request.group_number, "status": f"Тесты пройдены, половина баллов за один алгоритм снята!!! Результат из-за просроченного дедлайна меньше на {res[0]}! Данные не были записаны"}
        
"""Просто набор огромного количества проверок, все из-за возвращаемых значений одной функцией, в ней идет проверка на дату, пройденные тесты, верный вариант, 
изменение файлов с тестами (задаются в текстовом файле 'src/checktests.txt', в конструкция вида - '[!...]' - записываются файлы для исключения)

Проверка даты осуществляется с помощью функций из 'src/dates.py', котоыре извлекают даты для лабораторных работ из файла - 'src/dates.txt'. 
Вычисление проводится разницей между 2 датами. Если разница < 0, то колво баллов не уменьшается, если > 0 and < 7, то баллы за лабу уменьшаются на 1, дальше идет целочисленное деление на 7.


"""


    
    