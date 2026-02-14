from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.quiz import Quiz, QuizResult
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResultCreate

def get_quiz(db: Session, quiz_id: str):
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()

def get_quizzes(db: Session, class_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(Quiz)
    if class_id:
        query = query.filter(Quiz.class_id == class_id)
    return query.offset(skip).limit(limit).all()

def create_quiz(db: Session, quiz: QuizCreate, teacher_id: str):
    # Convert QuestionSchema list to JSON-serializable list of dicts
    questions_list = [q.dict() for q in quiz.questions_data]
    
    db_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        class_id=str(quiz.class_id),
        subject_id=str(quiz.subject_id),
        teacher_id=teacher_id,
        questions_data=questions_list,
        time_limit_minutes=quiz.time_limit_minutes,
        is_published=quiz.is_published
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

def submit_quiz_result(db: Session, student_id: str, result_in: QuizResultCreate):
    quiz = db.query(Quiz).filter(Quiz.id == str(result_in.quiz_id)).first()
    if not quiz:
        return None
    
    questions = quiz.questions_data
    score = 0
    total_points = 0
    
    for i, q in enumerate(questions):
        points = q.get('points', 1.0)
        total_points += points
        if i < len(result_in.answers) and result_in.answers[i] == q['correct_answer']:
            score += points
            
    db_result = QuizResult(
        quiz_id=str(result_in.quiz_id),
        student_id=student_id,
        score=score,
        total_points=total_points,
        answers=result_in.answers
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result
