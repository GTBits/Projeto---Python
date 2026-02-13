import urllib
from sqlalchemy import create_engine

SERVER = '.' 
DATABASE = 'AIGIS_DB'

def get_engine():
    params = urllib.parse.quote_plus(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")