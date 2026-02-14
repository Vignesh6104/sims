# Project Knowledge Transfer: School Information Management System (SIMS)

## 1. Project Overview
This is a comprehensive School Information Management System designed to handle various administrative and academic tasks. It features a modern, responsive web interface and a robust backend API. The system supports multiple user roles including Administrators, Teachers, Students, and Parents, each with tailored dashboards and functionalities.

## 2. Technology Stack

### Frontend
- **Framework:** React 18 (bootstrapped with Vite) for a fast and efficient development experience.
- **Styling:**
    - **Tailwind CSS (v4):** Utility-first CSS framework for rapid UI development.
    - **Radix UI:** Headless UI primitives for accessible and high-quality components (Dialog, Dropdown, Tabs, etc.).
    - **clsx / tailwind-merge:** Utilities for conditionally constructing `className` strings and resolving Tailwind conflicts.
    - **Lucide React:** Icon set.
- **State Management & Data Fetching:**
    - **React Context:** Used for global state like Authentication (`AuthContext`).
    - **Axios:** HTTP client with interceptors for handling JWT token injection and automatic token refreshing.
- **Routing:** `react-router-dom` (v6) for client-side routing, featuring nested routes and protected route wrappers.
- **Forms:** `react-hook-form` for efficient form validation and state management.
- **Visualization:** `recharts` for charts and graphs (e.g., student performance analytics).
- **Calendar:** `react-big-calendar` for scheduling and timetable views.
- **Utilities:** `date-fns` for date manipulation.

### Backend
- **Framework:** FastAPI (Python) for building high-performance APIs.
- **Database ORM:** SQLAlchemy for interacting with the relational database (PostgreSQL).
- **Migrations:** Alembic for handling database schema changes and version control.
- **Data Validation:** Pydantic for request/response schema validation and settings management (`pydantic-settings`).
- **Authentication:**
    - **JWT (JSON Web Tokens):** Implemented using `python-jose`.
    - **Hashing:** `passlib` with `bcrypt` for secure password storage.
- **File Handling:**
    - **Cloudinary:** For cloud-based image/file storage.
    - **ReportLab:** For generating PDF documents (likely for reports/transcripts).
    - **CSV Processing:** Built-in Python `csv` module for bulk data uploads.
- **Testing:** `pytest` for unit and integration testing.

## 3. Architecture & Project Structure

### Backend Structure (`backend/`)
The backend follows a modular, layered architecture:
- **`app/api/v1/`**: Contains API route handlers organized by module (e.g., `students.py`, `auth.py`). This separation ensures scalability.
- **`app/core/`**: Core configurations, security utilities (hashing, JWT creation), and global dependencies.
- **`app/crud/`**: The Create, Read, Update, Delete (CRUD) layer. It abstracts database interactions from the business logic in the API layer.
- **`app/db/`**: Database connection (`session.py`) and base model definitions.
- **`app/models/`**: SQLAlchemy database models representing the tables (e.g., `Student`, `Teacher`, `ClassRoom`).
- **`app/schemas/`**: Pydantic models (DTOs) for data validation, separating internal DB models from external API contracts.
- **`app/services/`**: (Optional) Business logic layer for complex operations (e.g., `auth_service.py`).

### Frontend Structure (`frontend/`)
The frontend is organized by feature and function:
- **`src/api/axios.js`**: Centralized Axios instance. It includes **Interceptors** that:
    1.  Automatically attach the `Authorization: Bearer <token>` header to requests.
    2.  Intercept `401 Unauthorized` responses to attempt a token refresh using the `refresh_token`. If successful, it retries the original request; otherwise, it logs the user out.
- **`src/context/AuthContext.jsx`**: Manages user session state (`user`, `role`, `token`). It handles login, logout, and initial profile fetching.
- **`src/components/`**: Reusable UI components. `ProtectedRoute.jsx` checks user roles and redirects unauthorized access.
- **`src/pages/`**: Application views, often organized by user role (e.g., `admin/`, `teacher/`, `student/`).
- **`src/routes.jsx`**: (Likely deprecated/unused in favor of direct routing in `App.jsx`).
- **`src/App.jsx`**: The main entry point defining the routing structure and layout wrappers.

## 4. Key Features & Modules

### Authentication & Security
- **JWT Auth:** Stateless authentication using Access (short-lived) and Refresh (long-lived) tokens.
- **Role-Based Access Control (RBAC):** Middleware and frontend wrappers ensure users only access features permitted for their role (Admin, Teacher, Student, Parent).

### Core Modules
1.  **User Management:**
    - **Admins:** Full system control.
    - **Teachers:** Manage classes, attendance, marks, and assignments.
    - **Students:** View profiles, marks, attendance, and timetables.
    - **Parents:** Monitor their child's progress.
2.  **Academic Management:**
    - **Classes & Sections:** Management of class structures (`ClassRoom` model).
    - **Subjects:** Curriculum management.
    - **Timetable:** Scheduling of classes and exams.
    - **Assignments:** Teachers can post assignments; Students can view them.
    - **Exams:** Scheduling and management of examinations.
    - **Marks/Results:** Recording and viewing of student grades.
3.  **Administrative:**
    - **Attendance:** Tracking for both students and (potentially) staff.
    - **Fees:** Fee structure definition and payment tracking.
    - **Library:** Book cataloging and borrowing records.
    - **Events:** School calendar events.
    - **Notifications:** System-wide or targeted alerts.
    - **HR & Payroll:** Salary structures and monthly payment records for staff.
    - **Asset Management:** Tracking school equipment and inventory.
