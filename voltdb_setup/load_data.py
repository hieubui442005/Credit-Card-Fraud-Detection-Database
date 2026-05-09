import csv
import json
import requests
import uuid
import time
import os
import sqlite3
import psycopg2
import pymysql
from concurrent.futures import ThreadPoolExecutor

# Configuration
VOLTDB_HOST = os.environ.get("VOLTDB_HOST", "localhost")
VOLTDB_URL = f"http://{VOLTDB_HOST}:8080/api/1.0/"
CSV_PATH = "../data/data_100000.csv"
SQLITE_DB = os.path.join(os.path.dirname(__file__), "fraud_sqlite.db")

PG_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "database": "fraud_db",
    "user": "admin",
    "password": "password",
    "port": 5432
}

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "database": "fraud_db",
    "user": "root",
    "password": "password",
    "port": 3306
}

# ===== VOLTDB FUNCTIONS =====
def query_voltdb(query):
    payload = {
        "Procedure": "@AdHoc",
        "Parameters": json.dumps([query])
    }
    try:
        response = requests.post(VOLTDB_URL, data=payload, timeout=10)
        res_json = response.json()
        return res_json
    except Exception as e:
        print(f"VoltDB error: {e}")
        return None

def init_voltdb_schema():
    schema_path = "schema.sql"
    if not os.path.exists(schema_path):
        print("Schema file not found")
        return
    
    with open(schema_path, "r") as f:
        content = f.read()
        # Extract only VoltDB queries (not PostgreSQL comments)
        lines = content.split('\n')
        current_query = ""
        for line in lines:
            if line.startswith("--"):
                continue
            current_query += line + " "
            if line.endswith(";"):
                query = current_query.strip()
                if query and not query.startswith("--"):
                    print(f"Executing: {query[:60]}...")
                    query_voltdb(query)
                    time.sleep(0.5)
                current_query = ""

# ===== POSTGRESQL FUNCTIONS =====
def init_postgres_schema():
    for attempt in range(5):
        try:
            conn = psycopg2.connect(**PG_CONFIG)
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS TransactionData CASCADE;")
            cur.execute("DROP TABLE IF EXISTS Account CASCADE;")
            
            cur.execute("""
                CREATE TABLE Account (
                    account_id VARCHAR(50) NOT NULL PRIMARY KEY
                )
            """)
            
            cur.execute("""
                CREATE TABLE TransactionData (
                    tx_id VARCHAR(50) NOT NULL,
                    step INTEGER,
                    type VARCHAR(20),
                    amount FLOAT,
                    nameOrig VARCHAR(50) NOT NULL,
                    oldbalanceOrg FLOAT,
                    newbalanceOrig FLOAT,
                    nameDest VARCHAR(50),
                    oldbalanceDest FLOAT,
                    newbalanceDest FLOAT,
                    isFraud SMALLINT,
                    isFlaggedFraud SMALLINT,
                    PRIMARY KEY (tx_id, nameOrig)
                )
            """)
            
            cur.execute("CREATE INDEX idx_nameOrig_pg ON TransactionData(nameOrig);")
            cur.execute("CREATE INDEX idx_isFraud_pg ON TransactionData(isFraud);")
            
            conn.commit()
            conn.close()
            print("✓ PostgreSQL schema created")
            return
        except Exception as e:
            print(f"PostgreSQL schema attempt {attempt+1} failed: {e}")
            time.sleep(2)

def bulk_insert_postgres(queries, batch_size=1000):
    if not queries:
        return
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        for i, q in enumerate(queries):
            try:
                cur.execute(q)
            except Exception as e:
                if i % 1000 == 0:
                    print(f"  PG insert error at {i}: {str(e)[:50]}")
        conn.commit()
        conn.close()
        print(f"✓ PostgreSQL: Inserted {len(queries)} records")
    except Exception as e:
        print(f"PostgreSQL bulk insert error: {e}")

# ===== MYSQL FUNCTIONS =====
def init_mysql_schema():
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS TransactionData;")
        cur.execute("DROP TABLE IF EXISTS Account;")
        
        cur.execute("""
            CREATE TABLE Account (
                account_id VARCHAR(50) NOT NULL PRIMARY KEY
            ) ENGINE=InnoDB
        """)
        
        cur.execute("""
            CREATE TABLE TransactionData (
                tx_id VARCHAR(50) NOT NULL,
                step INTEGER,
                type VARCHAR(20),
                amount FLOAT,
                nameOrig VARCHAR(50) NOT NULL,
                oldbalanceOrg FLOAT,
                newbalanceOrig FLOAT,
                nameDest VARCHAR(50),
                oldbalanceDest FLOAT,
                newbalanceDest FLOAT,
                isFraud TINYINT,
                isFlaggedFraud TINYINT,
                PRIMARY KEY (tx_id, nameOrig),
                INDEX idx_nameOrig (nameOrig),
                INDEX idx_isFraud (isFraud)
            ) ENGINE=InnoDB
        """)
        
        conn.commit()
        conn.close()
        print("✓ MySQL schema created")
    except Exception as e:
        print(f"MySQL schema error: {e}")

def init_sqlite_schema():
    try:
        conn = sqlite3.connect(SQLITE_DB)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS TransactionData;")
        cur.execute("DROP TABLE IF EXISTS Account;")
        cur.execute("""
            CREATE TABLE Account (
                account_id TEXT NOT NULL PRIMARY KEY
            )
        """)
        cur.execute("""
            CREATE TABLE TransactionData (
                tx_id TEXT NOT NULL,
                step INTEGER,
                type TEXT,
                amount REAL,
                nameOrig TEXT NOT NULL,
                oldbalanceOrg REAL,
                newbalanceOrig REAL,
                nameDest TEXT,
                oldbalanceDest REAL,
                newbalanceDest REAL,
                isFraud INTEGER,
                isFlaggedFraud INTEGER,
                PRIMARY KEY (tx_id, nameOrig)
            )
        """)
        cur.execute("CREATE INDEX idx_nameOrig_sqlite ON TransactionData(nameOrig);")
        cur.execute("CREATE INDEX idx_isFraud_sqlite ON TransactionData(isFraud);")
        conn.commit()
        conn.close()
        print("✓ SQLite schema created")
    except Exception as e:
        print(f"SQLite schema error: {e}")

