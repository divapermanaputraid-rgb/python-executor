"use client";

interface ExecutionControlsProps {
  onRun?: () => void;
  onStepNext?: () => void;
  onStepPrev?: () => void;
  onReset?: () => void;
  isRunning?: boolean;
  canStepNext?: boolean;
  canStepPrev?: boolean;
  currentStep?: number;
  totalSteps?: number;
}

export default function ExecutionControls({
  onRun,
  onStepNext,
  onStepPrev,
  onReset,
  isRunning = false,
  canStepNext = false,
  canStepPrev = false,
  currentStep = 0,
  totalSteps = 0,
}: ExecutionControlsProps) {
  return (
    <div className="h-12 border-b border-zinc-200 dark:border-zinc-800 px-4 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
      <div className="flex items-center gap-2">
        <button
          onClick={onRun}
          disabled={isRunning}
          className="px-3 py-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-medium text-xs flex items-center gap-1.5 shadow-sm transition"
        >
          <span>▶</span> Run Code
        </button>

        <div className="h-4 w-px bg-zinc-300 dark:bg-zinc-800 mx-1" />

        <button
          onClick={onStepPrev}
          disabled={!canStepPrev}
          className="px-2.5 py-1.5 rounded-md bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-700 disabled:opacity-40 text-xs font-medium text-zinc-700 dark:text-zinc-300 shadow-sm transition"
        >
          ⏮ Step Back
        </button>

        <button
          onClick={onStepNext}
          disabled={!canStepNext}
          className="px-2.5 py-1.5 rounded-md bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white font-medium text-xs shadow-sm transition flex items-center gap-1"
        >
          <span>Step Forward</span> ⏭
        </button>

        <button
          onClick={onReset}
          className="px-2.5 py-1.5 rounded-md bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-700 text-xs font-medium text-zinc-700 dark:text-zinc-300 shadow-sm transition"
        >
          ↺ Reset
        </button>
      </div>

      <div className="flex items-center gap-3 text-xs text-zinc-500 font-mono">
        {totalSteps > 0 ? (
          <span>
            Step <strong className="text-zinc-900 dark:text-zinc-100">{currentStep}</strong> of {totalSteps}
          </span>
        ) : (
          <span>Ready to execute</span>
        )}
      </div>
    </div>
  );
}
