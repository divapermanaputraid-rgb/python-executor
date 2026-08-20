export default function Sidebar() {
  return (
    <aside className="w-16 border-r border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 flex flex-col items-center py-4 gap-6">
      <button
        title="Code Editor"
        className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-500 text-white font-medium shadow"
      >
        Code
      </button>
      <button
        title="Settings"
        className="w-10 h-10 rounded-lg flex items-center justify-center text-zinc-600 dark:text-zinc-400 hover:bg-zinc-200 dark:hover:bg-zinc-800"
      >
        ⚙️
      </button>
    </aside>
  );
}
