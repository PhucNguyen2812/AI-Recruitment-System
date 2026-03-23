"""
generate_cvs.py
Phase 0 — Synthetic Data Generator
Sinh 1000 CV PDF (500 Chuẩn + 500 Rác) để train mô hình Random Forest.
Output:
  dataset/raw_cvs/relevant/   ← 500 CV Chuẩn
  dataset/raw_cvs/irrelevant/ ← 500 CV Rác
  dataset/labels.csv          ← nhãn tổng hợp
"""

import os
import random
import csv
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
TOTAL_RELEVANT = 500
TOTAL_IRRELEVANT = 500

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "..", "dataset")
RELEVANT_DIR = os.path.join(DATASET_DIR, "raw_cvs", "relevant")
IRRELEVANT_DIR = os.path.join(DATASET_DIR, "raw_cvs", "irrelevant")
LABELS_PATH = os.path.join(DATASET_DIR, "labels.csv")

os.makedirs(RELEVANT_DIR, exist_ok=True)
os.makedirs(IRRELEVANT_DIR, exist_ok=True)

fake_vi = Faker("vi_VN")
fake_en = Faker("en_US")
Faker.seed(42)
random.seed(42)

# ─────────────────────────────────────────────
# FONT — Dùng Helvetica (built-in ReportLab, hỗ trợ Latin đầy đủ)
# Tiếng Việt sẽ được romanize (transliterate) để tránh lỗi font embedding.
# Phase AI chỉ cần keyword matching, không cần hiển thị dấu tiếng Việt thực sự.
# ─────────────────────────────────────────────
FONT_NORMAL = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

def get_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CVTitle",
        fontName=FONT_BOLD,
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "CVSubtitle",
        fontName=FONT_NORMAL,
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555577"),
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "CVSection",
        fontName=FONT_BOLD,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "CVBody",
        fontName=FONT_NORMAL,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#333333"),
        spaceAfter=3,
    )
    bullet_style = ParagraphStyle(
        "CVBullet",
        fontName=FONT_NORMAL,
        fontSize=9,
        leading=13,
        leftIndent=14,
        textColor=colors.HexColor("#333333"),
        spaceAfter=2,
    )
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "section": section_style,
        "body": body_style,
        "bullet": bullet_style,
    }

# ─────────────────────────────────────────────
# KEYWORD POOLS — CV CHUẨN (RELEVANT)
# ─────────────────────────────────────────────
IT_TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++",
    "React", "Next.js", "FastAPI", "Django", "Node.js",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Docker", "Git", "Linux", "REST API", "Machine Learning",
    "Scikit-learn", "TensorFlow", "Data Structures", "Algorithms",
    "HTML", "CSS", "Object-Oriented Programming", "Unit Testing",
    "Agile", "Scrum", "CI/CD", "AWS", "Azure",
]
IT_EXPERIENCE_TEMPLATES = [
    "Developed RESTful APIs using FastAPI and PostgreSQL for a student management system.",
    "Built a web application with React frontend and Node.js backend serving 500+ users.",
    "Implemented machine learning model using Scikit-learn to classify customer reviews.",
    "Contributed to open-source Python project on GitHub with 200+ commits.",
    "Designed and optimized SQL queries reducing query time by 40%.",
    "Participated in Agile sprint planning and daily standups for a team of 6 developers.",
    "Deployed containerized applications using Docker and managed with Git.",
    "Analyzed datasets of 10,000+ records using Pandas and visualized with Matplotlib.",
    "Wrote unit tests achieving 85% code coverage for backend services.",
    "Integrated third-party APIs (payment, maps, notification) into existing platform.",
]
IT_PROJECTS = [
    "IT Intern Candidate Management System (Python, FastAPI, React)",
    "E-commerce Platform with Recommendation Engine (Scikit-learn, Django)",
    "Real-time Chat Application (WebSocket, Node.js, MongoDB)",
    "Student Grade Prediction using Decision Tree (Python, Pandas)",
    "Personal Finance Tracker Web App (Next.js, PostgreSQL)",
    "Automated Web Scraper for Job Listings (Python, BeautifulSoup)",
]
IT_EDUCATION = [
    "Bachelor of Science in Computer Science – Hanoi University of Science and Technology",
    "Bachelor of Engineering in Software Engineering – Ho Chi Minh City University of Technology",
    "Bachelor of Science in Information Technology – University of Science, VNU-HCM",
    "Bachelor of Science in Data Science – Foreign Trade University",
    "Bachelor of Engineering in Computer Engineering – Da Nang University of Technology",
]
IT_CERTS = [
    "AWS Certified Cloud Practitioner",
    "Google IT Support Professional Certificate",
    "Meta Front-End Developer Certificate",
    "Microsoft Azure Fundamentals (AZ-900)",
    "Coursera Deep Learning Specialization",
]

