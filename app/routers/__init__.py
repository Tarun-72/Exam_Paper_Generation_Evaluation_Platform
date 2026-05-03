from .exam import router as exam_router
from .student import router as student_router
from .teacher import router as teacher_router

__all__ = ["exam_router", "student_router", "teacher_router"]