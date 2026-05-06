# Настройка проекта TeamFinder
**Работа выполнена с учетом требований Варианта 1**

1. **Создайте виртуальное окружение:**
   ```bash
   python3 -m venv venv
   ```

2. **Активируйте окружение:**

    - **Windows (PowerShell):**
      ```bash
      venv\Scripts\Activate.ps1
      ```
    - **Windows (cmd):**
      ```bash
      venv\Scripts\activate
      ```
    - **Linux/Mac:**
      ```bash
      source venv/bin/activate
      ```

3. **Установите зависимости из `requirements.txt`:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запуск PostgreSQL**
```bash
docker compose up -d
```

5. **Выполните миграции**
```bash
python manage.py migrate
```

6. **Создайте суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Запустите сервер**

```bash
python manage.py runserver
```

### Тестовые данные для проверки

Для быстрой проверки функциональности проекта используйте следующие учётные записи:

**Обычный пользователь:**
- Email: `kruivan@mail.ru`
- Пароль: `1234Krutov`

**Администратор:**
- Создайте суперпользователя командой: `python manage.py createsuperuser`
- Админ-панель: `http://localhost:8000/admin`