MKT_TECH_SKILLS = [
    "Digital Marketing", "Content Marketing", "SEO", "SEM", "Google Ads",
    "Facebook Ads", "Instagram Ads", "Email Marketing", "Marketing Automation",
    "Google Analytics", "Meta Business Suite", "HubSpot", "Mailchimp",
    "Market Research", "Consumer Behavior", "Brand Management", "Copywriting",
    "Social Media Management", "Influencer Marketing", "A/B Testing",
    "Data-driven Marketing", "CRM", "Salesforce", "KPI Reporting",
    "Campaign Management", "Excel", "PowerPoint", "Canva", "Adobe Photoshop",
]
MKT_EXPERIENCE_TEMPLATES = [
    "Managed social media accounts (Facebook, Instagram, TikTok) growing followers by 35% in 3 months.",
    "Ran Google Ads campaigns with ROAS of 4.2x for an e-commerce client.",
    "Wrote SEO-optimized blog posts achieving top-5 Google ranking for 10 target keywords.",
    "Conducted market research and competitive analysis for product launch strategy.",
    "Created and scheduled 50+ content pieces per month across multi-channel platforms.",
    "Designed email marketing campaigns using Mailchimp achieving 28% open rate.",
    "Analyzed campaign performance using Google Analytics and reported bi-weekly KPIs to team lead.",
    "Collaborated with design team to produce visual assets for digital ads using Canva.",
    "Assisted in organizing offline events attracting 300+ participants.",
    "Developed influencer outreach strategy resulting in 5 brand collaborations.",
]
MKT_PROJECTS = [
    "Social Media Growth Campaign for Local F&B Brand (Facebook, TikTok)",
    "SEO Content Strategy for E-commerce Website (Shopify, Google Search Console)",
    "Email Nurturing Funnel for SaaS Product (Mailchimp, HubSpot)",
    "Competitor Analysis Report for Consumer Electronics Brand",
    "TikTok Viral Campaign resulting in 1M+ views organically",
    "Brand Awareness Campaign with KOL collaboration for Beauty Brand",
]
MKT_EDUCATION = [
    "Bachelor of Business Administration in Marketing – National Economics University",
    "Bachelor of Arts in Advertising and Communications – Ho Chi Minh City Open University",
    "Bachelor of Commerce in Marketing – University of Economics Ho Chi Minh City",
    "Bachelor of Business in Digital Marketing – RMIT University Vietnam",
    "Bachelor of Arts in Media and Communications – Hanoi University",
]
MKT_CERTS = [
    "Google Digital Marketing & E-commerce Certificate",
    "HubSpot Content Marketing Certification",
    "Meta Social Media Marketing Certificate",
    "Google Analytics Individual Qualification (GAIQ)",
    "SEMrush SEO Fundamentals Certificate",
]

