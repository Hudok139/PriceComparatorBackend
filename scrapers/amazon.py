from backend.utils import fetch_marketplace_data
from bs4 import BeautifulSoup

def scrape_amazon(product_name):
    html_content = fetch_marketplace_data("amazon", product_name)
    if not html_content: return []

    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    items = soup.find_all("div", {"data-component-type": "s-search-result"})[:3]

    for item in items:
        # Busca o título específico da Amazon
        title_tag = item.find("h2")
        # Busca o preço específico da Amazon
        price_whole = item.find("span", class_="a-price-whole")
        link_tag = item.find("a", class_="a-link-normal s-no-outline")

        if title_tag and price_whole:
            price_clean = price_whole.text.replace(".", "").replace(",", "")
            
            products.append({
                "name": title_tag.text.strip(),
                "price": float(price_clean),
                "store": "Amazon",
                "url": "https://www.amazon.com.br" + link_tag['href'] if link_tag else ""
            })
    return products