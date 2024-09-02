from datetime import datetime


def read_date_for_repo(repo_name, filepath="src/dates.txt"):
    """Считать дату из файла для конкретного репозитория."""
    with open(filepath, "r") as file:
        for line in file:
            repo_config = line.strip().split(":")
            if repo_config[0] == repo_name:
                return datetime.strptime(repo_config[1], "%Y-%m-%d")
    return None


def calculate_weeks_difference(date1, date2):
    """Рассчитать количество недель между двумя датами."""
    delta = date1 - date2
    if delta.days < 7 and delta.days > 0:
        return 1  # Если неделя еще не прошла
    elif delta.days < 0:
        return 0
    return delta.days // 7


def result(num_lab, comparison_date=None, date_file_path="src/dates.txt"):
    file_date = read_date_for_repo(num_lab, date_file_path)
    print(file_date)
    if isinstance(comparison_date, str):  # Если передана строка
        try:
            comparison_date = datetime.strptime(comparison_date, "%Y-%m-%d")
            print(comparison_date)
        except ValueError:
            print("Некорректный формат даты. Ожидается формат YYYY-MM-DD.")
            return -1
    elif isinstance(comparison_date, datetime):
        print(f"Дата передана в формате datetime: {comparison_date}")
    else:
        print("Не передана дата для сравнения или неверный формат.")
        return -1
    return calculate_weeks_difference(comparison_date, file_date)
    
