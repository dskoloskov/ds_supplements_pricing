import requests
import json
import time
import os

def fetch_all_supplements():
    # куки и хедеры вытащил руками из нетворка браузера, без них вб отдает пустоту
    cookies = {
         '_wbauid': '5573919711779467886',
         'x_wbaas_token': '1.1000.b49f8042a21748f298a00e8a56768978.MTV8MTg1LjI0Ny4xMTYuMTAzfE1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8yNi40IFNhZmFyaS82MDUuMS4xNXwxNzc5NzI3MDgyfHJldXNhYmxlfDJ8ZXlKb1lYTm9Jam9pSW4wPXwwfDN8MTc3OTU5NzQ4Mnwx.MEUCIEsLEuVWsdxJiZIgjfbB4xYBhbj6t2Fg/GAxZy2KMb0FAiEA99pHwfG8Dk4R2AzJiV1OdPUIJ3qzvBfXqCMir90VOW4=',
    }

    headers = {
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'ru',
        'Sec-Fetch-Mode': 'cors',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.4 Safari/605.1.15',
        'Referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BA%D1%80%D0%B5%D0%B0%D1%82%D0%B8%D0%BD',
        'Sec-Fetch-Dest': 'empty',
        'Cookie': '_wbauid=5573919711779467886; x_wbaas_token=1.1000.b49f8042a21748f298a00e8a56768978.MTV8MTg1LjI0Ny4xMTYuMTAzfE1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8yNi40IFNhZmFyaS82MDUuMS4xNXwxNzc5NzI3MDgyfHJldXNhYmxlfDJ8ZXlKb1lYTm9Jam9pSW4wPXwwfDN8MTc3OTU5NzQ4Mnwx.MEUCIEsLEuVWsdxJiZIgjfbB4xYBhbj6t2Fg/GAxZy2KMb0FAiEA99pHwfG8Dk4R2AzJiV1OdPUIJ3qzvBfXqCMir90VOW4=',
        'x-requested-with': 'XMLHttpRequest',
        'Priority': 'u=3, i',
        'x-queryid': 'qid557391971177946788620260522165110',
        'x-userid': '0',
        'deviceid': 'site_ac5b8125c2b7451b87d377602adb3999',
        'x-spa-version': '14.10.5',
    }

    queries = ['креатин', 'протеин', 'цитруллин']
    all_products = []

    for query in queries:
        print(f"собираем категорию: {query}")
        
        # парсим по 3 страницы на каждый запрос
        for page in range(1, 4):
            url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&curr=rub&dest=-1257786&page={page}&query={query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
            
            try:
                response = requests.get(url, cookies=cookies, headers=headers)
                # print(response.status_code) # дебаг
                
                data = response.json()
                products = data.get('data', {}).get('products', [])
                
                # сразу прокидываем категорию, чтобы в пандасе потом не склеивать
                for p in products:
                    p['search_category'] = query
                    all_products.append(p)
                    
                print(f"стр {page} - ок")
                time.sleep(2) # пауза, чтобы не поймать 429 ошибку
                
            except Exception as e:
                print(f"упали на {query} стр {page}: {e}")
                
    # дамп сырых данных
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/all_supplements_raw.json", "w", encoding="utf-8") as f:
        json.dump({"products": all_products}, f, ensure_ascii=False, indent=4)
        
    print(f"сбор завершен. уникальных sku: {len(all_products)}")

if __name__ == "__main__":
    fetch_all_supplements()