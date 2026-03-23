import psycopg2
import sys

try:
    conn = psycopg2.connect("dbname='ai_recruitment' user='postgres' password='123' host='localhost'")
    conn.autocommit = True
    cur = conn.cursor()
    print("Terminating other connections...")
    cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ai_recruitment' AND pid <> pg_backend_pid();")
    print("Dropping schema...")
    cur.execute("DROP SCHEMA public CASCADE;")
    print("Creating schema...")
    cur.execute("CREATE SCHEMA public;")
    print("Done")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