def bulk_insert_sqlite(account_rows, transaction_rows):
    try:
        conn = sqlite3.connect(SQLITE_DB)
        cur = conn.cursor()
        if account_rows:
            cur.executemany("INSERT OR IGNORE INTO Account (account_id) VALUES (?);", account_rows)
        if transaction_rows:
            cur.executemany(
                """
                INSERT OR IGNORE INTO TransactionData (
                    tx_id, step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
                    nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                transaction_rows,
            )
        conn.commit()
        conn.close()
        print(f"✓ SQLite: Inserted {len(transaction_rows)} records")
    except Exception as e:
        print(f"SQLite bulk insert error: {e}")

def bulk_insert_mysql(queries):
    if not queries:
        return
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        for i, q in enumerate(queries):
            try:
                cur.execute(q)
            except Exception as e:
                if i % 1000 == 0:
                    print(f"  MySQL insert error at {i}: {str(e)[:50]}")
        conn.commit()
        conn.close()
        print(f"✓ MySQL: Inserted {len(queries)} records")
    except Exception as e:
        print(f"MySQL bulk insert error: {e}")

# ===== MAIN LOAD FUNCTION =====
def load_data():
    print("Starting data loading into VoltDB, PostgreSQL, MySQL...")
    
    # Wait for VoltDB
    print("Waiting for VoltDB...")
    for i in range(30):
        try:
            res = requests.get(VOLTDB_URL, timeout=2)
            if res.status_code in [200, 400, 404]:
                print("✓ VoltDB ready")
                break
        except:
            pass
        if i < 29:
            print("  ...waiting...")
            time.sleep(2)
    
    # Initialize schemas
    print("\nInitializing VoltDB schema...")
    init_voltdb_schema()
    time.sleep(1)
    
    print("Initializing PostgreSQL schema...")
    init_postgres_schema()
    time.sleep(1)
    
    print("Initializing MySQL schema...")
    init_mysql_schema()
    time.sleep(1)

    print("Initializing SQLite schema...")
    init_sqlite_schema()
    time.sleep(1)
    
    # Load data
    print("\nReading CSV and preparing queries...")
    accounts_set = set()
    voltdb_queries = []
    pg_queries = []
    mysql_queries = []
    sqlite_account_rows = []
    sqlite_transaction_rows = []
    
    count = 0
    try:
        with open(CSV_PATH, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                count += 1
                
                orig = row['nameOrig']
                dest = row['nameDest']
                
                # Add accounts
                if orig not in accounts_set:
                    accounts_set.add(orig)
                    voltdb_queries.append(f"INSERT INTO Account (account_id) VALUES ('{orig}');")
                    pg_queries.append(f"INSERT INTO Account (account_id) VALUES ('{orig}');")
                    mysql_queries.append(f"INSERT INTO Account (account_id) VALUES ('{orig}');")
                    sqlite_account_rows.append((orig,))
                
                if dest not in accounts_set:
                    accounts_set.add(dest)
                    voltdb_queries.append(f"INSERT INTO Account (account_id) VALUES ('{dest}');")
                    pg_queries.append(f"INSERT INTO Account (account_id) VALUES ('{dest}');")
                    mysql_queries.append(f"INSERT INTO Account (account_id) VALUES ('{dest}');")
                    sqlite_account_rows.append((dest,))
                
                # Add transaction
                tx_id = str(uuid.uuid4())
                values = f"('{tx_id}', {row['step']}, '{row['type']}', {row['amount']}, '{orig}', {row['oldbalanceOrg']}, {row['newbalanceOrig']}, '{dest}', {row['oldbalanceDest']}, {row['newbalanceDest']}, {row['isFraud']}, {row['isFlaggedFraud']})"
                
                insert_stmt = f"INSERT INTO TransactionData VALUES {values};"
                voltdb_queries.append(insert_stmt)
                pg_queries.append(insert_stmt)
                mysql_queries.append(insert_stmt)
                sqlite_transaction_rows.append(
                    (
                        tx_id, int(row['step']), row['type'], float(row['amount']), orig,
                        float(row['oldbalanceOrg']), float(row['newbalanceOrig']), dest,
                        float(row['oldbalanceDest']), float(row['newbalanceDest']),
                        int(row['isFraud']), int(row['isFlaggedFraud'])
                    )
                )
                
                if count % 10000 == 0:
                    print(f"  Read {count} records...")
        
        print(f"\nTotal records: {count}")
        print(f"Total queries prepared: {len(pg_queries)}")
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print("\nInserting into SQLite...")
    bulk_insert_sqlite(sqlite_account_rows, sqlite_transaction_rows)
    
    # Insert data
    print("\nInserting into databases (in parallel)...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all jobs
        fut_volt = executor.submit(lambda: [query_voltdb(q) for q in voltdb_queries if len(q) > 0])
        fut_pg = executor.submit(bulk_insert_postgres, pg_queries)
        fut_mysql = executor.submit(bulk_insert_mysql, mysql_queries)
        
        # Wait for completion
        fut_volt.result()
        fut_pg.result()
        fut_mysql.result()
    
    print("\n✓ Data loading completed!")

if __name__ == "__main__":
    load_data()
