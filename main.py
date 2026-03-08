from fastapi import FastAPI
from backend.routes.products import product_router
from backend.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Comparador de Preços")

origins = [
    "https://hudok139.github.io",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router, prefix="/products", tags=["Products"])



@app.get("/")
async def root():
    return {"status": "API Online"}