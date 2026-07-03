import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import PromptBox from "./PromptBox";
import { markdownComponents, updateAssistantMessage } from "./chatWindowUtils.jsx";
import { getChatMessages } from "../api";

const API = "http://localhost:8000";

// In-memory frontend cache for chat messages
const messageCache = {};

function ChatWindow({ activeChatId, setActiveChatId, refreshChats }) {
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null);
  const lastCreatedChatIdRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (activeChatId === null) {
      setMessages([]);
    } else {
      if (messageCache[activeChatId]) {
        setMessages(messageCache[activeChatId]);
        return;
      }

      if (lastCreatedChatIdRef.current === activeChatId) {
        lastCreatedChatIdRef.current = null;
        return;
      }

      setMessages([]);
      getChatMessages(activeChatId)
        .then((data) => {
          const mapped = data.map((msg) => {
            if (msg.role === "assistant" && msg.metadata) {
              return {
                ...msg,
                metadata: {
                  ...msg.metadata,
                  latency: msg.metadata.latency_ms,
                },
              };
            }
            return msg;
          });
          messageCache[activeChatId] = mapped;
          setMessages(mapped);
        })
        .catch((err) => {
          console.error("Failed to load chat messages:", err);
          setMessages([
            { id: Date.now(), role: "assistant", content: "Failed to load chat history.", metadata: null }
          ]);
        });
    }
  }, [activeChatId]);

  async function sendMessage(prompt) {
    const assistantId = Date.now();

    setMessages((prev) => {
      const next = [
        ...prev,
        { id: assistantId - 1, role: "user", content: prompt },
        { id: assistantId, role: "assistant", content: "", metadata: null },
      ];
      if (activeChatId) {
        messageCache[activeChatId] = next;
      }
      return next;
    });

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API}/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: prompt, chat_id: activeChatId }),
      });

      if (!response.ok) throw new Error("Request failed");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let hasUpdatedChats = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() || "";

        for (const event of events) {
          if (!event.startsWith("data:")) continue;

          const raw = event.slice(5).trim();
          if (raw === "[DONE]") {
            if (!activeChatId) {
              refreshChats();
            }
            return;
          }

          let data;

          try {
            data = JSON.parse(raw);
          } catch {
            continue;
          }

          if (data.type === "token") {
            updateAssistantMessage(setMessages, assistantId, (msg) => ({
              ...msg,
              content: msg.content + data.content,
            }), activeChatId, messageCache);
          } else if (data.type === "meta") {
            const currentChatId = activeChatId || data.chat_id;
            updateAssistantMessage(setMessages, assistantId, (msg) => ({
              ...msg,
              metadata: {
                provider: data.provider,
                model: data.model,
                latency: data.latency_ms,
              },
            }), currentChatId, messageCache);

            if (data.chat_id) {
              lastCreatedChatIdRef.current = data.chat_id;
              setActiveChatId(data.chat_id);
              
              setMessages((prev) => {
                messageCache[data.chat_id] = prev;
                return prev;
              });

              if (!hasUpdatedChats) {
                hasUpdatedChats = true;
                refreshChats();
              }
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      updateAssistantMessage(setMessages, assistantId, (msg) => ({
        ...msg,
        content: "Something went wrong.",
      }), activeChatId, messageCache);
    }
  }



  return (
    <main className="flex h-screen flex-1 flex-col bg-black">
      <div className="flex-1 overflow-x-hidden overflow-y-auto px-8 py-8 pb-40">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center">
            <h1 className="text-5xl font-semibold text-white">Adaptive LLM Gateway</h1>
            <p className="mt-4 text-zinc-500">Ask anything.</p>
          </div>
        ) : (
          <div className="mx-auto w-full max-w-3xl space-y-8">
            {messages.map((msg) => {
              const isUser = msg.role === "user";
              const bubbleClass = isUser
                ? "bg-white text-black whitespace-pre-wrap"
                : "border border-zinc-800 bg-[#111] text-zinc-200 prose prose-invert max-w-none";

              return (
                <div key={msg.id} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                  <div className="max-w-[85%]">
                    <div className={`break-words overflow-x-auto rounded-2xl px-5 py-4 leading-7 ${bubbleClass}`}>
                      {msg.content.length === 0 ? (
                        <span className="animate-pulse text-zinc-500">Thinking...</span>
                      ) : isUser ? (
                        msg.content
                      ) : (
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>

                    {msg.role === "assistant" && msg.metadata && (
                      <div className="mt-3 flex flex-wrap gap-2 text-xs text-zinc-500">
                        <span className="rounded-full border border-zinc-800 px-3 py-1">{msg.metadata.provider}</span>
                        <span className="rounded-full border border-zinc-800 px-3 py-1">{msg.metadata.model}</span>
                        <span className="rounded-full border border-zinc-800 px-3 py-1">{msg.metadata.latency} ms</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
      <PromptBox onSend={sendMessage} />
    </main>
  );
}

export default ChatWindow;