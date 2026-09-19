import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import api from "../api/client";
import { Trash2, Search, Bell, UploadCloud } from "lucide-react";
import type { OutletContext } from "../components/Layout";
import type { Document, DocumentType } from "../types";
import axios from "axios";

export default function Documents() {
  const { subjectId, subjects } = useOutletContext<OutletContext>();
  const [docs, setDocs] = useState<Document[]>([]);
  const [filter, setFilter] = useState<string>("All");
  const [uploadStatus, setUploadStatus] = useState<Record<string, string>>({});

  const load = () => {
    if (!subjectId) return;
    api.listDocuments(subjectId).then((r) => setDocs(r.data));
  };

  useEffect(load, [subjectId]);

  if (!subjectId) {
    return (
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
        <p className="text-yellow-700 mt-4">Select a subject in the sidebar first.</p>
      </div>
    );
  }

  const subjectName = subjects.find((s) => s.id === subjectId)?.name;
  const types = ["All", ...new Set(docs.map((d) => d.document_type))];
  const filtered = filter === "All" ? docs : docs.filter((d) => d.document_type === filter);

  const remove = async (id: number) => {
    await api.deleteDocument(subjectId, id);
    load();
  };

  const upload = async (file: File, type: DocumentType, key: string) => {
    setUploadStatus((s) => ({ ...s, [key]: "Uploading..." }));
    try {
      await api.uploadDocument(subjectId, file, type);
      setUploadStatus((s) => ({ ...s, [key]: "✅ Uploaded!" }));
      load();
    } catch (e) {
      const msg = axios.isAxiosError(e) ? e.response?.data?.detail : "Failed";
      setUploadStatus((s) => ({ ...s, [key]: `❌ ${msg || "Failed"}` }));
    }
  };

  const uploadMultiple = async (files: File[]) => {
    setUploadStatus((s) => ({ ...s, pyq: "Uploading..." }));
    let success = 0;
    for (const f of files) {
      try {
        await api.uploadDocument(subjectId, f, "previous_year_question");
        success++;
      } catch {
        /* continue */
      }
    }
    setUploadStatus((s) => ({ ...s, pyq: `Uploaded ${success}/${files.length} PYQ files` }));
    load();
  };

  const badgeColor = (t: string) =>
    t === "syllabus" ? "bg-purple-50 text-purple-600" : "bg-green-50 text-green-600";

  return (
    <div>
      {/* Top bar */}
      <div className="flex items-center justify-between mb-6">
        <div className="relative w-96 max-w-full">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            placeholder="Search subjects, documents, questions..."
            className="w-full rounded-lg border border-gray-200 bg-white pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button className="text-gray-400 hover:text-gray-600">
          <Bell size={20} />
        </button>
      </div>

      <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
      <p className="text-gray-500 mb-6">
        Upload and manage documents for: <b>{subjectName}</b>
      </p>

      {/* Upload section */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <UploadCloud size={18} />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Upload Documents</h2>
            <p className="text-sm text-gray-500">Add syllabus, study material, or previous year papers.</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <UploadCard
            title="Syllabus"
            onSelect={(files) => upload(files[0], "syllabus", "syllabus")}
            status={uploadStatus.syllabus}
          />
          <UploadCard
            title="Study Material"
            onSelect={(files) => upload(files[0], "study_material", "study")}
            status={uploadStatus.study}
          />
          <UploadCard
            title="Previous Year Questions"
            multiple
            onSelect={uploadMultiple}
            status={uploadStatus.pyq}
          />
        </div>
      </div>

      {/* Document list */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">Uploaded Documents</h2>
          <select
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            {types.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          {filtered.length === 0 && (
            <p className="text-gray-500 text-sm">No documents yet — upload one above.</p>
          )}
          {filtered.map((d) => (
            <div
              key={d.id}
              className="border border-gray-100 rounded-lg p-3 flex items-center justify-between"
            >
              <span className="text-sm">📄 {d.file_name}</span>
              <div className="flex items-center gap-3">
                <span
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full ${badgeColor(
                    d.document_type
                  )}`}
                >
                  {d.document_type}
                </span>
                <span className="text-xs text-gray-400">{d.created_at?.slice(0, 10)}</span>
                <button onClick={() => remove(d.id)} className="text-gray-400 hover:text-red-600">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

interface UploadCardProps {
  title: string;
  multiple?: boolean;
  onSelect: (files: File[]) => void;
  status?: string;
}

function UploadCard({ title, multiple, onSelect, status }: UploadCardProps) {
  const [files, setFiles] = useState<File[] | null>(null);

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <p className="text-sm font-medium mb-2">{title}</p>
      <input
        type="file"
        accept=".pdf"
        multiple={multiple}
        onChange={(e) => setFiles(e.target.files ? Array.from(e.target.files) : null)}
        className="text-xs mb-3 w-full"
      />
      <button
        onClick={() => files && onSelect(files)}
        disabled={!files}
        className="w-full bg-primary text-white py-1.5 rounded-lg text-sm font-medium disabled:opacity-40"
      >
        Upload
      </button>
      {status && <p className="text-xs mt-2 text-gray-600">{status}</p>}
    </div>
  );
}
