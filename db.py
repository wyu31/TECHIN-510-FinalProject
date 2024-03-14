import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv('POSTGRESQLCONNSTR_DB_USER') or os.getenv('DB_USER')
db_pw = os.getenv('POSTGRESQLCONNSTR_DB_PASSWORD') or os.getenv('DB_PASSWORD')
db_host = os.getenv('POSTGRESQLCONNSTR_DB_HOST') or os.getenv('DB_HOST')
db_port = os.getenv('POSTGRESQLCONNSTR_DB_PORT') or os.getenv('DB_PORT')
db_name = os.getenv('POSTGRESQLCONNSTR_DB_NAME') or os.getenv('DB_NAME')

conn_str = f'postgresql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}'

def get_db_conn():
    print("conn_str", conn_str)  # Debugging print statement
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    return conn

def initialize_database():
    conn = get_db_conn()
    cur = conn.cursor()
    try:
        tables = [
            """
            CREATE TABLE IF NOT EXISTS groups (
                group_id SERIAL PRIMARY KEY,
                group_name TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id SERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL,
                member_name TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(group_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id SERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL,
                item TEXT NOT NULL,
                amount DECIMAL NOT NULL,
                paid_by TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(group_id)
            )
            """
        ]

        for table_sql in tables:
            cur.execute(table_sql)
        cur.execute('''
            ALTER TABLE expenses ADD COLUMN IF NOT EXISTS borrower TEXT;
            ''')    
        print("All tables were created successfully.")
    
    except psycopg2.Error as e:
        print(f"An error occurred while initializing the database: {e}")
    finally:
        cur.close()
        conn.close()

def get_group_ids():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT group_id FROM groups")
    group_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return group_ids

def get_group_member_ids(group_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT member_id FROM members WHERE group_id = %s", (group_id,))
    member_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return member_ids

def add_expense(group_id, item, amount, paid_by, borrower):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (group_id, item, amount, paid_by, borrower) VALUES (%s, %s, %s, %s, %s)", (group_id, item, amount, paid_by, borrower))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    initialize_database()
