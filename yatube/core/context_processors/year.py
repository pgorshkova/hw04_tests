import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    year = datetime.datetime.now().year
    return {
        'year': int(year)
    }
