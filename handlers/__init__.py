from .start import router as start_router
from .student_handlers import router as student_router
from .teacher_handlers import router as teacher_router
from .unknown import router as unknown_router

__all__ = ['start_router', 'student_router', 'teacher_router', 'unknown_router']

