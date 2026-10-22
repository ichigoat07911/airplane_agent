import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

load_dotenv()

DB_USER=os.getenv("DB_USER","root")
DB_PASSWORD=os.getenv("DB_PASSWORD","")
DB_HOST=os.getenv("DB_HOST","127.0.0.1")
DB_PORT=os.getenv("DB_PORT","3306")
DB_NAME = os.getenv("DB_NAME", "transport_db")

safe_password=urllib.parse.quote_plus(DB_PASSWORD)
DATABASE_URL=f"mysql+pymysql://{DB_USER}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine=create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True

)
Session_local=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

def get_db():
    db=Session_local()
    try:
        yield db
    finally:
        db.close()