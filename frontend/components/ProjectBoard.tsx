"use client";
import { useEffect, useState } from "react";
import { Download, Layout, FileText, CheckCircle2, Circle, Clock } from "lucide-react";

interface ProjectBoardProps {
  threadId: string;
  title?: string;
}

export default function ProjectBoard({ threadId, title = "KNOWLEDGE BASE" }: ProjectBoardProps) {
  const [data, setData] = useState<any>(null);
  
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // ROBUST FETCHING (Replaces direct Firestore)
  const fetchBoard = async () => {
    if (!threadId) return;
    try {
        const res = await fetch(`${API_BASE_URL}/agent/projects/${threadId}`);
        if (res.ok) {
            const json = await res.json();
            // Only update if data actually exists (avoid clearing on glitch)
            if (json && Object.keys(json).length > 0) {
                setData(json);
            }
        }
    } catch (e) {
        console.error("Board fetch error:", e);
    }
  };

  useEffect(() => {
    fetchBoard();
    const interval = setInterval(fetchBoard, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, [threadId]);

  const handleDownload = () => {
    // Placeholder for future download logic
    alert("Download feature coming soon!");
  };

  if (!data) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-4 p-8 text-center">
        <Layout className="w-12 h-12 opacity-20" />
        <p className="text-sm">Waiting for The Co-Founder to initialize the Knowledge Base...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-50">
      {/* HEADER */}
      <div className="p-4 border-b border-slate-200 bg-white flex justify-between items-center shadow-sm">
        <h2 className="font-bold text-sm tracking-wider text-slate-800 flex items-center gap-2">
          <FileText className="w-4 h-4 text-emerald-600" />
          {title}
        </h2>
        <button 
          onClick={handleDownload}
          title="Download All Files"
          className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-emerald-600 transition-colors"
        >
          <Download className="w-4 h-4" />
        </button>
      </div>

      {/* CONTENT SCROLL AREA */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        
        {/* SECTION: VISION */}
        {data.vision && (
            <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Vision & Strategy</h3>
                <div className="prose prose-sm prose-slate max-w-none text-slate-700 leading-relaxed whitespace-pre-wrap">
                    {data.vision}
                </div>
            </div>
        )}

        {/* SECTION: TASKS / ROADMAP */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
             <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Roadmap</h3>
             <span className="text-xs bg-white px-2 py-1 rounded border border-slate-200 text-slate-500 font-mono">
                {data.tasks?.filter((t: any) => t.status === "done").length || 0} / {data.tasks?.length || 0}
             </span>
          </div>
          
          <div className="divide-y divide-slate-100">
            {data.tasks && data.tasks.length > 0 ? (
              data.tasks.map((task: any, i: number) => (
                <div key={i} className="p-3 flex items-start gap-3 hover:bg-slate-50 transition-colors group">
                  <div className="mt-0.5 shrink-0">
                    {task.status === "done" ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    ) : task.status === "in_progress" ? (
                      <Clock className="w-4 h-4 text-amber-500 animate-pulse" />
                    ) : (
                      <Circle className="w-4 h-4 text-slate-300 group-hover:text-slate-400" />
                    )}
                  </div>
                  <span className={`text-sm ${task.status === "done" ? "text-slate-400 line-through decoration-slate-300" : "text-slate-700"}`}>
                    {task.title || task.description}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-slate-400 text-xs italic">
                No active roadmap items yet.
              </div>
            )}
          </div>
        </div>

        {/* SECTION: FILES (Placeholder for now) */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-3 bg-slate-50 border-b border-slate-200">
             <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Artifacts</h3>
            </div>
            <div className="p-4 text-center text-slate-400 text-xs italic">
                The Vault is empty.
            </div>
        </div>
      </div>
    </div>
  );
}