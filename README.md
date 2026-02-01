# School Information Management System (SIMS)

A comprehensive, full-stack application designed to streamline school operations, academic tracking, and communication between administrators, teachers, and students.

## 🚀 Key Features

- **Multi-Role Dashboards:** Specialized interfaces for Admins, Teachers, and Students.
- **Academic Management:** Timetable, Subject, Class, and Exam tracking.
- **Assignment System:** File-based submissions with re-submission capabilities.
- **Grading & Reporting:** Consistently tracked Exam marks and Assignment grades.
- **Communication:** Global notification and announcement system.
- **Security:** 
    - JWT authentication with **Refresh Token** mechanism for seamless UX.
    - Secure password recovery flow with time-limited tokens.

---

## 🛠️ Tech Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework.
- **Database:** [PostgreSQL](https://www.postgresql.org/) (Production) / [SQLite](https://www.sqlite.org/) (Development).
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) - SQL Toolkit and Object-Relational Mapper.
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/) - Lightweight database migration tool.
- **Authentication:** [Jose JWT](https://python-jose.readthedocs.io/) & [Passlib (Bcrypt)](https://passlib.readthedocs.io/).
- **Validation:** [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management.

### Frontend
- **Framework:** [React 18](https://reactjs.org/) with [Vite](https://vitejs.dev/) for fast builds.
- **UI Library:** [Material UI (MUI) 5](https://mui.com/) - React components for faster web development.
- **Routing:** [React Router 6](https://reactrouter.com/) - Declarative routing for React.
- **State Management:** React Context API (Auth) & Hooks.
- **API Client:** [Axios](https://axios-http.com/) - Promise-based HTTP client.
- **Form Handling:** [React Hook Form](https://react-hook-form.com/).
- **Notifications:** [Notistack](https://notistack.com/) - Stackable snackbars for React.
- **Animation:** [Framer Motion](https://www.framer.com/motion/).

---

## 📂 Detailed Project Structure

### Backend (`/backend`)
- `app/`
    - `api/v1/`: API endpoints categorized by module (auth, assignments, marks, etc.).
    - `core/`: Core configuration, security utilities, and global dependencies.
    - `crud/`: Create, Read, Update, Delete logic for database models.
    - `db/`: Database session management, base models, and initialization scripts.
    - `models/`: SQLAlchemy ORM models (Admin, Teacher, Student, Assignment, etc.).
    - `schemas/`: Pydantic schemas for data validation and serialization.
    - `services/`: Business logic services (attendance, marks processing).
    - `utils/`: Utility helpers like role checkers and response formatters.
- `alembic/`: Database migration environment and version scripts.
- `uploads/`: Local storage for submitted assignment files.
- `main.py`: FastAPI application setup and middleware configuration.
- `run.py`: Script to start the FastAPI development server.
- `run_init.py`: Script to initialize the database with default data/superuser.
- `reset_db.py`: Utility to wipe and recreate the database.

### Frontend (`/frontend`)
- `src/`
    - `api/`: Axios instances and API service definitions.
    - `components/`: Reusable UI components (Navbar, Sidebar, Layout, ProtectedRoute).
    - `context/`: AuthContext for global user state management.
    - `hooks/`: Custom React hooks (e.g., `useAuth`).
    - `pages/`: 
        - `admin/`: Admin-only features (User mgmt, Fees, Timetable).
        - `teacher/`: Teacher-only features (Grading, Attendance).
        - `student/`: Student-only features (Submissions, Marks).
    - `utils/`: Frontend helper functions and role utilities.
    - `App.jsx`: Main routing configuration.
    - `main.jsx`: React entry point.

---

## 🛠️ Detailed Setup Instructions

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ & npm
- PostgreSQL (or SQLite for local development as configured in `.env`)

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
   Configure the `.env` file in the `backend/` directory with your database credentials and secret keys.
5. **Database Migrations (Alembic):**
   ```bash
   # Apply migrations to the latest version
   alembic upgrade head
   
   # To create a new migration after model changes:
   # alembic revision --autogenerate -m "description of changes"
   ```
6. **Initialize Data:**
   Run the initialization script to create the default admin user and essential data:
   ```bash
   python run_init.py
   ```
7. **Run the Server:**
   ```bash
   python run.py
   ```
   The API will be available at `http://localhost:8000`.

### 3. Frontend Setup
1. **Navigate to the directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Run the Development Server:**
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

---

## 🗄️ Database Management

### Running Migrations
We use Alembic for version control of the database schema.
- **Upgrade:** `alembic upgrade head`
- **Downgrade:** `alembic downgrade -1`
- **History:** `alembic history`

### Troubleshooting
- If you encounter database conflicts during development, you can use `python reset_db.py` to wipe the database and start fresh (Warning: this deletes all data).
- Ensure the `PYTHONPATH` is set to the current directory if running scripts manually:
  `$env:PYTHONPATH="."` (Windows PowerShell)

---
*Built to provide a modern, efficient experience for school administration.*