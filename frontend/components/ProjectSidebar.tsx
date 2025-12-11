"use client";
import { useEffect, useState } from "react";
import { collection, query, orderBy, limit, onSnapshot } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { MessageSquare, Clock, Plus, FolderGit2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { clsx } from "clsx";

interface Project {
  thread_id: string;
  status: string;
  updated_at?: any;
}

export default function ProjectSidebar({ currentId, onSelect }: { currentId: string, onSelect: (id: string) => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const router = useRouter();

  useEffect(() => {
    // Queries the isolated 'cofounder_boards' collection
    const q = query(collection(db, "cofounder_boards"), orderBy("updated_at", "desc"), limit(20));
    
    const unsub = onSnapshot(q, (snapshot) => {
      const items: Project[] = [];
      snapshot.forEach((doc) => {
        items.push({ thread_id: doc.id, ...doc.data() } as Project);
      });
      setProjects(items);
    });
    return () => unsub();
  }, []);

  const handleNew = () => {
    const newId = "founder-" + Date.now();
    router.push(`?threadId=${newId}`);
  };

  return (
    <div className="w-64 h-full bg-slate-50 border-r border-slate-200 flex flex-col font-sans">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-white flex items-center gap-2 text-emerald-700">
        <FolderGit2 className="w-5 h-5" />
        <span className="font-bold tracking-tight text-sm">HISTORY</span>
      </div>

      {/* New Session Button */}
      <div className="p-4 border-b border-slate-200">
        <button 
          onClick={handleNew}
          className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Session
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {projects.length === 0 && (
            <div className="text-center text-xs text-slate-400 mt-4 italic">
                No history yet.
            </div>
        )}
        {projects.map((p) => (
          <button
            key={p.thread_id}
            onClick={() => onSelect(p.thread_id)}
            className={clsx(
              "w-full text-left p-3 rounded-lg text-sm transition-all border group",
              currentId === p.thread_id
                ? "bg-white border-slate-200 text-emerald-900 shadow-sm font-medium ring-1 ring-emerald-500/10"
                : "border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            )}
          >
            <div className="flex items-center gap-2 mb-1">
              <MessageSquare className={clsx("w-3 h-3", currentId === p.thread_id ? "text-emerald-500" : "text-slate-400")} />
              <span className="truncate">{p.thread_id.slice(-8)}</span>
            </div>
            {p.updated_at && (
              <div className="flex items-center gap-1 text-[10px] text-slate-400 pl-5">
                <Clock className="w-3 h-3" />
                <span>{new Date(p.updated_at.seconds * 1000).toLocaleDateString()}</span>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}