import sqlite3
import pandas as pd
import os

def build_database():
    csv_path = "data/processed/all_supplements_clean.csv"
    db_path = "data/processed/supplements.db"
    
    if not os.path.exists(csv_path):
        print("сначала нужно собрать и почистить данные!")
        return
        
    df = pd.read_csv(csv_path)
    
    # фиксим пустые значения, иначе sqlite ругается на NOT NULL при заливке
    df['Бренд'] = df['Бренд'].fillna('Без бренда')
    df['Категория'] = df['Категория'].fillna('Неизвестно')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # собираем физическую ER-модель
    # решил вынести бренды и категории в отдельные справочники, чтобы не дублировать текст
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    # главная таблица со связями (foreign keys)
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
    
    # чистим старые данные, если запускаем скрипт не в первый раз (защита от дублей)
    cursor.execute('DELETE FROM products')
    cursor.execute('DELETE FROM brands')
    cursor.execute('DELETE FROM categories')
    
    # заливаем уникальные категории и бренды
    for cat in df['Категория'].unique():
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (cat,))
        
    for brand in df['Бренд'].unique():
        cursor.execute('INSERT INTO brands (name) VALUES (?)', (brand,))
        
    # подтягиваем сгенерированные базой айдишники обратно в питон
    cursor.execute('SELECT name, id FROM categories')
    cat_dict = dict(cursor.fetchall())
    
    cursor.execute('SELECT name, id FROM brands')
    brand_dict = dict(cursor.fetchall())
    
    # мапим названия на id
    df['category_id'] = df['Категория'].map(cat_dict)
    df['brand_id'] = df['Бренд'].map(brand_dict)
    
    # готовим финальный датафрейм для заливки
    df_to_db = df[['category_id', 'brand_id', 'Название', 'Цена (руб)', 'Рейтинг', 'Кол-во отзывов']]
    df_to_db.columns = ['category_id', 'brand_id', 'name', 'price', 'rating', 'reviews']
    
    # массовая заливка
    # print("заливаем товары...")
    df_to_db.to_sql('products', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    
    print(f"база собрана: {db_path}")

if __name__ == "__main__":
    build_database()