import { useNavigate } from "react-router-dom";

const models = ["GPT-OSS 120B", "Gemini 2.5 Pro", "Qwen 3", "Compound", "Whisper"];

function Sidebar({ activeChatId, setActiveChatId, chats, refreshChats }) {
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

      <button
        onClick={() => setActiveChatId(null)}
        className="mt-6 w-full rounded-xl bg-white py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
      >
        + New Chat
      </button>

      <div className="mt-8 flex-1 overflow-y-auto min-h-0">
        <p className="mb-4 text-xs uppercase tracking-widest text-zinc-500">Conversations</p>
        {chats.length === 0 ? (
          <p className="text-sm text-zinc-600 italic">No chats yet.</p>
        ) : (
          <div className="space-y-1.5 pr-2">
            {chats.map((chat) => {
              const isActive = chat.id === activeChatId;
              return (
                <button
                  key={chat.id}
                  onClick={() => setActiveChatId(chat.id)}
                  className={`w-full text-left rounded-xl px-4 py-3 text-sm transition break-words ${
                    isActive
                      ? "bg-zinc-800 text-white font-medium border border-zinc-700"
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
                  }`}
                >
                  {chat.title || `Chat #${chat.id}`}
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="mt-6 pt-6 border-t border-zinc-900">
        <p className="mb-3 text-xs uppercase tracking-widest text-zinc-500">Available Models</p>
        <div className="flex flex-wrap gap-1.5">
          {models.slice(0, 4).map((model) => (
            <span key={model} className="rounded px-2 py-1 text-[10px] border border-zinc-800 bg-zinc-900 text-zinc-400">
              {model}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-6 space-y-4">
        <button
          onClick={handleLogout}
          className="w-full rounded-xl border border-red-950 py-3 text-red-400 transition hover:bg-red-950/20 text-sm"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;