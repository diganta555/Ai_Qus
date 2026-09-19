import { useState } from "react";
import type { KeyboardEvent } from "react";
import { useOutletContext } from "react-router-dom";
import api from "../api/client";
import { Send } from "lucide-react";
import type { OutletContext } from "../components/Layout";
import type { ChatMessage } from "../types";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

export default function AskQuestion() {
  const { subjectId, subjects } = useOutletContext<OutletContext>();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  if (!subjectId)
    return <p className="text-yellow-700">Select a subject in the sidebar first.</p>;
  const subjectName = subjects.find((s) => s.id === subjectId)?.name;

  const send = async () => {
    if (!input.trim()) return;
    const question = input;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: question }]);
    setLoading(true);
    try {
      const { data } = await api.ask(subjectId, question);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (e) {
      const msg = axios.isAxiosError(e) ? e.response?.data?.detail : undefined;
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${msg || "Something went wrong"}` },
      ]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") send();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <h1 className="text-2xl font-bold text-gray-900">Ask a Question</h1>
      <p className="text-gray-500 mb-4">
        Ask anything about <b>{subjectName}</b> — answers are grounded in your uploaded study
        material and syllabus.
      </p>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`max-w-2xl ${m.role === "user" ? "ml-auto" : ""}`}>
            <div
              className={`rounded-xl px-4 py-2.5 ${
                m.role === "user"
                  ? "bg-primary text-white"
                  : "bg-white border border-gray-200 prose prose-sm max-w-none"
              }`}
            >
              {m.role === "assistant" ? (
                <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                  {m.content}
                </ReactMarkdown>
              ) : (
                m.content
              )}
            </div>
            {m.sources && m.sources.length > 0 && (
              <details className="text-xs text-gray-500 mt-1">
                <summary className="cursor-pointer">Sources</summary>
                {m.sources.map((s, j) => (
                  <p key={j}>• {s}</p>
                ))}
              </details>
            )}
          </div>
        ))}
        {loading && <p className="text-gray-400 text-sm">Thinking...</p>}
      </div>

      <div className="flex gap-2">
        <input
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5"
          placeholder="Ask a question about this subject..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button onClick={send} className="bg-primary text-white px-4 rounded-lg">
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
