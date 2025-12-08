"use client";
import { useEffect, useState } from "react";
import { FolderGit2, Clock, CheckCircle2, ChevronRight } from "lucide-react";
import { clsx } from "clsx";

interface Project {
  thread_id: string;
  status: string;
  phase: string;
  updated_at: string;
}

export default function ProjectSidebar({ currentId, onSelect }: { currentId: string; onSelect: (id: string) => void }) {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    const fetchProjects = async () => {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      try {
        const res = await fetch(`${API_BASE_URL}/agent/projects`);
        if (res.ok) {
          const data = await res.json();
          setProjects(data.projects);
        }
      } catch (e) { console.error("Failed to load projects"); }
    };
    fetchProjects();
  }, []);

  return (
    <div className="w-64 bg-neutral-950 border-r border-neutral-800 flex flex-col h-full font-mono">
      <div className="p-4 border-b border-neutral-800 flex items-center gap-2 text-emerald-500">
        <FolderGit2 className="w-5 h-5" />
        <span className="font-bold tracking-tight">PROJECTS</span>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {projects.map((p) => (
          <button
            key={p.thread_id}
            onClick={() => onSelect(p.thread_id)}
            className={clsx(
              "w-full text-left p-3 rounded-lg border transition-all group",
              p.thread_id === currentId 
                ? "bg-emerald-900/20 border-emerald-500/50 text-emerald-100"
                : "bg-transparent border-transparent hover:bg-neutral-900 text-neutral-400"
            )}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] uppercase tracking-wider opacity-70">{p.phase}</span>
              {p.thread_id === currentId && <CheckCircle2 className="w-3 h-3 text-emerald-500" />}
            </div>
            <div className="text-xs font-medium truncate mb-1">{p.status}</div>
            <div className="flex items-center gap-1 text-[10px] text-neutral-600">
              <Clock className="w-3 h-3" />
              <span>{p.updated_at ? new Date(p.updated_at).toLocaleDateString() : "New"}</span>
            </div>
          </button>
        ))}
      </div>
      <div className="p-4 border-t border-neutral-800">
        <button 
          onClick={() => onSelect(`web-client-${Date.now()}`)}
          className="w-full py-2 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded text-xs text-neutral-300 transition-colors"
        >
          + New Mission
        </button>
      </div>
    </div>
  );
}