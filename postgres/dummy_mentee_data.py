"""
Dummy Mentee Data Generator - SQL Version
Hack-A-Week 2026 Mentorship Program
Generated for Person C - Uses Person A's Schema
"""

import random
import numpy as np
from typing import List, Dict
from datetime import datetime


# =======================
# CONFIGURATION
# =======================

# Basic Info
FIRST_NAMES = [
    "Aarav", "Priya", "Arjun", "Ananya", "Rohan", "Diya", "Kiran", "Sanjana",
    "Aditya", "Ishita", "Rahul", "Kavya", "Nikhil", "Shreya", "Vivek", "Pooja",
    "Amit", "Riya", "Suresh", "Meera", "Rajesh", "Neha", "Prakash", "Divya",
    "Suman", "Anjali", "Bikash", "Sunita", "Manish", "Sabina"
]

LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Thapa", "Shrestha", "Adhikari",
    "Rai", "Tamang", "Magar", "Gurung", "Karki", "Bhattarai", "Pandey", "Joshi",
    "Basnet", "Khadka", "Koirala", "Ghimire"
]

HOBBIES = [
    "Reading", "Gaming", "Photography", "Hiking", "Music", "Cooking", 
    "Chess", "Football", "Cricket", "Badminton", "Traveling", "Drawing",
    "Coding side projects", "Watching tech talks", "Blogging", "Guitar",
    "Sketching", "Dancing", "Building small projects", "Learning new frameworks"
]

# Campus roll number
BATCH_YEARS = ["078", "079", "080"]  # Mentees are typically recent batches
DEPT_CODES = {
    "Computer": "BCT",
    "Electrical": "BEL", 
    "Electronics (Communication/Information)": "BEX",
    "Civil": "BCE",
    "Mechanical": "BME",
    "Architecture": "BAR"
}

# Main interests (what mentees want to learn)
MAIN_INTERESTS = [
    "I want to learn Python programming",
    "I want to learn web development with React",
    "I want to learn mobile app development with Flutter",
    "I want to learn machine learning basics",
    "I want to learn data science and analytics",
    "I want to learn backend development with Node.js",
    "I want to learn DevOps and CI/CD",
    "I want to learn cloud computing (AWS)",
    "I want to learn cybersecurity fundamentals",
    "I want to learn system design",
    "I want to learn Django web framework",
    "I want to learn Kotlin app development",
    "I want to learn computer vision",
    "I want to learn natural language processing",
    "I want to learn full stack development",
    "I want to learn Docker and Kubernetes",
    "I want to learn database design (PostgreSQL)",
    "I want to learn API development",
    "I want to learn UI/UX design basics",
    "I want to learn blockchain development"
]

# Additional interests (optional secondary interests)
ADDITIONAL_INTERESTS = [
    "FastAPI", "TensorFlow", "PyTorch", "GraphQL", "MongoDB",
    "TypeScript", "Rust", "Go programming", "Redis",
    "Microservices", "Git and GitHub", "Agile methodologies"
]

# Future aspirations
FUTURE_ASPIRATIONS = [
    "I want to become a software engineer at a top tech company",
    "I want to build my own startup",
    "I want to become a machine learning engineer",
    "I want to work as a full stack developer",
    "I want to become a data scientist",
    "I want to specialize in cybersecurity",
    "I want to become a mobile app developer",
    "I want to work in AI research",
    "I want to become a DevOps engineer",
    "I want to build products that help people",
    "I want to work on open source projects full-time",
    "I want to become a backend architect",
    "I want to work in cloud infrastructure",
    "I want to become a tech entrepreneur",
    "I want to make impactful applications for Nepal"
]

# Learning preferences (Section 3)
MOTIVATIONS = [
    "Advancing your career or professional skills",
    "Exploring new knowledge or satisfying curiosity",
    "Making a positive impact on society or your community",
    "Receiving recognition or praise for your work",
    "Solving challenging problems or overcoming obstacles",
    "Gaining autonomy and control over your work or learning"
]

GUIDANCE_PREFERENCES = [
    "Provide a clear and direct instructions on exactly what to do.",
    "Provide space for trial-and-error and step in only if necessary.",
    "Step-by-step guidance and regular feedback at every stage."
]

FEEDBACK_STYLES = [
    "Encouraging, highlighting strengths while addressing issues",
    "Only on important points that matter most",
    "Detailed with guidance and regular check-ins"
]

DISCUSSION_STYLES = [
    "Speak openly and share thoughts as they come",
    "Contribute when needed and keep things balanced",
    "Listen carefully first and respond only when necessary"
]

DISAGREEMENT_APPROACHES = [
    "Explain your reasoning directly",
    "Ask questions until the issue becomes clear",
    "Try it their way first, then reassess"
]

COMMITMENT_STYLES = [
    "I commit carefully and make sure I can follow through",
    "I commit based on current capacity and reassess later",
    "I commit fully at the start and adapt my approach as I go"
]


