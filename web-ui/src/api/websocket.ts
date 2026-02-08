import { WebSocketMessage, AnalysisProgress } from '../types';

class WebSocketManager {
  private connections: Map<string, WebSocket> = new Map();
  private reconnectAttempts: Map<string, number> = new Map();
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  connect(url: string, name: string = 'default') {
    if (this.connections.has(name) && this.connections.get(name)?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log(`WebSocket connected: ${name}`);
      this.reconnectAttempts.set(name, 0);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        const { type, ...data } = message;
        this.emit(type, data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error: ${name}`, error);
    };

    ws.onclose = () => {
      console.log(`WebSocket closed: ${name}`);
      const attempts = this.reconnectAttempts.get(name) || 0;
      if (attempts < this.maxReconnectAttempts) {
        this.reconnectAttempts.set(name, attempts + 1);
        setTimeout(() => this.connect(url, name), this.reconnectDelay);
      }
    };

    this.connections.set(name, ws);
  }

  disconnect(name?: string) {
    if (name) {
      const ws = this.connections.get(name);
      if (ws) {
        ws.close();
        this.connections.delete(name);
      }
    } else {
      this.connections.forEach((ws) => ws.close());
      this.connections.clear();
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: (data: any) => void) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.delete(callback);
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach((callback) => callback(data));
    }
  }

  onAnalysisProgress(callback: (data: AnalysisProgress) => void) {
    this.on('analysis_progress', callback);
  }

  offAnalysisProgress(callback: (data: AnalysisProgress) => void) {
    this.off('analysis_progress', callback);
  }

  onAnalysisReport(callback: (data: { report: any }) => void) {
    this.on('analysis_report', callback);
  }

  offAnalysisReport(callback: (data: { report: any }) => void) {
    this.off('analysis_report', callback);
  }

  onCommandOutput(callback: (data: { output: string; command: string; mode: string }) => void) {
    this.on('command_output', callback);
  }

  offCommandOutput(callback: (data: { output: string; command: string; mode: string }) => void) {
    this.off('command_output', callback);
  }

  onNaturalLanguageOutput(callback: (data: { output: string; command: string; mode: string }) => void) {
    this.on('natural_language_output', callback);
  }

  offNaturalLanguageOutput(callback: (data: { output: string; command: string; mode: string }) => void) {
    this.off('natural_language_output', callback);
  }

  onSessionLoaded(callback: () => void) {
    this.on('session_loaded', callback);
  }

  offSessionLoaded(callback: () => void) {
    this.off('session_loaded', callback);
  }

  onSessionClosed(callback: () => void) {
    this.on('session_closed', callback);
  }

  offSessionClosed(callback: () => void) {
    this.off('session_closed', callback);
  }
}

export const wsManager = new WebSocketManager();
