import psycopg2

conn = psycopg2.connect("postgresql://postgres:password123@127.0.0.1:5432/mentorship_db")
cursor = conn.cursor()

with open('schema.sql', 'r') as f:
    cursor.execute(f.read())

conn.commit()
conn.close()