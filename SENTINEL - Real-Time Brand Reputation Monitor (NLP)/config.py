# 02_config.py
import urllib
from sqlalchemy import create_engine

# --- CONFIGURAÇÕES GERAIS ---
SERVER = '.' # Seu servidor
DATABASE = 'SENTINEL_DB'

def get_engine():
    params = urllib.parse.quote_plus(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Limiar para disparar crise (Se a negatividade passar de 40%, ALERTA!)
LIMITE_CRISE = 0.40