"use client";
import { useState, useEffect } from "react";
import { clsx } from "clsx";
import { 
  Menu, User, Plus, Mic, Send, X, 
  Layout, ToggleLeft, ToggleRight,
  Smartphone, Grid, Maximize2, ArrowLeft, MoreHorizontal, QrCode
} from "lucide-react";

// --- MOCK DATA ---
const MOCK_PROJECTS = [
  { id: "1", name: "Pizza Drone", date: "11/12/2025", status: "active" },
  { id: "2", name: "The Co-Founder", date: "13/12/2025", status: "active" },
  { id: "3", name: "Umami Cookbook", date: "12/12/2025", status: "pinned" },
];

export default function DesignLab() {
  const [viewMode, setViewMode] = useState<"grid" | "focus">("grid");
  const [activeScreen, setActiveScreen] = useState<"lobby" | "chat" | "drawer">("lobby");
  const [isWireframe, setIsWireframe] = useState(true);
  const [showQR, setShowQR] = useState(false);
  const [currentUrl, setCurrentUrl] = useState("");

  // Get current URL for QR code
  useEffect(() => {
    if (typeof window !== "undefined") {
      setCurrentUrl(window.location.href.replace("/design-lab", ""));
    }
  }, []);

  // --- STYLES ---
  const wf = isWireframe ? "grayscale contrast-125 font-mono border-2 border-black shadow-none rounded-none" : "";
  const wfText = isWireframe ? "font-mono" : "font-sans";
  const wfBg = isWireframe ? "bg-white" : "bg-slate-50";

  // --- MOCK SCREENS (Miniaturized for Grid, Full for Focus) ---
  
  const ScreenLobby = ({ mini = false }) => (
    <div className={clsx("flex flex-col h-full bg-white relative overflow-hidden", mini ? "pointer-events-none" : "")}>
      {/* Header */}
      <div className={clsx("flex justify-between items-center p-4 border-b", isWireframe ? "border-black" : "border-slate-100")}>
        <Menu className="w-5 h-5" />
        <div className="w-8 h-8 rounded-full border flex items-center justify-center"><User className="w-4 h-4"/></div>
      </div>
      {/* Body */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-6">
        <div>
            <h2 className={clsx("text-2xl font-bold", wfText)}>Hey Boss</h2>
            <p className="text-xs opacity-50">Time to build.</p>
        </div>
        <div className="w-full space-y-3">
            <div className={clsx("w-full py-3 border rounded-lg font-bold text-sm", isWireframe ? "border-black" : "border-slate-200 shadow-sm")}>Brainstorm</div>
            <div className={clsx("w-full py-3 border rounded-lg font-bold text-sm", isWireframe ? "border-black" : "border-slate-200 shadow-sm")}>Keep Building</div>
        </div>
      </div>
    </div>
  );

  const ScreenDrawer = ({ mini = false }) => (
    <div className={clsx("flex h-full bg-slate-500/20 relative", mini ? "pointer-events-none" : "")}>
      <div className={clsx("w-[85%] h-full bg-white border-r flex flex-col", isWireframe ? "border-black" : "border-slate-200")}>
        <div className="p-4 border-b flex justify-between items-center">
            <span className={clsx("font-bold", wfText)}>Projects</span>
            <X className="w-5 h-5" />
        </div>
        <div className="p-2 space-y-2">
            {MOCK_PROJECTS.map(p => (
                <div key={p.id} className={clsx("p-3 border rounded-lg flex items-center gap-3", isWireframe ? "border-black" : "bg-white border-slate-100")}>
                    <div className="w-2 h-2 bg-black rounded-full" />
                    <div className="flex-1 min-w-0">
                        <div className="text-xs font-bold truncate">{p.name}</div>
                        <div className="text-[9px] opacity-50">{p.date}</div>
                    </div>
                    {/* THE LEDGER REQUIREMENT: Context Menu */}
                    <MoreHorizontal className="w-4 h-4 opacity-50" />
                </div>
            ))}
        </div>
      </div>
    </div>
  );

  const ScreenChat = ({ mini = false }) => (
    <div className={clsx("flex flex-col h-full bg-white relative overflow-hidden", mini ? "pointer-events-none" : "")}>
       <div className={clsx("flex justify-between items-center p-4 border-b", isWireframe ? "border-black" : "border-slate-100")}>
        <div className="flex items-center gap-2">
            <Menu className="w-5 h-5" />
            <span className="font-bold text-sm">The Co-Founder</span>
        </div>
        <User className="w-5 h-5" />
      </div>
      <div className="flex-1 p-4 space-y-4">
        <div className="flex gap-2">
            <div className="w-6 h-6 rounded-full border flex items-center justify-center shrink-0"><Layout className="w-3 h-3"/></div>
            <div className={clsx("p-3 border rounded-xl text-xs", isWireframe ? "border-black" : "bg-slate-50 border-slate-100")}>
                Context loaded. Ready to build.
            </div>
        </div>
      </div>
      <div className="p-3 border-t">
        <div className={clsx("flex items-center gap-2 p-2 border rounded-full", isWireframe ? "border-black" : "border-slate-200")}>
            <Plus className="w-4 h-4" />
            <div className="flex-1 h-4 bg-transparent text-xs opacity-50">Type or speak...</div>
            <Mic className="w-4 h-4" />
            <Send className="w-4 h-4" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      
      {/* LAB NAVIGATION HEADER */}
      <div className="fixed top-0 left-0 right-0 h-16 bg-slate-900 text-white flex items-center justify-between px-4 z-50 shadow-md">
        <div className="flex items-center gap-4">
            <span className="font-bold tracking-wider text-emerald-400">VIBE LAB</span>
            <div className="h-6 w-px bg-slate-700" />
            {viewMode === "focus" && (
                <button onClick={() => setViewMode("grid")} className="flex items-center gap-2 text-xs hover:text-white text-slate-400">
                    <ArrowLeft className="w-4 h-4" /> Back to Grid
                </button>
            )}
        </div>
        <div className="flex items-center gap-3">
            <button 
                onClick={() => setShowQR(!showQR)}
                className={clsx("p-2 rounded hover:bg-slate-800 transition-colors", showQR && "bg-slate-800 text-emerald-400")}
                title="Mobile Test QR"
                aria-label="Show QR Code"
            >
                <QrCode className="w-5 h-5" />
            </button>
            <button 
                onClick={() => setIsWireframe(!isWireframe)}
                className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-full text-xs font-medium border border-slate-700"
                aria-label="Toggle Wireframe Mode"
            >
                {isWireframe ? <ToggleRight className="w-4 h-4 text-emerald-400" /> : <ToggleLeft className="w-4 h-4 text-slate-500" />}
                {isWireframe ? "Wireframe" : "Hi-Fi"}
            </button>
        </div>
      </div>

      {/* QR CODE OVERLAY */}
      {showQR && (
        <div className="fixed top-20 right-4 p-4 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 flex flex-col items-center animate-in fade-in slide-in-from-top-2">
            {/* Using a privacy-friendly QR API (no cookies) */}
            <img 
                src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(currentUrl.replace("localhost", "192.168.1.XX"))}`} 
                alt="Scan to test on mobile" 
                className="w-32 h-32 mb-2"
            />
            <p className="text-[10px] text-slate-500 text-center max-w-[150px]">
                Scan with phone to test<br/>(Ensure phone is on same WiFi)
            </p>
            <p className="text-[10px] text-slate-400 mt-2">Current: {currentUrl}</p>
        </div>
      )}

      {/* MAIN CONTENT AREA */}
      <div className="pt-24 pb-12 px-4 md:px-8 max-w-7xl mx-auto">
        
        {/* VIEW: GRID (THE CANVA BOARD) */}
        {viewMode === "grid" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {/* Lobby Card */}
                <div className="group cursor-pointer" onClick={() => { setActiveScreen("lobby"); setViewMode("focus"); }}>
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="font-bold text-slate-700">01. The Lobby</h3>
                        <Maximize2 className="w-4 h-4 opacity-0 group-hover:opacity-50" />
                    </div>
                    <div className={clsx("aspect-[9/19] border-4 rounded-3xl overflow-hidden shadow-sm transition-all group-hover:shadow-xl group-hover:border-emerald-500/50", isWireframe ? "border-slate-800" : "border-slate-200 bg-black")}>
                        <div className={clsx("w-full h-full", wf)}><ScreenLobby mini /></div>
                    </div>
                </div>

                {/* Drawer Card */}
                <div className="group cursor-pointer" onClick={() => { setActiveScreen("drawer"); setViewMode("focus"); }}>
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="font-bold text-slate-700">02. Project List</h3>
                        <Maximize2 className="w-4 h-4 opacity-0 group-hover:opacity-50" />
                    </div>
                    <div className={clsx("aspect-[9/19] border-4 rounded-3xl overflow-hidden shadow-sm transition-all group-hover:shadow-xl group-hover:border-emerald-500/50", isWireframe ? "border-slate-800" : "border-slate-200 bg-black")}>
                        <div className={clsx("w-full h-full", wf)}><ScreenDrawer mini /></div>
                    </div>
                </div>

                {/* Chat Card */}
                <div className="group cursor-pointer" onClick={() => { setActiveScreen("chat"); setViewMode("focus"); }}>
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="font-bold text-slate-700">03. Active Chat</h3>
                        <Maximize2 className="w-4 h-4 opacity-0 group-hover:opacity-50" />
                    </div>
                    <div className={clsx("aspect-[9/19] border-4 rounded-3xl overflow-hidden shadow-sm transition-all group-hover:shadow-xl group-hover:border-emerald-500/50", isWireframe ? "border-slate-800" : "border-slate-200 bg-black")}>
                        <div className={clsx("w-full h-full", wf)}><ScreenChat mini /></div>
                    </div>
                </div>
            </div>
        )}

        {/* VIEW: FOCUS (THE PLAYABLE PROTOTYPE) */}
        {viewMode === "focus" && (
            <div className="flex justify-center h-[calc(100vh-8rem)]">
                <div className={clsx("aspect-[9/19] h-full border-8 rounded-[3rem] overflow-hidden shadow-2xl relative", isWireframe ? "border-slate-800 bg-white" : "border-slate-900 bg-slate-900")}>
                    {/* Status Bar Mock */}
                    <div className="absolute top-0 left-0 right-0 h-6 bg-black/10 z-50 flex justify-center">
                        <div className="w-24 h-4 bg-black rounded-b-xl" />
                    </div>
                    
                    {/* Screen Content */}
                    <div className={clsx("w-full h-full pt-6 bg-white", wf)}>
                        {activeScreen === "lobby" && <ScreenLobby />}
                        {activeScreen === "drawer" && <ScreenDrawer />}
                        {activeScreen === "chat" && <ScreenChat />}
                    </div>

                    {/* Nav Hints (Lab Only) */}
                    <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-2 pointer-events-none opacity-0 hover:opacity-100 transition-opacity">
                        <div className="px-3 py-1 bg-black/75 text-white text-xs rounded-full">
                            Tap Header to Open Drawer
                        </div>
                    </div>
                </div>
            </div>
        )}

      </div>
    </div>
  );
}