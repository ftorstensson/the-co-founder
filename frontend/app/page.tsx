"use client";
import { useState, useRef, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Send, Loader2, User, Bot, Brain, Menu } from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import ProjectBoard from "../components/ProjectBoard"; // Keeping for logic, but might hide in V2
import ProjectSidebar from "../components/ProjectSidebar"; // Keeping for logic
import VoiceRecorder from "../components/VoiceRecorder";
import IdentityModal from "../components/IdentityModal";

function cn(...inputs: (string | undefined | null | false)[]) { return twMerge(clsx(inputs)); }
interface Message { role: "user" | "assistant"; content: string; }

function AgentInterface() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string>("");
  
  // UI STATES
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Mobile Drawer Logic

  useEffect(() => {
    const idFromUrl = searchParams.get("threadId");
    if (idFromUrl) {
      setThreadId(idFromUrl);
      fetchHistory(idFromUrl);
    } else {
      const newId = "founder-" + Date.now();
      setThreadId(newId);
      router.replace(`?threadId=${newId}`);
      setMessages([]);
    }
  }, [searchParams, router]);

  const fetchHistory = async (id: string) => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const res = await fetch(`${API_BASE_URL}/agent/history/${id}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages);
      }
    } catch (e) { console.error("Failed to load history", e); }
  };

  const switchThread = (id: string) => {
    setThreadId(id);
    router.push(`?threadId=${id}`);
    setIsSidebarOpen(false); // Close drawer on mobile select
  };

  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => { 
    e.preventDefault(); 
    if (!input.trim() || isLoading) return; 
    const userMessage = input.trim(); 
    setInput(""); 
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]); 
    setIsLoading(true);
    
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const response = await fetch(`${API_BASE_URL}/agent/invoke`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ 
            input: { messages: [{ type: "human", content: userMessage }] }, 
            config: { configurable: { thread_id: threadId } } 
        }) 
      });
      if (!response.ok) throw new Error("Network response");
      const data = await response.json();
      const lastMessage = data.output.messages[data.output.messages.length - 1];
      setMessages((prev) => [...prev, { role: "assistant", content: lastMessage.content }]);
    } catch (error) { 
      console.error("Error:", error); 
      setMessages((prev) => [...prev, { role: "assistant", content: "Error: Failed to connect." }]); 
    } finally { 
      setIsLoading(false); 
    }
  };

  const handleVoiceUpload = async (audioBlob: Blob) => {
    setIsLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: "[🎤 Audio Message Sent]" }]);
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");
    formData.append("thread_id", threadId);
    try {
        const response = await fetch(`${API_BASE_URL}/agent/voice`, { method: "POST", body: formData });
        if (!response.ok) throw new Error("Voice upload failed");
        const data = await response.json();
        const lastMessage = data.output.messages[data.output.messages.length - 1];
        setMessages((prev) => [...prev, { role: "assistant", content: lastMessage.content }]);
    } catch (error) { setMessages((prev) => [...prev, { role: "assistant", content: "Error: Voice processing failed." }]); } 
    finally { setIsLoading(false); }
  };

  if (!threadId) return null;

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">
      
      {/* IDENTITY MODAL (The Truth Layer) */}
      <IdentityModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />

      {/* MOBILE DRAWER OVERLAY */}
      {isSidebarOpen && (
        <div className="fixed inset-0 bg-slate-900/20 z-40 lg:hidden" onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* SIDEBAR (Responsive) */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-slate-200 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <ProjectSidebar currentId={threadId} onSelect={switchThread} />
      </div>

      {/* MAIN CONTENT (Mobile First Center Stage) */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-50 relative">
        
        {/* HEADER */}
        <header className="flex items-center justify-between p-4 bg-white border-b border-slate-200 shadow-sm z-10">
          <div className="flex items-center gap-3">
            <button 
                onClick={() => setIsSidebarOpen(true)}
                className="lg:hidden p-2 -ml-2 text-slate-500 hover:bg-slate-100 rounded-lg"
                aria-label="Open Sidebar"
            >
                <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center">
                    <Brain className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                    <h1 className="text-sm font-bold text-slate-900 leading-none">THE CO-FOUNDER</h1>
                    <span className="text-[10px] text-slate-400 font-medium tracking-wide">AUTO-PILOT ACTIVE</span>
                </div>
            </div>
          </div>
          
          {/* AVATAR BUTTON */}
          <button 
            onClick={() => setIsProfileOpen(true)}
            className="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-emerald-50 hover:text-emerald-600 hover:border-emerald-200 transition-all"
            aria-label="Identity Settings"
          >
            <User className="w-5 h-5" />
          </button>
        </header>

        {/* CHAT AREA (Centered & Constrained) */}
        <main className="flex-1 overflow-y-auto p-4">
          <div className="max-w-2xl mx-auto space-y-6">
            {messages.length === 0 && (
                <div className="text-center py-20 opacity-50">
                    <p className="text-sm text-slate-400">Start a new brain dump...</p>
                </div>
            )}
            
            {messages.map((msg, i) => (
                <div key={i} className={cn("flex items-start gap-3", msg.role === "user" ? "flex-row-reverse" : "flex-row")}>
                <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                    msg.role === "user" ? "bg-slate-200 border-slate-300" : "bg-emerald-100 border-emerald-200"
                )}>
                    {msg.role === "user" ? <User className="w-4 h-4 text-slate-500" /> : <Bot className="w-4 h-4 text-emerald-600" />}
                </div>
                <div className={cn(
                    "p-4 rounded-2xl text-sm leading-relaxed shadow-sm max-w-[85%]", 
                    msg.role === "user" ? "bg-white text-slate-800 rounded-tr-none border border-slate-200" : "bg-white text-slate-700 rounded-tl-none border border-emerald-100"
                )}>
                    {msg.content}
                </div>
                </div>
            ))}
            {isLoading && <div className="text-center text-xs text-slate-400 animate-pulse">Thinking...</div>}
            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* INPUT AREA (Centered) */}
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="max-w-2xl mx-auto flex gap-2">
            <VoiceRecorder onRecordingComplete={handleVoiceUpload} disabled={isLoading} />
            <form onSubmit={handleSubmit} className="flex-1 flex gap-2">
                <input 
                    value={input} 
                    onChange={(e) => setInput(e.target.value)} 
                    placeholder="Type or speak..." 
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all text-slate-900 text-sm" 
                    disabled={isLoading} 
                />
                <button 
                    type="submit" 
                    disabled={isLoading || !input.trim()} 
                    className="px-4 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-sm"
                    aria-label="Send Message"
                >
                    <Send className="w-4 h-4" />
                </button>
            </form>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL (Hidden on Mobile, Visible Desktop) */}
      <div className="hidden xl:block w-[400px] border-l border-slate-200 bg-white">
        <ProjectBoard threadId={threadId} title="KNOWLEDGE BASE" />
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="bg-slate-50 h-screen w-screen" />}>
      <AgentInterface />
    </Suspense>
  );
}