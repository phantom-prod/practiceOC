from src.funcofgitapi import *
from src.dates import *
from datetime import datetime


def take_variant(lab, taskid):
    if lab == 2:
        if taskid < 17:
            return taskid + 4
        elif taskid > 16:
            return taskid - 16
    elif lab == 3:
        if taskid < 21:
            return taskid
        else:
            return taskid % 20
    else: return taskid


class GitHub:
    @classmethod
    def check_commit(cls, lab: int, nick: str, num_in_list: int) -> list[int]:
        REPO_OWNER = "suai-os-2024"
        repo = f"{REPO_OWNER}/os-task{lab}-{nick}"
        commits = get_commits(repo)
        sha = 0
        flag = 1
        commit_date = 0
        for commit in commits:
            sha = commit['sha']
            commit_date = commit['commit']['committer']['date']
            runs = get_workflow_runs(repo, sha)
            
            if runs['total_count'] > 0:
                all_tests_passed = True
                for run in runs['workflow_runs']:
                    if run['conclusion'] != 'success':
                        all_tests_passed = False
                        break
                
                if all_tests_passed:
                    print(f"Первый коммит, прошедший все тесты: {sha}, дата коммита: {commit_date}")
                    
                    break
                
        if commit_date == 0:
            return [-5, flag] # not detected successful commit
        id = 0
        workflow_runs = get_workflow_runs_by_sha(repo, sha)
        if workflow_runs:
            id = check_all_tests_passed(repo, workflow_runs)
        print("TASKDID is ", id)
        taskid = int(id)
        if taskid == 0 and lab != 0:
            return [-3, flag] # file with taskid not detected
        #var = take_variant(lab, taskid)
        if lab == 2 or lab == 3:
            if taskid != take_variant(lab, num_in_list):
                return [-2, flag]# flag of wrong taskid
        elif lab == 0:
            print("Лабораторная работа 0 без варианта!")
        else:
            if num_in_list != taskid:
                return [-2, flag]
            
        flag_of_changes = check_changes(repo, sha, lab)
        if flag_of_changes == 0:
            return [-4, flag] # detected changes in file
        
        date = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
        
        res = result(str(lab), date)
        if lab == 4: # проверка в 4 работе на наличие файла, который указывает об 1 сделанном алгоритме)
            flag = check_file_in_commit(repo, sha, "ALGORITHM.txt")

        return [res, flag]
        
"""Этот файл для проверки коммита
Сначала проверяется наличие успешных коммитов, потом отбирается самый первый (щас я понимаю, что логики уже немного из-за того, что если на первом вылетит какой-то 
нюанс, то и все дальнейшие проверки накроются, просто нужно убрать reversed на 30 строке)
вместе с этим мы получаем дату этого коммита, которую потом закинем в функции для сравнения м вывода колва -баллов, но перед этим проверяем на наличие верного таскид,
который совпадает с номером в гугл таблице (для 2 и 3 лабы, которые на графы, специально сделана отдельная функция вычисления нужного таксид))
Потом идет проверка на изменение файлов с тестами - питоновский файл src/funcofgitapi.py - содержит все функцию, который вызываются тут, а файл checktests.txt -
- предзназначен для проверки файлов, которые не должны изменяться."""