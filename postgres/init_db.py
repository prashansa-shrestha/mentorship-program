import os
import psycopg2


script_dir=os.path.dirname(os.path.abspath(__file__))
schema_path=os.path.join(script_dir,'schema_minimal.sql')

try:
    # 2. Use 'with' for the connection to ensure it closes even if things crash
    with psycopg2.connect("postgresql://postgres:password123@127.0.0.1:5432/mentorship_db") as conn:
        with conn.cursor() as cursor:
            # 3. Read and execute the SQL
            with open(schema_path, 'r') as f:
                cursor.execute(f.read())
            
            # Commit is handled automatically by the 'with conn' block in psycopg2
            print("Schema applied successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

conn.commit()
conn.close()