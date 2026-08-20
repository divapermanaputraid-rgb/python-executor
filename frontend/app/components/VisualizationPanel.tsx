"use client";

import { useState } from "react";

export interface ValueReprUI {
  type: string;
  repr: string;
  length?: number | null;
  inspectable?: boolean;
}

export interface FrameStateUI {
  frame_id: string;
  function: string;
  scope: string;
  line: number;
  variables: Record<string, ValueReprUI>;
}

export interface ExecutionSnapshotUI {
  status: string;
  current_line: number | null;
  current_frame_id: string | null;
  variables: Record<string, ValueReprUI>;
  call_stack: FrameStateUI[];
  stdout: string;
  stderr: string;
  exception: { type: string; message: string } | null;
}

interface VisualizationPanelProps {
  snapshot?: ExecutionSnapshotUI | null;
}

export default function VisualizationPanel({ snapshot = null }: VisualizationPanelProps) {
  const [activeTab, setActiveTab] = useState<"variables" | "stack" | "output">("variables");

  const variables = snapshot?.variables || {};
  const callStack = snapshot?.call_stack || [];
  const stdout = snapshot?.stdout || "";
  const stderr = snapshot?.stderr || "";
  const exception = snapshot?.exception;

  return (
    <div className="flex-1 flex flex-col border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
      <div className="h-10 px-2 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setActiveTab("variables")}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
              activeTab === "variables"
                ? "bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm"
                : "text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200"
            }`}
          >
            Variables ({Object.keys(variables).length})
          </button>
          <button
            onClick={() => setActiveTab("stack")}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
              activeTab === "stack"
                ? "bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm"
                : "text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200"
            }`}
          >
            Call Stack ({callStack.length})
          </button>
          <button
            onClick={() => setActiveTab("output")}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
              activeTab === "output"
                ? "bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm"
                : "text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200"
            }`}
          >
            Output {stdout && "•"}
          </button>
        </div>
      </div>

      <div className="flex-1 p-4 overflow-auto font-mono text-sm">
        {activeTab === "variables" && (
          <div className="space-y-3">
            {Object.keys(variables).length === 0 ? (
              <div className="text-zinc-400 text-xs italic">No variables in current scope.</div>
            ) : (
              <div className="border border-zinc-200 dark:border-zinc-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-zinc-100 dark:bg-zinc-950 text-zinc-500 uppercase font-semibold">
                    <tr>
                      <th className="px-3 py-2">Name</th>
                      <th className="px-3 py-2">Type</th>
                      <th className="px-3 py-2">Value</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                    {Object.entries(variables).map(([name, val]) => (
                      <tr key={name} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/40">
                        <td className="px-3 py-2 font-bold text-blue-600 dark:text-blue-400">{name}</td>
                        <td className="px-3 py-2 text-zinc-500">{val.type}</td>
                        <td className="px-3 py-2 font-mono text-zinc-900 dark:text-zinc-100">{val.repr}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "stack" && (
          <div className="space-y-2">
            {callStack.length === 0 ? (
              <div className="text-zinc-400 text-xs italic">Call stack empty.</div>
            ) : (
              callStack.slice().reverse().map((frame, i) => (
                <div
                  key={frame.frame_id || i}
                  className="p-3 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-zinc-50 dark:bg-zinc-950 text-xs"
                >
                  <div className="flex items-center justify-between font-bold text-zinc-800 dark:text-zinc-200">
                    <span>{frame.function}()</span>
                    <span className="text-zinc-400 font-normal">Line {frame.line}</span>
                  </div>
                  <div className="text-zinc-500 text-[11px] mt-0.5 uppercase tracking-wide">
                    Scope: {frame.scope}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "output" && (
          <div className="h-full flex flex-col gap-3">
            <div className="flex-1 bg-black text-green-400 p-3 rounded-lg font-mono text-xs overflow-auto whitespace-pre-wrap border border-zinc-800">
              {stdout || <span className="text-zinc-600 italic">Program stdout is empty...</span>}
            </div>

            {exception && (
              <div className="bg-red-950/40 border border-red-800 text-red-300 p-3 rounded-lg text-xs font-mono">
                <div className="font-bold">{exception.type}</div>
                <div>{exception.message}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
