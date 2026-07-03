import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

export const markdownComponents = {
  code({ inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || "");

    return !inline && match ? (
      <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" className="my-4 rounded-lg" {...props}>
        {String(children).replace(/\n$/, "")}
      </SyntaxHighlighter>
    ) : (
      <code className="rounded bg-zinc-800 px-1.5 py-0.5 font-mono text-sm text-zinc-100" {...props}>
        {children}
      </code>
    );
  },
  table: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-lg border border-zinc-800">
      <table className="w-full border-collapse text-left text-sm text-zinc-300">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="border-b border-zinc-800 bg-zinc-900 font-semibold text-white">{children}</thead>,
  th: ({ children }) => <th className="p-3">{children}</th>,
  td: ({ children }) => <td className="border-t border-zinc-800 p-3">{children}</td>,
  h1: ({ children }) => <h1 className="mb-2 mt-6 text-2xl font-bold text-white">{children}</h1>,
  h2: ({ children }) => <h2 className="mb-2 mt-5 text-xl font-semibold text-white">{children}</h2>,
  h3: ({ children }) => <h3 className="mb-2 mt-4 text-lg font-medium text-white">{children}</h3>,
  p: ({ children }) => <p className="mb-4 last:mb-0 text-zinc-300">{children}</p>,
  ul: ({ children }) => <ul className="mb-4 list-disc space-y-1 pl-5 text-zinc-300">{children}</ul>,
  ol: ({ children }) => <ol className="mb-4 list-decimal space-y-1 pl-5 text-zinc-300">{children}</ol>,
};

export function updateAssistantMessage(setMessages, assistantId, updater, activeChatId, messageCache) {
  setMessages((prev) => {
    const next = prev.map((msg) => (msg.id === assistantId ? updater(msg) : msg));
    if (activeChatId && messageCache) {
      messageCache[activeChatId] = next;
    }
    return next;
  });
}