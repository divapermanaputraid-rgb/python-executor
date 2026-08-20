export default function TutorPanel() {
  return (
    <div className="w-80 flex flex-col bg-white dark:bg-zinc-900">
      <div className="h-10 px-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
          AI Tutor
        </span>
      </div>
      <div className="flex-1 p-4 flex items-center justify-center text-zinc-400 text-sm">
        Socratic AI Tutor Chat
      </div>
    </div>
  );
}
