"use client";

import { useState } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import EditorPanel from "./components/EditorPanel";
import ExecutionControls from "./components/ExecutionControls";
import VisualizationPanel, { ExecutionSnapshotUI } from "./components/VisualizationPanel";
import TutorPanel, { ChatMessage } from "./components/TutorPanel";
import InputPromptModal from "./components/InputPromptModal";
import { executeCode, executeCodeStream, explainTutorStep, StreamItem } from "./services/api";

export default function Home() {
  const [code, setCode] = useState("# Write Python code here\nx = 5\ny = 10\nprint(x + y)");
  const [activeLine, setActiveLine] = useState<number | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  const [snapshots, setSnapshots] = useState<ExecutionSnapshotUI[]>([]);
  const [currentSnapshot, setCurrentSnapshot] = useState<ExecutionSnapshotUI | null>(null);

  // Tutor chat state
  const [tutorMessages, setTutorMessages] = useState<ChatMessage[]>([]);
  const [suggestedQuestion, setSuggestedQuestion] = useState("");
  const [tutorLoading, setTutorLoading] = useState(false);

  // Input prompting state
  const [inputRequired, setInputRequired] = useState(false);
  const [inputPrompt, setInputPrompt] = useState("");
  const [submittedInputs, setSubmittedInputs] = useState<string[]>([]);

  const fetchTutorExplanation = async (snap: ExecutionSnapshotUI | null, userQ?: string) => {
    setTutorLoading(true);
    try {
      const res = await explainTutorStep(code, [], snap, userQ);
      if (userQ) {
        setTutorMessages((prev) => [
          ...prev,
          { sender: "student", text: userQ },
          { sender: "tutor", text: res.tutor_response },
        ]);
      } else {
        setTutorMessages((prev) => [
          ...prev,
          { sender: "tutor", text: res.tutor_response },
        ]);
      }
      setSuggestedQuestion(res.suggested_question);
    } catch {
      // fallback
    } finally {
      setTutorLoading(false);
    }
  };

  const runExecution = async (inputs: string[] = []) => {
    setIsRunning(true);
    setSnapshots([]);
    setCurrentStep(0);
    setTotalSteps(0);
    setActiveLine(null);
    setCurrentSnapshot(null);
    setTutorMessages([]);

    try {
      const items: StreamItem[] = [];
      await executeCodeStream(code, inputs, (item) => {
        items.push(item);
      });

      const collectedSnapshots = items.map((it) => it.snapshot);
      setSnapshots(collectedSnapshots);
      setTotalSteps(collectedSnapshots.length);

      if (collectedSnapshots.length > 0) {
        const firstSnap = collectedSnapshots[0];
        setCurrentStep(1);
        setCurrentSnapshot(firstSnap);
        setActiveLine(firstSnap.current_line);
        fetchTutorExplanation(firstSnap);
      }

      const lastEvent = items[items.length - 1]?.event;
      if (lastEvent?.type === "input_requested") {
        setInputPrompt(lastEvent.prompt || "Enter input: ");
        setInputRequired(true);
      }
    } catch {
      try {
        const res = await executeCode(code, inputs);
        const snaps: ExecutionSnapshotUI[] = res.snapshots;
        setSnapshots(snaps);
        setTotalSteps(snaps.length);

        if (snaps.length > 0) {
          setCurrentStep(1);
          setCurrentSnapshot(snaps[0]);
          setActiveLine(snaps[0].current_line);
          fetchTutorExplanation(snaps[0]);
        }
      } catch (err: any) {
        console.error("Execution API Error:", err);
      }
    } finally {
      setIsRunning(false);
    }
  };

  const handleRun = () => {
    setSubmittedInputs([]);
    runExecution([]);
  };

  const handleInputSubmit = (val: string) => {
    const nextInputs = [...submittedInputs, val];
    setSubmittedInputs(nextInputs);
    setInputRequired(false);
    runExecution(nextInputs);
  };

  const handleStepNext = () => {
    if (currentStep < totalSteps && snapshots.length >= currentStep) {
      const nextStep = currentStep + 1;
      const nextSnap = snapshots[nextStep - 1];
      setCurrentStep(nextStep);
      setCurrentSnapshot(nextSnap);
      setActiveLine(nextSnap?.current_line ?? null);
      fetchTutorExplanation(nextSnap);
    }
  };

  const handleStepPrev = () => {
    if (currentStep > 1) {
      const prevStep = currentStep - 1;
      const prevSnap = snapshots[prevStep - 1];
      setCurrentStep(prevStep);
      setCurrentSnapshot(prevSnap);
      setActiveLine(prevSnap?.current_line ?? null);
      fetchTutorExplanation(prevSnap);
    }
  };

  const handleSendTutorMessage = (msg: string) => {
    fetchTutorExplanation(currentSnapshot, msg);
  };

  const handleReset = () => {
    setSnapshots([]);
    setCurrentStep(0);
    setTotalSteps(0);
    setActiveLine(null);
    setCurrentSnapshot(null);
    setTutorMessages([]);
    setSuggestedQuestion("");
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
          <TutorPanel
            messages={tutorMessages}
            onSendMessage={handleSendTutorMessage}
            suggestedQuestion={suggestedQuestion}
            isLoading={tutorLoading}
          />
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
