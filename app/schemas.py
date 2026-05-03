from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionCreate(BaseModel):
    topic: str
    difficulty: str
    question_type: str

class QuestionOut(BaseModel):
    id: int
    topic: str
    difficulty: str
    question_type: str
    question_text: str
    answer: str
    marks: float
    is_plagiarism_checked: bool

    class Config:
        from_attributes = True

class ExamCreate(BaseModel):
    total_questions: int = Field(..., gt=0)
    difficulty_split: dict
    subject: Optional[str] = None

class ExamOut(BaseModel):
    questions: List[QuestionOut]

class SubmissionCreate(BaseModel):
    question_id: int
    student_answer: str

class SubmissionBatchCreate(BaseModel):
    submissions: List[SubmissionCreate]
    session_id: Optional[int] = None

class SubmissionOut(BaseModel):
    id: int
    question_id: int
    student_answer: str
    score: float
    semantic_score: Optional[float]
    explanation: str
    is_auto_evaluated: bool
    teacher_override_score: Optional[float]
    teacher_feedback: Optional[str]

    class Config:
        from_attributes = True

class ResultOut(BaseModel):
    question_id: int
    question_text: str
    correct_answer: str
    student_answer: str
    score: float
    semantic_score: Optional[float]
    explanation: str
    teacher_feedback: Optional[str]

class ExamSummaryOut(BaseModel):
    session_id: int
    total_score: float
    max_score: float
    percentage: float
    time_taken_seconds: Optional[int]
    results: List[ResultOut]

class TeacherReviewOut(BaseModel):
    submission_id: int
    question_id: int
    question_text: str
    student_answer: str
    auto_score: float
    new_score: Optional[float]
    feedback: Optional[str]

class AnalyticsOut(BaseModel):
    total_exams: int
    average_score: float
    score_distribution: dict
    difficulty_performance: dict
    question_type_performance: dict
