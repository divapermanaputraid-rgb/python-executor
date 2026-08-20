export default function Header() {
  return (
    <header className="h-14 border-b border-zinc-200 dark:border-zinc-800 px-4 flex items-center justify-between bg-white dark:bg-zinc-900">
      <div className="flex items-center gap-3">
        <span className="font-bold text-lg text-zinc-900 dark:text-zinc-100">
          Python Execution Flow Tutor
        </span>
        <span className="text-xs px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 font-medium">
          v0.1.0
        </span>
      </div>
      <div className="flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400">
        <span>Real Runtime Tracing</span>
      </div>
    </header>
  );
}
