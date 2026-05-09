import psycopg2, pymysql, sqlite3, time
import pandas as pd

PG_CREDS = {"dbname": "fraud_db", "user": "admin", "password": "password", "host": "127.0.0.1", "port": 5432}
MYSQL_CREDS = {"database": "fraud_db", "user": "root", "password": "password", "host": "127.0.0.1", "port": 3306}
SQLITE_DB = "fraud_sqlite.db"
query = "SELECT * FROM TransactionData LIMIT 5"

try:
    conn = psycopg2.connect(**PG_CREDS)
    df = pd.read_sql_query(query, conn)
    print("PG Count:", len(df))
except Exception as e:
    print("PG Error:", e)

try:
    conn = pymysql.connect(**MYSQL_CREDS)
    df = pd.read_sql_query(query, conn)
    print("MySQL Count:", len(df))
except Exception as e:
    print("MySQL Error:", e)
