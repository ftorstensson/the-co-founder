"use client";
import { useState } from "react";
import { clsx } from "clsx";
import { Layout, Mic, User, ToggleLeft, ToggleRight } from "lucide-react";
import VoiceRecorder from "../../components/VoiceRecorder";
import IdentityModal from "../../components/IdentityModal";
import ProjectSidebar from "../../components/ProjectSidebar";

export default function DesignLab() {
  const [isWireframe, setIsWireframe] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeSidebar, setActiveSidebar] = useState("demo-1");

  // Wireframe CSS Injector
  const wireframeClass = isWireframe ? "grayscale contrast-125 font-mono border-2 border-black" : "";

  return (
    <div className={clsx("min-h-screen bg-slate-50 p-8 font-sans", isWireframe && "font-mono bg-white")}>
      
      {/* HEADER / CONTROLS */}
      <div className="fixed top-0 left-0 right-0 bg-white border-b border-slate-200 p-4 z-50 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-2">
          <div className="bg-purple-600 text-white p-2 rounded-lg font-bold">LAB</div>
          <h1 className="font-bold text-slate-800">The Vibe Design System</h1>
        </div>
        
        <button 
          onClick={() => setIsWireframe(!isWireframe)}
          className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors text-sm font-medium"
          aria-label={isWireframe ? "Disable Wireframe Mode" : "Enable Wireframe Mode"}
        >
          {isWireframe ? <ToggleRight className="w-5 h-5 text-purple-600" /> : <ToggleLeft className="w-5 h-5 text-slate-400" />}
          {isWireframe ? "WIREFRAME MODE: ON" : "VIBE MODE: ON"}
        </button>
      </div>

      <div className="mt-20 max-w-5xl mx-auto space-y-12">
        
        {/* SECTION: ATOMS */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-slate-400 uppercase tracking-widest border-b pb-2">01. Atoms (Input / Output)</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* CARD: Voice Recorder */}
            <div className={clsx("p-6 bg-white rounded-xl shadow-sm border border-slate-100", wireframeClass)}>
              <h3 className="text-sm font-semibold mb-4 text-slate-500">Voice Recorder</h3>
              <div className="flex justify-center">
                <VoiceRecorder onRecordingComplete={(blob) => alert(`Recorded ${blob.size} bytes`)} />
              </div>
              <p className="text-xs text-center mt-4 text-slate-400">States: Idle / Recording (Pulse) / Disabled</p>
            </div>

            {/* CARD: Buttons */}
            <div className={clsx("p-6 bg-white rounded-xl shadow-sm border border-slate-100 space-y-2", wireframeClass)}>
              <h3 className="text-sm font-semibold mb-4 text-slate-500">Buttons</h3>
              <button className="w-full px-4 py-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700">Primary Action</button>
              <button className="w-full px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50">Secondary Action</button>
              <button disabled className="w-full px-4 py-2 bg-slate-100 text-slate-400 rounded-xl cursor-not-allowed">Disabled</button>
            </div>

          </div>
        </section>

        {/* SECTION: MOLECULES */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-slate-400 uppercase tracking-widest border-b pb-2">02. Molecules (Modals & Cards)</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* CARD: Identity Modal Trigger */}
            <div className={clsx("p-6 bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col items-center justify-center h-64", wireframeClass)}>
              <h3 className="text-sm font-semibold mb-4 text-slate-500">Identity Editor</h3>
              <button 
                onClick={() => setIsModalOpen(true)}
                className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-emerald-50 hover:text-emerald-600 hover:border-emerald-200 transition-all"
                aria-label="Open Identity Modal"
              >
                <User className="w-8 h-8" />
              </button>
              <p className="text-xs mt-4 text-slate-400">Click to test Modal functionality</p>
            </div>

            {/* CARD: Chat Bubble Spec */}
            <div className={clsx("p-6 bg-white rounded-xl shadow-sm border border-slate-100 space-y-4", wireframeClass)}>
              <h3 className="text-sm font-semibold mb-2 text-slate-500">Message Bubbles</h3>
              
              {/* User Bubble */}
              <div className="flex flex-row-reverse items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-slate-500" />
                </div>
                <div className="bg-white text-slate-800 rounded-2xl rounded-tr-none border border-slate-200 p-4 text-sm shadow-sm">
                    This is a user message. It aligns right.
                </div>
              </div>

              {/* AI Bubble */}
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-100 border border-emerald-200 flex items-center justify-center shrink-0">
                    <Mic className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="bg-white text-slate-700 rounded-2xl rounded-tl-none border border-emerald-100 p-4 text-sm shadow-sm">
                    This is an AI response. It aligns left and uses the primary accent color for the border.
                </div>
              </div>

            </div>
          </div>
        </section>

        {/* SECTION: ORGANISMS */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-slate-400 uppercase tracking-widest border-b pb-2">03. Organisms (Complex Structures)</h2>
          
          <div className={clsx("h-[500px] border border-slate-200 rounded-xl overflow-hidden flex relative", wireframeClass)}>
             {/* Note: In a real lab, we'd mock the data props for Sidebar */}
             <div className="w-64 h-full border-r border-slate-200 bg-white">
                <div className="p-4 text-xs text-slate-400 text-center uppercase tracking-widest">Sidebar Component Area</div>
                {/* We can't easily render ProjectSidebar here without mocking the API context, 
                    so we placeholder it for V1 of the Lab */}
                <div className="p-4 space-y-2 opacity-50">
                    <div className="h-8 bg-slate-100 rounded w-full"></div>
                    <div className="h-8 bg-slate-100 rounded w-full"></div>
                    <div className="h-8 bg-slate-100 rounded w-full"></div>
                </div>
             </div>
             <div className="flex-1 bg-slate-50 flex items-center justify-center">
                <p className="text-slate-400 text-sm">Main Content Area</p>
             </div>
          </div>
        </section>

      </div>

      {/* MODAL MOUNT */}
      <IdentityModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}