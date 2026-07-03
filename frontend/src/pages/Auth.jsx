import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, register } from "../api";

const COPY = {
  login: {
    title: "Welcome Back",
    submit: "Login",
    toggle: "Don't have an account? Register",
  },
  register: {
    title: "Create Account",
    submit: "Register",
    toggle: "Already have an account? Login",
  },
};

function Auth() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const mode = isLogin ? COPY.login : COPY.register;

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isLogin) {
        localStorage.setItem("token", (await login(email, password)).access_token);
        navigate("/dashboard");
      } else {
        await register(email, password);
        alert("Account created successfully!");
        setIsLogin(true);
        setPassword("");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-black px-6">
      <div className="w-full max-w-md rounded-3xl border border-zinc-800 bg-[#0B0B0B] p-8">
        <h1 className="text-3xl font-semibold text-white">{mode.title}</h1>
        <p className="mt-2 text-zinc-500">Adaptive LLM Gateway</p>
        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-xl border border-zinc-800 bg-black px-4 py-3 text-white outline-none focus:border-white"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-xl border border-zinc-800 bg-black px-4 py-3 text-white outline-none focus:border-white"
          />
          {error && (
            <p className="text-sm text-red-400">{error}</p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-white py-3 font-medium text-black transition hover:bg-zinc-300 disabled:opacity-60"
          >
            {loading ? "Please wait..." : mode.submit}
          </button>
        </form>
        <button
          onClick={() => {
            setIsLogin((prev) => !prev);
            setError("");
          }}
          className="mt-6 w-full text-center text-sm text-zinc-500 transition hover:text-white"
        >
          {mode.toggle}
        </button>
      </div>
    </div>
  );
}

export default Auth;