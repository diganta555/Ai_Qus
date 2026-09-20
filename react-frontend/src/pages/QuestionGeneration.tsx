import { useEffect, useState } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import api from "../api/client";
import type { OutletContext } from "../components/Layout";
import type { GenerateQuestionsParams } from "../types";
import axios from "axios";
import { Play, Loader2 } from "lucide-react";
import type { GeneratedQuestion } from "../types";

const STEPS: [string, string][] = [
  ["1. Analyze Syllabus", "/analyze-syllabus"],
  ["2. Extract PYQs", "/extract-pyqs"],
  ["3. Classify Topics", "/classify-topics"],
  ["4. Map Concepts", "/map-concepts"],
  ["5. Analyze Repetition", "/analyze-repetition"],
  ["6. Analyze Patterns", "/analyze-patterns"],
  ["7. Build Knowledge Base", "/build-knowledge-base"],
];

interface GenResult {
  ok: boolean;
  total_generated?: number;
  final_top_n?: number;
  msg?: string;
}


export default function QuestionGeneration() {
  const { subjectId, subjects } = useOutletContext<OutletContext>();
  const [kbExists, setKbExists] = useState(false);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [pipelineError, setPipelineError] = useState<string | null>(null);
  const [genParams, setGenParams] = useState<GenerateQuestionsParams>({
    num_topics: 8,
    questions_per_topic: 4,
    final_top_n: 20,
  });
  const [genResult, setGenResult] = useState<GenResult | null>(null);
  const [genLoading, setGenLoading] = useState(false);
  const [stepStatus, setStepStatus] = useState<Record<string, boolean>>({});
  const [preview, setPreview] = useState<GeneratedQuestion[]>([]);
  const [previewIsPrevious, setPreviewIsPrevious] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!subjectId) return;
    api.knowledgeBaseStatus(subjectId).then((r) => setKbExists(r.data.exists));
    api.pipelineStatus(subjectId).then((r) => {
      setStepStatus(r.data);
      const completedCount = Object.values(r.data).filter(Boolean).length;
      setPipelineStep(completedCount);
    });
    setPipelineError(null);

    // Show whatever was already generated for this subject, if anything,
    // instead of a blank page until the user clicks Generate again.
    setGenResult(null);
    setPreview([]);
    api.finalQuestions(subjectId).then((r) => {
      if (r.data.length > 0) {
        setGenResult({ ok: true, final_top_n: r.data.length });
        setPreview(r.data.slice(0, 3));
        setPreviewIsPrevious(true);
      }
    }).catch(() => {});
  }, [subjectId]);

  if (!subjectId)
    return <p className="text-yellow-700">Select a subject in the sidebar first.</p>;
  const subjectName = subjects.find((s) => s.id === subjectId)?.name;

  const runFullPipeline = async () => {
    setPipelineRunning(true);
    setPipelineError(null);
    setStepStatus({});   // clear stale badges from any previous run before starting fresh
    setPipelineStep(0);
    for (let i = 0; i < STEPS.length; i++) {
      const [label, endpoint] = STEPS[i];
      const stepKey = endpoint.replace("/", "").replace(/-/g, "_");
      try {
        await api.runStep(subjectId, endpoint);

        // Poll until this step finishes (success or failed)
        let finished = false;
        while (!finished) {
          await new Promise((r) => setTimeout(r, 2000));
          const { data } = await api.jobStatus(subjectId, stepKey);
          if (data.status === "success") {
            finished = true;
          } else if (data.status === "failed") {
            throw new Error(data.error || "Step failed");
          }
          // if "running" or "not_started", keep polling
        }

        const status = await api.pipelineStatus(subjectId);
        setStepStatus(status.data);
        setPipelineStep(Object.values(status.data).filter(Boolean).length);
      } catch (e) {
        setPipelineError(`Failed at step: ${label}`);
        setPipelineRunning(false);
        return;
      }
    }

    setPipelineRunning(false);
    api.knowledgeBaseStatus(subjectId).then((r) => setKbExists(r.data.exists));
  };

  const generate = async () => {
    setGenLoading(true);
    setGenResult(null);
    setPreview([]);
    setPreviewIsPrevious(false);
    try {
      const { data } = await api.generateQuestions(subjectId, genParams);
      setGenResult({ ok: true, ...data });
      const questions = await api.finalQuestions(subjectId);
      setPreview(questions.data.slice(0, 3));
    } catch (e) {
      const msg = axios.isAxiosError(e) ? e.response?.data?.detail : undefined;
      setGenResult({ ok: false, msg: msg || "Generation failed" });
    }
    setGenLoading(false);
  };

  const updateParam = (key: keyof GenerateQuestionsParams, value: number) => {
    setGenParams((p) => ({ ...p, [key]: value }));
  };

  const progressPct = pipelineRunning || pipelineStep > 0
    ? Math.round((pipelineStep / STEPS.length) * 100)
    : 0;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">AI Question Generation Engine</h1>
      <p className="text-gray-500 mb-4">
        Run the analysis pipeline for: <b>{subjectName}</b>
      </p>

      {kbExists && !pipelineRunning && (
        <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg p-3 mb-6 text-sm">
          ✅ Knowledge base already built for this subject — you can skip straight to
          "Generate Final Questions" below, or re-run the pipeline if you've updated documents.
        </div>
      )}

      {/* Run Full Pipeline */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="font-semibold text-gray-900">Run Analysis Pipeline</h2>
            <p className="text-sm text-gray-500">
              Runs all 7 analysis steps in order, one click.
            </p>
          </div>
          <button
            onClick={runFullPipeline}
            disabled={pipelineRunning}
            className="bg-primary text-white px-5 py-2.5 rounded-lg font-medium disabled:opacity-60 flex items-center gap-2"
          >
            {pipelineRunning ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Running step {pipelineStep}/{STEPS.length}...
              </>
            ) : (
              <>
                <Play size={16} /> Run Full Pipeline
              </>
            )}
          </button>
        </div>

        {(pipelineRunning || pipelineStep > 0) && (
          <div>
            <div className="w-full bg-gray-100 rounded-full h-2.5 mb-1">
              <div
                className="bg-primary h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              />
            </div>
            <p className="text-xs text-gray-500">
              {pipelineStep}/{STEPS.length} steps completed
              {pipelineRunning && pipelineStep <= STEPS.length && !pipelineError && (
                <> — running {STEPS[pipelineStep - 1]?.[0]}</>
              )}
            </p>
            <div className="flex flex-wrap gap-2 mt-2">
              {STEPS.map(([label, endpoint]) => {
                const key = endpoint.replace("/", "").replace(/-/g, "_");
                const done = stepStatus[key];
                return (
                  <span
                    key={endpoint}
                    className={`text-xs px-2 py-1 rounded-full ${
                      done ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {done ? "✅" : "⬜"} {label}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {pipelineError && (
          <div className="mt-3 bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
            {pipelineError}
          </div>
        )}
        {!pipelineRunning && pipelineStep === STEPS.length && !pipelineError && (
          <div className="mt-3 bg-green-50 border border-green-200 text-green-700 rounded-lg p-3 text-sm">
            ✅ Full pipeline completed successfully.
          </div>
        )}
      </div>

      {/* Generate Questions */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="font-semibold mb-4">Generate Questions</h2>
        <div className="grid grid-cols-3 gap-4 mb-4">
          {(
            [
              ["num_topics", "Number of top topics"],
              ["questions_per_topic", "Questions per topic"],
              ["final_top_n", "Final question count"],
            ] as [keyof GenerateQuestionsParams, string][]
          ).map(([key, label]) => (
            <div key={key}>
              <label className="text-sm text-gray-600">{label}</label>
              <input
                type="number"
                value={genParams[key]}
                onChange={(e) => updateParam(key, Number(e.target.value))}
                className="w-full mt-1 rounded-lg border border-gray-300 px-3 py-2"
              />
            </div>
          ))}
        </div>
        <button
          onClick={generate}
          disabled={genLoading}
          className="bg-primary text-white px-5 py-2.5 rounded-lg font-medium disabled:opacity-50"
        >
          {genLoading ? "Generating... this may take 1-2 minutes" : "⚡ Generate Final Questions"}
        </button>
        {genResult && (
          <div
            className={`mt-4 rounded-lg p-3 text-sm ${
              genResult.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
            }`}
          >
            {genResult.ok
              ? previewIsPrevious
                ? `Showing your most recent generated set — ${genResult.final_top_n} questions.`
                : `Generated ${genResult.total_generated} candidates → ${genResult.final_top_n} ranked questions.`
              : `Generation failed: ${genResult.msg}`}
          </div>
        )}

        {preview.length > 0 && (
          <div className="mt-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              {previewIsPrevious ? "Previously Generated — Preview" : "Preview"}
            </h3>
            <div className="space-y-2">
              {preview.map((q, i) => (
                <div key={q.id} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-800">
                      Q{i + 1}. [{q.topic_name}] {q.question_text.slice(0, 90)}
                      {q.question_text.length > 90 ? "..." : ""}
                    </span>
                    <span className="text-xs font-semibold bg-green-50 text-green-600 px-2.5 py-1 rounded-full ml-3 whitespace-nowrap">
                      {q.evidence_score}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => navigate("/results")}
              className="mt-3 text-primary text-sm font-medium hover:underline"
            >
              See all {genResult?.final_top_n} questions in Results →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}