# =======================
# EMBEDDING GENERATOR
# =======================

def generate_realistic_embedding(dim=384) -> List[float]:
    """Generate 384-dim normalized embedding (all-MiniLM-L6-v2 compatible)"""
    vec = np.random.randn(dim) * 0.1
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


# =======================
# MENTEE GENERATOR
# =======================

def generate_campus_roll(existing_rolls: set) -> str:
    """Generate unique campus roll number for mentees"""
    # Mentees are mostly Computer/Electronics students
    streams = ["Computer", "Electronics (Communication/Information)", "Electrical"]
    stream = random.choice(streams)
    dept_code = DEPT_CODES.get(stream, "BCT")
    batch = random.choice(BATCH_YEARS)

    # Generate unique roll
    for _ in range(100):
        roll_num = random.randint(1, 150)
        roll = f"{batch}{dept_code}{roll_num:03d}"
        if roll not in existing_rolls:
            existing_rolls.add(roll)
            return roll

    # Fallback
    roll_num = len(existing_rolls) + 1
    return f"{batch}{dept_code}{roll_num:03d}"


def generate_mentee(i: int, existing_rolls: set) -> Dict:
    """Generate realistic mentee matching your exact Google Form"""

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    # Section 1: Basic Information
    campus_roll = generate_campus_roll(existing_rolls)

    # Q5: Hobby (70% have it)
    hobby = random.choice(HOBBIES) if random.random() < 0.7 else ""

    # Section 2: Learning Goals
    # Q6: Main Interest
    main_interest = random.choice(MAIN_INTERESTS)

    # Q7: Expertise level (mentees are 1-3, mostly 1-2)
    main_expertise_level = random.choices([1, 2, 3], weights=[0.5, 0.4, 0.1])[0]

    # Q8-9: Additional interests (40% have them)
    has_additional = random.random() < 0.4
    additional_interest = random.choice(ADDITIONAL_INTERESTS) if has_additional else ""
    additional_level = random.randint(1, 2) if has_additional else None

    # Q10: Future aspirations
    future_aspiration = random.choice(FUTURE_ASPIRATIONS)

    # Section 3: Learning Preferences
    # Q11: Motivations (select up to 2)
    num_motivations = random.choices([1, 2], weights=[0.3, 0.7])[0]
    motivations = random.sample(MOTIVATIONS, num_motivations)

    # Q12-16: Single choice questions
    guidance_pref = random.choice(GUIDANCE_PREFERENCES)
    feedback_style = random.choice(FEEDBACK_STYLES)
    discussion_style = random.choice(DISCUSSION_STYLES)
    disagreement_approach = random.choice(DISAGREEMENT_APPROACHES)
    commitment_style = random.choice(COMMITMENT_STYLES)

    return {
        # Section 1
        "Name": f"{first} {last}",
        "Campus Roll Number": campus_roll,
        "Personal email address": f"{first.lower()}.{last.lower()}{i:02d}@student.edu.np",
        "Hobby (Optional)": hobby,

        # Section 2
        "Main Interest": main_interest,
        "Your Expertise Level (Above Area)": main_expertise_level,
        "Additional Interest Areas (Optional)": additional_interest,
        "Your Expertise Level (Optional)": additional_level if additional_level else "",
        "Future Aspirations": future_aspiration,

        # Section 3
        "When making decisions about how to spend your time or energy, what motivates you the most?": ", ".join(motivations),
        "When you're unsure about your next step, the guidance you prefer is": guidance_pref,
        "When receiving feedback, you usually prefer it to be": feedback_style,
        "In a discussion where ideas are being exchanged, you usually": discussion_style,
        "If a mentor suggests an approach you believe is wrong, you are most likely to": disagreement_approach,
        "When you commit to something, what best describes how you usually handle it?": commitment_style,
    }


def get_dummy_mentees(n: int = 30) -> List[Dict]:
    """Generate n mentees with unique campus rolls"""
    existing_rolls = set()
    return [generate_mentee(i, existing_rolls) for i in range(n)]


# =======================
# VALIDATION
# =======================

def validate_mentee_data(mentees: List[Dict]) -> List[str]:
    """Validate mentees match form constraints"""
    errors = []

    for i, m in enumerate(mentees):
        # Required fields
        required = ["Name", "Campus Roll Number", "Personal email address", 
                   "Main Interest", "Your Expertise Level (Above Area)",
                   "Future Aspirations"]

        for field in required:
            if not m.get(field):
                errors.append(f"Mentee {i}: missing required field '{field}'")

        # Expertise level range (mentees are 1-3)
        main_level = m.get("Your Expertise Level (Above Area)")
        if main_level and not (1 <= main_level <= 5):
            errors.append(f"Mentee {i}: Main expertise level must be 1-5, got {main_level}")

    # Unique emails
    emails = [m.get("Personal email address") for m in mentees]
    if len(emails) != len(set(emails)):
        errors.append("Duplicate email addresses found")

    # Unique campus rolls
    rolls = [m.get("Campus Roll Number") for m in mentees]
    if len(rolls) != len(set(rolls)):
        errors.append("Duplicate campus roll numbers found")

    return errors


