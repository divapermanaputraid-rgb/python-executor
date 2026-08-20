export default function VisualizationPanel() {
  return (
    <div className="flex-1 flex flex-col border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
      <div className="h-10 px-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Execution Visualizer
        </span>
      </div>
      <div className="flex-1 p-4 flex items-center justify-center text-zinc-400 text-sm">
        Visualization Panel (Variables, Call Stack, Line Flow)
      </div>
    </div>
  );
}
