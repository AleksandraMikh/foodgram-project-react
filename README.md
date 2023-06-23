# Foodgram, платформа с рецептами
## Учебный проект
- [x] написан backend
- [x] настроен CI/CD (тесты + контейнеризация + деплой)


# Деплой на:
Адрес: http://158.160.66.255/

Логин: admin

Почта: admin@admin.ru

Пароль: admin

_сейчас не поддеживается_




# Для запуска проекта локально выполни

```
git clone https://github.com/AleksandraMikh/foodgram-project-react.git
cd foodgram-project-react
python3 -m venv venv
source venv/bin/activate
cd backend/foodgram_project/
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Зайди через браузер на http://localhost:8000/admin/ и введи учётные данные суперпользователя, чтобы увидеть админ-зону.


Для загрузки csv из директории, содержащей mamnge.py, выполни команду 

```
python manage.py set-ingredients
```
