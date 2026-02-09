from src.backend.app.common.exceptions import AppException

class AssessmentNotFound(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Assessment not found",
            detail_ar="التقييم غير موجود"
        )

class DomainNotFound(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Assessment domain not found",
            detail_ar="مجال التقييم غير موجود"
        )

class ElementResponseNotFound(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Element response not found",
            detail_ar="استجابة العنصر غير موجودة"
        )

class InvalidAssessmentStatus(AppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Invalid assessment status transition",
            detail_ar="تحول حالة التقييم غير صالح"
        )