4.  **Academic Enhancements:**
    - **Online Quizzes:** Assessment tool with automated scoring and results tracking.
5.  **Communication:**
    - **Leave Management:** Application and approval workflow for students/teachers.
    - **Feedback System:** Grievance and feedback submission for all users.

### Data Handling
- **Bulk Uploads:** The system supports uploading CSV files for bulk creation of records (e.g., `students/upload` endpoint), handling validation and duplicate checks efficiently.

## 5. API Call Workflow (Step-by-Step)

This section describes the lifecycle of an API request from the frontend to the backend and back.

### Phase 1: Request Initiation (Frontend)
1.  **Trigger:** A user action (e.g., clicking "Save") or a component mounting (`useEffect`) calls an Axios function.
2.  **Request Interceptor (`frontend/src/api/axios.js`):** 
    - Before the request leaves, an interceptor checks `localStorage` for an `access_token`.
    - If found, it injects the header: `Authorization: Bearer <token>`.
3.  **Transmission:** The request is sent to the backend URL (e.g., `POST /api/v1/students/`).

### Phase 2: Authorization & Processing (Backend)
1.  **Routing:** FastAPI identifies the target endpoint based on the method and path.
2.  **Authentication Dependency (`backend/app/api/deps.py`):**
    - The `reusable_oauth2` dependency extracts the Bearer token.
    - `get_current_user` decodes the JWT using the system's `SECRET_KEY`.
    - It validates the token's expiration (`exp`) and integrity.
    - It uses the `sub` (User ID) and `role` claims in the token to fetch the user object from the database.
3.  **Permission Check:** 
    - Endpoints use specific dependencies like `get_current_active_superuser` or `get_current_active_staff` to enforce RBAC.
4.  **Execution:**
    - The API router calls the relevant CRUD function, which uses SQLAlchemy to interact with the database.
5.  **Response Construction:**
    - FastAPI uses Pydantic Schemas to filter and serialize data into a JSON response.

### Phase 3: Response Handling (Frontend)
1.  **Success:** Data is returned to the calling component.
2.  **Failure - Token Expiry:**
    - If a `401 Unauthorized` is received, the interceptor attempts a silent refresh using the `refresh_token`.
    - On success, it retries the original request; otherwise, it redirects to `/login`.
3.  **UI Feedback:** Errors are displayed via Toast notifications.

## 6. Project Development Workflow

This section outlines the standard process for developing and deploying new features or fixes.

### Feature Implementation Cycle
1.  **Backend - Model Definition:**
    - Define the new data structure in `backend/app/models/`.
    - Register the model in `backend/app/db/base.py` to ensure Alembic detects it.
2.  **Backend - Database Migration:**
    - Generate a migration script: `alembic revision --autogenerate -m "description of change"`.
    - Apply the migration: `alembic upgrade head`.
3.  **Backend - Schema & CRUD:**
    - Create Pydantic schemas in `backend/app/schemas/` for request validation and response serialization.
    - Implement the database logic in `backend/app/crud/`.
4.  **Backend - API Router:**
    - Create or update the router in `backend/app/api/v1/`.
    - Include the router in `backend/app/main.py`.
5.  **Frontend - API Integration:**
    - Use the centralized Axios instance in `frontend/src/api/axios.js` to create services for the new endpoints.
6.  **Frontend - UI Development:**
    - Build the user interface in `frontend/src/pages/`, utilizing Radix UI primitives and Tailwind CSS.
    - Update routing in `frontend/src/App.jsx` and add the new page to the `Sidebar` or `Navbar` if necessary.

### Testing & Quality Assurance
- **Backend Testing:** Run `pytest` from the `backend/` directory to execute unit and functional tests.
- **Frontend Linting:** Run `npm run lint` in the `frontend/` directory to ensure code style consistency.

### Deployment & CI/CD
- **Frontend Deployment:** Managed by **Vercel**. The `frontend/vercel.json` ensures that all routes are redirected to `index.html` for client-side routing (SPA support).
- **Backend Deployment:** Designed to be hosted on platforms supporting Python/FastAPI (e.g., Render, Railway, or traditional VPS).
- **Database:** Uses PostgreSQL in production. Schema synchronization is strictly managed via Alembic migrations.
- **Media/File Storage:** All persistent files (profile images, assignments) are offloaded to **Cloudinary** to keep the application stateless and scalable.

### Data Management Utilities
- **`run_init.py`:** Use this script to bootstrap the database with essential data and the initial admin account.
- **`reset_db.py`:** A destructive utility used during development to quickly wipe and recreate the database schema.

## 7. Testing & Verification

The project includes a comprehensive suite of functional tests located in `backend/app/tests/`.

### Key Test Suites:
- **`test_functional.py`:** Covers core CRUD operations for Teachers, Students, Classrooms, and Notifications.
- **`test_new_features.py`:** Verifies the recently added modules:
    - **Leave Management:** End-to-end flow from application to admin approval.
    - **Feedback System:** Submission and resolution tracking.
    - **Online Quizzes:** Teacher creation, student submission, and automated scoring validation.
    - **Administrative:** Access verification for Salaries and Asset management.

### Running Tests:
To execute the tests, navigate to the `backend/` directory and run:
```bash
$env:PYTHONPATH = "."; ..\venv\Scripts\python.exe -m pytest
```
All core and new features have been verified to work correctly as of the latest implementation.
