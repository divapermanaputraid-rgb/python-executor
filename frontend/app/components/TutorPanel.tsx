"use client";

import { useState } from "react";
import { ExecutionSnapshotUI } from "../services/api";

export interface ChatMessage {
  sender: "tutor" | "student";
  text: string;
}

interface TutorPanelProps {
  messages?: ChatMessage[];
  onSendMessage?: (msg: string) => void;
  suggestedQuestion?: string;
  isLoading?: boolean;
}

export default function TutorPanel({
  messages = [],
  onSendMessage,
  suggestedQuestion,
  isLoading = false,
}: TutorPanelProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    if (onSendMessage) onSendMessage(input);
    setInput("");
  };

  return (
    <div className="w-80 flex flex-col border-l border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
      <div className="h-10 px-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Socratic AI Tutor
        </span>
        {isLoading && (
          <span className="text-[10px] text-blue-500 animate-pulse font-mono">Thinking...</span>
        )}
      </div>

      <div className="flex-1 p-3 overflow-auto space-y-3 font-sans text-xs">
        {messages.length === 0 ? (
          <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-800 dark:text-blue-200 border border-blue-200 dark:border-blue-900 leading-relaxed">
            👋 <strong>Welcome!</strong> Run code or step through execution. I will ask Socratic questions to help you understand Python execution flow step-by-step.
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`p-2.5 rounded-lg max-w-[90%] leading-relaxed ${
                msg.sender === "tutor"
                  ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 self-start"
                  : "bg-blue-600 text-white self-end ml-auto"
              }`}
            >
              {msg.text}
            </div>
          ))
        )}
      </div>

      {suggestedQuestion && (
        <div className="p-2 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950">
          <button
            onClick={() => onSendMessage && onSendMessage(suggestedQuestion)}
            className="w-full text-left p-1.5 rounded text-[11px] bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 hover:border-blue-400 text-blue-600 dark:text-blue-400 font-medium truncate"
          >
            💡 Hint: {suggestedQuestion}
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="p-2 border-t border-zinc-200 dark:border-zinc-800 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask or explain your answer..."
          className="flex-1 px-2.5 py-1.5 text-xs rounded border border-zinc-300 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 outline-none focus:ring-1 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-3 py-1.5 text-xs font-semibold rounded bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm"
        >
          Send
        </button>
      </form>
    </div>
  );
}
