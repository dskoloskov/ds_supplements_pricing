import sqlite3
import pandas as pd
import os

def build_database():
    print("Начинаем проектирование базы данных...")
    
    # Пути к нашему чистому CSV и будущей БД
    csv_path = "data/processed/all_supplements_clean.csv"
    db_path = "data/processed/supplements.db"
    
    if not os.path.exists(csv_path):
        print(f"Ошибка: Файл {csv_path} не найден!")
        return
        
    df = pd.read_csv(csv_path)
    # --- ИСПРАВЛЕНИЕ ОШИБКИ NOT NULL ---
    # Если Pandas нашел пустые ячейки (NaN), заменяем их на обычный текст
    df['Бренд'] = df['Бренд'].fillna('Без бренда')
    df['Категория'] = df['Категория'].fillna('Неизвестно')
    # -----------------------------------
    
    # Подключаемся к SQLite (файл создастся автоматически, если его нет)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Строим физическую ER-модель (создаем таблицы)
    print("Генерируем SQL-код и создаем таблицы...")
    
    # Справочник категорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Справочник брендов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Основная таблица товаров со связями
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        brand_id INTEGER,
        name TEXT NOT NULL,
        price INTEGER,
        rating REAL,
        reviews INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories (id),
        FOREIGN KEY (brand_id) REFERENCES brands (id)
    )
    ''')
    
    # Очищаем таблицы перед заливкой (защита от дублей при повторных запусках)
    cursor.execute('DELETE FROM products')
    cursor.execute('DELETE FROM brands')
    cursor.execute('DELETE FROM categories')
    
    # 2. Заполняем справочники
    print("Заполняем справочники уникальными категориями и брендами...")
    
    unique_categories = df['Категория'].unique()
    for cat in unique_categories:
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (cat,))
        
    unique_brands = df['Бренд'].unique()
    for brand in unique_brands:
        cursor.execute('INSERT INTO brands (name) VALUES (?)', (brand,))
        
    # 3. Связываем товары со справочниками
    print("Проставляем ключи (Foreign Keys) и заливаем товары в БД...")
    
    # Достаем сгенерированные ID из базы
    cursor.execute('SELECT name, id FROM categories')
    cat_dict = dict(cursor.fetchall())
    
    cursor.execute('SELECT name, id FROM brands')
    brand_dict = dict(cursor.fetchall())
    
    # Меняем текст на ID в датафрейме
    df['category_id'] = df['Категория'].map(cat_dict)
    df['brand_id'] = df['Бренд'].map(brand_dict)
    
    # Оставляем только те колонки, которые нужны для SQL таблицы
    df_to_db = df[['category_id', 'brand_id', 'Название', 'Цена (руб)', 'Рейтинг', 'Кол-во отзывов']]
    df_to_db.columns = ['category_id', 'brand_id', 'name', 'price', 'rating', 'reviews']
    
    # 4. Массовая заливка (Bulk Insert)
    df_to_db.to_sql('products', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    
    print(f"\nГотово! Реляционная база данных успешно собрана в {db_path}")

if __name__ == "__main__":
    build_database()