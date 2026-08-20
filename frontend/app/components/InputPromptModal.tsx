"use client";

import { useState } from "react";

interface InputPromptModalProps {
  promptText?: string;
  onSubmit: (val: string) => void;
}

export default function InputPromptModal({ promptText = "Input requested by Python program:", onSubmit }: InputPromptModalProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(value);
    setValue("");
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
        <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 uppercase tracking-wide mb-2">
          Interactive Input Required
        </h3>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4 font-mono bg-zinc-100 dark:bg-zinc-950 p-2 rounded border border-zinc-200 dark:border-zinc-800">
          {promptText}
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            type="text"
            autoFocus
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Type value and press Enter..."
            className="w-full px-3 py-2 text-sm border border-zinc-300 dark:border-zinc-700 rounded-lg bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              type="submit"
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm"
            >
              Submit Input
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
