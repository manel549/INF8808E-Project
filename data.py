# data.py
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://postgres.zmuhejhildpmdudskpih:Shadha.20182020@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"

try:
    engine = create_engine(DATABASE_URL)
except OperationalError as e:
    print("Erreur de connexion à la base :", e.orig)
    engine = None
except Exception as e:
    print("Autre erreur :", e)
    engine = None

def get_dataframe(table_name="data"):
    if engine is None:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        print("Erreur lors de la lecture des données :", e)
        return pd.DataFrame()
