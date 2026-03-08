import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Carrega as variáveis do arquivo .env
load_dotenv()

# Busca a URL do ambiente, se não achar, usa um valor padrão (fallback)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

#sqlite:///./precos.db significa:
# sqlite é o protocolo
# :// é o separador
# / é o caminho do arquivo


if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./precos.db"
    print("ATENÇÃO!!!!! Usando sqlite local")

engine = create_engine(DATABASE_URL) # conecta a aplicação ao banco, traduz comandos python para SQL e envia para o .db, controla a pool de conexões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#autocommit = false: o db não deve salvar nada sozinho, somente se dermos a ordem com o db.commit()
#autoflush = false: sql não envia mudanças ao banco sem a ordem
#bind = engine: conecta a session à engine

Base = declarative_base() # herda as classes criadas no python para servir de tabela no banco de dados

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()