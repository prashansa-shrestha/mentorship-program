"""
Dummy Mentor Data Generator - SQL Version
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

# Section 1: Basic Info
FIRST_NAMES = [
    "Aarav", "Priya", "Arjun", "Ananya", "Rohan", "Diya", "Kiran", "Sanjana",
    "Aditya", "Ishita", "Rahul", "Kavya", "Nikhil", "Shreya", "Vivek", "Pooja",
    "Amit", "Riya", "Suresh", "Meera", "Rajesh", "Neha", "Prakash", "Divya"
]

LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Thapa", "Shrestha", "Adhikari",
    "Rai", "Tamang", "Magar", "Gurung", "Karki", "Bhattarai", "Pandey", "Joshi"
]

HOBBIES = [
    "Reading", "Gaming", "Photography", "Hiking", "Music", "Cooking", 
    "Chess", "Football", "Cricket", "Badminton", "Traveling", "Drawing",
    "Coding side projects", "Open source contribution", "Blogging", "Guitar"
]

# Campus roll number components
BATCH_YEARS = ["075", "076", "077", "078", "079"]
DEPT_CODES = {
    "Computer": "BCT",
    "Electrical": "BEL", 
    "Electronics (Communication/Information)": "BEX",
    "Civil": "BCE",
    "Mechanical": "BME",
    "Architecture": "BAR",
    "Aerospace": "BAE",
    "Chemical": "BCH"
}

# Section 2: Expertise
ENGINEERING_STREAMS = [
    "Civil", "Electrical", "Electronics (Communication/Information)", 
    "Computer", "Mechanical", "Architecture", "Aerospace", "Chemical"
]

EXPERIENCE_TYPES = ["Industry", "Academia", "Entrepreneurship", "Government"]

WORK_AFFILIATIONS = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Tesla",
    "Fusemachines", "Leapfrog Technology", "F1Soft", "eSewa",
    "Khalti", "CloudFactory", "Verisk Nepal", "Deerwalk",
    "Kathmandu University", "Tribhuvan University", "IOE Pulchowk",
    "Self-employed startup", "Freelance consultant", "Research lab"
]

# Main expertise areas (tech-focused)
MAIN_EXPERTISE_AREAS = [
    "Python", "Java", "C++", "JavaScript", "React", "Node.js",
    "Machine Learning", "Data Science", "Deep Learning", "Computer Vision",
    "Web Development", "Mobile Development", "Flutter", "Android",
    "DevOps", "Cloud Computing", "AWS", "Docker", "Kubernetes",
    "Cybersecurity", "Blockchain", "System Design", "Databases",
    "UI/UX Design", "Backend Development", "Frontend Development"
]

ADDITIONAL_SKILLS = [
    "Kotlin", "Swift", "Go", "Rust", "TypeScript", "GraphQL",
    "PostgreSQL", "MongoDB", "Redis", "FastAPI", "Django",
    "TensorFlow", "PyTorch", "NLP", "LangChain", "API Design"
]

# Section 3: Mentoring Style
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

CONTACT_METHODS = [
    "WhatsApp - +977-98XXXXXXXX",
    "Instagram - https://www.instagram.com/",
    "LinkedIn - https://www.linkedin.com/in/",
    "Discord - username#1234",
    "Telegram - @username"
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
# MENTOR GENERATOR
# =======================

def generate_campus_roll(stream: str, existing_rolls: set) -> str:
    """Generate unique campus roll number"""
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


def generate_mentor(i: int, existing_rolls: set) -> Dict:
    """Generate realistic mentor matching your exact Google Form"""

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    # Section 1: Basic Information
    num_streams = random.choices([1, 2], weights=[0.7, 0.3])[0]
    eng_streams = random.sample(ENGINEERING_STREAMS, num_streams)
    primary_stream = eng_streams[0]

    campus_roll = generate_campus_roll(primary_stream, existing_rolls)
    hobby = random.choice(HOBBIES) if random.random() < 0.7 else ""

    # Section 2: Expertise
    num_exp = random.choices([1, 2], weights=[0.6, 0.4])[0]
    experiences = random.sample(EXPERIENCE_TYPES, num_exp)

    has_work = any(e in ["Industry", "Academia", "Entrepreneurship"] for e in experiences)
    work_affiliation = random.choice(WORK_AFFILIATIONS) if has_work else ""

    main_expertise = random.choice(MAIN_EXPERTISE_AREAS)
    main_expertise_level = random.choices([3, 4, 5], weights=[0.3, 0.5, 0.2])[0]

    has_additional = random.random() < 0.5
    additional_expertise = random.choice(ADDITIONAL_SKILLS) if has_additional else ""
    additional_level = random.randint(2, 4) if has_additional else None

    mentee_capacity = random.choices([1, 2, 3, 4], weights=[0.1, 0.3, 0.4, 0.2])[0]
    hours_per_week = random.choices(
        ["Less than 1 hour", "1–2 hours", "2–3 hours", "3+ hours"],
        weights=[0.1, 0.4, 0.4, 0.1]
    )[0]

    contact_template = random.choice(CONTACT_METHODS)
    if "instagram.com" in contact_template:
        contact = f"Instagram - https://www.instagram.com/{first.lower()}{last.lower()}"
    elif "linkedin.com" in contact_template:
        contact = f"LinkedIn - https://www.linkedin.com/in/{first.lower()}-{last.lower()}"
    elif "WhatsApp" in contact_template:
        contact = f"WhatsApp - +977-98{random.randint(10000000, 99999999)}"
    else:
        contact = contact_template.replace("username", f"{first.lower()}{i}")

    # Section 3: Mentoring Style
    num_motivations = random.choices([1, 2], weights=[0.3, 0.7])[0]
    motivations = random.sample(MOTIVATIONS, num_motivations)

    guidance_pref = random.choice(GUIDANCE_PREFERENCES)
    feedback_style = random.choice(FEEDBACK_STYLES)
    discussion_style = random.choice(DISCUSSION_STYLES)
    disagreement_approach = random.choice(DISAGREEMENT_APPROACHES)
    commitment_style = random.choice(COMMITMENT_STYLES)

    return {
        "Name": f"{first} {last}",
        "Campus Roll Number": campus_roll,
        "Personal email address": f"{first.lower()}.{last.lower()}{i:02d}@gmail.com",
        "Hobby (Optional)": hobby,
        "Engineering stream you will mentor for": ", ".join(eng_streams),
        "Your Experience": ", ".join(experiences),
        "Current Work Affiliation (if applicable)": work_affiliation,
        "Main Expertise": main_expertise,
        "Your Expertise Level (Above Area)": main_expertise_level,
        "Additional Mentorship Areas (Optional)": additional_expertise,
        "Your Expertise Level (Optional)": additional_level if additional_level else "",
        "How many mentees will you be taking?": mentee_capacity,
        "How many hours per week can you realistically dedicate to mentoring sessions ?": hours_per_week,
        "Where should your mentee contact you?": contact,
        "When making decisions about how to spend your time or energy, what motivates you the most?": ", ".join(motivations),
        "When you're unsure about your next step, the guidance you prefer is": guidance_pref,
        "When giving feedback, you usually prefer it to be": feedback_style,
        "In a discussion where ideas are being exchanged, you usually": discussion_style,
        "If a mentee suggests an approach you believe is wrong, you are most likely to": disagreement_approach,
        "When you commit to something, what best describes how you usually handle it?": commitment_style,
    }


def get_dummy_mentors(n: int = 20) -> List[Dict]:
    """Generate n mentors with unique campus rolls"""
    existing_rolls = set()
    return [generate_mentor(i, existing_rolls) for i in range(n)]


# =======================
# VALIDATION
# =======================

def validate_mentor_data(mentors: List[Dict]) -> List[str]:
    """Validate mentors match form constraints"""
    errors = []

    for i, m in enumerate(mentors):
        required = ["Name", "Campus Roll Number", "Personal email address", 
                   "Main Expertise", "Your Expertise Level (Above Area)",
                   "How many mentees will you be taking?",
                   "Where should your mentee contact you?"]

        for field in required:
            if not m.get(field):
                errors.append(f"Mentor {i}: missing required field '{field}'")

        main_level = m.get("Your Expertise Level (Above Area)")
        if main_level and not (1 <= main_level <= 5):
            errors.append(f"Mentor {i}: Main expertise level must be 1-5, got {main_level}")

        capacity = m.get("How many mentees will you be taking?")
        if capacity and capacity not in [1, 2, 3, 4]:
            errors.append(f"Mentor {i}: Mentee capacity must be 1-4, got {capacity}")

    emails = [m.get("Personal email address") for m in mentors]
    if len(emails) != len(set(emails)):
        errors.append("Duplicate email addresses found")

    rolls = [m.get("Campus Roll Number") for m in mentors]
    if len(rolls) != len(set(rolls)):
        errors.append("Duplicate campus roll numbers found")

    return errors


# =======================
# SQL EXPORT (NEW!)
# =======================

def export_to_sql(mentors: List[Dict], filename: str = "generate_dummy_data.sql"):
    """Export mentor data as SQL INSERT statements for Person B"""

    with open(filename, 'w', encoding='utf-8') as f:
        # Write header
        f.write("-- Dummy Mentor Data for Hack-A-Week 2026\n")
        f.write(f"-- Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}\n")
        f.write(f"-- Total mentors: {len(mentors)}\n")
        f.write("-- This file uses Person A's schema definition\n\n")

        for mentor in mentors:
            # Generate embedding vector (384 dimensions)
            embedding = generate_realistic_embedding(384)
            embedding_str = '[' + ','.join(f"{x:.6f}" for x in embedding) + ']'

            # Escape single quotes for SQL
            def escape(text):
                if text is None or text == "":
                    return ""
                return str(text).replace("'", "''")

            # Handle optional numeric field
            additional_level = mentor.get('Your Expertise Level (Optional)')
            if additional_level and str(additional_level).strip():
                additional_level_sql = str(additional_level)
            else:
                additional_level_sql = "NULL"

            # Build INSERT statement
            sql = f"""INSERT INTO mentors (
    name, 
    campus_roll, 
    email, 
    hobby, 
    engineering_streams, 
    experience_types, 
    work_affiliation, 
    main_expertise, 
    main_expertise_level, 
    additional_expertise, 
    additional_expertise_level, 
    mentee_capacity, 
    hours_per_week, 
    contact_method, 
    motivations, 
    guidance_preference, 
    feedback_style, 
    discussion_style, 
    disagreement_approach, 
    commitment_style, 
    embedding
) VALUES (
    '{escape(mentor['Name'])}',
    '{escape(mentor['Campus Roll Number'])}',
    '{escape(mentor['Personal email address'])}',
    '{escape(mentor.get('Hobby (Optional)', ''))}',
    '{escape(mentor['Engineering stream you will mentor for'])}',
    '{escape(mentor['Your Experience'])}',
    '{escape(mentor.get('Current Work Affiliation (if applicable)', ''))}',
    '{escape(mentor['Main Expertise'])}',
    {mentor['Your Expertise Level (Above Area)']},
    '{escape(mentor.get('Additional Mentorship Areas (Optional)', ''))}',
    {additional_level_sql},
    {mentor['How many mentees will you be taking?']},
    '{escape(mentor['How many hours per week can you realistically dedicate to mentoring sessions ?'])}',
    '{escape(mentor['Where should your mentee contact you?'])}',
    '{escape(mentor["When making decisions about how to spend your time or energy, what motivates you the most?"])}',
    '{escape(mentor["When you're unsure about your next step, the guidance you prefer is"])}',
    '{escape(mentor["When giving feedback, you usually prefer it to be"])}',
    '{escape(mentor["In a discussion where ideas are being exchanged, you usually"])}',
    '{escape(mentor["If a mentee suggests an approach you believe is wrong, you are most likely to"])}',
    '{escape(mentor["When you commit to something, what best describes how you usually handle it?"])}',
    '{embedding_str}'
);

