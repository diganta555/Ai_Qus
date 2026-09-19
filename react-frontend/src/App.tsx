import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Subjects from "./pages/Subjects";
import Documents from "./pages/Documents";
import UploadPage from "./pages/UploadPage";
import QuestionGeneration from "./pages/QuestionGeneration";
import AskQuestion from "./pages/AskQuestion";
import Results from "./pages/Results";

function ProtectedLayout() {
  const { user } = useAuth();
  const [subjectId, setSubjectId] = useState<number | null>(null);
  if (!user) return <Navigate to="/login" />;
  return <Layout subjectId={subjectId} setSubjectId={setSubjectId} />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/subjects" element={<Subjects />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/generate" element={<QuestionGeneration />} />
            <Route path="/ask" element={<AskQuestion />} />
            <Route path="/results" element={<Results />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
