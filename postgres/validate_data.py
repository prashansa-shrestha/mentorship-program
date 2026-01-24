# postgres/validate_data.py

from typing import Any, Dict
import numpy as np
from db_utils import get_db_connection, DB_CONFIG


def check_unique_emails(conn) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT email, COUNT(*)
            FROM users
            GROUP BY email
            HAVING COUNT(*) > 1;
        """)
        rows = cur.fetchall()

    if not rows:
        print("✅ All users have unique emails")
        return True

    print("❌ Duplicate emails found:")
    for email, count in rows:
        print(f"   {email}: {count}")
    return False


def check_mentor_expertise_level(conn) -> bool:
    """
    mentor_profiles.expertise_level must be between 1 and 5.
    Uses mentor_profile_id as identifier.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT mentor_profile_id, expertise_level
            FROM mentor_profiles
            WHERE expertise_level < 1 OR expertise_level > 5;
        """)
        rows = cur.fetchall()

    if not rows:
        print("✅ All mentor_profiles have valid expertise_level (1–5)")
        return True

    print("❌ Invalid mentor expertise_level values:")
    for mid, lvl in rows:
        print(f"   mentor_profile {mid}: {lvl}")
    return False


def check_mentee_interest_level(conn) -> bool:
    """
    mentee_profiles.main_interest_level must be between 1 and 5.
    Uses mentee_profile_id as identifier.
    """
    interest_column = "main_interest_level"

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT mentee_profile_id, {interest_column}
            FROM mentee_profiles
            WHERE {interest_column} < 1 OR {interest_column} > 5;
        """)
        rows = cur.fetchall()

    if not rows:
        print(f"✅ All mentee_profiles have valid {interest_column} (1–5)")
        return True

    print(f"❌ Invalid mentee {interest_column} values:")
    for mid, lvl in rows:
        print(f"   mentee_profile {mid}: {lvl}")
    return False


def check_embedding_dimensions(conn, expected_dim: int = 384) -> bool:
    """
    Uses pgvector's vector_dims(embedding_vector) to check dimension.
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

    print(f"❌ {bad_count} embeddings have wrong dimension")
    return False


def check_embedding_norms(conn, tolerance: float = 0.01) -> bool:
    """
    Loads embedding_vector values, computes L2 norm, and checks they are ~1.0.
    """
    embedding_pk_column = "embedding_id"

    with conn.cursor() as cur:
        cur.execute(f"SELECT {embedding_pk_column}, embedding_vector FROM embeddings;")
        rows = cur.fetchall()

    bad = []
    for eid, vec in rows:
        arr = np.array(vec)
        norm = np.linalg.norm(arr)
        if not (1 - tolerance <= norm <= 1 + tolerance):
            bad.append((eid, norm))

    if not bad:
        print("✅ All embeddings have norm ≈ 1.0")
        return True

    print("❌ Embeddings with bad norm:")
    for eid, norm in bad[:20]:
        print(f"   {embedding_pk_column} {eid}: norm={norm:.4f}")
    if len(bad) > 20:
        print(f"   ... and {len(bad) - 20} more")
    return False


def check_orphaned_mentor_profiles(conn) -> bool:
    """
    mentor_profiles.user_id must exist in users.user_id.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT mp.mentor_profile_id
            FROM mentor_profiles mp
            LEFT JOIN users u ON mp.user_id = u.user_id
            WHERE u.user_id IS NULL;
        """)
        rows = cur.fetchall()

    if not rows:
        print("✅ No orphaned mentor_profiles (all have valid users)")
        return True

    print("❌ Orphaned mentor_profiles found:")
    for (mid,) in rows:
        print(f"   mentor_profile {mid}")
    return False


def check_orphaned_mentee_profiles(conn) -> bool:
    """
    mentee_profiles.user_id must exist in users.user_id.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT mp.mentee_profile_id
            FROM mentee_profiles mp
            LEFT JOIN users u ON mp.user_id = u.user_id
            WHERE u.user_id IS NULL;
        """)
        rows = cur.fetchall()

    if not rows:
        print("✅ No orphaned mentee_profiles (all have valid users)")
        return True

    print("❌ Orphaned mentee_profiles found:")
    for (mid,) in rows:
        print(f"   mentee_profile {mid}")
    return False


def check_orphaned_records(conn) -> bool:
    """
    Wrapper to run all orphan checks.
    Extend later for embeddings/matches if needed.
    """
    ok = True
    ok &= check_orphaned_mentor_profiles(conn)
    ok &= check_orphaned_mentee_profiles(conn)
    return ok


def check_mentor_capacity(conn) -> bool:
    """
    Check that assigned mentees per mentor do not exceed capacity.

    mentor_profiles:
      - PK: mentor_profile_id (uuid)
      - capacity column: max_mentee_capacity

    matches:
      - FK: mentor_id (uuid) -> mentor_profiles.mentor_profile_id
    """
    mentor_pk_column = "mentor_profile_id"
    capacity_column = "max_mentee_capacity"

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT mp.{mentor_pk_column},
                   mp.{capacity_column},
                   COUNT(m.match_id) AS assigned
            FROM mentor_profiles mp
            LEFT JOIN matches m ON m.mentor_id = mp.{mentor_pk_column}
            GROUP BY mp.{mentor_pk_column}, mp.{capacity_column}
            HAVING COUNT(m.match_id) > mp.{capacity_column};
        """)
        rows = cur.fetchall()

    if not rows:
        print("✅ Mentor capacity constraints respected")
        return True

    print("❌ Mentors over capacity:")
    for mid, cap, assigned in rows:
        print(f"   mentor {mid}: capacity={cap}, assigned={assigned}")
    return False


def main() -> None:
    print("Running validate_data...")
    with get_db_connection(DB_CONFIG) as conn:
        all_ok = True

        all_ok &= check_unique_emails(conn)
        all_ok &= check_mentor_expertise_level(conn)
        all_ok &= check_mentee_interest_level(conn)
        all_ok &= check_embedding_dimensions(conn)
        all_ok &= check_embedding_norms(conn)
        all_ok &= check_orphaned_records(conn)
        all_ok &= check_mentor_capacity(conn)

        print("\nSummary:")
        print("✅ All checks passed" if all_ok else "❌ Some checks failed")


if __name__ == "__main__":
    main()
