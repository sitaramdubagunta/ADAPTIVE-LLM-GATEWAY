import { useNavigate } from "react-router-dom";

const models = ["GPT-OSS 120B", "Gemini 2.5 Pro", "Qwen 3", "Compound", "Whisper"];

function Sidebar() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/auth");
  }

  return (
    <aside className="hidden h-screen w-72 flex-col border-r border-zinc-900 bg-[#090909] p-6 lg:flex">
      <div>
        <h1 className="text-2xl font-semibold text-white">LLM Gateway</h1>
        <p className="mt-2 text-sm text-zinc-500">Adaptive AI Router</p>
      </div>

      <div className="mt-10">
        <p className="mb-4 text-xs uppercase tracking-widest text-zinc-500">Available Models</p>
        <div className="space-y-2">
          {models.map((model) => (
            <div key={model} className="rounded-lg border border-zinc-800 bg-[#111] px-4 py-3 text-sm text-zinc-300">
              {model}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-auto space-y-4">
        <button
          onClick={handleLogout}
          className="w-full rounded-xl border border-red-900 py-3 text-red-400 transition hover:bg-red-950/40"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;