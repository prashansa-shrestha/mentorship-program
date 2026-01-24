"""
Database Initialization Script - Person B
Hack-A-Week 2026
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection config (reads from .env values)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'vectorbridge',    # Match your .env
    'password': 'matching',     # Match your .env
    'database': 'postgres'
}



def create_database():
    """Create mentorship_db if it doesn't exist"""
    print("🔄 Connecting to PostgreSQL...")
    print(f"   User: {DB_CONFIG['user']}")
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='mentorship_db'")
    exists = cursor.fetchone()
    
    if not exists:
        print("📦 Creating mentorship_db database...")
        cursor.execute('CREATE DATABASE mentorship_db')
        print("✅ Database created!")
    else:
        print("✅ Database already exists")
    
    cursor.close()
    conn.close()

def init_database():
    """Load schema and dummy data"""
    
    # Now connect to mentorship_db
    DB_CONFIG['database'] = 'mentorship_db'
    
    print("\n🔄 Connecting to mentorship_db...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Enable pgvector extension
    print("📦 Enabling pgvector extension...")
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Load schema if tables don't exist
    print("📋 Loading schema...")
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        print("✅ Schema loaded")
    except Exception as e:
        print(f"⚠️  Schema note: {e}")
    
    # Load Person C's mentor data
    print("👨‍🏫 Loading mentor dummy data...")
    with open('mentors_dummy_data.sql', 'r', encoding='utf-8') as f:
        mentor_sql = f.read()
        cursor.execute(mentor_sql)
    
    # Load Person C's mentee data
    print("👨‍🎓 Loading mentee dummy data...")
    with open('mentee_dummy_data.sql', 'r', encoding='utf-8') as f:
        mentee_sql = f.read()
        cursor.execute(mentee_sql)
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM mentors;")
    mentor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM mentees;")
    mentee_count = cursor.fetchone()[0]
    
    print(f"\n✅ Database ready!")
    print(f"   📊 Mentors: {mentor_count}")
    print(f"   📊 Mentees: {mentee_count}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("🧪 Initializing Hack-A-Week 2026 Database...\n")
    create_database()
    init_database()
    print("\n🎉 Complete!")
