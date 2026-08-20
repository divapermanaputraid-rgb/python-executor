import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import EditorPanel from "./components/EditorPanel";
import VisualizationPanel from "./components/VisualizationPanel";
import TutorPanel from "./components/TutorPanel";

export default function Home() {
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-zinc-100 dark:bg-zinc-950">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex overflow-hidden">
          <EditorPanel />
          <VisualizationPanel />
          <TutorPanel />
        </main>
      </div>
    </div>
  );
}
