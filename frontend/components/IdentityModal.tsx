"use client";
import { useState, useEffect } from "react";
import { X, Save, User, Loader2 } from "lucide-react";

interface IdentityModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function IdentityModal({ isOpen, onClose }: IdentityModalProps) {
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      fetch(`${API_BASE_URL}/agent/profile`)
        .then((res) => res.json())
        .then((data) => setContent(data.content || ""))
        .catch((e) => console.error("Profile Load Error:", e))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetch(`${API_BASE_URL}/agent/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      onClose();
    } catch (e) {
      console.error("Profile Save Error:", e);
      alert("Failed to save profile.");
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        {/* HEADER */}
        <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <div className="flex items-center gap-2 text-slate-800 font-semibold">
            <User className="w-5 h-5 text-emerald-600" />
            <span>Identity & Truth</span>
          </div>
          <button 
            onClick={onClose} 
            className="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-500"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* BODY */}
        <div className="flex-1 p-4 overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-slate-500">
                This is the raw context the Co-Founder uses to understand you. 
                Edit this to update your bio, preferences, and "Golden Rules."
              </p>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full h-64 p-4 text-sm font-mono text-slate-700 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 resize-none leading-relaxed"
                placeholder="# User Profile\n\nName: ...\nRole: ...\n\n## Rules\n- Never use jargon.\n- Prefer bullet points."
              />
            </div>
          )}
        </div>

        {/* FOOTER */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-end">
          <button
            onClick={handleSave}
            disabled={isSaving || isLoading}
            className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-medium transition-all shadow-sm active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {isSaving ? "Saving..." : "Save Truth"}
          </button>
        </div>
      </div>
    </div>
  );
}