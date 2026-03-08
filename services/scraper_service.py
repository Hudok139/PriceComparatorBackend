from sqlalchemy.orm import Session

from backend.scrapers.amazon import scrape_amazon
from backend.services.mercado_livre_api import search_mercado_livre
from backend.models.product import Product, PriceHistory
import time
import random


def run_all_scrapers(product_query: str, db: Session):
    print(f" LOG: Iniciando scrapers para '{product_query}'")
    scrapers = [search_mercado_livre, scrape_amazon]
    all_results = []
    
    for scraper_func in scrapers:
        results = scraper_func(product_query)
        if results:
            print(f" LOG: Scraper {scraper_func.__name__} retornou {len(results)} itens brutos.")
            all_results.extend(results)
        else:
            print(f" WARNING: Scraper {scraper_func.__name__} retornou LISTA VAZIA.")
        time.sleep(random.uniform(1,3)) # tempo de espera para o site não desconfiar que é um bot 

    processed_count = 0
    
    for index, item in enumerate(all_results):
        
        try:
            # 1. Verifica se já existe um histórico com essa URL
            existing_price = db.query(PriceHistory).filter(PriceHistory.url == item["url"]).first()
            
            if not existing_price:
                
                # Criar Produto
                new_product = Product(
                    name=item["name"][:150],
                    brand="Mercado Livre",
                    category="SSD"
                )
                db.add(new_product)
                db.commit()
                db.refresh(new_product)
                
                # Criar Preço
                new_price = PriceHistory(
                    product_id=new_product.id,
                    price=item["price"],
                    store=item["store"],
                    url=item["url"]
                )
                db.add(new_price)
                processed_count += 1
                print(f"   -> Sucesso: Produto {new_product.id} e preço salvos.")
            
            else:
                print(f"   -> URL já existe no banco. Verificando mudança de preço...")
                if existing_price.price != item["price"]:
                    new_price = PriceHistory(
                        product_id=existing_price.product_id,
                        price=item["price"],
                        store=item["store"],
                        url=item["url"]
                    )
                    db.add(new_price)
                    processed_count += 1
                    print(f"   -> Preço atualizado para {item['price']}")
                else:
                    print(f"   -> Preço idêntico ao anterior. Nada a fazer.")

        except Exception as e:
            print(f" ERROR: Falha ao processar item {index + 1}: {e}")
            db.rollback() # Limpa a transação se der erro

    db.commit()
    print(f" LOG: Finalizado. Total processado com sucesso: {processed_count}")
    return processed_count