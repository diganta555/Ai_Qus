import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import api from "../api/client";
import type { OutletContext } from "../components/Layout";
import type { DocumentType } from "../types";
import axios from "axios";

export default function UploadPage() {
  const { subjectId, subjects } = useOutletContext<OutletContext>();
  const [status, setStatus] = useState<Record<string, string>>({});

  if (!subjectId)
    return <p className="text-yellow-700">Select a subject in the sidebar first.</p>;
  const subjectName = subjects.find((s) => s.id === subjectId)?.name;

  const upload = async (file: File, type: DocumentType, key: string) => {
    try {
      await api.uploadDocument(subjectId, file, type);
      setStatus((s) => ({ ...s, [key]: "✅ Uploaded!" }));
    } catch (e) {
      const msg = axios.isAxiosError(e) ? e.response?.data?.detail : "Failed";
      setStatus((s) => ({ ...s, [key]: `❌ ${msg || "Failed"}` }));
    }
  };

  const uploadMultiple = async (files: File[]) => {
    let success = 0;
    for (const f of files) {
      try {
        await api.uploadDocument(subjectId, f, "previous_year_question");
        success++;
      } catch {
        /* continue */
      }
    }
    setStatus((s) => ({ ...s, pyq: `Uploaded ${success}/${files.length} PYQ files` }));
  };

  return (
    <div>
      <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Upload Documents</h1>
      <p className="text-gray-500 mb-6 text-sm sm:text-base">
        Uploading for: <b>{subjectName}</b>
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <UploadCard
          title="Syllabus"
          accept=".pdf"
          onSelect={(files) => upload(files[0], "syllabus", "syllabus")}
          status={status.syllabus}
        />
        <UploadCard
          title="Study Material"
          accept=".pdf"
          onSelect={(files) => upload(files[0], "study_material", "study")}
          status={status.study}
        />
        <UploadCard
          title="Previous Year Questions"
          accept=".pdf"
          multiple
          onSelect={uploadMultiple}
          status={status.pyq}
        />
      </div>
    </div>
  );
}

interface UploadCardProps {
  title: string;
  accept: string;
  multiple?: boolean;
  onSelect: (files: File[]) => void;
  status?: string;
}

function UploadCard({ title, accept, multiple, onSelect, status }: UploadCardProps) {
  const [files, setFiles] = useState<File[] | null>(null);

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4">
      <p className="font-medium mb-2">{title}</p>
      <input
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={(e) => setFiles(e.target.files ? Array.from(e.target.files) : null)}
        className="text-sm mb-3 w-full"
      />
      <button
        onClick={() => files && onSelect(files)}
        disabled={!files}
        className="w-full bg-primary text-white py-2 rounded-lg text-sm font-medium disabled:opacity-40"
      >
        Upload
      </button>
      {status && <p className="text-sm mt-2 text-gray-600 break-words">{status}</p>}
    </div>
  );
}