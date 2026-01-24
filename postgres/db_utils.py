# postgres/db_utils.py

from typing import Dict, Any
import psycopg2
from psycopg2.extensions import connection
import pandas as pd


DB_CONFIG: Dict[str, Any] = {
    "dbname": "mentor_db",
    "user": "postgres",
    "password": "postgres123",
    "host": "127.0.0.1",
    "port": 5433,
}


def get_db_connection(config: Dict[str, Any]) -> connection:
    """
    Create and return a new psycopg2 connection using the given config.
    """
    return psycopg2.connect(**config)


def test_connection(config: Dict[str, Any]) -> bool:
    """
    Test DB connectivity. Returns True if SELECT 1 succeeds, else False.
    """
    try:
        with get_db_connection(config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        print("✅ DB connection OK")
        return True
    except Exception as e:
        print(f"❌ DB connection failed: {e}")
        return False


def get_table_counts(conn: connection) -> Dict[str, int]:
    """
    Return row counts for key tables.
    """
    tables = ["users", "mentor_profiles", "mentee_profiles", "embeddings", "matches"]
    counts: Dict[str, int] = {}
    with conn.cursor() as cur:
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            (cnt,) = cur.fetchone()
            counts[table] = cnt
    return counts


def verify_embedding_dimensions(conn: connection, expected_dim: int = 384) -> bool:
    """
    Verify all embeddings have the expected dimension.
    Returns True if OK, else False.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM embeddings "
            "WHERE vector_dims(embedding_vector) != %s;",
            (expected_dim,),
        )
        (bad_count,) = cur.fetchone()

    if bad_count == 0:
        print(f"✅ All embeddings are {expected_dim}-dimensional")
        return True
    else:
        print(f"❌ {bad_count} embeddings have wrong dimension")
        return False


def export_matches_to_csv(conn: connection, filename: str) -> None:
    """
    Export the matches table to a CSV file at the given path.
    """
    df = pd.read_sql("SELECT * FROM matches;", conn)
    df.to_csv(filename, index=False)
    print(f"✅ Exported matches to {filename}")


if __name__ == "__main__":
    print("Running db_utils manual test...")
    ok = test_connection(DB_CONFIG)
    print("test_connection returned:", ok)

    if ok:
        with get_db_connection(DB_CONFIG) as conn:
            print("Table counts:", get_table_counts(conn))
            verify_embedding_dimensions(conn)
            # We'll add get_mentor_capacity_stats(conn) later once columns are confirmed
            export_matches_to_csv(conn, "matches_export.csv")
            print("Done running helpers.")
