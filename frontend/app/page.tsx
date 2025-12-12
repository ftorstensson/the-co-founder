"use client";
import { useState, useRef, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Send, Loader2, User, Bot, Brain } from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import ProjectBoard from "../components/ProjectBoard";
import ProjectSidebar from "../components/ProjectSidebar";
import VoiceRecorder from "../components/VoiceRecorder";

function cn(...inputs: (string | undefined | null | false)[]) { return twMerge(clsx(inputs)); }
interface Message { role: "user" | "assistant"; content: string; }

function AgentInterface() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string>("");

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
        const response = await fetch(`${API_BASE_URL}/agent/voice`, {
            method: "POST",
            body: formData,
        });
        if (!response.ok) throw new Error("Voice upload failed");
        const data = await response.json();
        const lastMessage = data.output.messages[data.output.messages.length - 1];
        setMessages((prev) => [...prev, { role: "assistant", content: lastMessage.content }]);
    } catch (error) {
        console.error("Voice Error:", error);
        setMessages((prev) => [...prev, { role: "assistant", content: "Error: Voice processing failed." }]);
    } finally {
        setIsLoading(false);
    }
  };

  if (!threadId) return null;

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">
      <div className="hidden md:block border-r border-slate-200 bg-white">
        <ProjectSidebar currentId={threadId} onSelect={switchThread} />
      </div>

      <div className="flex-1 flex flex-col min-w-0 border-r border-slate-200 bg-slate-50">
        <header className="flex items-center justify-between p-4 border-b border-slate-200 bg-white shadow-sm z-10">
          <div className="flex items-center">
            <Brain className="w-5 h-5 mr-3 text-emerald-600" />
            <h1 className="text-lg font-bold tracking-tight text-slate-900">THE CO-FOUNDER <span className="text-slate-400 font-normal">CONSOLE</span></h1>
          </div>
          <div className="text-xs text-slate-400 flex items-center gap-2">
            {isLoading && <Loader2 className="w-3 h-3 animate-spin" />}
            {isLoading ? "Scribe Thinking..." : "Auto-Pilot Active"}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 opacity-80">
              <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center mb-4 border border-slate-200">
                <Brain className="w-8 h-8 text-emerald-600" />
              </div>
              <p className="font-medium text-slate-600">Knowledge Engine Ready</p>
              <p className="text-xs text-slate-400 mt-1">Session: {threadId.slice(-6)}</p>
            </div>
          )}
          
          {messages.map((msg, i) => (
            <div key={i} className={cn("flex items-start max-w-2xl gap-3", msg.role === "user" ? "ml-auto justify-end" : "mr-auto justify-start")}>
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center border border-slate-200 shadow-sm shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-emerald-600" />
                </div>
              )}
              <div className={cn("p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm", msg.role === "user" ? "bg-emerald-600 text-white rounded-tr-sm" : "bg-white border border-slate-200 text-slate-700 rounded-tl-sm")}>{msg.content}</div>
              {msg.role === "user" && (<div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center border border-slate-300 shrink-0 mt-1"><User className="w-4 h-4 text-slate-500" /></div>)}
            </div>
          ))}
          {isLoading && (<div className="flex items-center gap-2 p-4 text-slate-400"><Loader2 className="w-4 h-4 animate-spin" /><span className="text-xs uppercase font-semibold tracking-wider">Thinking...</span></div>)}
          <div ref={messagesEndRef} />
        </main>

        <div className="p-4 border-t border-slate-200 bg-white">
          <div className="flex gap-2 relative">
            <VoiceRecorder onRecordingComplete={handleVoiceUpload} disabled={isLoading} />
            <form onSubmit={handleSubmit} className="flex-1 flex gap-2">
                <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Dump your thoughts here..." className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all text-slate-900 placeholder:text-slate-400" disabled={isLoading} />
                <button type="submit" aria-label="Send" disabled={isLoading || !input.trim()} className="px-4 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 disabled:opacity-50 disabled:hover:bg-emerald-600 transition-colors shadow-sm"><Send className="w-4 h-4" /></button>
            </form>
          </div>
        </div>
      </div>
      <div className="w-[400px] hidden lg:block border-l border-slate-200 bg-white">
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