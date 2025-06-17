# data.py
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# DATABASE_URL = "postgresql://postgres.zmuhejhildpmdudskpih:Shadha.20182020@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"

# try:
#     engine = create_engine(DATABASE_URL)
# except OperationalError as e:
#     print("Erreur de connexion à la base :", e.orig)
#     engine = None
# except Exception as e:
#     print("Autre erreur :", e)
#     engine = None

# def get_dataframe(table_name="data"):
#     if engine is None:
#         return pd.DataFrame()
#     try:
#         with engine.connect() as conn:
#             df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
#         return df
#     except Exception as e:
#         print("Erreur lors de la lecture des données :", e)
#         return pd.DataFrame()
# import pandas as pd
# from sqlalchemy import create_engine


#DATABASE_URL = "postgresql://postgres.zmuhejhildpmdudskpih:Shadha.20182020@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from functools import lru_cache
import psutil


DATABASE_URL = "postgresql://postgres.zmuhejhildpmdudskpih:Shadha.20182020@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"

@lru_cache(maxsize=1)
def get_dataframe(table_name="data"):
    print("[DEBUG] Chargement des données depuis la base (une seule fois normalement)")
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM data", engine)
    mem = psutil.Process().memory_info().rss / 1024**2
    print(f"[DEBUG] RAM utilisée : {mem:.2f} Mo")
    return df
