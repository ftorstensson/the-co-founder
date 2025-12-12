"use client";
import { useState, useRef } from "react";
import { Mic, Square, Loader2 } from "lucide-react";
import { clsx } from "clsx";

interface VoiceRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  disabled?: boolean;
}

export default function VoiceRecorder({ onRecordingComplete, disabled }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" }); // Default to webm for Chrome/Firefox
        onRecordingComplete(blob);
        stream.getTracks().forEach((track) => track.stop()); // Turn off mic
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not access microphone. Please allow permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <button
      type="button"
      onClick={isRecording ? stopRecording : startRecording}
      disabled={disabled}
      className={clsx(
        "p-3 rounded-xl transition-all shadow-sm flex items-center justify-center",
        isRecording 
          ? "bg-red-500 text-white animate-pulse hover:bg-red-600" 
          : "bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700",
        disabled && "opacity-50 cursor-not-allowed"
      )}
      title={isRecording ? "Stop Recording" : "Start Voice Note"}
    >
      {isRecording ? <Square className="w-4 h-4 fill-current" /> : <Mic className="w-4 h-4" />}
    </button>
  );
}