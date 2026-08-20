export default function EditorPanel() {
  return (
    <div className="flex-1 flex flex-col border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
      <div className="h-10 px-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Code Editor
        </span>
      </div>
      <div className="flex-1 p-4 font-mono text-sm">
        <textarea
          className="w-full h-full p-2 border border-zinc-200 dark:border-zinc-800 rounded bg-zinc-50 dark:bg-zinc-950 resize-none outline-none font-mono"
          defaultValue={`# Write Python code here\nx = 5\ny = 10\nprint(x + y)`}
        />
      </div>
    </div>
  );
}
