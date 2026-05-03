from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app import models, schemas
from app.database import SessionLocal, engine
from app.services.generator import generate_question
from datetime import datetime
import json
import random

router = APIRouter(prefix="", tags=["Exam"])

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/generate-question", response_model=schemas.QuestionOut)
def create_question(request: schemas.QuestionCreate, db: Session = Depends(get_db)):
    if request.difficulty.lower() not in {"easy", "medium", "hard"}:
        raise HTTPException(status_code=400, detail="Difficulty must be easy, medium, or hard.")
    if request.question_type.lower() not in {"mcq", "short", "long", "case-based", "code-based"}:
        raise HTTPException(status_code=400, detail="Question type must be one of: mcq, short, long, case-based, code-based.")
    return generate_question(db, request.topic, request.difficulty.lower(), request.question_type.lower())

@router.post("/create-exam", response_model=schemas.ExamOut)
def create_exam(request: schemas.ExamCreate, db: Session = Depends(get_db)):
    split = request.difficulty_split
    if not all(level in split for level in ["easy", "medium", "hard"]):
        raise HTTPException(status_code=400, detail="difficulty_split must include easy, medium, and hard ratios.")

    total = request.total_questions
    counts = {
        level: max(1, int(total * float(split[level])))
        for level in ["easy", "medium", "hard"]
    }
    while sum(counts.values()) > total:
        for level in ["hard", "medium", "easy"]:
            if sum(counts.values()) > total and counts[level] > 1:
                counts[level] -= 1
    while sum(counts.values()) < total:
        counts["medium"] += 1

    questions = []
    for difficulty, count in counts.items():
        query = db.query(models.Question).filter(models.Question.difficulty == difficulty).order_by(func.random()).limit(count).all()
        if len(query) < count:
            raise HTTPException(
                status_code=400,
                detail=(f"Insufficient questions for difficulty '{difficulty}'. "
                        f"Requested {count}, available {len(query)}."),
            )
        questions.extend(query)

    return schemas.ExamOut(questions=questions)

@router.get("/questions", response_model=list[schemas.QuestionOut])
def list_questions(db: Session = Depends(get_db)):
    return db.query(models.Question).order_by(models.Question.id.desc()).all()

@router.post("/start-exam-session")
def start_exam_session(request: schemas.ExamCreate, db: Session = Depends(get_db)):
    split = request.difficulty_split
    if not all(level in split for level in ["easy", "medium", "hard"]):
        raise HTTPException(status_code=400, detail="difficulty_split must include easy, medium, and hard ratios.")

    total = request.total_questions
    counts = {
        level: max(1, int(total * float(split[level])))
        for level in ["easy", "medium", "hard"]
    }
    while sum(counts.values()) > total:
        for level in ["hard", "medium", "easy"]:
            if sum(counts.values()) > total and counts[level] > 1:
                counts[level] -= 1
    while sum(counts.values()) < total:
        counts["medium"] += 1

    questions = []
    for difficulty, count in counts.items():
        query = db.query(models.Question).filter(models.Question.difficulty == difficulty).order_by(func.random()).limit(count).all()
        if len(query) < count:
            raise HTTPException(
                status_code=400,
                detail=(f"Insufficient questions for difficulty '{difficulty}'. "
                        f"Requested {count}, available {len(query)}."),
            )
        questions.extend(query)

    session_data = {
        "questions": [
            {
                "id": q.id,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "answer": q.answer,
                "marks": q.marks,
            }
            for q in questions
        ]
    }
    
    exam_session = models.ExamSession(
        session_name=f"Exam Session {len(db.query(models.ExamSession).all()) + 1}",
        subject=request.subject or "General",
        questions_data=session_data,
        max_score=sum(q.marks for q in questions),
        started_at=datetime.utcnow(),
    )
    db.add(exam_session)
    db.commit()
    db.refresh(exam_session)
    
    return {
        "session_id": exam_session.id,
        "questions": [
            schemas.QuestionOut(
                id=q.id,
                topic=q.topic,
                difficulty=q.difficulty,
                question_type=q.question_type,
                question_text=q.question_text,
                answer=q.answer,
                marks=q.marks,
                is_plagiarism_checked=q.is_plagiarism_checked,
            )
            for q in questions
        ],
    }
