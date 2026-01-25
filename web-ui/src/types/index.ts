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
