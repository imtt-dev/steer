"use client";

import React, { useState, useEffect } from "react";
import { 
  LayoutDashboard, Activity, Settings, Search, Bell, ChevronRight, Zap, BrainCircuit, Loader2, BookOpen, ShieldCheck, CheckCircle2
} from "lucide-react";
import { cn } from "@/lib/utils";
import { IncidentModal } from "@/components/IncidentModal";
import { Incident } from "@/app/data"; 

export default function Dashboard() {
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [activeTab, setActiveTab] = useState<'incidents' | 'runs' | 'rules'>('incidents');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [rules, setRules] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const incRes = await fetch('/api/incidents');
        const incData = await incRes.json();
        if (incData.incidents) {
          setIncidents(prev => {
            return incData.incidents.map((newInc: Incident) => {
              const existing = prev.find(p => p.id === newInc.id);
              return existing ? { ...newInc, status: existing.status } : newInc;
            });
          });
        }
        const rulesRes = await fetch('/api/rules');
        const rulesData = await rulesRes.json();
        if (rulesData.rules) setRules(rulesData.rules);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleIncidentResolved = (id: string) => {
    setIncidents(current => current.map(inc => inc.id === id ? { ...inc, status: 'Resolved' } : inc));
    setSelectedIncident(null); 
  };

  return (
    <div className="flex h-screen bg-black text-zinc-200 font-sans selection:bg-zinc-800">
      <aside className="w-64 border-r border-zinc-800 flex flex-col bg-zinc-950/50">
        <div className="p-6 border-b border-zinc-800/50">
          <div className="flex items-center gap-2 text-white mb-1">
            <div className="w-5 h-5 bg-white rounded-sm"></div><span className="font-bold tracking-tight">Steer</span>
          </div>
          <p className="text-xs text-zinc-500 font-mono">Mission Control v0.1</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          <NavItem icon={<Activity size={18} />} label="Incidents" active={activeTab === 'incidents'} onClick={() => setActiveTab('incidents')} count={incidents.filter(i => i.status === 'Active').length} />
          <NavItem icon={<LayoutDashboard size={18} />} label="Runs History" active={activeTab === 'runs'} onClick={() => setActiveTab('runs')} />
          <NavItem icon={<BookOpen size={18} />} label="Rules Registry" active={activeTab === 'rules'} onClick={() => setActiveTab('rules')} />
        </nav>
        <div className="p-4 border-t border-zinc-800/50">
           <div className="flex items-center gap-3"><div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center text-xs font-medium">JD</div><div className="text-xs"><div className="text-white font-medium">Jane Doe</div><div className="text-zinc-500">Engineering</div></div></div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden bg-black">
        <header className="h-16 border-b border-zinc-800 flex items-center justify-between px-8 bg-zinc-950/30">
            <h1 className="text-lg font-semibold text-white capitalize">{activeTab.replace('-', ' ')}</h1>
            <div className="flex items-center gap-4"><button className="text-zinc-400 hover:text-white"><Bell size={18} /></button></div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          {activeTab === 'incidents' && (
            <div className="max-w-5xl mx-auto space-y-4">
              {incidents.filter(i => i.status === 'Active').length === 0 && (
                <div className="text-center py-20 text-zinc-500 border border-dashed border-zinc-800 rounded-lg">
                  <CheckCircle2 size={48} className="opacity-20 mb-4 mx-auto text-green-500" /><p className="font-medium text-zinc-400">All Systems Nominal</p><p className="text-sm mt-1">No active incidents detected.</p>
                </div>
              )}
              {incidents.filter(i => i.status === 'Active').map((incident) => (
                <IncidentCard key={incident.id} incident={incident} onClick={() => setSelectedIncident(incident)} />
              ))}
            </div>
          )}

          {activeTab === 'runs' && (
            <div className="max-w-6xl mx-auto">
                <div className="border border-zinc-800 rounded-lg overflow-hidden">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-zinc-900/50 text-zinc-500 font-medium">
                            <tr>
                                <th className="px-6 py-3 w-24">Status</th>
                                <th className="px-6 py-3 w-32">Time</th>
                                <th className="px-6 py-3 w-32">Agent</th>
                                {/* FIX: ALLOW WRAPPING ON INPUT */}
                                <th className="px-6 py-3 w-64">Input</th>
                                <th className="px-6 py-3">Result / Error</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800 bg-zinc-950">
                            {incidents.map((run) => {
                                const isError = run.trace.some(t => t.type === 'error');
                                const errorStep = run.trace.find(t => t.type === 'error');
                                const outputStep = run.trace.find(t => t.type === 'success');
                                return (
                                    <tr key={run.id} className="hover:bg-zinc-900/30 transition-colors">
                                        <td className="px-6 py-4 align-top">
                                            {isError ? <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-950/30 text-red-400 border border-red-900/50">BLOCKED</span> : <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-950/30 text-green-400 border border-green-900/50">PASSED</span>}
                                        </td>
                                        <td className="px-6 py-4 font-mono text-zinc-500 text-xs align-top">{new Date(run.timestamp).toLocaleTimeString()}</td>
                                        <td className="px-6 py-4 font-medium text-zinc-300 align-top">{run.agent_name}</td>
                                        
                                        {/* FIX: INPUT COLUMN WRAPS NOW */}
                                        <td className="px-6 py-4 text-zinc-400 max-w-xs whitespace-pre-wrap break-words align-top">
                                            {run.trace.find(t => t.type === 'user')?.content || "-"}
                                        </td>
                                        
                                        <td className="px-6 py-4 font-mono text-xs max-w-lg break-words whitespace-pre-wrap align-top">
                                            {isError ? <span className="text-red-400 block">{errorStep?.content?.replace("❌ ", "") || "Unknown Error"}</span> : <span className="text-emerald-400 block">{outputStep?.content || "Success"}</span>}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
          )}

          {activeTab === 'rules' && (
             <div className="max-w-5xl mx-auto space-y-8">
                {Object.entries(rules).map(([agentName, agentRules]) => (
                    <div key={agentName} className="space-y-4">
                        <div className="flex items-center gap-2 pb-2 border-b border-zinc-800"><h3 className="text-lg font-medium text-white capitalize">{agentName} Rules</h3></div>
                        <div className="grid gap-4">
                            {agentRules.map((rule: any, idx: number) => (
                                <div key={idx} className="bg-zinc-950 border border-zinc-800 rounded-lg p-5 flex items-start gap-4"><div className="w-8 h-8 rounded bg-blue-950/30 border border-blue-900/50 text-blue-400 flex items-center justify-center shrink-0"><ShieldCheck size={16} /></div><div><p className="text-sm text-zinc-300">"{rule.content}"</p><span className="text-xs text-zinc-600 mt-1 block uppercase">{rule.category}</span></div></div>
                            ))}
                        </div>
                    </div>
                ))}
             </div>
          )}
        </div>
      </main>
      {selectedIncident && <IncidentModal incident={selectedIncident} isOpen={!!selectedIncident} onClose={() => setSelectedIncident(null)} onResolve={() => handleIncidentResolved(selectedIncident.id)} />}
    </div>
  );
}

// Keep NavItem and IncidentCard (Same as before)
function NavItem({ icon, label, active, count, onClick }: any) {
  return <button onClick={onClick} className={cn("w-full flex items-center justify-between px-3 py-2 rounded-md text-sm transition-all", active ? "bg-zinc-900 text-white font-medium" : "text-zinc-400 hover:text-white hover:bg-zinc-900/50")}><div className="flex items-center gap-3">{icon}{label}</div>{count > 0 && <span className="bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full text-xs border border-red-500/20">{count}</span>}</button>;
}
function IncidentCard({ incident, onClick }: { incident: Incident, onClick: () => void }) {
    const isFastPath = incident.detection_source === 'FAST_PATH';
    const BadgeIcon = isFastPath ? Zap : BrainCircuit;
    const isResolved = incident.status === 'Resolved';
    return <div onClick={onClick} className={cn("group border rounded-lg p-5 transition-all cursor-pointer flex items-center justify-between", isResolved ? "bg-zinc-950/30 border-zinc-800 opacity-60" : "bg-zinc-950 border-zinc-800 hover:border-zinc-600")}><div className="flex items-start gap-4"><div className={cn("w-10 h-10 rounded-lg flex items-center justify-center shrink-0 border", isResolved ? "bg-green-950/30 border-green-900/50 text-green-500" : "bg-red-950/30 border-red-900/50 text-red-500")}>{isResolved ? <CheckCircle2 size={20} /> : <Activity size={20} />}</div><div><div className="flex items-center gap-2 mb-1"><h3 className={cn("text-base font-medium", isResolved ? "text-zinc-500 line-through" : "text-zinc-200")}>{incident.title}</h3><span className={cn("px-1.5 py-0.5 rounded text-[10px] font-mono uppercase border flex items-center gap-1", isFastPath ? "bg-amber-500/10 border-amber-500/20 text-amber-400" : "bg-blue-500/10 border-blue-500/20 text-blue-400")}><BadgeIcon size={10} />{incident.detection_source}</span></div><div className="flex items-center gap-4 text-sm text-zinc-500"><span className="font-mono">{incident.id}</span><span>•</span><span>{new Date(incident.timestamp).toLocaleTimeString()}</span></div></div></div><ChevronRight className="text-zinc-700 group-hover:text-zinc-400" /></div>;
}