import psycopg2
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(script_dir, 'schema_minimal.sql')

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password123@localhost:5432/mentorship_db")

conn = psycopg2.connect(db_url)
cursor = conn.cursor()

print("🗑️  Dropping existing tables...")

# Drop tables in reverse order
tables = ['matches', 'embeddings', 'mentee_profiles', 'mentor_profiles', 'users']

for table in tables:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        print(f"  ✓ Dropped {table}")
    except Exception as e:
        print(f"  ⚠️  {table}: {e}")

conn.commit()

print("\n📋 Creating fresh schema...")

# Recreate from schema
with open(schema_path, 'r') as f:
    cursor.execute(f.read())

conn.commit()
cursor.close()
conn.close()

print("✅ Database reset complete!")
