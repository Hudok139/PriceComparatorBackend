import requests

BASE_URL = "https://api.mercadolibre.com/sites/MLB/search"

def extract_brand(item):
    attributes = item.get("attributes", [])
    
    for attr in attributes:
        if attr.get("id") == "BRAND":
            return attr.get("value_name")
    
    return None

def search_mercado_livre(product_query: str):
    try:
        params = {
            "q": product_query,
            "limit": 5,
            "sort": "price_asc",
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
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