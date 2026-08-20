"use client";

import { useRef, useEffect } from "react";
import Editor, { OnMount } from "@monaco-editor/react";

interface EditorPanelProps {
  code?: string;
  onChange?: (val: string) => void;
  activeLine?: number | null;
  readOnly?: boolean;
}

export default function EditorPanel({
  code = "# Write Python code here\nx = 5\ny = 10\nprint(x + y)",
  onChange,
  activeLine = null,
  readOnly = false,
}: EditorPanelProps) {
  const editorRef = useRef<any>(null);
  const decorationsRef = useRef<string[]>([]);

  const handleEditorDidMount: OnMount = (editor) => {
    editorRef.current = editor;
  };

  useEffect(() => {
    if (!editorRef.current) return;

    if (activeLine !== null && activeLine > 0) {
      decorationsRef.current = editorRef.current.deltaDecorations(
        decorationsRef.current,
        [
          {
            range: {
              startLineNumber: activeLine,
              startColumn: 1,
              endLineNumber: activeLine,
              endColumn: 1,
            },
            options: {
              isWholeLine: true,
              className: "bg-yellow-100 dark:bg-yellow-900/30 border-l-4 border-yellow-500",
              glyphMarginClassName: "text-yellow-500 font-bold",
            },
          },
        ]
      );
      editorRef.current.revealLineInCenterIfOutsideViewport(activeLine);
    } else {
      decorationsRef.current = editorRef.current.deltaDecorations(
        decorationsRef.current,
        []
      );
    }
  }, [activeLine]);

  return (
    <div className="flex-1 flex flex-col border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
      <div className="h-10 px-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Code Editor (Monaco)
        </span>
        {activeLine && (
          <span className="text-xs px-2 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-200 font-mono">
            Executing line {activeLine}
          </span>
        )}
      </div>
      <div className="flex-1 relative">
        <Editor
          height="100%"
          defaultLanguage="python"
          theme="vs-dark"
          value={code}
          onChange={(val) => onChange && onChange(val || "")}
          onMount={handleEditorDidMount}
          options={{
            readOnly,
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            lineNumbers: "on",
            glyphMargin: true,
          }}
        />
      </div>
    </div>
  );
}
