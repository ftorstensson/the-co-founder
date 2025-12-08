"use client";
import { useEffect, useState } from "react";
import { LayoutDashboard, Circle, Download, Loader2 } from "lucide-react";
import { doc, onSnapshot } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function ProjectBoard({ threadId }: { threadId: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { if (!threadId) return; const unsub = onSnapshot(doc(db, "project_boards", threadId), (doc) => { if (doc.exists()) setData(doc.data()); else setData(null); setLoading(false); }); return () => unsub(); }, [threadId]);

  const handleDownload = () => { const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; window.open(`${API_BASE_URL}/agent/download/${threadId}`, "_blank"); };

  if (loading) return <div className="h-full flex items-center justify-center text-neutral-600"><Loader2 className="w-6 h-6 animate-spin" /></div>;

  const phase = data?.phase || "Discovery";
  const status = data?.status || "Waiting for mission brief...";
  const tasks = data?.tasks || [];

  return (
    <div className="h-full flex flex-col bg-neutral-900/50 border-l border-neutral-800 font-mono">
      <div className="p-4 border-b border-neutral-800 flex items-center justify-between">
        <div className="flex items-center gap-2 text-purple-400">
          <LayoutDashboard className="w-4 h-4" />
          <h2 className="font-bold tracking-tight text-sm">PROJECT BOARD</h2>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={handleDownload} className="text-xs flex items-center gap-1 text-emerald-400 hover:text-emerald-300 transition-colors border border-emerald-500/30 px-2 py-1 rounded bg-emerald-500/10"><Download className="w-3 h-3" /> Download</button>
          <div className="text-[10px] text-neutral-600">ID: {threadId.slice(-6)}</div>
        </div>
      </div>
      <div className="p-4 space-y-6 overflow-y-auto flex-1">
        <div className="bg-neutral-950 border border-neutral-800 rounded p-3">
          <div className="text-[10px] text-neutral-500 uppercase tracking-wider mb-1">Current Status</div>
          <div className="text-sm text-purple-300 animate-pulse">{status}</div>
        </div>
        <div className="space-y-2">
          <div className="text-[10px] text-neutral-500 uppercase tracking-wider">Phase</div>
          <div className="inline-block px-2 py-1 rounded text-xs font-bold border border-blue-500/30 bg-blue-500/10 text-blue-400">{phase}</div>
        </div>
        <div className="space-y-2">
          <div className="text-[10px] text-neutral-500 uppercase tracking-wider flex justify-between"><span>Tasks</span><span>{tasks.length}</span></div>
          {tasks.length === 0 ? (<div className="text-sm text-neutral-600 italic border border-dashed border-neutral-800 p-2 rounded text-center">No active tasks.</div>) : (tasks.map((task: string, i: number) => (<div key={i} className="flex items-start gap-3 p-2 bg-neutral-950/30 rounded border border-neutral-800/30"><Circle className="w-3 h-3 mt-1 text-purple-500/50" /><span className="text-xs text-neutral-300">{task}</span></div>)))}
        </div>
      </div>
    </div>
  );
}