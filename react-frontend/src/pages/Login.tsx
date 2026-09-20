import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  BookOpen, FileText, BarChart3, HelpCircle, Target, Mail, Lock, Eye, EyeOff,
  Upload, Sparkles, LineChart, AlertCircle, X, Menu,
} from "lucide-react";
import axios from "axios";

type Tab = "login" | "signup";

const NAV_LINKS = [
  { id: "features", label: "Features" },
  { id: "subjects", label: "Subjects" },
  { id: "how-it-works", label: "How It Works" },
  { id: "about", label: "About" },
];

export default function Login() {
  const [tab, setTab] = useState<Tab>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  // Auto-dismiss the popup after a few seconds
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 4000);
    return () => clearTimeout(t);
  }, [toast]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (tab === "login") await login(email, password);
      else await signup(email, password, name);
      navigate("/");
    } catch (err) {
      const status = axios.isAxiosError(err) ? err.response?.status : undefined;
      const detail =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? String(err.response.data.detail)
          : "";

      let msg = detail || `${tab === "login" ? "Sign in" : "Sign up"} failed`;

      // Normalize the message shown to the user for a wrong-password / bad-credentials case
      if (tab === "login" && (status === 401 || status === 400)) {
        msg = "Incorrect email or password. Please try again.";
      }

      setError(msg);
      setToast(msg);
    }
    setLoading(false);
  };

  const scrollToSection = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    setMobileMenuOpen(false);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Wrong-password / login-failure popup */}
      {toast && (
        <div className="fixed top-5 right-5 left-5 sm:left-auto z-50 animate-[fadeIn_0.2s_ease-out]">
          <div className="flex items-start gap-3 bg-white border border-red-200 shadow-lg rounded-xl px-4 py-3 sm:max-w-sm">
            <AlertCircle className="text-red-500 shrink-0 mt-0.5" size={20} />
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-900">Sign in failed</p>
              <p className="text-sm text-gray-600">{toast}</p>
            </div>
            <button
              onClick={() => setToast("")}
              className="text-gray-400 hover:text-gray-600 shrink-0"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Top nav */}
      <header className="flex items-center justify-between px-4 sm:px-8 py-4 border-b border-gray-100 bg-white sticky top-0 z-40">
        <div className="flex items-center gap-2 min-w-0">
          <BookOpen className="text-primary shrink-0" size={22} />
          <span className="font-bold text-gray-900 whitespace-nowrap">AI QBank</span>
          <span className="text-gray-400 text-sm hidden sm:inline whitespace-nowrap">Your Study Companion</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm text-gray-600">
          {NAV_LINKS.map(({ id, label }) => (
            <a key={id} href={`#${id}`} onClick={scrollToSection(id)} className="hover:text-gray-900">
              {label}
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => {
              setTab("login");
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className="bg-primary text-white text-sm font-medium px-3 sm:px-4 py-2 rounded-lg hover:bg-primaryDark transition whitespace-nowrap"
          >
            Sign In
          </button>
          <button
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="md:hidden text-gray-500 hover:text-gray-800 p-1"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </header>

      {/* Mobile nav dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-gray-100 px-4 py-3 flex flex-col gap-3 sticky top-[65px] z-30">
          {NAV_LINKS.map(({ id, label }) => (
            <a key={id} href={`#${id}`} onClick={scrollToSection(id)} className="text-sm text-gray-600 hover:text-gray-900">
              {label}
            </a>
          ))}
        </div>
      )}

      {/* Hero + auth card — fills the first viewport (minus the header) */}
      <div className="min-h-[calc(100vh-73px)] max-w-6xl mx-auto px-4 sm:px-8 py-12 sm:py-16 grid md:grid-cols-2 gap-10 md:gap-12 items-center content-center">
        {/* Left: marketing content */}
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-medium bg-primary/10 text-primary px-3 py-1.5 rounded-full mb-4">
            📚 From Past Papers to Better Preparation
          </span>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight mb-4">
            Smarter Preparation<br />
            <span className="text-primary">with AI</span>
          </h1>
          <p className="text-gray-500 text-base sm:text-lg mb-8 max-w-md">
            Upload your study materials, analyze past year questions, and get AI-powered
            questions, insights, and personalized practice — all in one place.
          </p>
        </div>

        {/* Right: auth card */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8 w-full max-w-md mx-auto">
          <h2 className="text-xl font-bold text-gray-900">
            {tab === "login" ? "Welcome Back" : "Create your account"}
          </h2>
          <p className="text-gray-500 text-sm mb-6">
            {tab === "login" ? "Sign in to continue to AI QBank" : "Start generating smarter practice questions"}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {tab === "signup" && (
              <div>
                <label className="text-sm font-medium text-gray-700">Name</label>
                <input
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            )}

            <div>
              <label className="text-sm font-medium text-gray-700">Email Address</label>
              <div className="relative mt-1">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  required
                  placeholder="you@example.com"
                  className="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Password</label>
              <div className="relative mt-1">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="Enter your password"
                  className="w-full rounded-lg border border-gray-300 pl-9 pr-9 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {tab === "login" && (
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-gray-600">
                  <input
                    type="checkbox"
                    checked={remember}
                    onChange={(e) => setRemember(e.target.checked)}
                    className="rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  Remember me
                </label>
                <a href="#" className="text-primary font-medium">Forgot password?</a>
              </div>
            )}

            {error && <p className="text-red-600 text-sm">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary hover:bg-primaryDark text-white font-medium py-2.5 rounded-lg transition disabled:opacity-60"
            >
              {loading ? "Please wait..." : tab === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            {tab === "login" ? (
              <>
                Don't have an account?{" "}
                <button onClick={() => setTab("signup")} className="text-primary font-medium">
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button onClick={() => setTab("login")} className="text-primary font-medium">
                  Sign in
                </button>
              </>
            )}
          </p>
        </div>
      </div>

      {/* Features section */}
      <section id="features" className="scroll-mt-[73px] min-h-[calc(100vh-73px)] flex items-center border-t border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-12 sm:py-16 w-full">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 text-center mb-3">
            Everything you need to prepare smarter
          </h2>
          <p className="text-gray-500 text-center max-w-xl mx-auto mb-10">
            From raw study material to a ranked, exam-ready question bank — AI QBank handles the
            whole pipeline.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <Feature icon={FileText} color="bg-blue-50 text-blue-500" title="Upload & Analyze" desc="Syllabus, Notes, PYQs" />
            <Feature icon={BarChart3} color="bg-green-50 text-green-500" title="Find Key Topics" desc="Based on historical patterns" />
            <Feature icon={HelpCircle} color="bg-yellow-50 text-yellow-500" title="Generate Questions" desc="AI-powered, high-quality" />
            <Feature icon={Target} color="bg-red-50 text-red-500" title="Practice & Improve" desc="Track progress and get insights" />
          </div>
        </div>
      </section>

      {/* Subjects section */}
      <section id="subjects" className="scroll-mt-[73px] min-h-[calc(100vh-73px)] flex items-center border-t border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-12 sm:py-16 w-full">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 text-center mb-3">
            Works for any subject
          </h2>
          <p className="text-gray-500 text-center max-w-xl mx-auto mb-10">
            Whether it's engineering, science, or the humanities — upload your syllabus and past
            papers, and AI QBank builds a question bank tailored to that subject.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {["Algorithms & CS", "Mathematics", "Physics & Chemistry", "Economics", "Biology", "Business Studies", "Law", "Any custom subject"].map((s) => (
              <div key={s} className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-5 text-center">
                <p className="text-sm font-medium text-gray-800">{s}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works section */}
      <section id="how-it-works" className="scroll-mt-[73px] min-h-[calc(100vh-73px)] flex items-center bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-12 sm:py-16 w-full">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 text-center mb-10">
            How It Works
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            <Step number={1} icon={Upload} title="Upload materials" desc="Add your syllabus, notes, and previous year question papers." />
            <Step number={2} icon={LineChart} title="AI analyzes patterns" desc="We find recurring topics, weightage, and question trends." />
            <Step number={3} icon={Sparkles} title="Generate questions" desc="Grounded, high-quality questions are created from your material." />
            <Step number={4} icon={Target} title="Practice & improve" desc="Download question sets and track your prep as exam day nears." />
          </div>
        </div>
      </section>

      {/* About section */}
      <section id="about" className="scroll-mt-[73px] min-h-[calc(100vh-73px)] flex items-center border-t border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-4 sm:px-8 py-12 sm:py-16 text-center w-full">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">About AI QBank</h2>
          <p className="text-gray-500 leading-relaxed">
            AI QBank was built to solve a simple problem: students spend hours guessing what to
            study instead of studying it. By analyzing your syllabus alongside real past-year
            question patterns, AI QBank surfaces exactly what tends to be asked — so your
            preparation time goes where it matters most before an exam.
          </p>
          <button
            onClick={() => {
              setTab("login");
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className="mt-8 bg-primary text-white text-sm font-medium px-6 py-2.5 rounded-lg hover:bg-primaryDark transition"
          >
            Back to Sign In
          </button>
        </div>
      </section>

      <footer className="border-t border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-8 text-center text-sm text-gray-400">
          © {new Date().getFullYear()} AI QBank — Your Study Companion
        </div>
      </footer>
    </div>
  );
}

function Feature({
  icon: Icon,
  color,
  title,
  desc,
}: {
  icon: typeof FileText;
  color: string;
  title: string;
  desc: string;
}) {
  return (
    <div>
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-2 ${color}`}>
        <Icon size={18} />
      </div>
      <p className="text-sm font-semibold text-gray-900">{title}</p>
      <p className="text-xs text-gray-500">{desc}</p>
    </div>
  );
}

function Step({
  number,
  icon: Icon,
  title,
  desc,
}: {
  number: number;
  icon: typeof Upload;
  title: string;
  desc: string;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 relative">
      <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-3">
        <Icon size={18} />
      </div>
      <span className="absolute top-4 right-4 text-xs font-semibold text-gray-300">
        {String(number).padStart(2, "0")}
      </span>
      <p className="text-sm font-semibold text-gray-900 mb-1">{title}</p>
      <p className="text-xs text-gray-500">{desc}</p>
    </div>
  );
}