from typing import Optional
from pydantic import BaseModel


class requestModel(BaseModel):
    group_number: str
    login: str
    
    
class check_tests(requestModel):
    number_of_lab: int

    
class exist_user(requestModel):
    ok: bool = True
    #user_id: int
    login: str
    num_in_list: int
    status: str
    
class return_info_lab(check_tests):
    ok: bool = True
    status: str
    
class fill_fields(BaseModel):
    flag: list[int]
    num_in_list: int
    num_of_lab: int
    group_number: int
    
    
"""Этот файл используется для указания передаваемых в функции параметров и возвращаемых.
Важно заметить, что первый класс, наследуется от класса basemodel, который, если перейти в документацию, позволяет передавать классы, 
структуры различного вида и возвращать их же. Все остальные наследуется от других классов, копируя их поля."""