from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.sql import func
from app import models, schemas
from app.database import SessionLocal
from app.services.evaluator import evaluate_answer
import json
from datetime import datetime

router = APIRouter(prefix="", tags=["Student"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/submit-exam", response_model=schemas.SubmissionOut)
def submit_exam(request: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    score, explanation, semantic_score = evaluate_answer(question, request.student_answer)
    submission = models.Submission(
        question_id=request.question_id,
        student_answer=request.student_answer,
        score=score,
        explanation=explanation,
        semantic_score=semantic_score,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission

@router.post("/submit-exam-batch", response_model=List[schemas.SubmissionOut])
def submit_exam_batch(request: schemas.SubmissionBatchCreate, db: Session = Depends(get_db)):
    submissions = []
    session_id = request.session_id
    exam_session = None
    
    if session_id:
        exam_session = db.query(models.ExamSession).filter(models.ExamSession.id == session_id).first()
        if not exam_session:
            raise HTTPException(status_code=404, detail=f"Exam session {session_id} not found.")
    
    total_score = 0.0
    for item in request.submissions:
        question = db.query(models.Question).filter(models.Question.id == item.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {item.question_id} not found.")

        score, explanation, semantic_score = evaluate_answer(question, item.student_answer)
        total_score += score
        submission = models.Submission(
            question_id=item.question_id,
            student_answer=item.student_answer,
            score=score,
            semantic_score=semantic_score,
            explanation=explanation,
            exam_session_id=session_id,
        )
        db.add(submission)
        submissions.append(submission)

    if exam_session:
        exam_session.total_score = total_score
        exam_session.submitted = 1
        exam_session.completed_at = datetime.utcnow()
        if exam_session.started_at:
            exam_session.time_taken_seconds = int((exam_session.completed_at - exam_session.started_at).total_seconds())
        db.add(exam_session)
    
    db.commit()
    for submission in submissions:
        db.refresh(submission)
    return submissions

@router.get("/results", response_model=list[schemas.ResultOut])
def get_results(db: Session = Depends(get_db)):
    submissions = db.query(models.Submission).all()
    return [
        schemas.ResultOut(
            question_id=sub.question_id,
            question_text=sub.question.question_text,
            correct_answer=sub.question.answer,
            student_answer=sub.student_answer,
            score=sub.teacher_override_score if sub.teacher_override_score is not None else sub.score,
            semantic_score=sub.semantic_score,
            explanation=sub.explanation,
            teacher_feedback=sub.teacher_feedback,
        )
        for sub in submissions
    ]

@router.get("/exam-summary/{session_id}", response_model=schemas.ExamSummaryOut)
def get_exam_summary(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ExamSession).filter(models.ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found.")
    
    submissions = db.query(models.Submission).filter(models.Submission.exam_session_id == session_id).all()
    results = [
        schemas.ResultOut(
            question_id=sub.question_id,
            question_text=sub.question.question_text,
            correct_answer=sub.question.answer,
            student_answer=sub.student_answer,
            score=sub.teacher_override_score if sub.teacher_override_score is not None else sub.score,
            semantic_score=sub.semantic_score,
            explanation=sub.explanation,
            teacher_feedback=sub.teacher_feedback,
        )
        for sub in submissions
    ]
    
    total_score = sum([r.score for r in results])
    max_score = session.max_score
    percentage = (total_score / max_score * 100) if max_score > 0 else 0.0
    
    return schemas.ExamSummaryOut(
        session_id=session_id,
        total_score=total_score,
        max_score=max_score,
        percentage=percentage,
        time_taken_seconds=session.time_taken_seconds,
        results=results,
    )
