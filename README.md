## «Фудграм» — площадка, на которой люди могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок», позволяющий создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск проекта в контейнерах Docker:

### Клонируем проект:

git clone git@github.com:kamilisx/foodgram-project-react.git


### Создаем .env-файл с необходимыми переменными:

    POSTGRES_USER=user_postg
    POSTGRES_PASSWORD=user_password
    POSTGRES_DB=foodgram_db
    DB_NAME=db
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=secret
    DEBUG = False
    ALLOWED_HOSTS = 127.0.0.1, localhost, host

### Собераем и запускаем контейнеры, собираем статику и создаем superuser

```
cd ..
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend python manage.py createsuperuser
```
### Загружаем базу данных ингредиентов

```
docker compose exec backend python manage.py write_from_csv_to_db
```

### Проект запущен и доступен по адресу http://edagramm.ddns.net/

### Технологии:

	• Python 3.9
	• Django 3.2.3
	• gunicorn 20.1.0
	• Доменное имя: https://www.noip.com

### Авторы: Frontend - Яндекс Практикум, Backend - Исхаков Камиль