# ─────────────────────────────────────────────
# KEYWORD POOLS — CV RÁC (IRRELEVANT)
# ─────────────────────────────────────────────
IRRELEVANT_FIELDS = [
    {
        "field": "Agriculture",
        "skills": ["Crop Science", "Soil Analysis", "Irrigation Systems", "Pest Management",
                   "Agricultural Machinery", "Fertilizer Application", "Greenhouse Management",
                   "Livestock Care", "Organic Farming", "Rural Development"],
        "experiences": [
            "Managed 5-hectare rice paddy field using modern irrigation techniques.",
            "Conducted soil testing and recommended fertilizer plans for 20 farmers.",
            "Operated agricultural machinery for harvesting season efficiently.",
            "Assisted veterinary team in livestock health monitoring program.",
        ],
        "education": "Bachelor of Science in Agriculture – Can Tho University",
        "job_title": "Agricultural Technician Intern",
    },
    {
        "field": "Mechanical Engineering",
        "skills": ["AutoCAD", "SolidWorks", "CNC Machining", "Thermodynamics", "Fluid Mechanics",
                   "Welding", "Manufacturing Processes", "PLC Programming", "Quality Control",
                   "Material Science"],
        "experiences": [
            "Designed mechanical components using SolidWorks for automotive parts.",
            "Operated CNC lathe and milling machines in production workshop.",
            "Conducted quality inspection of manufactured parts per ISO standards.",
            "Troubleshot hydraulic system failures in heavy equipment.",
        ],
        "education": "Bachelor of Engineering in Mechanical Engineering – Ho Chi Minh City University of Technology",
        "job_title": "Mechanical Engineer Intern",
    },
    {
        "field": "Nursing & Healthcare",
        "skills": ["Patient Care", "Vital Signs Monitoring", "Medication Administration",
                   "Wound Care", "CPR", "Medical Records", "Phlebotomy", "HIPAA Compliance",
                   "Emergency Response", "Clinical Documentation"],
        "experiences": [
            "Provided direct patient care in 30-bed general ward under supervision.",
            "Administered medications and documented patient responses accurately.",
            "Assisted in minor surgical procedures and post-op nursing care.",
            "Collaborated with medical team for patient discharge planning.",
        ],
        "education": "Bachelor of Science in Nursing – University of Medicine and Pharmacy, Ho Chi Minh City",
        "job_title": "Nurse Intern",
    },
    {
        "field": "Culinary Arts",
        "skills": ["Food Preparation", "Knife Skills", "Pastry Making", "Menu Planning",
                   "Kitchen Safety", "HACCP", "Food Costing", "Inventory Management",
                   "Guest Service", "Wine Pairing"],
        "experiences": [
            "Prepared mise en place for 150-cover restaurant service daily.",
            "Developed seasonal dessert menu increasing dessert sales by 20%.",
            "Maintained kitchen cleanliness and food safety per HACCP standards.",
            "Assisted head chef in catering events for 500+ guests.",
        ],
        "education": "Diploma in Culinary Arts – Hoa Sen University",
        "job_title": "Kitchen Intern",
    },
    {
        "field": "Civil Engineering",
        "skills": ["AutoCAD Civil 3D", "Structural Analysis", "Concrete Mix Design",
                   "Site Supervision", "Building Codes", "Quantity Surveying",
                   "Project Scheduling", "MS Project", "Road Construction", "Land Surveying"],
        "experiences": [
            "Assisted in structural design of 3-story residential building.",
            "Prepared quantity takeoff and Bill of Quantities for road construction project.",
            "Monitored construction site compliance with safety regulations.",
            "Conducted topographic survey using total station equipment.",
        ],
        "education": "Bachelor of Engineering in Civil Engineering – Ho Chi Minh City University of Technology",
        "job_title": "Civil Engineer Intern",
    },
    {
        "field": "Fashion Design",
        "skills": ["Garment Construction", "Pattern Making", "Adobe Illustrator", "Trend Research",
                   "Textile Knowledge", "Hand Sketching", "3D Prototyping", "Sewing",
                   "Fashion Merchandising", "Color Theory"],
        "experiences": [
            "Designed and constructed 10-piece capsule collection for graduation show.",
            "Assisted senior designer in preparing fashion week presentation.",
            "Sourced sustainable fabrics and materials for eco-friendly clothing line.",
            "Managed inventory and visual merchandising for boutique store.",
        ],
        "education": "Bachelor of Arts in Fashion Design – Ho Chi Minh City University of Architecture",
        "job_title": "Fashion Design Intern",
    },
]

