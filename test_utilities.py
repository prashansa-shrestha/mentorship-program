"""
Test Database Utilities
Separated from production code for safety
"""

import psycopg2
from typing import Optional


class TestDatabaseHelper:
    """
    Database utilities for testing only.
    Provides safe methods to clear test data with built-in safeguards.
    """

    def __init__(self, db_config: str):
        """
        Initialize test helper with safety checks.

        Args:
            db_config: PostgreSQL connection string

        Raises:
            ValueError: If attempting to use on production database
        """
        # Safety check - prevent production use
        if any(keyword in db_config.lower() for keyword in ['prod', 'production']):
            raise ValueError("❌ Cannot use test utilities on production database")

        self.conn = psycopg2.connect(db_config)
        self.cursor = self.conn.cursor()
        self._db_config = db_config

    def clear_matches(self) -> int:
        """
        Clear all matches from the database.
        Use this before each test run for isolation.

        Returns:
            int: Number of matches deleted
        """
        try:
            self.cursor.execute("DELETE FROM matches")
            deleted_count = self.cursor.rowcount
            self.conn.commit()
            return deleted_count
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Failed to clear matches: {e}")

    def clear_match_outcomes(self) -> int:
        """
        Clear match outcomes separately (if table exists).

        Returns:
            int: Number of outcomes deleted
        """
        try:
            # Check if table exists first
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'match_outcomes'
                )
            """)
            table_exists = self.cursor.fetchone()[0]

            if table_exists:
                self.cursor.execute("DELETE FROM match_outcomes")
                deleted_count = self.cursor.rowcount
                self.conn.commit()
                return deleted_count
            return 0
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Failed to clear match outcomes: {e}")

    def clear_all_test_data(self) -> dict:
        """
        Nuclear option - clear all test-related tables.
        Use with caution!

        Returns:
            dict: Count of deleted records per table
        """
        results = {}

        # Order matters due to foreign keys
        tables = ['matches']  # Add more as schema grows

        try:
            for table in tables:
                self.cursor.execute(f"DELETE FROM {table}")
                results[table] = self.cursor.rowcount

            self.conn.commit()
            return results
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Failed to clear all test data: {e}")

    def get_match_count(self) -> int:
        """
        Get current number of matches in database.

        Returns:
            int: Total match count
        """
        self.cursor.execute("SELECT COUNT(*) FROM matches")
        return self.cursor.fetchone()[0]

    def get_recent_matches(self, minutes: int = 5) -> int:
        """
        Get count of recently created matches.

        Args:
            minutes: Look back this many minutes

        Returns:
            int: Count of recent matches
        """
        self.cursor.execute(f"""
            SELECT COUNT(*) 
            FROM matches 
            WHERE created_at > NOW() - INTERVAL '{minutes} minutes'
        """)
        return self.cursor.fetchone()[0]

    def close(self):
        """Close database connections."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context manager exit."""
        self.close()


# Convenience function for one-off clearing
def clear_test_matches(db_config: str) -> int:
    """
    Quick function to clear matches without creating helper instance.

    Args:
        db_config: PostgreSQL connection string

    Returns:
        int: Number of matches deleted
    """
    with TestDatabaseHelper(db_config) as helper:
        return helper.clear_matches()
