"use client";

import React, { useState } from "react";
import { 
  X, Zap, BrainCircuit, AlertCircle, CheckCircle2, Bot, User, Terminal, ArrowRight, Sparkles, HelpCircle, PenLine 
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Incident } from "@/app/data";

interface IncidentModalProps {
  incident: Incident;
  isOpen: boolean;
  onClose: () => void;
  onResolve?: () => void;
}

export function IncidentModal({ incident, isOpen, onClose, onResolve }: IncidentModalProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [customRule, setCustomRule] = useState(""); 
  const [teachStatus, setTeachStatus] = useState<'idle' | 'teaching' | 'resolved'>('idle');

  if (!isOpen) return null;

  const handleTeach = async () => {
    if (!selectedOption) return;
    
    setTeachStatus('teaching');

    let ruleContent = "";
    
    if (selectedOption === "custom") {
        ruleContent = `Custom Rule: ${customRule}`;
    } else {
        const option = incident.teaching_options.find(o => o.id === selectedOption);
        // CRITICAL FIX: Use logic_change (The Instruction) if available, otherwise description
        ruleContent = option?.logic_change || (option ? `${option.title}: ${option.description}` : "General Fix");
    }
    
    const targetAgent = incident.agent_name || "default_agent";
    
    console.log(`🚀 Teaching agent: ${targetAgent} with rule: ${ruleContent}`);

    try {
      const response = await fetch('/api/teach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_name: targetAgent,
          rule_content: ruleContent,
          category: incident.detection_label,
          incident_id: incident.id 
        })
      });

      if (!response.ok) throw new Error("Failed");

      setTimeout(() => {
        setTeachStatus('resolved');
        setTimeout(() => { if (onResolve) onResolve(); }, 1000); 
      }, 500); 

    } catch (e) {
      console.error(e);
      setTeachStatus('idle'); 
    }
  };

  const isFastPath = incident.detection_source === 'FAST_PATH';
  const badgeColor = isFastPath ? "bg-amber-500/10 text-amber-400 border-amber-500/20" : "bg-blue-500/10 text-blue-400 border-blue-500/20";
  const BadgeIcon = isFastPath ? Zap : BrainCircuit;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-zinc-950 border border-zinc-800 w-full max-w-3xl max-h-[90vh] rounded-xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* HEADER */}
        <div className="p-6 border-b border-zinc-800 flex items-start justify-between shrink-0 bg-zinc-950">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className={cn("px-2 py-1 rounded-full border text-xs font-mono font-medium flex items-center gap-1.5", badgeColor)}>
                <BadgeIcon size={12} />
                {incident.detection_label.toUpperCase()}
              </div>
              <span className="text-zinc-500 text-xs font-mono">{new Date(incident.timestamp).toLocaleTimeString()}</span>
              <span className="text-zinc-600 text-xs font-mono px-2 border-l border-zinc-800">AGENT: {incident.agent_name?.toUpperCase()}</span>
            </div>
            <h2 className="text-xl font-semibold text-zinc-100 tracking-tight">{incident.title}</h2>
          </div>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-300 transition-colors"><X size={20} /></button>
        </div>

        {/* CONTENT */}
        <div className="overflow-y-auto flex-1 p-6 space-y-8">
          
          {/* TRACE */}
          <div className="space-y-3">
            <h3 className="text-xs font-mono text-zinc-500 uppercase tracking-wider">Execution Trace</h3>
            <div className="relative border-l-2 border-zinc-800 ml-3 space-y-6 py-2">
              {incident.trace.map((step, idx) => (
                <div key={step.id} className="relative pl-8">
                  <div className={cn("absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 flex items-center justify-center bg-zinc-950", step.type === 'error' ? "border-red-500 text-red-500" : "border-zinc-700 text-zinc-500")}>
                    {step.type === 'error' && <div className="w-1.5 h-1.5 rounded-full bg-red-500" />}
                  </div>
                  <div className={cn("p-3 rounded-lg border text-sm", step.type === 'error' ? "bg-red-950/10 border-red-900/50 text-red-200" : "bg-zinc-900/50 border-zinc-800 text-zinc-300")}>
                    <div className="flex items-center gap-2 mb-1 text-xs font-mono opacity-70">
                      {getStepIcon(step.type)}
                      <span className="uppercase">{step.title}</span>
                    </div>
                    <p className={cn(step.type === 'tool' ? "font-mono text-xs text-amber-200/80 whitespace-pre-wrap" : "")}>{step.content}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* OPTIONS */}
          <div className="space-y-3 pt-4 border-t border-zinc-800/50">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono text-zinc-500 uppercase tracking-wider">Recommended Fixes</h3>
              <span className="text-xs text-zinc-600 flex items-center gap-1"><Sparkles size={12} /> AI Generated</span>
            </div>

            {teachStatus === 'resolved' ? (
              <div className="bg-green-950/20 border border-green-900/50 rounded-lg p-8 flex flex-col items-center justify-center text-center">
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 mb-3"><CheckCircle2 size={24} /></div>
                <h4 className="text-green-400 font-medium">Rule Deployed</h4>
              </div>
            ) : (
              <div className="grid gap-3">
                {incident.teaching_options.map((option) => (
                  <div 
                    key={option.id}
                    onClick={() => setSelectedOption(option.id)}
                    className={cn("group relative p-4 rounded-lg border cursor-pointer transition-all", selectedOption === option.id ? "bg-zinc-900 border-zinc-500 ring-1 ring-zinc-500" : "bg-zinc-900/20 border-zinc-800 hover:border-zinc-700")}
                  >
                    <div className="flex items-center justify-between">
                        <div><h4 className="text-sm font-medium text-zinc-200">{option.title}</h4><p className="text-sm text-zinc-400">{option.description}</p></div>
                        {option.recommended && <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] border border-emerald-500/20">RECOMMENDED</span>}
                    </div>
                  </div>
                ))}
                <div 
                    onClick={() => setSelectedOption("custom")}
                    className={cn("group relative p-4 rounded-lg border cursor-pointer transition-all", selectedOption === "custom" ? "bg-zinc-900 border-zinc-500 ring-1 ring-zinc-500" : "bg-zinc-900/20 border-zinc-800 hover:border-zinc-700")}
                >
                    <div className="flex items-center gap-2 mb-2"><PenLine size={16} className="text-zinc-400"/><h4 className="text-sm font-medium text-zinc-200">Write Custom Rule</h4></div>
                    {selectedOption === "custom" && <textarea className="w-full bg-zinc-950 border border-zinc-700 rounded p-2 text-sm text-white font-mono" rows={3} placeholder="e.g. Always redact emails..." value={customRule} onChange={(e) => setCustomRule(e.target.value)} onClick={(e) => e.stopPropagation()} />}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* FOOTER */}
        {teachStatus !== 'resolved' && (
          <div className="p-4 border-t border-zinc-800 bg-zinc-900/50 flex justify-end gap-3">
            <button onClick={onClose} className="px-4 py-2 text-sm text-zinc-400 hover:text-white">Dismiss</button>
            <button 
              onClick={handleTeach}
              disabled={!selectedOption || (selectedOption === "custom" && !customRule)}
              className="px-4 py-2 bg-white text-black text-sm font-medium rounded hover:bg-zinc-200 disabled:opacity-50 flex items-center gap-2"
            >
              <Zap size={14} className="fill-black" /> Teach Agent
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// Keep existing sub-components (MetricCard, getStepIcon)
function MetricCard({ label, score }: { label: string, score: number }) {
  const isLow = score < 50;
  return (
    <div className={cn(
      "p-3 rounded border flex flex-col items-center justify-center gap-1",
      isLow ? "bg-red-950/10 border-red-900/30" : "bg-zinc-900/30 border-zinc-800"
    )}>
      <span className={cn("text-2xl font-bold font-mono", isLow ? "text-red-400" : "text-emerald-400")}>
        {score}%
      </span>
      <span className="text-[10px] uppercase tracking-wider text-zinc-500">{label}</span>
    </div>
  );
}

function getStepIcon(type: string) {
  switch (type) {
    case 'user': return <User size={12} />;
    case 'agent': return <Bot size={12} />;
    case 'tool': return <Terminal size={12} />;
    case 'error': return <AlertCircle size={12} />;
    default: return <ArrowRight size={12} />;
  }
}