IRRELEVANT_FORMAT_ERRORS = [
    # Format lỗi, thiếu thông tin cơ bản
    {"type": "minimal", "body": "I want job. I am hardworking. Please hire me. Thank you."},
    {"type": "gibberish", "body": "asdf jkl qwerty uiop zxcvbn mnbvcxz lkjhgfdsa poiuytrewq"},
    {"type": "spam", "body": " ".join(["HIRING", "RECRUITMENT", "JOB", "WORK", "SALARY"] * 20)},
]

LANGUAGES = ["English", "Vietnamese (Native)", "Japanese (N3)", "Chinese (HSK 3)",
             "Korean (TOPIK 2)", "French (B1)", "German (A2)"]

GPA_RELEVANT = [round(random.uniform(3.0, 4.0), 2) for _ in range(600)]
GPA_IRRELEVANT = [round(random.uniform(2.0, 3.2), 2) for _ in range(600)]

# ─────────────────────────────────────────────
# PDF BUILDER
# ─────────────────────────────────────────────
def build_cv_pdf(filepath: str, story: list):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story)


def hr_line():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=6)


def section_header(text: str, styles: dict):
    return Paragraph(f"<b>{text.upper()}</b>", styles["section"])


def bullet_item(text: str, styles: dict):
    return Paragraph(f"• {text}", styles["bullet"])


