import axios from "axios";
import type { AxiosInstance } from "axios";
import type {
  AuthResponse, Subject, Document, DocumentType, GeneratedQuestion,
  TopicPattern, GenerateQuestionsParams, GenerateQuestionsResult,
  AskResponse, KnowledgeBaseStatus,
} from "../types";

const API_BASE: string = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8080";

const client: AxiosInstance = axios.create({ baseURL: API_BASE });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export interface QuestionBatch {
  batch_id: string;
  created_at: string;
  question_count: number;
}

export const api = {
  login: (email: string, password: string) =>
    client.post<AuthResponse>("/auth/login", { email, password }),
  signup: (email: string, password: string, name: string) =>
    client.post<AuthResponse>("/auth/signup", { email, password, name }),

  listSubjects: () => client.get<Subject[]>("/subjects"),
  // createSubject: (name: string) => client.post<Subject>("/subjects", { name }),
    createSubject: (payload: {
    name: string;
    subject_code?: string;
    description?: string;
    category?: string;
  }) => client.post<Subject>("/subjects", payload),
  deleteSubject: (id: number) => client.delete(`/subjects/${id}`),

  listDocuments: (subjectId: number) =>
    client.get<Document[]>(`/subjects/${subjectId}/documents`),
  uploadDocument: (subjectId: number, file: File, documentType: DocumentType) => {
    const form = new FormData();
    form.append("file", file);
    form.append("document_type", documentType);
    return client.post<Document>(`/subjects/${subjectId}/documents`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  deleteDocument: (subjectId: number, docId: number) =>
    client.delete(`/subjects/${subjectId}/documents/${docId}`),

  runStep: (subjectId: number, endpoint: string) =>
    client.post(`/subjects/${subjectId}${endpoint}`),
  knowledgeBaseStatus: (subjectId: number) =>
    client.get<KnowledgeBaseStatus>(`/subjects/${subjectId}/knowledge-base-status`),

  generateQuestions: (subjectId: number, params: GenerateQuestionsParams) =>
    client.post<GenerateQuestionsResult>(
      `/subjects/${subjectId}/generate-questions`,
      null,
      { params }
    ),
  finalQuestions: (subjectId: number) =>
    client.get<GeneratedQuestion[]>(`/subjects/${subjectId}/final-questions`),
  patterns: (subjectId: number) =>
    client.get<TopicPattern[]>(`/subjects/${subjectId}/patterns`),
  downloadPdf: (subjectId: number) =>
    client.get(`/subjects/${subjectId}/final-questions/pdf`, {
      responseType: "blob",
    }),

  ask: (subjectId: number, question: string) =>
    client.post<AskResponse>(`/subjects/${subjectId}/ask`, { question }),

  pipelineStatus: (subjectId: number) =>
    client.get<Record<string, boolean>>(`/subjects/${subjectId}/pipeline-status`),

  jobStatus: (subjectId: number, step: string) =>
    client.get<{ status: string; error?: string }>(`/subjects/${subjectId}/job-status/${step}`),

  // --- Batches: every time "Generate Final Questions" runs, the backend
  // stamps the new set with a batch_id. These let the UI list past sets
  // (1, 2, 3, ...) and fetch any one of them.
  listBatches: (subjectId: number) =>
    client.get<QuestionBatch[]>(`/subjects/${subjectId}/batches`),
  batchQuestions: (subjectId: number, batchId: string) =>
    client.get<GeneratedQuestion[]>(`/subjects/${subjectId}/batches/${batchId}/questions`),
};

export default api;