# =======================
# SQL EXPORT (NEW!)
# =======================

def export_to_sql(mentees: List[Dict], filename: str = "mentee_dummy_data.sql"):
    """Export mentee data as SQL INSERT statements for Person B"""

    with open(filename, 'w', encoding='utf-8') as f:
        # Write header
        f.write("-- Dummy Mentee Data for Hack-A-Week 2026\n")
        f.write(f"-- Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}\n")
        f.write(f"-- Total mentees: {len(mentees)}\n")
        f.write("-- This file uses Person A's schema definition\n\n")

        for mentee in mentees:
            # Generate embedding vector (384 dimensions)
            embedding = generate_realistic_embedding(384)
            embedding_str = '[' + ','.join(f"{x:.6f}" for x in embedding) + ']'

            # Escape single quotes for SQL
            def escape(text):
                if text is None or text == "":
                    return ""
                return str(text).replace("'", "''")

            # Handle optional numeric field
            additional_level = mentee.get('Your Expertise Level (Optional)')
            if additional_level and str(additional_level).strip():
                additional_level_sql = str(additional_level)
            else:
                additional_level_sql = "NULL"

            # Build INSERT statement
            sql = f"""INSERT INTO mentees (
    name, 
    campus_roll, 
    email, 
    hobby, 
    main_interest, 
    main_interest_level, 
    additional_interest, 
    additional_interest_level, 
    future_aspirations, 
    motivations, 
    guidance_preference, 
    feedback_style, 
    discussion_style, 
    disagreement_approach, 
    commitment_style, 
    embedding
) VALUES (
    '{escape(mentee['Name'])}',
    '{escape(mentee['Campus Roll Number'])}',
    '{escape(mentee['Personal email address'])}',
    '{escape(mentee.get('Hobby (Optional)', ''))}',
    '{escape(mentee['Main Interest'])}',
    {mentee['Your Expertise Level (Above Area)']},
    '{escape(mentee.get('Additional Interest Areas (Optional)', ''))}',
    {additional_level_sql},
    '{escape(mentee['Future Aspirations'])}',
    '{escape(mentee["When making decisions about how to spend your time or energy, what motivates you the most?"])}',
    '{escape(mentee["When you're unsure about your next step, the guidance you prefer is"])}',
    '{escape(mentee["When receiving feedback, you usually prefer it to be"])}',
    '{escape(mentee["In a discussion where ideas are being exchanged, you usually"])}',
    '{escape(mentee["If a mentor suggests an approach you believe is wrong, you are most likely to"])}',
    '{escape(mentee["When you commit to something, what best describes how you usually handle it?"])}',
    '{embedding_str}'
);

"""
            f.write(sql)

    print(f"✅ Generated {len(mentees)} SQL INSERT statements")
    print(f"📁 File saved: {filename}")


# =======================
# MAIN
# =======================

if __name__ == "__main__":
    print("🧪 Generating dummy MENTEE data for Hack-A-Week 2026...\n")

    # Generate 30 test profiles (matching mentor count)
    mentees = get_dummy_mentees(30)

    print(f"✅ Generated {len(mentees)} mentees\n")

    # Validate
    errors = validate_mentee_data(mentees)
    if errors:
        print(f"❌ {len(errors)} validation errors:")
        for error in errors[:5]:
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")
        print("\n⚠️  Proceeding with SQL generation anyway...\n")
    else:
        print("✅ All mentee data valid!\n")

    # Sample preview
    print("📋 Sample Mentee (first entry):")
    sample = mentees[0]
    for key, value in list(sample.items())[:8]:
        if value:
            display_value = str(value)[:30] + "..." if len(str(value)) > 30 else value
            print(f"   {key}: {display_value}")
    print("   ... (and more fields)\n")

    # Test embedding
    print("🔢 Test Embedding:")
    emb = generate_realistic_embedding(384)
    print(f"   Length: {len(emb)} dimensions")
    print(f"   Norm: {np.linalg.norm(emb):.4f} (should be ~1.0)")
    print(f"   Sample: [{emb[0]:.4f}, {emb[1]:.4f}, {emb[2]:.4f}, ...]\n")

    # Export to SQL
    print("💾 Exporting to SQL file...")
    export_to_sql(mentees, "mentorship-program/postgres/mentee_dummy_data.sql")

    print("\n🎉 Complete! Ready for Person B's init_db.py")
    print("\n📦 Deliverable:")
    print("   ✓ mentee_dummy_data.sql (30 test mentee profiles)")
    print("\n🔄 Next Step:")
    print("   → Send mentee_dummy_data.sql to Person B")
    print("   → Person B will load it into PostgreSQL database")