import json
import pandas as pd
import os

def clean_wb_data():
    raw_path = "data/raw/all_supplements_raw.json"
    
    # если парсер не отработал или упал, то и чистить нечего
    if not os.path.exists(raw_path):
        print("нет файла с сырыми данными, запускай wb_parser.py")
        return

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # структура json у вб хитрая, иногда products лежит внутри data, иногда снаружи
    # видимо зависит от того, как апишка отвечает
    products = data.get('data', {}).get('products', [])
    if not products:
        products = data.get('products', [])
        
    print(f"всего товаров на обработку: {len(products)}")
    
    clean_items = []
    for p in products:
        sizes = p.get("sizes", [])
        actual_price = 0
        
        # вытаскиваем цену. у вб она умножена на 100 (копейки)
        if sizes: 
            price_block = sizes[0].get("price", {})
            raw_price = price_block.get("product", 0) 
            
            # если нет скидочной цены, пробуем взять базовую
            if raw_price == 0:
                raw_price = price_block.get("basic", 0)
                
            actual_price = int(raw_price / 100) 
            # print(f"дебаг цены: {raw_price} -> {actual_price}")

        item = {
            "Категория": p.get("search_category", "Неизвестно"),
            "Бренд": p.get("brand", "Без бренда"),
            "Название": p.get("name", "Без названия"),
            "Цена (руб)": actual_price,
            "Рейтинг": p.get("reviewRating", p.get("rating", 0)), # иногда ключи рейтинга отличаются
            "Кол-во отзывов": p.get("feedbacks", 0),
        }
        clean_items.append(item)
        
    df = pd.DataFrame(clean_items)
    
    # закомментил удаление дублей, вроде парсер нормально сработал
    # df = df.drop_duplicates(subset=['Название', 'Бренд'])
    
    os.makedirs("data/processed", exist_ok=True)
    out_path = "data/processed/all_supplements_clean.csv"
    
    # index=False обязательно, чтобы пандас не плодил лишнюю колонку Unnamed: 0
    df.to_csv(out_path, index=False, encoding="utf-8")
    
    print("данные очищены и сохранены в csv")
    # print(df.head()) # проверка что всё ок

if __name__ == "__main__":
    clean_wb_data()