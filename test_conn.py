import psycopg2

try:
    conn = psycopg2.connect(
        dbname='mentor_db',
        user='postgres',
        password='postgres123',
        host='localhost',
        port=5432
    )
    print('✅ Connection successful!')
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    print(cursor.fetchone()[0])
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
