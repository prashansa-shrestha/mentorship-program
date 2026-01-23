import psycopg2

print("Connecting...")

conn = psycopg2.connect(
    dbname="mentor_db",
    user="postgres",
    password="postgres123",
    host="127.0.0.1",
    port=5433,  # IMPORTANT: use the host port you mapped for Docker, e.g. 5433
)

cur = conn.cursor()
cur.execute("SELECT version();")
print("Connected to:", cur.fetchone())
cur.close()
conn.close()
