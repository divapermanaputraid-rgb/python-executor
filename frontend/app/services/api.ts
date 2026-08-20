export interface ValueReprUI {
  type: string;
  repr: string;
  length?: number | null;
  inspectable?: boolean;
}

export interface FrameStateUI {
  frame_id: string;
  function: string;
  scope: string;
  line: number;
  variables: Record<string, ValueReprUI>;
}

export interface ExecutionSnapshotUI {
  status: string;
  current_line: number | null;
  current_frame_id: string | null;
  variables: Record<string, ValueReprUI>;
  call_stack: FrameStateUI[];
  stdout: string;
  stderr: string;
  exception: { type: string; message: string } | null;
}

export interface StreamItem {
  event: Record<string, any>;
  snapshot: ExecutionSnapshotUI;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function executeCode(code: string, inputs?: string[]) {
  const res = await fetch(`${API_BASE_URL}/api/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, inputs }),
  });

  if (!res.ok) {
    throw new Error(`Execution failed: ${res.statusText}`);
  }

  return res.json();
}

export async function executeCodeStream(
  code: string,
  inputs: string[],
  onItem: (item: StreamItem) => void
) {
  const res = await fetch(`${API_BASE_URL}/api/execute/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, inputs }),
  });

  if (!res.ok || !res.body) {
    throw new Error(`Stream failed: ${res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const block of lines) {
      const trimmed = block.trim();
      if (trimmed.startsWith("data: ")) {
        const jsonStr = trimmed.replace("data: ", "");
        if (jsonStr === "[DONE]") break;

        try {
          const item: StreamItem = JSON.parse(jsonStr);
          onItem(item);
        } catch {
          // ignore malformed lines
        }
      }
    }
  }
}
