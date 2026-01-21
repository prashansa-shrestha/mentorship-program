import psycopg2

conn = psycopg2.connect("postgresql://user:password@localhost:5432/mentor_db")
cursor = conn.cursor()

with open('schema.sql', 'r') as f:
    cursor.execute(f.read())

conn.commit()
conn.close()