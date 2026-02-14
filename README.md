# School Information Management System (SIMS)

A comprehensive, full-stack application designed to streamline school operations, academic tracking, and communication between administrators, teachers, parents, and students.

## 🚀 Key Features

- **Profile Management (NEW):**
    - **Unified Profile Portal**: Personalized settings for all user roles.
    - **Image Cropping**: Interactive UI for perfectly framing profile pictures.
    - **Real-time Sync**: Global state updates immediately after profile changes.
- **Multi-Role Dashboards:** specialized interfaces for Admins, Teachers, Parents, and Students (Optimized for speed).
- **Academic Management:** Timetable, Subject, Class, Exam, and Attendance tracking.
- **Assignment System:** Cloud-based file submissions (via Cloudinary) with direct download capabilities.
- **Grading & Reporting:** 
    - Consistently tracked Exam marks and Assignment grades.
    - Automated PDF report generation for student performance.
- **Financial Management:** Fee tracking, payment status, and history for students and parents.
- **Library System:** Catalog management, book issuing, and availability tracking.
- **Communication & Events:** 
    - Global notification and announcement system.
    - Integrated school calendar for events and holidays.
- **Data Visualization:** Interactive dashboards with charts for attendance, marks, and financial trends.
- **Security:** 
    - JWT authentication with **Refresh Token** mechanism for seamless UX.
    - Secure password recovery flow with time-limited tokens.
    - Role-based access control (RBAC) across all endpoints.

---

