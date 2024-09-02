ПРОИЗВОДСТВЕННАЯ ПРАКТИКА 2024

Для запуска проекта необходимо следующее:

1) Клонировать репозиторий
1) Создать папку .venv командой python3 -m venv venv
1) Использовать команду pip install -r requirements.txt
1) В файле config/config.py создать переменную sheet\_id и вставить токен таблицы
1) В файле config/gitToken.py создать переменную token и вставить токен авторизации GitHub
1) Получить доступ к API для Google Sheets в сервисе Google Cloud, скачать Client Secret в формате json, переименовать файл в credential.json и поместить в папку config
