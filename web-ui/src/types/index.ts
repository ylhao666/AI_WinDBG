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

export interface StackFrame {
  address: string;
  function: string;
  module: string;
  offset?: string;
  source_file?: string;
  line_number?: number;
}

export interface ModuleInfo {
  name: string;
  base_address: string;
  size: string;
  path?: string;
  version?: string;
  symbols_loaded?: boolean;
}

export interface ExceptionInfo {
  code: string;
  description: string;
  address?: string;
  flags?: string;
}

export interface AnalysisReport {
  summary: string;
  crash_type: string;
  exception_code: string;
  exception_address: string;
  exception_description: string;
  exception_info?: ExceptionInfo;
  call_stack?: StackFrame[];
  modules?: ModuleInfo[];
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

export interface AnalysisTask {
  task_id: string;
  status: AnalysisStatus;
  progress: number;
  message: string;
  result?: AnalysisReport;
  error?: string;
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