## 🛠️ Tech Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework.
- **Database:** [PostgreSQL](https://www.postgresql.org/) (Production) / [SQLite](https://www.sqlite.org/) (Development).
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) - SQL Toolkit and Object-Relational Mapper.
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/) - Lightweight database migration tool.
- **Authentication:** [Jose JWT](https://python-jose.readthedocs.io/) & [Passlib (Bcrypt)](https://passlib.readthedocs.io/).
- **File Storage:** [Cloudinary](https://cloudinary.com/) - Cloud-based image and video management.
- **PDF Generation:** [ReportLab](https://www.reportlab.com/) - Engine for creating complex PDF documents.
- **Validation:** [Pydantic v2](https://docs.pydantic.dev/) - Data validation and settings management.

### Frontend
- **Framework:** [React 18](https://reactjs.org/) with [Vite](https://vitejs.dev/) for fast builds.
- **UI Library:** [Material UI (MUI) 5](https://mui.com/) - React components for faster web development.
- **Data Grids:** [@mui/x-data-grid](https://mui.com/x/react-data-grid/) for complex data handling.
- **Visualizations:** [Recharts](https://recharts.org/) - Composable charting library.
- **Calendar:** [React Big Calendar](https://jquense.github.io/react-big-calendar/) - Flexbox-based calendar component.
- **Routing:** [React Router 6](https://reactrouter.com/) - Declarative routing for React.
- **State Management:** React Context API (Auth) & Hooks.
- **API Client:** [Axios](https://axios-http.com/) - Promise-based HTTP client.
- **Form Handling:** [React Hook Form](https://react-hook-form.com/).

---

## 📂 Detailed Project Structure

### Backend (`/backend`)
- `app/`
    - `api/v1/`: API endpoints categorized by module:
        - `auth.py`, `admins.py`, `students.py`, `teachers.py`, `parents.py`: User management.
        - `attendance.py`, `marks.py`, `exams.py`, `assignments.py`: Academic records.
        - `class_rooms.py`, `subjects.py`, `timetable.py`: School structure.
        - `fees.py`, `library.py`, `notifications.py`, `events.py`: School services.
        - `dashboard.py`: Aggregated data for role-specific homepages.
    - `core/`: Core configuration, security utilities, and global dependencies.
    - `crud/`: CRUD logic for each database model.
    - `db/`: Database session management, base models, and initialization scripts.
    - `models/`: SQLAlchemy ORM models.
    - `schemas/`: Pydantic schemas for data validation and serialization.
    - `services/`: Complex business logic (e.g., marks processing, attendance calculation).
    - `utils/`: Utility helpers like `pdf_generator.py` and role checkers.
- `alembic/`: Database migration environment and version scripts.
- `run_init.py`: Script to initialize the database with default data/superuser.
- `reset_db.py`: Utility to wipe and recreate the database.

### Frontend (`/frontend`)
- `src/`
    - `api/`: Axios instances and API service definitions.
    - `components/`: Reusable UI components (Navbar, Sidebar, Layout, ProtectedRoute).
    - `context/`: AuthContext for global user state management.
    - `pages/`: 
        - `admin/`: Management of Users, Fees, Library, and School structure.
        - `teacher/`: Grading, Attendance, and Timetable views.
        - `student/`: Submissions, Attendance, Marks, and Library.
        - `ParentDashboard.jsx`: Monitoring student progress and fees.
    - `utils/`: Frontend helper functions and role utilities.
    - `routes.jsx`: Main routing configuration.

---

## 🏗️ Project Architecture

This section provides a high-level overview of the system design, intended to assist in creating UML diagrams and understanding the data flow.

### 1. System Components (Component Diagram)
- **Frontend (Client):** Optimized React-based SPA with **30s API timeouts** to handle cloud database cold starts and intelligent state locking for profile refreshes.
- **Backend (Server):** High-performance **FastAPI** service featuring:
    - **Aggregated Query Logic**: Reduces database round-trips by over 90% for dashboard statistics.
    - **Advanced Token Security**: Unique JWT `jti` identifiers and automated session renewal.
    - **Alembic Versioning**: Structured database schema evolution.
- **External Services:**
    - **Cloudinary:** Primary storage for submitted assignment files and documents.
    - **PostgreSQL:** Persistent storage for all relational data.

### 2. Core Data Models (Class Diagram)
The system is built around several key entity clusters:
- **User Management:** An inheritance-like structure where `Admin`, `Teacher`, `Student`, and `Parent` roles share authentication logic but have distinct profiles.
- **Academic Structure:** 
    - `ClassRoom` links `Students`, `Subjects`, and `Timetable` entries.
    - `Subject` connects a specific course of study to a `Teacher`.
- **Student Records:**
    - `Attendance`: Tracks daily presence per student/subject.
    - `Marks` & `Exams`: Records academic performance.
    - `Assignments`: Tracks cloud-stored files and teacher feedback.
- **Support Systems:** `Library` (books/issuance), `Fees` (financial tracking), and `Notifications`.

### 3. Key Logical Flows (Sequence Diagrams)
- **Authentication:** Login -> JWT Generation -> Storage in Browser Context -> Interceptor-based API calls.
- **Assignment Submission:** Frontend Upload -> FastAPI Service -> Cloudinary Storage -> Database Record Update.
- **Report Generation:** User Request -> Service Layer -> Data Aggregation -> ReportLab PDF Generation -> File Stream Return.

---

## 🛠️ Detailed Setup Instructions

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ & npm
- PostgreSQL (or SQLite for local development)
- Cloudinary Account (for file uploads)

### 2. Backend Setup
1. **Navigate to the directory:**
   ```bash
   cd backend
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in:
   - `SQLALCHEMY_DATABASE_URI`
   - `SECRET_KEY`
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
5. **Database Migrations (Alembic):**
   ```bash
   alembic upgrade head
   ```
6. **Initialize Data:**
   Run the initialization script to create the default admin user:
   ```bash
   python run_init.py
   ```
   **Default Credentials:**
   - **Email:** `admin@school.com`
   - **Password:** `admin`

7. **Run the Server:**
   ```bash
   python run.py
   ```

### 3. Frontend Setup
1. **Navigate to the directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Environment Variables:**
   Create a `.env` file with `VITE_API_URL=http://localhost:8000/api/v1`.
4. **Run the Development Server:**
   ```bash
   npm run dev
   ```

---

## 🗄️ Database Management

- **Apply Migrations:** `alembic upgrade head`
- **Revert Last Migration:** `alembic downgrade -1`
- **Reset Database:** `python reset_db.py` (Deletes all data, use with caution)

---
*Built to provide a modern, efficient experience for school administration.*