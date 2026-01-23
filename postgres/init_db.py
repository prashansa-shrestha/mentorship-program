"""
init_db.py - Test database connection for Person B
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def test_connection():
    """Test if database is accessible and schema exists."""
    try:
        # Connect to database
        conn = psycopg2.connect(
            dbname="mentor_db",
            user="postgres",
            password="postgres123",
            host="127.0.0.1",
            port=5433,
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Database connection successful!")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Check if pgvector extension is enabled
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
        vector_ext = cursor.fetchone()
        
        if vector_ext:
            print("\n✅ pgvector extension is enabled")
        else:
            print("\n❌ pgvector extension NOT found - Person A needs to add it")
        
        # Check for sample data
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM mentor_profiles")
        mentor_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM mentee_profiles")
        mentee_count = cursor.fetchone()['count']
        
        print(f"\n📈 Data Status:")
        print(f"  - Users: {user_count}")
        print(f"  - Mentors: {mentor_count}")
        print(f"  - Mentees: {mentee_count}")
        
        if user_count == 0:
            print("\n⚠️  No data found - Waiting for Person C to run populate_db.py")
        else:
            print("\n✅ Database has data - Ready for scoring tests!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
