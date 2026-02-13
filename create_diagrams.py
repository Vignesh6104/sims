from PIL import Image, ImageDraw, ImageFont
import os

def draw_text_centered(draw, pos, text, fill=(0,0,0), font=None):
    draw.text(pos, text, fill=fill, anchor="mm", font=font)

def create_diagram_v2(filename, title, elements, connections):
    # Higher resolution for better clarity
    width, height = 1200, 900
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        # Attempt to load a better font if possible, else default
        font_size = 14
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    except:
        font = None
        title_font = None

    # Draw Title
    draw.text((width/2, 40), title, fill=(0, 0, 0), anchor="mm")
    
    # Draw Elements
    for eid, info in elements.items():
        x, y, w, h = info[:4]
        text = info[4]
        color = info[5] if len(info) > 5 else (240, 240, 240) # Light grey default
        
        # Draw Box with shadow
        draw.rectangle([x+3, y+3, x+w+3, y+h+3], fill=(200, 200, 200))
        draw.rectangle([x, y, x+w, y+h], fill=color, outline=(0, 0, 0), width=2)
        
        # Draw Header/Title of box
        header_h = 30
        draw.rectangle([x, y, x+w, y+header_h], fill=(100, 149, 237), outline=(0, 0, 0), width=2)
        
        lines = text.split('\n')
        # Header text
        draw.text((x + w/2, y + header_h/2), lines[0], fill=(255, 255, 255), anchor="mm")
        
        # Body text
        if len(lines) > 1:
            body_text = "\n".join(lines[1:])
            draw.text((x + 10, y + header_h + 10), body_text, fill=(0, 0, 0))

    # Draw Connections
    for start_id, end_id, label in connections:
        if start_id in elements and end_id in elements:
            s = elements[start_id]
            e = elements[end_id]
            
            # Mid-points
            s_center = (s[0] + s[2]/2, s[1] + s[3]/2)
            e_center = (e[0] + e[2]/2, e[1] + e[3]/2)
            
            # Simple line for now
            draw.line([s_center, e_center], fill=(50, 50, 50), width=2)
            
            # Arrow head at end
            # Calculate angle roughly or just draw at border
            # For simplicity, draw mid-point label
            mid_pt = ((s_center[0] + e_center[0])/2, (s_center[1] + e_center[1])/2)
            draw.text(mid_pt, label, fill=(255, 0, 0), anchor="mm")

    img.save(filename)
    print(f"Saved {filename}")

# --- 1. ACCURATE ER DIAGRAM ---
# Based on actual model fields
er_elements = {
    "students": (50, 100, 200, 150, "students\nid (PK)\nemail\nfull_name\nclass_id (FK)\nparent_id (FK)\nroll_number"),
    "classrooms": (400, 100, 200, 100, "classrooms\nid (PK)\nname\nteacher_id (FK)"),
    "teachers": (750, 100, 200, 120, "teachers\nid (PK)\nemail\nfull_name\nqualification"),
    "attendance": (50, 400, 200, 100, "attendance\nid (PK)\nstudent_id (FK)\ndate\nstatus"),
    "marks": (400, 400, 200, 120, "marks\nid (PK)\nstudent_id (FK)\nsubject\nscore\nexam_id (FK)"),
    "exams": (750, 400, 200, 80, "exams\nid (PK)\nname\ndate"),
    "assignments": (50, 650, 200, 120, "assignments\nid (PK)\nclass_id (FK)\nsubject_id (FK)\nteacher_id (FK)"),
    "submissions": (400, 650, 200, 120, "submissions\nid (PK)\nassignment_id (FK)\nstudent_id (FK)\ngrade"),
    "fee_payments": (750, 650, 200, 120, "fee_payments\nid (PK)\nstudent_id (FK)\namount_paid\nstatus")
}
er_conns = [
    ("students", "classrooms", "N:1"),
    ("teachers", "classrooms", "1:N"),
    ("students", "attendance", "1:N"),
    ("students", "marks", "1:N"),
    ("exams", "marks", "1:N"),
    ("classrooms", "assignments", "1:N"),
    ("assignments", "submissions", "1:N"),
    ("students", "submissions", "1:N"),
    ("students", "fee_payments", "1:N")
]
create_diagram_v2("er_diag.png", "ACCURATE ENTITY RELATIONSHIP DIAGRAM", er_elements, er_conns)

