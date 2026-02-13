# SIMS Backend

This directory contains the FastAPI backend for the School Information Management System.

## 🚀 Quick Start

1. **Setup Environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure Variables:**
   Create a `.env` file based on `.env.example`.

3. **Database:**
   ```bash
   alembic upgrade head
   python run_init.py
   ```

4. **Run:**
   ```bash
   python run.py
   ```

## 🛠️ Tech Stack
- FastAPI, SQLAlchemy, Alembic, PostgreSQL.
- Cloudinary (Files), ReportLab (PDFs).

Refer to the root [README.md](../README.md) for detailed instructions.