# ─────────────────────────────────────────────
# GENERATOR — CV CHUẨN
# ─────────────────────────────────────────────
def generate_relevant_cv(index: int, position: str) -> list:
    styles = get_styles()
    story = []

    # Determine pool based on position
    if position == "IT_Intern":
        skill_pool = IT_TECH_SKILLS
        exp_pool = IT_EXPERIENCE_TEMPLATES
        proj_pool = IT_PROJECTS
        edu_pool = IT_EDUCATION
        cert_pool = IT_CERTS
        job_title = "Software Engineering / IT Intern Applicant"
    else:  # Marketing_Intern
        skill_pool = MKT_TECH_SKILLS
        exp_pool = MKT_EXPERIENCE_TEMPLATES
        proj_pool = MKT_PROJECTS
        edu_pool = MKT_EDUCATION
        cert_pool = MKT_CERTS
        job_title = "Digital Marketing Intern Applicant"

    # Personal info
    use_vn = random.random() > 0.5
    if use_vn:
        full_name = fake_vi.name().encode('ascii', 'ignore').decode('ascii') or fake_en.name()
        if not full_name.strip():
            full_name = fake_en.name()
        email = fake_en.email()
        phone = f"+84 {random.randint(30,99)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        city = random.choice(["Ho Chi Minh City", "Hanoi", "Da Nang", "Can Tho"])
    else:
        full_name = fake_en.name()
        email = fake_en.email()
        phone = fake_en.phone_number()
        city = random.choice(["Ho Chi Minh City", "Hanoi", "Da Nang"])

    story.append(Paragraph(full_name, styles["title"]))
    story.append(Paragraph(job_title, styles["subtitle"]))
    contact = f"{email} | {phone} | {city} | github.com/{fake_en.user_name()}"
    story.append(Paragraph(contact, styles["subtitle"]))
    story.append(Spacer(1, 6))
    story.append(hr_line())

    # Objective
    story.append(section_header("Objective", styles))
    obj_text = (
        f"Enthusiastic and motivated student seeking a {position.replace('_', ' ')} position "
        f"to apply technical knowledge and contribute to real-world projects while developing "
        f"professional skills in a dynamic team environment."
    )
    story.append(Paragraph(obj_text, styles["body"]))
    story.append(hr_line())

    # Skills — pick 8-14 keywords
    story.append(section_header("Technical Skills", styles))
    n_skills = random.randint(8, min(14, len(skill_pool)))
    chosen_skills = random.sample(skill_pool, n_skills)
    # Split into 2 columns visual
    half = (len(chosen_skills) + 1) // 2
    col1 = chosen_skills[:half]
    col2 = chosen_skills[half:]
    skill_rows = []
    for i in range(max(len(col1), len(col2))):
        s1 = f"• {col1[i]}" if i < len(col1) else ""
        s2 = f"• {col2[i]}" if i < len(col2) else ""
        skill_rows.append([
            Paragraph(s1, styles["bullet"]),
            Paragraph(s2, styles["bullet"]),
        ])
    if skill_rows:
        tbl = Table(skill_rows, colWidths=["50%", "50%"])
        tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(tbl)
    story.append(hr_line())

    # Education
    story.append(section_header("Education", styles))
    edu = random.choice(edu_pool)
    gpa = random.choice(GPA_RELEVANT)
    grad_year = random.randint(2024, 2026)
    story.append(Paragraph(f"<b>{edu}</b>", styles["body"]))
    story.append(Paragraph(f"Expected Graduation: {grad_year} | GPA: {gpa}/4.0", styles["body"]))
    story.append(hr_line())

    # Experience
    story.append(section_header("Experience / Internship", styles))
    n_exp = random.randint(2, 4)
    chosen_exp = random.sample(exp_pool, min(n_exp, len(exp_pool)))
    company = fake_en.company()
    duration = f"{random.randint(1,6)} month(s) internship at {company}"
    story.append(Paragraph(f"<b>{duration}</b>", styles["body"]))
    for e in chosen_exp:
        story.append(bullet_item(e, styles))
    story.append(hr_line())

    # Projects
    story.append(section_header("Projects", styles))
    n_proj = random.randint(1, 3)
    chosen_proj = random.sample(proj_pool, min(n_proj, len(proj_pool)))
    for p in chosen_proj:
        story.append(bullet_item(p, styles))
    story.append(hr_line())

    # Certifications (optional 60%)
    if random.random() > 0.4:
        story.append(section_header("Certifications", styles))
        cert = random.choice(cert_pool)
        year = random.randint(2023, 2025)
        story.append(bullet_item(f"{cert} ({year})", styles))
        story.append(hr_line())

    # Languages
    story.append(section_header("Languages", styles))
    langs = random.sample(LANGUAGES, random.randint(2, 3))
    for lang in langs:
        story.append(bullet_item(lang, styles))

    return story


