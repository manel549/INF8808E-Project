# data.py
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from functools import lru_cache
import psutil


DATABASE_URL = "postgresql://postgres.zmuhejhildpmdudskpih:Shadha.20182020@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"

def get_dataframe(table_name="data", cols="*", where_clause=None):
    engine = create_engine(DATABASE_URL)
    quoted_cols = ", ".join([f'"{col.strip()}"' for col in cols.split(",")]) if cols != "*" else "*"
    query = f'SELECT {quoted_cols} FROM "{table_name}"'  
    if where_clause:
        query += f" WHERE {where_clause}"
    df = pd.read_sql(query, engine)
   
    return df
