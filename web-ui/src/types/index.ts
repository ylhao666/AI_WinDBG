export interface SessionStatus {
  state: string;
  dump_file: string | null;
  display_mode: string;
  session_active: boolean;
  session_pid: number | null;
  windbg_available: boolean;
}

export interface CommandResult {
  success: boolean;
  output: string;
  command: string;
  error?: string;
}

export interface AnalysisReport {
  summary: string;
  crash_type: string;
  exception_code: string;
  exception_address: string;
  exception_description: string;
  root_cause: string;
  suggestions: string[];
  confidence: number;
}

export enum AnalysisStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  ERROR = 'error',
  CANCELLED = 'cancelled'
}

export interface AnalysisProgress {
  task_id: string;
  status: AnalysisStatus;
  progress: number;
  message: string;
  result?: AnalysisReport;
  error?: string;
}

export interface AnalysisThinking {
  task_id: string;
  content: string;
  timestamp?: string;
}

export interface AnalysisTask {
  task_id: string;
  status: AnalysisStatus;
  progress: number;
  message: string;
  result?: AnalysisReport;
  error?: string;
  thinking_history: AnalysisThinking[];
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface Config {
  app_name: string;
  app_version: string;
  windbg_path: string;
  symbol_path: string;
  llm_provider: string;
  llm_model: string;
  web_enabled: boolean;
  web_port: number;
}

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface CommandHistoryItem {
  command: string;
  timestamp: string;
}
