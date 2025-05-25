# create_db.py
import sqlite3

# Подключение к базе данных (файл создается автоматически)
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Создание таблицы, если она не существует
query = (""" CREATE TABLE IF NOT EXISTS users(user_id INTEGER, name TEXT, city TEXT) """)
cursor.execute(query)
# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()