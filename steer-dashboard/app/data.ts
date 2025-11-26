// app/data.ts

export type TraceStep = {
  id: string;
  type: 'user' | 'agent' | 'tool' | 'error' | 'success';
  title: string;
  content?: string;
  metadata?: Record<string, string>;
};

export type TeachingOption = {
  id: string;
  title: string;
  description: string;
  recommended?: boolean;
  logic_change: string; 
};

export type Incident = {
  id: string;
  title: string;
  
  // NEW: Dynamic Agent Name
  agent_name?: string; 
  
  status: 'Active' | 'Resolved';
  detection_source: 'FAST_PATH' | 'SLOW_PATH';
  detection_label: string;
  severity: 'High' | 'Medium' | 'Low';
  timestamp: string;
  
  metrics?: {
    faithfulness: number;
    relevance: number;
    context_precision: number; 
  };
  
  trace: TraceStep[];
  teaching_options: TeachingOption[]; 
};