# ─────────────────────────────────────────────
# GENERATOR — CV RÁC
# ─────────────────────────────────────────────
def generate_irrelevant_cv(index: int) -> list:
    styles = get_styles()
    story = []

    irr_type = random.random()

    # 15% format lỗi nặng (blank/gibberish)
    if irr_type < 0.15:
        err = random.choice(IRRELEVANT_FORMAT_ERRORS)
        story.append(Paragraph("Applicant", styles["title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(err["body"], styles["body"]))
        return story

    # 85% ngành nghề sai hoàn toàn
    field_data = random.choice(IRRELEVANT_FIELDS)

    full_name = fake_en.name()
    email = fake_en.email()
    phone = fake_en.phone_number()
    city = random.choice(["Ho Chi Minh City", "Hanoi", "Da Nang", "Hue"])

    story.append(Paragraph(full_name, styles["title"]))
    story.append(Paragraph(f"{field_data['job_title']}", styles["subtitle"]))
    story.append(Paragraph(f"{email} | {phone} | {city}", styles["subtitle"]))
    story.append(Spacer(1, 6))
    story.append(hr_line())

    # Objective
    obj_text = (
        f"Dedicated professional with experience in the {field_data['field']} sector "
        f"seeking an internship opportunity to apply specialized knowledge and grow professionally."
    )
    story.append(section_header("Objective", styles))
    story.append(Paragraph(obj_text, styles["body"]))
    story.append(hr_line())

    # Skills (domain-irrelevant)
    story.append(section_header("Skills", styles))
    n_skills = random.randint(5, len(field_data["skills"]))
    chosen_skills = random.sample(field_data["skills"], n_skills)
    for skill in chosen_skills:
        story.append(bullet_item(skill, styles))
    story.append(hr_line())

    # Education
    story.append(section_header("Education", styles))
    gpa = random.choice(GPA_IRRELEVANT)
    grad_year = random.randint(2023, 2026)
    story.append(Paragraph(f"<b>{field_data['education']}</b>", styles["body"]))
    story.append(Paragraph(f"Expected Graduation: {grad_year} | GPA: {gpa}/4.0", styles["body"]))
    story.append(hr_line())

    # Experience
    story.append(section_header("Experience", styles))
    n_exp = random.randint(1, len(field_data["experiences"]))
    chosen_exp = random.sample(field_data["experiences"], n_exp)
    company = fake_en.company()
    story.append(Paragraph(f"<b>Intern at {company}</b>", styles["body"]))
    for e in chosen_exp:
        story.append(bullet_item(e, styles))
    story.append(hr_line())

    # Languages
    story.append(section_header("Languages", styles))
    langs = random.sample(LANGUAGES, random.randint(1, 2))
    for lang in langs:
        story.append(bullet_item(lang, styles))

    return story


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    labels = []

    # 1. Generate RELEVANT CVs (250 IT + 250 Marketing)
    print(f"=== Generating {TOTAL_RELEVANT} RELEVANT CVs ===")
    positions = (
        ["IT_Intern"] * (TOTAL_RELEVANT // 2) +
        ["Marketing_Intern"] * (TOTAL_RELEVANT // 2)
    )
    random.shuffle(positions)

    for i, pos in enumerate(positions):
        filename = f"relevant_{i+1:04d}.pdf"
        filepath = os.path.join(RELEVANT_DIR, filename)
        story = generate_relevant_cv(i, pos)
        build_cv_pdf(filepath, story)
        labels.append({"filename": filename, "label": 1, "position": pos})
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{TOTAL_RELEVANT}] Relevant CVs generated...")

    print(f"✓ {TOTAL_RELEVANT} Relevant CVs done.\n")

    # 2. Generate IRRELEVANT CVs
    print(f"=== Generating {TOTAL_IRRELEVANT} IRRELEVANT CVs ===")
    for i in range(TOTAL_IRRELEVANT):
        filename = f"irrelevant_{i+1:04d}.pdf"
        filepath = os.path.join(IRRELEVANT_DIR, filename)
        story = generate_irrelevant_cv(i)
        build_cv_pdf(filepath, story)
        labels.append({"filename": filename, "label": 0, "position": "None"})
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{TOTAL_IRRELEVANT}] Irrelevant CVs generated...")

    print(f"✓ {TOTAL_IRRELEVANT} Irrelevant CVs done.\n")

    # 3. Write labels.csv
    with open(LABELS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "label", "position"])
        writer.writeheader()
        writer.writerows(labels)

    print(f"✓ labels.csv written to: {LABELS_PATH}")
    print(f"\n{'='*50}")
    print(f"  PHASE 0 COMPLETE")
    print(f"  Relevant CVs : {TOTAL_RELEVANT}  → {RELEVANT_DIR}")
    print(f"  Irrelevant CVs: {TOTAL_IRRELEVANT} → {IRRELEVANT_DIR}")
    print(f"  Labels CSV   : {LABELS_PATH}")
    print(f"{'='*50}\n")
    print("Next step: Run `python verify_data.py` to validate PDF text extraction.")


if __name__ == "__main__":
    main()
