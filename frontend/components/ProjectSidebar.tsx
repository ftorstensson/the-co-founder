"use client";
import { useEffect, useState, useRef } from "react";
import { MessageSquare, Clock, Plus, FolderGit2, MoreVertical, Trash2, Edit2, Pin, PinOff, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { clsx } from "clsx";

interface Project {
  thread_id: string;
  project_name?: string;
  status: string;
  updated_at?: any;
  is_pinned?: boolean;
}

export default function ProjectSidebar({ currentId, onSelect }: { currentId: string, onSelect: (id: string) => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  
  // MENU STATE
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const menuRef = useRef<HTMLDivElement>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // POLLING FETCH (The Robust Fix)
  const fetchProjects = async () => {
    try {
        const res = await fetch(`${API_BASE_URL}/agent/projects`);
        if (res.ok) {
            const data = await res.json();
            const items = data.projects || [];
            // Sort: Pinned First
            items.sort((a: Project, b: Project) => {
                if (a.is_pinned === b.is_pinned) return 0;
                return a.is_pinned ? -1 : 1;
            });
            setProjects(items);
        }
    } catch (e) {
        console.error("Sidebar fetch error:", e);
    } finally {
        setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects(); // Initial fetch
    const interval = setInterval(fetchProjects, 5000); // Poll every 5s for updates
    return () => clearInterval(interval);
  }, []);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpenId(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleNew = () => {
    const newId = "founder-" + Date.now();
    router.push(`?threadId=${newId}`);
  };

  const handleAction = async (e: React.MouseEvent, action: string, project: Project) => {
    e.stopPropagation();
    setMenuOpenId(null);

    if (action === "pin") {
        // Optimistic Update
        setProjects(prev => prev.map(p => p.thread_id === project.thread_id ? {...p, is_pinned: !p.is_pinned} : p));
        await fetch(`${API_BASE_URL}/agent/thread/${project.thread_id}/pin`, { method: "POST" });
        fetchProjects();
    }
    if (action === "delete") {
        if (!confirm("Are you sure you want to delete this session?")) return;
        setProjects(prev => prev.filter(p => p.thread_id !== project.thread_id));
        await fetch(`${API_BASE_URL}/agent/thread/${project.thread_id}`, { method: "DELETE" });
        if (currentId === project.thread_id) router.push("/");
        fetchProjects();
    }
    if (action === "rename") {
        setEditingId(project.thread_id);
        setEditName(project.project_name || "");
    }
  };

  const saveRename = async (e: React.FormEvent, id: string) => {
    e.preventDefault();
    if (!editName.trim()) return;
    setEditingId(null);
    // Optimistic Update
    setProjects(prev => prev.map(p => p.thread_id === id ? {...p, project_name: editName} : p));
    await fetch(`${API_BASE_URL}/agent/thread/${id}/rename`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: editName })
    });
    fetchProjects();
  };

  return (
    <div className="w-64 h-full bg-slate-50 border-r border-slate-200 flex flex-col font-sans">
      <div className="p-4 border-b border-slate-200 bg-white flex items-center gap-2 text-emerald-700">
        <FolderGit2 className="w-5 h-5" />
        <span className="font-bold tracking-tight text-sm">HISTORY</span>
      </div>

      <div className="p-4 border-b border-slate-200">
        <button 
          onClick={handleNew}
          aria-label="New Session"
          className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Session
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {isLoading && projects.length === 0 && (
             <div className="flex justify-center p-4 text-slate-400">
                 <Loader2 className="w-5 h-5 animate-spin" />
             </div>
        )}
        {!isLoading && projects.length === 0 && (
            <div className="text-center text-xs text-slate-400 mt-4 italic">
                No history yet.
            </div>
        )}
        {projects.map((p) => (
          <div key={p.thread_id} className="relative group">
             {editingId === p.thread_id ? (
                 <form onSubmit={(e) => saveRename(e, p.thread_id)} className="p-2">
                     <input 
                        autoFocus
                        aria-label="Rename project"
                        placeholder="Project Name"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onBlur={() => setEditingId(null)}
                        className="w-full text-sm border border-emerald-500 rounded px-2 py-1 outline-none"
                     />
                 </form>
             ) : (
                <button
                    onClick={() => onSelect(p.thread_id)}
                    aria-label={`Select project ${p.project_name || "Untitled"}`}
                    className={clsx(
                    "w-full text-left p-3 rounded-lg text-sm transition-all border group pr-8",
                    currentId === p.thread_id
                        ? "bg-white border-slate-200 text-emerald-900 shadow-sm font-medium ring-1 ring-emerald-500/10"
                        : "border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                    )}
                >
                    <div className="flex items-center gap-2 mb-1">
                    {p.is_pinned ? <Pin className="w-3 h-3 text-emerald-500 fill-emerald-500" /> : 
                     <MessageSquare className={clsx("w-3 h-3", currentId === p.thread_id ? "text-emerald-500" : "text-slate-400")} />}
                    <span className="truncate font-medium flex-1">{p.project_name || "Untitled Session"}</span>
                    </div>
                    {p.updated_at && (
                    <div className="flex items-center gap-1 text-[10px] text-slate-400 pl-5">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(p.updated_at).toLocaleDateString()}</span>
                    </div>
                    )}
                </button>
             )}

             {/* MENU TRIGGER */}
             {!editingId && (
                 <button 
                    onClick={(e) => { e.stopPropagation(); setMenuOpenId(menuOpenId === p.thread_id ? null : p.thread_id); }}
                    aria-label="Project Options"
                    className="absolute right-2 top-3 p-1 rounded hover:bg-slate-200 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity"
                 >
                     <MoreVertical className="w-4 h-4" />
                 </button>
             )}

             {/* DROPDOWN MENU */}
             {menuOpenId === p.thread_id && (
                 <div ref={menuRef} className="absolute right-0 top-8 w-32 bg-white border border-slate-200 shadow-lg rounded-lg z-20 py-1 overflow-hidden">
                     <button onClick={(e) => handleAction(e, "pin", p)} className="w-full text-left px-3 py-2 text-xs hover:bg-slate-50 flex items-center gap-2 text-slate-700">
                         {p.is_pinned ? <PinOff className="w-3 h-3"/> : <Pin className="w-3 h-3"/>}
                         {p.is_pinned ? "Unpin" : "Pin"}
                     </button>
                     <button onClick={(e) => handleAction(e, "rename", p)} className="w-full text-left px-3 py-2 text-xs hover:bg-slate-50 flex items-center gap-2 text-slate-700">
                         <Edit2 className="w-3 h-3"/> Rename
                     </button>
                     <div className="border-t border-slate-100 my-1"></div>
                     <button onClick={(e) => handleAction(e, "delete", p)} className="w-full text-left px-3 py-2 text-xs hover:bg-red-50 flex items-center gap-2 text-red-600">
                         <Trash2 className="w-3 h-3"/> Delete
                     </button>
                 </div>
             )}
          </div>
        ))}
      </div>
    </div>
  );
}