# --- 2. SYSTEM ARCHITECTURE ---
arch_elements = {
    "client": (100, 350, 200, 150, "Client Layer\nWeb Browser\nMobile Browser\n(React SPA)"),
    "api_gateway": (450, 350, 250, 150, "API Layer (FastAPI)\nREST Endpoints\nJWT Auth\nRole Checker"),
    "db_layer": (850, 350, 250, 150, "Data Layer\nPostgreSQL\nSQLAlchemy ORM\nMigrations (Alembic)")
}
arch_conns = [
    ("client", "api_gateway", "HTTPS / JSON"),
    ("api_gateway", "db_layer", "SQL / AsyncPG")
]
create_diagram_v2("arch_diag.png", "SYSTEM ARCHITECTURE (3-TIER)", arch_elements, arch_conns)

# --- 3. USE CASE DIAGRAM ---
uc_elements = {
    "admin": (50, 100, 150, 200, "System Admin\n- Manage Users\n- Define Fees\n- Setup Classes\n- Library Config", (255, 220, 220)),
    "teacher": (50, 350, 150, 200, "Teacher\n- Mark Attendance\n- Post Assignments\n- Grade Students\n- Manage Timetable", (220, 255, 220)),
    "student": (50, 600, 150, 200, "Student\n- View Schedule\n- Submit Work\n- Check Marks\n- Borrow Books", (220, 220, 255)),
    "use_cases": (400, 50, 600, 800, "SIMS FUNCTIONAL SCOPE\n\n[ADMIN ACTIONS]\nCreate Student/Teacher/Parent Accounts\nAssign Subjects to Teachers\nGenerate Financial Reports\n\n[TEACHER ACTIONS]\nDaily Attendance Entry\nExam Mark Management\nUpload Learning Resources\n\n[STUDENT/PARENT ACTIONS]\nTrack Academic Progress\nPay Fees Online\nLibrary Catalog Search\nNotifications & Events")
}
uc_conns = [
    ("admin", "use_cases", "manage"),
    ("teacher", "use_cases", "update"),
    ("student", "use_cases", "access")
]
create_diagram_v2("usecase_diag.png", "ACCURATE USE CASE DIAGRAM", uc_elements, uc_conns)

# --- 4. DATA FLOW DIAGRAM (LEVEL 0/1) ---
dfd_elements = {
    "user_ext": (50, 350, 150, 150, "External Entity\n(User: Admin/Staff/\nStudent/Parent)"),
    "auth_proc": (300, 350, 200, 150, "Process 1.0\nAuthentication &\nAuthorization"),
    "core_proc": (600, 350, 250, 150, "Process 2.0\nSchool Management\nEngine (CRUD)"),
    "data_store": (950, 350, 200, 150, "Data Store\nSIMS PostgreSQL\nDatabase")
}
dfd_conns = [
    ("user_ext", "auth_proc", "Credentials"),
    ("auth_proc", "core_proc", "Valid Session"),
    ("core_proc", "data_store", "Read/Write"),
    ("core_proc", "user_ext", "Response Data")
]
create_diagram_v2("dfd_diag.png", "DATA FLOW DIAGRAM (LEVEL 1)", dfd_elements, dfd_conns)

# --- 5. CLASS DIAGRAM ---
class_elements = {
    "base_model": (450, 50, 200, 80, "Base (SQLAlchemy)\nMetadata\nRegistry"),
    "user_class": (450, 200, 200, 100, "User (Implicit)\nemail\nhashed_password\nfull_name"),
    "student_class": (150, 400, 200, 120, "Student\nroll_number\ndate_of_birth\naddress"),
    "teacher_class": (750, 400, 200, 120, "Teacher\nqualification\nspecialization"),
    "classroom_class": (450, 400, 200, 100, "ClassRoom\nname\nteacher_id"),
    "mark_class": (450, 650, 200, 100, "Mark\nsubject\nscore\nexam_id")
}
class_conns = [
    ("base_model", "user_class", "inherits"),
    ("user_class", "student_class", "specializes"),
    ("user_class", "teacher_class", "specializes"),
    ("student_class", "classroom_class", "belongs_to"),
    ("teacher_class", "classroom_class", "manages"),
    ("student_class", "mark_class", "has")
]
create_diagram_v2("class_diag.png", "CLASS RELATIONSHIP DIAGRAM", class_elements, class_conns)
