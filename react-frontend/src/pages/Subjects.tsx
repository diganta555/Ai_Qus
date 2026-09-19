import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import api from "../api/client";
import type { OutletContext } from "../components/Layout";
import { Pencil, Trash2, Search, Bell, BookOpen, Library } from "lucide-react";

const CATEGORIES = ["Computer Science", "Artificial Intelligence", "Mathematics", "Physics", "Other"];

export default function Subjects() {
  const { subjectId, setSubjectId, subjects, setSubjects } = useOutletContext<OutletContext>();
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const navigate = useNavigate();

  const refresh = () => api.listSubjects().then((r) => setSubjects(r.data));

    const create = async (e: FormEvent) => {
    e.preventDefault();
    if (!name) return;
    await api.createSubject({
      name,
      subject_code: code || undefined,
      description: description || undefined,
      category: category || undefined,
    });
    setName("");
    setCode("");
    setDescription("");
    setCategory("");
    refresh();
  };

  const remove = async (id: number) => {
    await api.deleteSubject(id);
    setConfirmId(null);
    refresh();
  };

  const filtered = subjects.filter((s) =>
    s.name.toLowerCase().includes(search.toLowerCase())
  );

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

      <h1 className="text-2xl font-bold text-gray-900">Subjects</h1>
      <p className="text-gray-500 mb-6">Create a new subject and manage your existing subjects.</p>

      {/* Create New Subject */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <BookOpen size={18} />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Create New Subject</h2>
            <p className="text-sm text-gray-500">
              Add a new subject to organize your documents and generate questions.
            </p>
          </div>
        </div>

        <form onSubmit={create} className="grid grid-cols-4 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Subject Name *</label>
            <input
              required
              placeholder="e.g. Advanced Algorithms"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Subject Code (Optional)</label>
            <input
              placeholder="e.g. CSC902"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Description (Optional)</label>
            <input
              placeholder="Brief description about the subject"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Category (Optional)</label>
            <select
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">Select Category</option>
              {CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="col-span-4 flex justify-end">
            <button
              type="submit"
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primaryDark"
            >
              + Create Subject
            </button>
          </div>
        </form>
      </div>

      {/* Your Subjects */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
              <Library size={18} />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900">Your Subjects</h2>
              <p className="text-sm text-gray-500">All the subjects you have created.</p>
            </div>
          </div>
          <div className="relative w-64">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              placeholder="Search subjects..."
              className="w-full rounded-lg border border-gray-200 pl-8 pr-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-100">
              <th className="py-2 pr-3 font-medium">#</th>
              <th className="py-2 pr-3 font-medium">Subject Name</th>
              <th className="py-2 pr-3 font-medium">Subject Code</th>
              <th className="py-2 pr-3 font-medium">Category</th>
              <th className="py-2 pr-3 font-medium">Description</th>
              <th className="py-2 pr-3 font-medium">Created On</th>
              <th className="py-2 pr-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s, i) => (
              <tr key={s.id} className="border-b border-gray-50">
                <td className="py-3 pr-3 text-gray-500">{i + 1}</td>
                <td className="py-3 pr-3 font-medium text-gray-900">{s.name}</td>
                                <td className="py-3 pr-3 text-gray-500">{s.subject_code || "—"}</td>
                <td className="py-3 pr-3">
                  {s.category ? (
                    <span className="text-xs font-medium bg-blue-50 text-blue-600 px-2.5 py-1 rounded-full">
                      {s.category}
                    </span>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
                <td className="py-3 pr-3 text-gray-500 max-w-xs truncate">{s.description || "—"}</td>
                <td className="py-3 pr-3 text-gray-500">
                  {new Date(s.created_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </td>
                  <td className="py-3 pr-3">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => {
                        setSubjectId(s.id);
                        navigate("/documents");
                      }}
                      className={`text-xs font-medium px-2.5 py-1 rounded-lg border ${
                        subjectId === s.id
                          ? "bg-primary text-white border-primary"
                          : "border-gray-300 text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      {subjectId === s.id ? "Active" : "Select"}
                    </button>
                    <button className="text-gray-400 hover:text-primary">
                      <Pencil size={15} />
                    </button>
                    <button
                      onClick={() => setConfirmId(s.id)}
                      className="text-gray-400 hover:text-red-600"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="py-6 text-center text-gray-400">
                  No subjects found.
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {confirmId !== null && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-700 mb-2">
              Delete this subject and all its documents, analysis, and generated questions?
              This cannot be undone.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => remove(confirmId)}
                className="bg-red-600 text-white px-3 py-1 rounded-lg text-sm"
              >
                Yes, delete
              </button>
              <button
                onClick={() => setConfirmId(null)}
                className="px-3 py-1 rounded-lg text-sm border border-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}