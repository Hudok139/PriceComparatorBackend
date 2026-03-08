from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.product import Product, PriceHistory
from backend.schemas.product import ProductCreate
from sqlalchemy import func
from backend.services.scraper_service import run_all_scrapers

product_router = APIRouter()

@product_router.post("/", status_code=201)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    # 1. Criar o objeto do Produto
    new_product = Product(
        name=product_data.name,
        brand=product_data.brand,
        description=product_data.description,
        category=product_data.category,
        image_url=product_data.image_url
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product) # Pega o ID gerado pelo banco

    # 2. Criar o primeiro registro de preço atrelado a esse produto
    new_price = PriceHistory(
        product_id=new_product.id,
        price=product_data.initial_price.price,
        store=product_data.initial_price.store,
        url=product_data.initial_price.url
    )
    
    db.add(new_price)
    db.commit()
    
    return {"message": "Produto e preço inicial cadastrados!", "id": new_product.id}


@product_router.get("/")
def search_products(q: Optional[str] = Query(None, min_length=3), db: Session = Depends(get_db)):
    # Criamos uma subquery para achar a data do preço mais recente de cada produto
    subquery = db.query(
        PriceHistory.product_id,
        func.max(PriceHistory.timestamp).label("latest_timestamp")
    ).group_by(PriceHistory.product_id).subquery()

    # Agora fazemos o Join: Produto + Histórico de Preço mais recente
    query = db.query(Product, PriceHistory).join(
        PriceHistory, Product.id == PriceHistory.product_id
    ).join(
        subquery, 
        (PriceHistory.product_id == subquery.c.product_id) & 
        (PriceHistory.timestamp == subquery.c.latest_timestamp)
    )

    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))

    results = query.all()

    # Formatamos a resposta para ficar bonita no JSON
    return [
        {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "current_price": ph.price,
            "store": ph.store,
            "url": ph.url,
            "last_update": ph.timestamp
        }
        for p, ph in results
    ]

@product_router.post("/refresh")
def refresh_prices(q: str, db: Session = Depends(get_db)):
    count = run_all_scrapers(q, db)
    return {"message": f"Busca finalizada. {count} preços atualizados"}



@product_router.get("/search")
def search_and_update(q: str, db: Session = Depends(get_db)):
    if not q:
        return {"error": "Você precisa digitar um termo de busca."}
    
    # 1. Roda o scraper e popula o banco
    processed_count = run_all_scrapers(q, db)
    
    # 2. Busca os produtos com o preço mais recente (Join)
    search_pattern = f"%{q.replace(' ', '%')}%"
    
    # Subquery para pegar o timestamp mais recente
    subquery = db.query(
        PriceHistory.product_id,
        func.max(PriceHistory.timestamp).label("latest_timestamp")
    ).group_by(PriceHistory.product_id).subquery()

    # Join para pegar Produto + Preço atualizado
    query = db.query(Product, PriceHistory).join(
        PriceHistory, Product.id == PriceHistory.product_id
    ).join(
        subquery, 
        (PriceHistory.product_id == subquery.c.product_id) & 
        (PriceHistory.timestamp == subquery.c.latest_timestamp)
    ).filter(Product.name.ilike(search_pattern))

    results = query.all()
    

    return {
        "message": f"Busca concluída. {processed_count} preços processados.",
        "results": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "current_price": ph.price, 
                "store": ph.store,
                "url": ph.url
            }
            for p, ph in results
        ]
    }