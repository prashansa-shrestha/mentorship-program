"""
Test both mentor and mentee dummy data
Run: python test_all_data.py
"""

import sys
import os

# Import from both scripts
sys.path.insert(0, os.path.dirname(__file__))

try:
    from dummy_mentor_data import get_dummy_mentors, generate_realistic_embedding as gen_emb_mentor
    from dummy_mentee_data import get_dummy_mentees, generate_realistic_embedding as gen_emb_mentee
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure dummy_mentor_data.py and dummy_mentee_data.py exist in postgres/")
    sys.exit(1)

import numpy as np
import pandas as pd

print("🧪 Testing ALL Dummy Data...\n")

# =======================
# TEST MENTORS
# =======================
print("=" * 50)
print("📋 TESTING MENTORS")
print("=" * 50)

mentors = get_dummy_mentors(20)

# Test 1: Count
print(f"✅ Generated {len(mentors)} mentors")
assert len(mentors) == 20

# Test 2: Required fields
required = ["Name", "Campus Roll Number", "Personal email address", "Main Expertise"]
for i, m in enumerate(mentors):
    for field in required:
        assert m.get(field), f"Mentor {i}: missing '{field}'"
print(f"✅ All required fields present")

# Test 3: Expertise levels (3-5)
levels = [m["Your Expertise Level (Above Area)"] for m in mentors]
assert all(3 <= l <= 5 for l in levels)
print(f"✅ Expertise levels: {set(levels)}")

# Test 4: Unique emails
emails = [m["Personal email address"] for m in mentors]
assert len(emails) == len(set(emails))
print(f"✅ All emails unique")

# Test 5: Capacity
capacities = [m["How many mentees will you be taking?"] for m in mentors]
total_capacity = sum(capacities)
print(f"✅ Total capacity: {total_capacity} mentees")

# =======================
# TEST MENTEES
# =======================
print("\n" + "=" * 50)
print("📋 TESTING MENTEES")
print("=" * 50)

mentees = get_dummy_mentees(30)

# Test 1: Count
print(f"✅ Generated {len(mentees)} mentees")
assert len(mentees) == 30

# Test 2: Required fields
required_mentee = ["Name", "Campus Roll Number", "Personal email address", "Main Interest", "Future Aspirations"]
for i, m in enumerate(mentees):
    for field in required_mentee:
        assert m.get(field), f"Mentee {i}: missing '{field}'"
print(f"✅ All required fields present")

# Test 3: Expertise levels (1-3)
levels_mentee = [m["Your Expertise Level (Above Area)"] for m in mentees]
assert all(1 <= l <= 3 for l in levels_mentee)
print(f"✅ Expertise levels: {set(levels_mentee)}")

# Test 4: Unique emails
emails_mentee = [m["Personal email address"] for m in mentees]
assert len(emails_mentee) == len(set(emails_mentee))
print(f"✅ All emails unique")

# =======================
# TEST EMBEDDINGS
# =======================
print("\n" + "=" * 50)
print("🔢 TESTING EMBEDDINGS")
print("=" * 50)

# Test from mentor script
emb = gen_emb_mentor()
assert len(emb) == 384
norm = np.linalg.norm(emb)
assert 0.99 < norm < 1.01
print(f"✅ Mentor embedding: 384-dim, norm={norm:.4f}")

# Test from mentee script
emb2 = gen_emb_mentee()
assert len(emb2) == 384
norm2 = np.linalg.norm(emb2)
assert 0.99 < norm2 < 1.01
print(f"✅ Mentee embedding: 384-dim, norm={norm2:.4f}")

# =======================
# EXCEL FILES
# =======================
print("\n" + "=" * 50)
print("📁 EXCEL FILES")
print("=" * 50)

try:
    mentor_df = pd.read_excel("dummy_mentor_responses.xlsx")
    print(f"✅ dummy_mentor_responses.xlsx: {len(mentor_df)} rows")
except FileNotFoundError:
    print(f"⚠️  dummy_mentor_responses.xlsx not found - run: python dummy_mentor_data.py")

try:
    mentee_df = pd.read_excel("dummy_mentee_responses.xlsx")
    print(f"✅ dummy_mentee_responses.xlsx: {len(mentee_df)} rows")
except FileNotFoundError:
    print(f"⚠️  dummy_mentee_responses.xlsx not found - run: python dummy_mentee_data.py")

# =======================
# MATCHING FEASIBILITY
# =======================
print("\n" + "=" * 50)
print("📊 MATCHING FEASIBILITY")
print("=" * 50)

print(f"Mentor capacity: {total_capacity}")
print(f"Total mentees: {len(mentees)}")

if total_capacity >= len(mentees):
    print(f"✅ Sufficient capacity! ({total_capacity - len(mentees)} extra)")
else:
    print(f"⚠️  Short {len(mentees) - total_capacity} slots")

# =======================
# FINAL
# =======================
print("\n" + "=" * 50)
print("🎉 ALL TESTS PASSED!")
print("=" * 50)
print("\n✅ Mentor data: Ready")
print("✅ Mentee data: Ready")
print("✅ Embeddings: Valid")
print("✅ Ready for Person B's populate_db.py!")
