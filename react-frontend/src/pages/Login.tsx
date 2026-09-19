import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { BookOpen, FileText, BarChart3, HelpCircle, Target, Mail, Lock, Eye, EyeOff } from "lucide-react";
import axios from "axios";

type Tab = "login" | "signup";

export default function Login() {
  const [tab, setTab] = useState<Tab>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (tab === "login") await login(email, password);
      else await signup(email, password, name);
      navigate("/");
    } catch (err) {
      const msg =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : `${tab === "login" ? "Sign in" : "Sign up"} failed`;
      setError(msg);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top nav */}
      <header className="flex items-center justify-between px-8 py-4 border-b border-gray-100 bg-white">
        <div className="flex items-center gap-2">
          <BookOpen className="text-primary" size={22} />
          <span className="font-bold text-gray-900">AI QBank</span>
          <span className="text-gray-400 text-sm hidden sm:inline">Your Study Companion</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm text-gray-600">
          <a href="#" className="hover:text-gray-900">Features</a>
          <a href="#" className="hover:text-gray-900">Subjects</a>
          <a href="#" className="hover:text-gray-900">How It Works</a>
          <a href="#" className="hover:text-gray-900">About</a>
        </nav>
        <button
          onClick={() => setTab("login")}
          className="bg-primary text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-primaryDark transition"
        >
          Sign In
        </button>
      </header>

      {/* Hero + auth card */}
      <div className="max-w-6xl mx-auto px-8 py-16 grid md:grid-cols-2 gap-12 items-center">
        {/* Left: marketing content */}
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-medium bg-primary/10 text-primary px-3 py-1.5 rounded-full mb-4">
            📚 From Past Papers to Better Preparation
          </span>
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight mb-4">
            Smarter Preparation<br />
            <span className="text-primary">with AI</span>
          </h1>
          <p className="text-gray-500 text-lg mb-8 max-w-md">
            Upload your study materials, analyze past year questions, and get AI-powered
            questions, insights, and personalized practice — all in one place.
          </p>

          <div className="grid grid-cols-2 gap-4 max-w-md">
            <Feature icon={FileText} color="bg-blue-50 text-blue-500" title="Upload & Analyze" desc="Syllabus, Notes, PYQs" />
            <Feature icon={BarChart3} color="bg-green-50 text-green-500" title="Find Key Topics" desc="Based on historical patterns" />
            <Feature icon={HelpCircle} color="bg-yellow-50 text-yellow-500" title="Generate Questions" desc="AI-powered, high-quality" />
            <Feature icon={Target} color="bg-red-50 text-red-500" title="Practice & Improve" desc="Track progress and get insights" />
          </div>
        </div>

        {/* Right: auth card */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 w-full max-w-md mx-auto">
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

          <div className="flex items-center gap-3 my-6">
            <div className="h-px bg-gray-200 flex-1" />
            <span className="text-xs text-gray-400">or continue with</span>
            <div className="h-px bg-gray-200 flex-1" />
          </div>

          <div className="space-y-3">
            <button className="w-full flex items-center justify-center gap-2 border border-gray-300 rounded-lg py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
              <span>🔍</span> Continue with Google
            </button>
            <button className="w-full flex items-center justify-center gap-2 border border-gray-300 rounded-lg py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
              <span>🐙</span> Continue with GitHub
            </button>
          </div>

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
