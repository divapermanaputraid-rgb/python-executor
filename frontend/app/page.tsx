"use client";

import { useState } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import EditorPanel from "./components/EditorPanel";
import ExecutionControls from "./components/ExecutionControls";
import VisualizationPanel, { ExecutionSnapshotUI } from "./components/VisualizationPanel";
import TutorPanel from "./components/TutorPanel";
import InputPromptModal from "./components/InputPromptModal";

export default function Home() {
  const [code, setCode] = useState("# Write Python code here\nname = input('Enter name: ')\nprint(f'Hello {name}')");
  const [activeLine, setActiveLine] = useState<number | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [currentSnapshot, setCurrentSnapshot] = useState<ExecutionSnapshotUI | null>(null);

  // Input prompting state
  const [inputRequired, setInputRequired] = useState(false);
  const [inputPrompt, setInputPrompt] = useState("");
  const [submittedInputs, setSubmittedInputs] = useState<string[]>([]);

  const demoSnapshots: ExecutionSnapshotUI[] = [
    {
      status: "WAITING_FOR_INPUT",
      current_line: 2,
      current_frame_id: "f1",
      variables: {},
      call_stack: [
        { frame_id: "f1", function: "<module>", scope: "global", line: 2, variables: {} },
      ],
      stdout: "",
      stderr: "",
      exception: null,
    },
    {
      status: "COMPLETED",
      current_line: 3,
      current_frame_id: "f1",
      variables: { name: { type: "str", repr: "'Alice'" } },
      call_stack: [
        {
          frame_id: "f1",
          function: "<module>",
          scope: "global",
          line: 3,
          variables: { name: { type: "str", repr: "'Alice'" } },
        },
      ],
      stdout: "Hello Alice\n",
      stderr: "",
      exception: null,
    },
  ];

  const handleRun = () => {
    setIsRunning(true);
    setCurrentStep(1);
    setTotalSteps(2);
    setActiveLine(2);
    setCurrentSnapshot(demoSnapshots[0]);

    if (code.includes("input(")) {
      setInputPrompt("Enter name: ");
      setInputRequired(true);
    }
    setIsRunning(false);
  };

  const handleInputSubmit = (val: string) => {
    setSubmittedInputs((prev) => [...prev, val]);
    setInputRequired(false);
    // Advance to step 2 after receiving input
    setCurrentStep(2);
    setActiveLine(3);
    setCurrentSnapshot({
      ...demoSnapshots[1],
      variables: { name: { type: "str", repr: `'${val}'` } },
      stdout: `Hello ${val}\n`,
    });
  };

  const handleStepNext = () => {
    if (currentStep < totalSteps) {
      const next = currentStep + 1;
      setCurrentStep(next);
      setActiveLine(next === 2 ? 3 : 4);
      setCurrentSnapshot(demoSnapshots[next - 1]);
    }
  };

  const handleStepPrev = () => {
    if (currentStep > 1) {
      const prev = currentStep - 1;
      setCurrentStep(prev);
      setActiveLine(prev === 1 ? 2 : 3);
      setCurrentSnapshot(demoSnapshots[prev - 1]);
    }
  };

  const handleReset = () => {
    setCurrentStep(0);
    setTotalSteps(0);
    setActiveLine(null);
    setCurrentSnapshot(null);
    setInputRequired(false);
    setSubmittedInputs([]);
    setIsRunning(false);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-zinc-100 dark:bg-zinc-950">
      <Header />
      <ExecutionControls
        onRun={handleRun}
        onStepNext={handleStepNext}
        onStepPrev={handleStepPrev}
        onReset={handleReset}
        isRunning={isRunning}
        canStepNext={currentStep < totalSteps && totalSteps > 0 && !inputRequired}
        canStepPrev={currentStep > 1}
        currentStep={currentStep}
        totalSteps={totalSteps}
      />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex overflow-hidden">
          <EditorPanel
            code={code}
            onChange={setCode}
            activeLine={activeLine}
          />
          <VisualizationPanel snapshot={currentSnapshot} />
          <TutorPanel />
        </main>
      </div>

      {inputRequired && (
        <InputPromptModal
          promptText={inputPrompt}
          onSubmit={handleInputSubmit}
        />
      )}
    </div>
  );
}
