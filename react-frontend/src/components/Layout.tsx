import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import api from "../api/client";
import type { Subject } from "../types";
import {
  BookOpen, LayoutDashboard, Folder, FileText, Upload,
  Sparkles, MessageCircle, BarChart3, LogOut, Menu, X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

const NAV: NavItem[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/subjects", label: "Subjects", icon: Folder },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/upload", label: "Upload", icon: Upload },
  { to: "/generate", label: "Question Generation", icon: Sparkles },
  { to: "/ask", label: "Ask Question", icon: MessageCircle },
  { to: "/results", label: "Results", icon: BarChart3 },
];

export interface OutletContext {
  subjectId: number | null;
  setSubjectId: Dispatch<SetStateAction<number | null>>;
  subjects: Subject[];
  setSubjects: Dispatch<SetStateAction<Subject[]>>;
}

interface LayoutProps {
  subjectId: number | null;
  setSubjectId: Dispatch<SetStateAction<number | null>>;
}

export default function Layout({ subjectId, setSubjectId }: LayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    api.listSubjects().then((r) => {
      setSubjects(r.data);
      // Auto-select if exactly one subject and nothing is active yet
      if (r.data.length === 1 && !subjectId) {
        setSubjectId(r.data[0].id);
      }
    }).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const context: OutletContext = { subjectId, setSubjectId, subjects, setSubjects };
  const activeSubject = subjects.find((s) => s.id === subjectId);

  return (
    <div className="min-h-screen md:flex">
      {/* Backdrop — closes the drawer when tapped, mobile only */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 bg-black/30 z-40 md:hidden"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col p-4 transform transition-transform duration-200 ease-in-out
          md:static md:translate-x-0 md:z-auto
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <BookOpen className="text-primary" size={22} />
            <span className="font-bold text-gray-900">AI QBank</span>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="md:hidden text-gray-400 hover:text-gray-600"
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>
        <p className="text-xs text-gray-400 mb-4">Your Study Companion</p>

        {/* Active subject — moved to top, always visible */}
        <div className="mb-4">
          <label className="text-xs font-medium text-gray-400 uppercase tracking-wide">
            Active Subject
          </label>
          <select
            className="mt-1 w-full text-sm font-medium rounded-lg border border-gray-300 bg-primary/5 px-2.5 py-2 text-primary focus:outline-none focus:ring-2 focus:ring-primary"
            value={subjectId ?? ""}
            onChange={(e) =>
              setSubjectId(e.target.value ? Number(e.target.value) : null)
            }
          >
            <option value="">-- Select a subject --</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
          {!activeSubject && subjects.length > 0 && (
            <p className="text-xs text-amber-600 mt-1">Pick a subject to get started</p>
          )}
        </div>

        {user && (
          <div className="mb-4 pb-4 border-b border-gray-100">
            <p className="text-sm text-gray-600">👤 {user.name || user.email}</p>
            <button
              onClick={handleLogout}
              className="mt-2 flex items-center gap-1 text-sm text-gray-500 hover:text-red-600"
            >
              <LogOut size={14} /> Log out
            </button>
          </div>
        )}

        <nav className="flex flex-col gap-1 overflow-y-auto">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-gray-600 hover:bg-gray-50"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white sticky top-0 z-30">
          <button
            onClick={() => setMobileOpen(true)}
            className="text-gray-500 hover:text-gray-800 p-1"
            aria-label="Open menu"
          >
            <Menu size={22} />
          </button>
          <div className="flex items-center gap-2">
            <BookOpen className="text-primary" size={18} />
            <span className="font-bold text-gray-900 text-sm">AI QBank</span>
          </div>
          <div style={{ width: 22 }} />
        </div>

        <main className="flex-1 p-4 sm:p-8 overflow-y-auto min-w-0">
          <Outlet context={context} />
        </main>
      </div>
    </div>
  );
}