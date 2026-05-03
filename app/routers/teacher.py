"""Teacher and analytics endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from sqlalchemy.sql import func
from app import models, schemas
from app.database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="", tags=["Teacher"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/teacher/override-score")
def override_score(
    submission_id: int,
    new_score: float,
    feedback: str,
    db: Session = Depends(get_db)
):
    """Override auto-evaluated score with teacher feedback."""
    submission = db.query(models.Submission).filter(models.Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    
    if new_score < 0 or new_score > 5:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 5.")
    
    submission.teacher_override_score = new_score
    submission.teacher_feedback = feedback
    submission.is_auto_evaluated = False
    
    # Update exam session total if applicable
    if submission.exam_session_id:
        exam_session = db.query(models.ExamSession).filter(
            models.ExamSession.id == submission.exam_session_id
        ).first()
        if exam_session:
            total_score = db.query(func.sum(
                func.coalesce(models.Submission.teacher_override_score, models.Submission.score)
            )).filter(
                models.Submission.exam_session_id == submission.exam_session_id
            ).scalar() or 0.0
            exam_session.total_score = total_score
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return {
        "submission_id": submission_id,
        "new_score": new_score,
        "feedback": feedback,
        "status": "updated"
    }


@router.get("/teacher/review/{session_id}")
def get_session_for_review(session_id: int, db: Session = Depends(get_db)):
    """Get all submissions in a session for teacher review."""
    session = db.query(models.ExamSession).filter(models.ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found.")
    
    submissions = db.query(models.Submission).filter(
        models.Submission.exam_session_id == session_id
    ).all()
    
    review_data = []
    for sub in submissions:
        review_data.append({
            "submission_id": sub.id,
            "question_id": sub.question_id,
            "question_text": sub.question.question_text,
            "expected_answer": sub.question.answer,
            "student_answer": sub.student_answer,
            "auto_score": sub.score,
            "semantic_score": sub.semantic_score,
            "ai_explanation": sub.explanation,
            "current_override_score": sub.teacher_override_score,
            "current_feedback": sub.teacher_feedback,
            "marks": sub.question.marks
        })
    
    return {
        "session_id": session_id,
        "session_name": session.session_name,
        "total_submissions": len(submissions),
        "submissions": review_data
    }


@router.get("/analytics/performance")
def get_performance_analytics(db: Session = Depends(get_db)):
    """Get analytics about exam performance."""
    sessions = db.query(models.ExamSession).all()
    submissions = db.query(models.Submission).all()
    
    if not sessions or not submissions:
        return {
            "total_exams": 0,
            "average_score": 0.0,
            "score_distribution": {},
            "difficulty_performance": {},
            "question_type_performance": {}
        }
    
    # Score statistics
    scores = [s.score for s in submissions if s.score is not None]
    total_exams = len(sessions)
    average_score = sum(scores) / len(scores) if scores else 0.0
    
    # Score distribution (0-1, 1-2, 2-3, 3-4, 4-5)
    bins = {
        "0-1": 0, "1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0
    }
    for score in scores:
        if score < 1:
            bins["0-1"] += 1
        elif score < 2:
            bins["1-2"] += 1
        elif score < 3:
            bins["2-3"] += 1
        elif score < 4:
            bins["3-4"] += 1
        else:
            bins["4-5"] += 1
    
    # Performance by difficulty
    difficulty_perf = {}
    for diff in ["easy", "medium", "hard"]:
        diff_scores = [
            s.score for s in submissions 
            if s.question.difficulty.lower() == diff and s.score is not None
        ]
        if diff_scores:
            difficulty_perf[diff] = {
                "average": sum(diff_scores) / len(diff_scores),
                "count": len(diff_scores)
            }
    
    # Performance by question type
    type_perf = {}
    for q_type in ["mcq", "short", "long", "case-based", "code-based"]:
        type_scores = [
            s.score for s in submissions 
            if s.question.question_type.lower() == q_type and s.score is not None
        ]
        if type_scores:
            type_perf[q_type] = {
                "average": sum(type_scores) / len(type_scores),
                "count": len(type_scores)
            }
    
    return {
        "total_exams": total_exams,
        "total_submissions": len(submissions),
        "average_score": average_score,
        "score_distribution": bins,
        "difficulty_performance": difficulty_perf,
        "question_type_performance": type_perf
    }


@router.get("/analytics/plagiarism")
def get_plagiarism_analytics(db: Session = Depends(get_db)):
    """Get plagiarism detection statistics."""
    questions = db.query(models.Question).all()
    checked = [q for q in questions if q.is_plagiarism_checked]
    
    return {
        "total_questions": len(questions),
        "plagiarism_checked": len(checked),
        "pending_check": len(questions) - len(checked)
    }
