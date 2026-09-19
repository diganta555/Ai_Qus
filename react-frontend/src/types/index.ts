export interface User {
  id: number;
  email: string;
  name: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Subject {
  id: number;
  name: string;
  subject_code: string | null;
  description: string | null;
  category: string | null;
  created_at: string;
}

export type DocumentType = "syllabus" | "study_material" | "previous_year_question";

export interface Document {
  id: number;
  subject_id: number;
  document_type: DocumentType;
  file_name: string;
  file_path: string;
  created_at: string;
}

export interface EvidenceBreakdown {
  syllabus_relevance: number;
  historical_support: number;
  study_material_support: number;
  pattern_compatibility: number;
  difficulty_compatibility: number;
  novelty: number;
}

export interface GeneratedQuestion {
  id: number;
  question_text: string;
  answer_text: string | null;
  topic_name: string;
  marks: number | null;
  difficulty: string | null;
  question_type: string | null;
  evidence_score: number;
  evidence_breakdown: EvidenceBreakdown | null;
  generation_reason: string | null;
  supporting_years: number[];
}

export interface TopicPattern {
  topic_id: number;
  topic_name: string;
  unit_name: string;
  frequency: number;
  total_papers: number;
  years: number[];
  marks_distribution: Record<string, number>;
  question_types: Record<string, number>;
  recurrence_intervals: number[];
  concept_count: number;
  exact_repeat_count: number;
  near_repeat_count: number;
}

export interface GenerateQuestionsParams {
  num_topics: number;
  questions_per_topic: number;
  final_top_n: number;
}

export interface GenerateQuestionsResult {
  total_generated: number;
  valid: number;
  rejected: number;
  final_top_n: number;
}

export interface AskResponse {
  answer: string;
  sources: string[];
}

export interface KnowledgeBaseStatus {
  exists: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

export type StepStatusMap = Record<string, boolean>;
