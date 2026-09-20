import { useEffect, useState } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import api from "../api/client";
import type { OutletContext } from "../components/Layout";
import { FileText, HelpCircle, Sparkles, Upload, Zap, ArrowRight, Search, Bell } from "lucide-react";

interface SubjectSummary {
  id: number;
  name: string;
  docCount: number;
  questionCount: number;
}

export default function Dashboard() {
  const { subjectId, subjects, setSubjects } = useOutletContext<OutletContext>();
  const [summaries, setSummaries] = useState<SubjectSummary[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all(
      subjects.map(async (s) => {
        const [docs, questions] = await Promise.all([
          api.listDocuments(s.id).catch(() => ({ data: [] })),
          api.finalQuestions(s.id).catch(() => ({ data: [] })),
        ]);
        return {
          id: s.id,
          name: s.name,
          docCount: docs.data.length,
          questionCount: questions.data.length,
        };
      })
    ).then(setSummaries);
  }, [subjects]);

  const totalDocs = summaries.reduce((a, s) => a + s.docCount, 0);
  const totalQuestions = summaries.reduce((a, s) => a + s.questionCount, 0);
  const userName = JSON.parse(localStorage.getItem("user") || "{}")?.name || "there";

  const refreshSubjects = () => api.listSubjects().then((r) => setSubjects(r.data));

  return (
    <div>
      {/* Top bar */}
      <div className="flex items-center justify-between gap-3 mb-6">
        <div className="relative flex-1 sm:w-96 sm:flex-none max-w-full">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            placeholder="Search subjects, documents, questions..."
            className="w-full rounded-lg border border-gray-200 bg-white pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button className="text-gray-400 hover:text-gray-600 shrink-0">
          <Bell size={20} />
        </button>
      </div>

      <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Welcome back, {userName}! 👋</h1>
      <p className="text-gray-500 mb-6 text-sm sm:text-base">Ready to generate questions and boost your preparation?</p>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <StatCard icon={FileText} color="bg-purple-50 text-purple-500" label="Total Subjects" value={subjects.length} sub="Manage your subjects" />
        <StatCard icon={FileText} color="bg-green-50 text-green-500" label="Documents Uploaded" value={totalDocs} sub="PDFs, Notes, PYQs" />
        <StatCard icon={HelpCircle} color="bg-orange-50 text-orange-500" label="Questions Generated" value={totalQuestions} sub="Across all subjects" />
      </div>

      {/* Quick actions + recent subjects */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900">Quick Actions</h2>
          <p className="text-sm text-gray-500 mb-4">Get started with these common tasks</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <QuickAction
              icon={Upload}
              color="bg-blue-50 text-blue-500"
              title="Upload Documents"
              desc="Add syllabus, notes or previous year papers"
              buttonLabel="Upload Now"
              onClick={() => navigate("/upload")}
            />
            <QuickAction
              icon={Zap}
              color="bg-green-50 text-green-500"
              title="Run Pipeline"
              desc="Analyze documents and generate insights"
              buttonLabel="Run Analysis"
              onClick={() => navigate("/generate")}
            />
            <QuickAction
              icon={HelpCircle}
              color="bg-yellow-50 text-yellow-500"
              title="Generate Questions"
              desc="Create high-quality questions using AI"
              buttonLabel="Generate"
              onClick={() => navigate("/generate")}
            />
            <QuickAction
              icon={Sparkles}
              color="bg-purple-50 text-purple-500"
              title="View Results"
              desc="See your generated question bank"
              buttonLabel="View Results"
              onClick={() => navigate("/results")}
            />
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-semibold text-gray-900">Recent Subjects</h2>
            <button onClick={() => navigate("/subjects")} className="text-primary text-sm flex items-center gap-1">
              View All <ArrowRight size={14} />
            </button>
          </div>
          <div className="space-y-3 mt-3">
            {summaries.length === 0 && (
              <p className="text-sm text-gray-500">No subjects yet.</p>
            )}
            {summaries.map((s) => (
              <div
                key={s.id}
                className={`p-3 rounded-lg border ${s.id === subjectId ? "border-primary bg-primary/5" : "border-gray-100"}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm text-gray-900">{s.name}</span>
                  {s.id === subjectId && (
                    <span className="text-xs font-semibold bg-green-50 text-green-600 px-2 py-0.5 rounded-full">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">
                  {s.docCount} documents · {s.questionCount} questions
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <button onClick={refreshSubjects} className="text-xs text-gray-400 hover:text-gray-600">
        Refresh data
      </button>
    </div>
  );
}

function StatCard({
  icon: Icon,
  color,
  label,
  value,
  sub,
}: {
  icon: typeof FileText;
  color: string;
  label: string;
  value: number;
  sub: string;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-start gap-3">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${color}`}>
        <Icon size={18} />
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-xs text-gray-400">{sub}</p>
      </div>
    </div>
  );
}

function QuickAction({
  icon: Icon,
  color,
  title,
  desc,
  buttonLabel,
  onClick,
}: {
  icon: typeof FileText;
  color: string;
  title: string;
  desc: string;
  buttonLabel: string;
  onClick: () => void;
}) {
  return (
    <div className="rounded-xl border border-gray-100 p-4 hover:border-gray-200 transition">
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-2 ${color}`}>
        <Icon size={16} />
      </div>
      <p className="text-sm font-semibold text-gray-900">{title}</p>
      <p className="text-xs text-gray-500 mb-3">{desc}</p>
      <button
        onClick={onClick}
        className="w-full text-sm font-medium border border-gray-300 rounded-lg py-1.5 hover:bg-gray-50"
      >
        {buttonLabel}
      </button>
    </div>
  );
}