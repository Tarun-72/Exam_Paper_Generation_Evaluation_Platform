from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(128), index=True)
    difficulty = Column(String(32), index=True)  # easy, medium, hard
    question_type = Column(String(32), index=True)  # mcq, short, long, case-based, code-based
    question_text = Column(Text, nullable=False, unique=True)
    answer = Column(Text, nullable=False)
    marks = Column(Float, default=5.0)  # Question weightage
    embedding = Column(JSON, nullable=True)  # Sentence transformer embedding for plagiarism detection
    is_plagiarism_checked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submissions = relationship("Submission", back_populates="question")

class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(128), nullable=False)
    subject = Column(String(128), nullable=True)
    questions_data = Column(JSON, nullable=False)
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    submitted = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)

    submissions = relationship("Submission", back_populates="exam_session")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    exam_session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=True)
    student_answer = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    semantic_score = Column(Float, nullable=True)  # Sentence transformer based score
    is_auto_evaluated = Column(Boolean, default=True)
    teacher_override_score = Column(Float, nullable=True)
    teacher_feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("Question", back_populates="submissions")
    exam_session = relationship("ExamSession", back_populates="submissions")
