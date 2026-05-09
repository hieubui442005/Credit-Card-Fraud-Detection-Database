import psycopg2, pymysql, sqlite3, time, pandas as pd
from urllib.error import URLError

PG_CREDS = {"dbname": "fraud_db", "user": "admin", "password": "password", "host": "127.0.0.1", "port": "5432"}
MYSQL_CREDS = {"database": "fraud_db", "user": "root", "password": "password", "host": "127.0.0.1", "port": 3306}
SQLITE_DB = "fraud_sqlite.db"
query = "SELECT * FROM TransactionData LIMIT 10;"

def query_postgres(query):
    try:
        conn = psycopg2.connect(**PG_CREDS)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return len(df)
    except Exception as e: return f"Error: {e}"

def query_sqlite(query):
    try:
        conn = sqlite3.connect(SQLITE_DB)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return len(df)
    except Exception as e: return f"Error: {e}"

print("PG:", query_postgres(query))
print("SQLite:", query_sqlite(query))
