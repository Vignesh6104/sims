# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.admin import Admin
from app.models.class_room import ClassRoom
from app.models.attendance import Attendance
from app.models.marks import Mark
from app.models.subject import Subject
from app.models.exam import Exam
from app.models.fee import FeeStructure, FeePayment
from app.models.timetable import Timetable
from app.models.assignment import Assignment, Submission
from app.models.notification import Notification
from app.models.event import Event
from app.models.library import Book, BorrowRecord
from app.models.parent import Parent