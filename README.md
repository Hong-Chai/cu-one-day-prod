# Я предод? by Team34

## Описание
Хороший эксперт - не равно хороший преподаватель. Наш IT продукт помогает начинающим преподавателям сделать свои лекции доступными для понимания студентами.

*Проект выполнен в рамках Буткэмпа с ЦУ.*

## Необходимое ПО
- [Python 3.13](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)


## Установка
1. Создайте виртуальное окружение:
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    venv\Scripts\activate
    ```

2. Установите необходимые библиотеки:
    ```bash
    pip install -r requirements.txt
    ```
## Конфигурация приложения

1. Скопируйте файл ```template.env``` в ```.env```
    ```bash
    # linux / macOS
    cp template.env .env
    # windows
    copy template.env .env
    ```

2. Заполните файл ```.env```
> [!IMPORTANT]
> Для работы приложения необходим ключ Mistral AI API, получить можно на их сайте (есть бесплатный тариф)

## Настройка перед запуском
Перед запуском мигрируйте БД, создайте суперпользователя
```bash
cd prepod 
python manage.py migrate
python manage.py createsuperuser # далее следуйте инструкциям
```

## Запуск dev режима
Без ```.env``` файла, по умолчанию DEBUG=True
```bash
cd olymptest # НЕ нужно, если уже в каталоге с прошлого этапа
python manage.py runserver 
```
Проект будет запущен на [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/)

Админка будет доступна на [`http://127.0.0.1:8000/admin/`](http://127.0.0.1:8000/admin/)


## Особые пожелания
Всем читающим эту скучную пачку документации, теплый привет! ❤ *(Писать это еще скучнее..)*

