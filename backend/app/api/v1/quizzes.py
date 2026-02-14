from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.quiz import QuizInDB, QuizCreate, QuizResultCreate, QuizResultInDB
from app.crud import crud_quiz

router = APIRouter()

@router.post("/", response_model=QuizInDB)
def create_quiz(
    quiz_in: QuizCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff), # Admins/Teachers
) -> Any:
    return crud_quiz.create_quiz(db=db, quiz=quiz_in, teacher_id=str(current_user.id))

@router.get("/", response_model=List[QuizInDB])
def read_quizzes(
    db: Session = Depends(deps.get_db),
    class_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_quiz.get_quizzes(db, class_id=class_id, skip=skip, limit=limit)

@router.post("/submit", response_model=QuizResultInDB)
def submit_quiz(
    result_in: QuizResultCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    # Only students can submit
    if not hasattr(current_user, "roll_number"):
        raise HTTPException(status_code=400, detail="Only students can submit quiz results")
    
    result = crud_quiz.submit_quiz_result(db, student_id=str(current_user.id), result_in=result_in)
    if not result:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return result
