import requests
from cachetools import cached, TTLCache

BASE_URL = "https://api.mercadolibre.com/sites/MLB/search"
cache = TTLCache(maxsize=100, ttl=3600)


def extract_brand(item):
    attributes = item.get("attributes", [])
    
    for attr in attributes:
        if attr.get("id") == "BRAND":
            return attr.get("value_name")
    
    return None

#O decorator lru_cache armazena o retorno da função, isso é útil pra que a mesma consulta não seja realizada repetidamente
@cached(cache)
def search_mercado_livre(product_query: str):
    try:
        params = {
            "q": product_query,
            "limit": 5,
            "sort": "price_asc",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "X-Client-Id": "6069149323200303"
        }

        response = requests.get(
            BASE_URL,
            params=params,
            headers=headers,
            timeout=10
        )

        print("Status ML:", response.status_code)

        if response.status_code != 200:
            print(f"Erro na API do Mercado Livre: {response.status_code}")
            print(response.text)
            return []
        
        if response.status_code == 429:
            print("Aviso: Limite de requisições atingido no ML. Aguardando...")
            return []

        data = response.json()
        results = []

        for item in data.get("results", []):
            results.append({
                "name": item.get("title"),
                "price": float(item.get("price", 0)),
                "store": "Mercado Livre",
                "url": item.get("permalink"),
                "brand": extract_brand(item),
                "category": product_query
            })

        return results

    except Exception as e:
        print(f"Erro ao buscar na API do Mercado Livre: {e}")
        return []