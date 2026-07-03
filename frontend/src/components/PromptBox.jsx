import { useState } from "react";

function PromptBox({ onSend }) {
  const [prompt, setPrompt] = useState("");

  function handleSend() {
    const value = prompt.trim();

    if (!value) return;

    onSend(value);
    setPrompt("");
  }

  return (
    <div className="border-t border-zinc-900 bg-black p-6">
      <div className="mx-auto flex max-w-4xl items-center rounded-2xl border border-zinc-800 bg-[#0B0B0B] px-4 py-3">
        <textarea
          rows={1}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Message LLM Gateway..."
          className="flex-1 resize-none bg-transparent text-white outline-none placeholder:text-zinc-500"
        />

        <button
          onClick={handleSend}
          className="ml-3 rounded-full bg-white px-5 py-2 text-black transition hover:bg-zinc-300"
        >
          ↑
        </button>
      </div>
    </div>
  );
}

export default PromptBox;