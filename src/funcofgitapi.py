import requests
from config.gitToken import token
import re
import zipfile
from io import BytesIO

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "Accept-Encoding": "identity"
}


def get_workflow_runs_by_sha(repo, commit_sha): # Получаем run id коммита
    url = f"https://api.github.com/repos/{repo}/actions/runs"
    params = {"head_sha": commit_sha}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        runs = response.json()
        return runs['workflow_runs']
    else:
        print(f"Не удалось получить workflow runs для commit_sha: {commit_sha}")
        return None


def get_workflow_run_log_archive(repo, run_id): # Получаем логи проведенных тестов
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        zip_file = BytesIO(response.content)
        return zip_file
    else:
        print(f"Не удалось получить архив логов для run_id: {run_id}")
        return None


def extract_and_read_zip(zip_file): # Распаковываем и читаем архив логов (чтение логов напрмую через запрос невозможно из-за сжатия логов)
    logs = ""
    with zipfile.ZipFile(zip_file) as archive:
        for file_name in archive.namelist():
            with archive.open(file_name) as log_file:
                file_logs = log_file.read().decode('utf-8', errors='ignore')
                logs += file_logs
    return logs


def find_taskid_in_logs(logs):
    print("Поиск TASKID в логах...")
    match = re.search(r'TASKID\s+is\s+(\d+)', logs)
    if match:
        taskid = match.group(1)
        print(f"TASKID найден: {taskid}")
        return taskid
    else:
        print("TASKID не найден в логах.")
        return 0


def check_all_tests_passed(repo, runs):
    taskid = 0
    for run in runs:
        run_id = run['id']
        print(f"Получение логов для run_id: {run_id}...")
        zip_file = get_workflow_run_log_archive(repo, run_id)
        if zip_file:
            logs = extract_and_read_zip(zip_file)
            if logs:
                taskid = find_taskid_in_logs(logs)
                if taskid != 0:
                    return taskid
        else:
            print(f"Архив логов для run_id {run_id} не найден.")
    
    return taskid


def get_commits(repo):
        url = f"https://api.github.com/repos/{repo}/commits"
        response = requests.get(url, headers=headers)
        commits = response.json()
        return commits


def get_workflow_runs(repo, commit_sha):
    url = f"https://api.github.com/repos/{repo}/actions/runs"
    params = {"head_sha": commit_sha}
    response = requests.get(url, headers=headers, params=params)
    runs = response.json()
    return runs


def get_commit_files(repo, sha):
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        commit_data = response.json()
        files = commit_data['files']
        return files
    else:
        print(f"Не удалось получить файлы для commit_sha: {sha}")
        return None




def parse_test_paths(repo_name, text_in_cfg,  config_file="src/checktests.txt"):
    """Парсинг конфигурационного файла для получения путей (директорий и файлов) и исключений."""
    with open(config_file, "r") as file:
        for line in file:
            repo_config = line.strip().split(":")
            if repo_config[0] == text_in_cfg:
                paths = []
                exclusions = {}

                path_entries = repo_config[1].split(",") if repo_config[1].strip() else None
                if path_entries:
                    for entry in path_entries:
                        if "[!" in entry:  # Если есть исключения
                            dir_path, excl_part = entry.split("[!")
                            excl_items = excl_part.rstrip("]").split(",")
                            exclusions[dir_path] = excl_items
                            paths.append(dir_path)
                        else:
                            paths.append(entry)
                return paths, exclusions
    return None, None


def get_commit_files(repo, sha):
    """Получить список файлов, измененных в коммите."""
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commit_data = response.json()
        return [file['filename'] for file in commit_data['files']]
    else:
        print(f"Не удалось получить файлы для commit_sha: {sha}")
        return []


def is_excluded(file, path, exclusions):
    """Проверить, исключен ли файл или директория из проверки."""
    excluded_items = exclusions.get(path, [])
    for excl_item in excluded_items:
        if excl_item.endswith("/") and file.startswith(path + excl_item):
            # Исключение поддиректории
            return True
        elif file == path + excl_item:
            # Исключение отдельного файла
            return True
    return False


def check_test_paths_modified(changed_files, test_paths, exclusions):
    """Проверить, изменялись ли файлы или директории, указанные в конфиге, с учетом исключений."""
    for file in changed_files:
        for path in test_paths:
            if file.startswith(path):
                if not is_excluded(file, path, exclusions):
                    print(f"Изменение в тестовом файле или директории: {file}")
                    return True
    return False


def check_changes(repo_name, sha, text_in_cfg):
    # Получаем директории, файлы для проверки и исключения для данного репозитория
    test_paths, exclusions = parse_test_paths(repo_name, text_in_cfg)
    
    if test_paths is None:
        print(f"Проверка для репозитория {repo_name} не требуется.")
        return 1
 
    # Получаем измененные файлы для данного коммита
    changed_files = get_commit_files(repo_name, sha)
    if not changed_files:
        print(f"Не удалось получить измененные файлы для коммита {sha}.")
        return -2

    # Проверяем, были ли изменены указанные файлы или директории с учетом исключений
    test_files_modified = check_test_paths_modified(changed_files, test_paths, exclusions)
    if test_files_modified:
        print("Тестовые файлы или директории были изменены.")
        return 0
    else:
        print("Тестовые файлы или директории не были изменены.")
        return 1


def check_file_in_commit(repo, sha, filename):
    """Проверить, есть ли файл с именем filename в указанном коммите."""
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        commit_data = response.json()
        files = commit_data.get('files', [])
        for file_info in files:
            if file_info['filename'] == filename:
                return 1
    return 0

"""Здесь файл просто с набором функций для работы с гитапи, к ним есть небольшие комментарии, и если посмотреть немного и поразбираться, то можно понять,
что происходит. Расписывать возле каждой функции, что она делает, я не хочу. По кратиким коментам и названиям, я думаю, все будет понятно))))"""


