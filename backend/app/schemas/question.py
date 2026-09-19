from pydantic import BaseModel


class ExtractedQuestionItem(BaseModel):
    question_number: int | None = None
    question_text: str
    marks: int | None = None
    question_type: str | None = None


class ExtractedQuestionsResult(BaseModel):
    year: int | None = None
    questions: list[ExtractedQuestionItem]


class ExtractedQuestionOut(BaseModel):
    id: int
    subject_id: int
    document_id: int
    year: int | None
    question_number: int | None
    question_text: str
    marks: int | None
    question_type: str | None

    class Config:
        from_attributes = True
        
        
class TopicClassification(BaseModel):
    question_id: int
    matched_unit_name: str | None = None
    matched_topic_name: str | None = None
    confidence: str  # "high" | "medium" | "low" | "no_match"


class TopicClassificationBatch(BaseModel):
    classifications: list[TopicClassification]
    

class ConceptGroup(BaseModel):
    concept_name: str
    description: str | None = None
    question_ids: list[int]


class ConceptMappingResult(BaseModel):
    concepts: list[ConceptGroup]    
    

class TopicPattern(BaseModel):
    topic_name: str
    unit_name: str
    frequency: int
    total_papers: int
    years: list[int]
    marks_distribution: dict[str, int]
    question_types: dict[str, int]
    recurrence_intervals: list[int]
    concept_count: int
    exact_repeat_count: int
    near_repeat_count: int


class PatternAnalysisResult(BaseModel):
    total_papers_analyzed: int
    topics: list[TopicPattern]
    
class QuestionBlueprint(BaseModel):
    topic_id: int
    topic_name: str
    unit_name: str
    historical_frequency: int
    total_papers: int
    historical_years: list[int]
    preferred_marks: list[int]
    question_types: list[str]
    difficulty: str
    recurrence_pattern: str   # "consistent" | "observed" | "occasional" | "rare"
    evidence_strength: float  # 0-100, used later by the ranker
    
    
class GeneratedQuestionItem(BaseModel):
    question_text: str
    marks: int
    difficulty: str
    question_type: str


class GeneratedQuestionsBatch(BaseModel):
    questions: list[GeneratedQuestionItem]


class ValidationResult(BaseModel):
    is_valid: bool
    rejection_reason: str | None = None
    
class AskQuestionRequest(BaseModel):
    question: str


class AskQuestionResponse(BaseModel):
    answer: str
    sources: list[str] = []
    
class AnswerResult(BaseModel):
    answer_text: str