import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import api from "../api/client";
import { PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";
import type { OutletContext } from "../components/Layout";
import type { GeneratedQuestion, TopicPattern, Document } from "../types";
import { FileText, Layers, HelpCircle, Gauge, Download, RefreshCw } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

const COLORS = [
  "#7c3aed", "#a78bfa", "#f472b6", "#fb923c",
  "#34d399", "#60a5fa", "#fbbf24", "#f87171",
];

type Tab = "overview" | "topics" | "questions" | "documents" | "downloads";

const TABS: { key: Tab; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "topics", label: "Topics & Coverage" },
  { key: "questions", label: "Generated Questions" },
  { key: "documents", label: "Document Insights" },
  { key: "downloads", label: "Downloads" },
];

export default function Results() {
  const { subjectId, subjects } = useOutletContext<OutletContext>();
  const [questions, setQuestions] = useState<GeneratedQuestion[]>([]);
  const [patterns, setPatterns] = useState<TopicPattern[]>([]);
  const [docs, setDocs] = useState<Document[]>([]);
  const [tab, setTab] = useState<Tab>("overview");
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    if (!subjectId) return;
    api.finalQuestions(subjectId).then((r) => setQuestions(r.data));
    api.patterns(subjectId).then((r) => setPatterns(r.data));
    api.listDocuments(subjectId).then((r) => setDocs(r.data));
  }, [subjectId]);

  if (!subjectId) return <p className="text-yellow-700">Select a subject in the sidebar first.</p>;
  const subjectName = subjects.find((s) => s.id === subjectId)?.name || "";

  if (questions.length === 0) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">Results</h1>
        <p className="text-gray-500">
          No generated questions yet — run "Generate Final Questions" in the Question
          Generation tab.
        </p>
      </div>
    );
  }

  const uniqueTopics = new Set(questions.map((q) => q.topic_name)).size;

  const difficultyCounts: Record<string, number> = { easy: 0, medium: 0, hard: 0 };
  questions.forEach((q) => {
    const d = (q.difficulty || "medium").toLowerCase();
    if (difficultyCounts[d] !== undefined) difficultyCounts[d]++;
  });
  const difficultyData = [
    { name: "Easy", value: difficultyCounts.easy },
    { name: "Medium", value: difficultyCounts.medium },
    { name: "Hard", value: difficultyCounts.hard },
  ];
  const avgDifficultyLabel =
    Object.entries(difficultyCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "medium";

  const topicCounts: Record<string, { count: number; difficulties: string[] }> = {};
  questions.forEach((q) => {
    if (!topicCounts[q.topic_name]) topicCounts[q.topic_name] = { count: 0, difficulties: [] };
    topicCounts[q.topic_name].count++;
    topicCounts[q.topic_name].difficulties.push(q.difficulty || "medium");
  });
  const pieData = Object.entries(topicCounts).map(([name, v]) => ({ name, value: v.count }));
  const topTopics = Object.entries(topicCounts)
    .map(([name, v]) => ({
      name,
      count: v.count,
      avgDifficulty: mostCommon(v.difficulties),
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  const downloadPdf = async () => {
    const { data } = await api.downloadPdf(subjectId);
    const url = window.URL.createObjectURL(new Blob([data], { type: "application/pdf" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `${subjectName}_question_bank.pdf`;
    a.click();
  };

  return (
    <div>
      <p className="text-sm text-gray-400 mb-1">Results &gt; {subjectName}</p>
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-bold text-gray-900">{subjectName} - Results</h1>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs font-medium bg-green-50 text-green-600 px-3 py-1.5 rounded-full">
            ✅ Pipeline Completed
          </span>
          <button className="flex items-center gap-1.5 bg-primary text-white text-sm font-medium px-3 py-1.5 rounded-lg">
            <RefreshCw size={14} /> Run Again
          </button>
        </div>
      </div>
      <p className="text-gray-500 mb-6">
        Analysis completed! Here are the key insights and generated questions.
      </p>

      {/* Tabs */}
      <div className="flex gap-6 border-b border-gray-200 mb-6">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`pb-3 text-sm font-medium ${
              tab === t.key ? "text-primary border-b-2 border-primary" : "text-gray-500"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <>
          <div className="grid grid-cols-4 gap-4 mb-6">
            <StatCard icon={FileText} color="bg-purple-50 text-purple-500" label="Documents Processed" value={docs.length} sub="PDFs, Notes" />
            <StatCard icon={Layers} color="bg-blue-50 text-blue-500" label="Topics Identified" value={uniqueTopics} sub="From syllabus & documents" />
            <StatCard icon={HelpCircle} color="bg-green-50 text-green-500" label="Questions Generated" value={questions.length} sub="High-quality questions" />
            <StatCard icon={Gauge} color="bg-orange-50 text-orange-500" label="Average Difficulty" value={cap(avgDifficultyLabel)} sub="Based on topic analysis" small />
          </div>

          <div className="grid grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold text-gray-900">Topic Distribution</h2>
              <p className="text-xs text-gray-500 mb-3">Breakdown of topics based on generated questions</p>
              <div className="flex items-center justify-center">
                <PieChart width={220} height={220}>
                  <Pie data={pieData} dataKey="value" innerRadius={55} outerRadius={90}>
                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mt-2">
                {pieData.slice(0, 8).map((p, i) => (
                  <div key={p.name} className="flex items-center gap-1.5 text-gray-600">
                    <span className="w-2 h-2 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                    {p.name} {((p.value / questions.length) * 100).toFixed(0)}%
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold text-gray-900">Difficulty Distribution</h2>
              <p className="text-xs text-gray-500 mb-3">Distribution of generated questions by difficulty</p>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={difficultyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#7c3aed" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center justify-between mb-1">
                <h2 className="font-semibold text-gray-900">Source Documents</h2>
                <button onClick={() => setTab("documents")} className="text-primary text-xs">View All →</button>
              </div>
              <p className="text-xs text-gray-500 mb-3">Documents used for analysis</p>
              <div className="space-y-2">
                {docs.slice(0, 5).map((d) => (
                  <div key={d.id} className="flex items-center gap-2 text-sm">
                    <FileText size={14} className="text-red-400 shrink-0" />
                    <div className="min-w-0">
                      <p className="truncate text-gray-800">{d.file_name}</p>
                      <p className="text-xs text-gray-400 capitalize">{d.document_type.replace(/_/g, " ")}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div className="col-span-2 bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-gray-900">Top Topics by Question Count</h2>
                <button onClick={() => setTab("topics")} className="text-primary text-xs">View All →</button>
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="py-2">#</th><th>Topic Name</th><th>No. of Questions</th><th>Avg. Difficulty</th>
                  </tr>
                </thead>
                <tbody>
                  {topTopics.map((t, i) => (
                    <tr key={t.name} className="border-b border-gray-50">
                      <td className="py-2 text-gray-400">{i + 1}</td>
                      <td>{t.name}</td>
                      <td>{t.count}</td>
                      <td>
                        <span className="text-xs font-medium bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full capitalize">
                          {t.avgDifficulty}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="bg-primary/5 border border-primary/20 rounded-xl p-5 flex flex-col items-start justify-center gap-2">
              <p className="text-2xl">💡</p>
              <h3 className="font-semibold text-gray-900">Ready to Practice?</h3>
              <p className="text-sm text-gray-500 mb-2">
                Use the generated questions to review and study this subject.
              </p>
              <button onClick={downloadPdf} className="bg-primary text-white text-sm font-medium px-4 py-2 rounded-lg flex items-center gap-2">
                <Download size={14} /> Download Question Bank
              </button>
            </div>
          </div>
        </>
      )}

      {tab === "topics" && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Historical Pattern Analysis</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2">Topic</th><th>Category</th><th>Appearances</th><th>Years</th>
              </tr>
            </thead>
            <tbody>
              {patterns.map((p, i) => (
                <tr key={i} className="border-b border-gray-50">
                  <td className="py-2">{p.topic_name}</td>
                  <td>{p.unit_name}</td>
                  <td>{p.frequency}/{p.total_papers}</td>
                  <td>{p.years.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "questions" && (
        <div className="space-y-2">
          {questions.map((q, i) => (
            <div key={q.id} className="bg-white border border-gray-200 rounded-xl">
              <button
                onClick={() => setExpanded(expanded === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left"
              >
                <span className="text-sm">
                  Q{i + 1}. [{q.topic_name}] {q.question_text.slice(0, 80)}...
                </span>
                <span className="text-xs font-semibold bg-green-50 text-green-600 px-2.5 py-1 rounded-full ml-3 whitespace-nowrap">
                  Evidence: {q.evidence_score}
                </span>
              </button>
              {expanded === i && (
                <div className="px-4 pb-4 text-sm text-gray-700 space-y-1 border-t border-gray-100 pt-3">
                <p><b>Full question:</b> {q.question_text}</p>
                {q.answer_text && (
                  <div className="bg-green-50 border border-green-100 rounded-lg p-3 mt-2">
                    <p className="font-semibold text-green-800 mb-1">Answer</p>
                    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                      {q.answer_text}
                    </ReactMarkdown>
                  </div>
                )}
                  <p><b>Marks:</b> {q.marks} | <b>Difficulty:</b> {q.difficulty} | <b>Type:</b> {q.question_type}</p>
                  <p><b>Why this question?</b> {q.generation_reason}</p>
                  <p><b>Supporting years:</b> {q.supporting_years?.join(", ")}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "documents" && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900 mb-3">All Source Documents</h2>
          <div className="space-y-2">
            {docs.map((d) => (
              <div key={d.id} className="flex items-center justify-between border border-gray-100 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-red-400" />
                  <span className="text-sm">{d.file_name}</span>
                </div>
                <span className="text-xs text-gray-400 capitalize">{d.document_type.replace(/_/g, " ")}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "downloads" && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Downloads</h2>
          <button onClick={downloadPdf} className="bg-primary text-white text-sm font-medium px-4 py-2.5 rounded-lg flex items-center gap-2">
            <Download size={16} /> Download Question Bank (PDF)
          </button>
        </div>
      )}
    </div>
  );
}

function cap(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function mostCommon(arr: string[]): string {
  const counts: Record<string, number> = {};
  arr.forEach((a) => { counts[a] = (counts[a] || 0) + 1; });
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || "medium";
}

function StatCard({
  icon: Icon, color, label, value, sub, small,
}: {
  icon: typeof FileText; color: string; label: string; value: string | number; sub: string; small?: boolean;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-start gap-3">
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${color}`}>
        <Icon size={16} />
      </div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className={`font-bold text-gray-900 ${small ? "text-lg" : "text-xl"}`}>{value}</p>
        <p className="text-xs text-gray-400">{sub}</p>
      </div>
    </div>
  );
}
