"""
Dummy Mentor Data Generator - Mentors Only
Hack-A-Week 2026 Mentorship Program
Generated: January 21, 2026
"""

import random
import numpy as np
import pandas as pd
from typing import List, Dict

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
    # Q6: Engineering stream (typically 1-2 selections)
    num_streams = random.choices([1, 2], weights=[0.7, 0.3])[0]
    eng_streams = random.sample(ENGINEERING_STREAMS, num_streams)
    primary_stream = eng_streams[0]
    
    # Q2: Campus roll based on primary stream
    campus_roll = generate_campus_roll(primary_stream, existing_rolls)
    
    # Q5: Hobby (70% have it)
    hobby = random.choice(HOBBIES) if random.random() < 0.7 else ""
    
    # Section 2: Expertise
    # Q7: Experience (typically 1-2 selections)
    num_exp = random.choices([1, 2], weights=[0.6, 0.4])[0]
    experiences = random.sample(EXPERIENCE_TYPES, num_exp)
    
    # Q8: Work affiliation (if has Industry/Academia/Entrepreneurship)
    has_work = any(e in ["Industry", "Academia", "Entrepreneurship"] for e in experiences)
    work_affiliation = random.choice(WORK_AFFILIATIONS) if has_work else ""
    
    # Q9: Main expertise
    main_expertise = random.choice(MAIN_EXPERTISE_AREAS)
    
    # Q10: Main expertise level (mentors are 3-5)
    main_expertise_level = random.choices([3, 4, 5], weights=[0.3, 0.5, 0.2])[0]
    
    # Q11-12: Additional skills (50% have them)
    has_additional = random.random() < 0.5
    additional_expertise = random.choice(ADDITIONAL_SKILLS) if has_additional else ""
    additional_level = random.randint(2, 4) if has_additional else None
    
    # Q13: Mentee capacity
    mentee_capacity = random.choices([1, 2, 3, 4], weights=[0.1, 0.3, 0.4, 0.2])[0]
    
    # Q14: Hours per week
    hours_per_week = random.choices(
        ["Less than 1 hour", "1–2 hours", "2–3 hours", "3+ hours"],
        weights=[0.1, 0.4, 0.4, 0.1]
    )[0]
    
    # Q15: Contact method
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
    # Q16: Motivations (select up to 2)
    num_motivations = random.choices([1, 2], weights=[0.3, 0.7])[0]
    motivations = random.sample(MOTIVATIONS, num_motivations)
    
    # Q17-21: Single choice questions
    guidance_pref = random.choice(GUIDANCE_PREFERENCES)
    feedback_style = random.choice(FEEDBACK_STYLES)
    discussion_style = random.choice(DISCUSSION_STYLES)
    disagreement_approach = random.choice(DISAGREEMENT_APPROACHES)
    commitment_style = random.choice(COMMITMENT_STYLES)
    
    return {
        # Section 1
        "Name": f"{first} {last}",
        "Campus Roll Number": campus_roll,
        "Personal email address": f"{first.lower()}.{last.lower()}{i:02d}@gmail.com",
        "Hobby (Optional)": hobby,
        
        # Section 2
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
        
        # Section 3
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
        # Required fields
        required = ["Name", "Campus Roll Number", "Personal email address", 
                   "Main Expertise", "Your Expertise Level (Above Area)",
                   "How many mentees will you be taking?",
                   "Where should your mentee contact you?"]
        
        for field in required:
            if not m.get(field):
                errors.append(f"Mentor {i}: missing required field '{field}'")
        
        # Expertise level range
        main_level = m.get("Your Expertise Level (Above Area)")
        if main_level and not (1 <= main_level <= 5):
            errors.append(f"Mentor {i}: Main expertise level must be 1-5, got {main_level}")
        
        # Mentee capacity
        capacity = m.get("How many mentees will you be taking?")
        if capacity and capacity not in [1, 2, 3, 4]:
            errors.append(f"Mentor {i}: Mentee capacity must be 1-4, got {capacity}")
    
    # Unique emails
    emails = [m.get("Personal email address") for m in mentors]
    if len(emails) != len(set(emails)):
        errors.append("Duplicate email addresses found")
    
    # Unique campus rolls
    rolls = [m.get("Campus Roll Number") for m in mentors]
    if len(rolls) != len(set(rolls)):
        errors.append("Duplicate campus roll numbers found")
    
    return errors

# =======================
# EXCEL EXPORT
# =======================

def export_to_excel(mentors: List[Dict]):
    """Export to Excel matching Google Form format"""
    
    mentor_df = pd.DataFrame(mentors)
    mentor_df.to_excel("dummy_mentor_responses.xlsx", index=False)
    print(f"✅ Saved {len(mentors)} mentor responses to dummy_mentor_responses.xlsx")

# =======================
# MAIN
# =======================

if __name__ == "__main__":
    print("🧪 Generating dummy MENTOR data for Hack-A-Week 2026...\n")
    
    # Generate
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
    else:
        print("✅ All mentor data valid!")
    
    # Sample
    print("\n📋 Sample Mentor:")
    sample = mentors[0]
    for key, value in sample.items():
        if value:  # Only show non-empty
            print(f"   {key}: {value}")
    
    # Test embedding
    print("\n🔢 Test Embedding:")
    emb = generate_realistic_embedding()
    print(f"   Length: {len(emb)}")
    print(f"   Norm: {np.linalg.norm(emb):.4f}")
    print(f"   Sample: {emb[:5]}...")
    
    # Export
    print("\n💾 Exporting to Excel...")
    export_to_excel(mentors)
    
    print("\n🎉 Mentor dummy data generation complete!")
    print("\n📦 Functions available for Person B:")
    print("   from generate_dummy_data import get_dummy_mentors, generate_realistic_embedding")
    print("\n📁 File created:")
    print("   - dummy_mentor_responses.xlsx (20 mentors)")