"""
            f.write(sql)

    print(f"✅ Generated {len(mentors)} SQL INSERT statements")
    print(f"📁 File saved: {filename}")


# =======================
# MAIN
# =======================

if __name__ == "__main__":
    print("🧪 Generating dummy MENTOR data for Hack-A-Week 2026...\n")

    # Generate 20 test profiles (as per Day 1 requirements)
    mentors = get_dummy_mentors(20)

    print(f"✅ Generated {len(mentors)} mentors\n")

    # Validate
    errors = validate_mentor_data(mentors)
    if errors:
        print(f"❌ {len(errors)} validation errors:")
        for error in errors[:5]:
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")
        print("\n⚠️  Proceeding with SQL generation anyway...\n")
    else:
        print("✅ All mentor data valid!\n")

    # Sample preview
    print("📋 Sample Mentor (first entry):")
    sample = mentors[0]
    for key, value in list(sample.items())[:8]:
        if value:
            display_value = str(value)[:20] + "..." if len(str(value)) > 20 else value
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
    export_to_sql(mentors, "mentorship-program/postgres/mentors_dummy_data.sql")

    print("\n🎉 Complete! Ready for Person B's init_db.py")
    print("\n📦 Deliverable:")
    print("   ✓ mentors_dummy_data.sql (20 test mentor profiles)")
    print("\n🔄 Next Step:")
    print("   → Send mentors_dummy_data.sql to Person B")
    print("   → Person B will load it into PostgreSQL database")